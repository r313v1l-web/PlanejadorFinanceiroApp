import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    layout="wide", 
    page_title="Family Wealth Manager Pro", 
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 1. SISTEMA DE CONEXÃO E VALIDAÇÃO DE DADOS
# ============================================================================
@st.cache_data(ttl=300)  # Cache de 5 minutos
def carregar_dados():
    """Carrega e valida todos os dados das planilhas"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Estrutura completa das abas e suas colunas esperadas
        estrutura_abas = {
            "config": ["Chave", "Valor", "Descricao"],
            "investimentos": ["Instituicao", "Ativo", "Tipo", "Valor_Atual", 
                             "Data_Entrada", "Rendimento_Mensal", "Categoria", "Observacao"],
            "historico": ["Data", "Tipo", "Valor", "Categoria", 
                         "Subcategoria", "Descricao", "Responsavel", "Fixo"],
            "sonhos_projetos": ["Nome", "Descricao", "Valor_Alvo", "Valor_Atual", 
                               "Data_Alvo", "Prioridade", "Status", "Categoria"],
            "fluxo_fixo": ["Nome", "Valor", "Tipo", "Categoria", 
                          "Data_Inicio", "Data_Fim", "Recorrencia", "Observacao"],
            "categorias": ["Nome", "Tipo", "Orcamento_Mensal", "Cor"]
        }
        
        dados = {}
        
        for aba, colunas in estrutura_abas.items():
            try:
                df = conn.read(worksheet=aba, ttl=0)
                df = df.dropna(how='all')  # Remove linhas completamente vazias
                
                # Garante que todas as colunas existam
                for coluna in colunas:
                    if coluna not in df.columns:
                        df[coluna] = None
                
                # Conversões de tipos de dados
                if aba == "investimentos" and 'Valor_Atual' in df.columns:
                    df['Valor_Atual'] = pd.to_numeric(df['Valor_Atual'], errors='coerce').fillna(0)
                
                if aba == "historico" and 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
                
                if aba == "sonhos_projetos" and 'Valor_Alvo' in df.columns:
                    df['Valor_Alvo'] = pd.to_numeric(df['Valor_Alvo'], errors='coerce').fillna(0)
                    df['Valor_Atual'] = pd.to_numeric(df['Valor_Atual'], errors='coerce').fillna(0)
                
                if aba == "fluxo_fixo" and 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
                
                dados[aba] = df[colunas]  # Mantém apenas as colunas definidas
                
            except Exception as e:
                st.sidebar.warning(f"Aba {aba}: Criando estrutura vazia")
                dados[aba] = pd.DataFrame(columns=colunas)
        
        return dados, conn
        
    except Exception as e:
        st.error(f"Erro crítico ao conectar: {e}")
        return None, None

def salvar_dados(conn, aba, df):
    """Salva dados com tratamento de erro"""
    try:
        conn.update(worksheet=aba, data=df)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar {aba}: {e}")
        return False

# ============================================================================
# 2. MOTOR DE PROJEÇÃO AVANÇADO
# ============================================================================
def calcular_projecao(dados, meses=120):
    """
    Calcula projeção detalhada do patrimônio considerando:
    - Investimentos atuais
    - Fluxos fixos (com datas)
    - Rendimentos variáveis
    - Inflação
    - Metas específicas
    """
    
    # Configurações
    config = dict(zip(dados['config']['Chave'], dados['config']['Valor']))
    
    meta_final = float(config.get('meta_patrimonio', 1000000))
    rendimento_padrao = float(config.get('rendimento_mensal', 0.008))  # 0.8%
    inflacao_mensal = float(config.get('inflacao_mensal', 0.004))  # 0.4%
    
    # Preparar dados
    patrimonio_atual = dados['investimentos']['Valor_Atual'].sum()
    
    # Processar fluxos fixos
    fluxos = dados['fluxo_fixo'].copy()
    fluxos['Data_Inicio'] = pd.to_datetime(fluxos['Data_Inicio'], errors='coerce')
    fluxos['Data_Fim'] = pd.to_datetime(fluxos['Data_Fim'], errors='coerce')
    
    # Inicializar simulação
    resultados = []
    patrimonio = patrimonio_atual
    mes_atual = date.today().replace(day=1)
    
    # Preparar array para crescimento do patrimônio
    patrimonio_mensal = [patrimonio]
    datas_mensais = [mes_atual]
    fluxos_liquidos = [0]
    rendimentos_mensais = [0]
    
    for mes in range(1, meses + 1):
        data_simulada = mes_atual + relativedelta(months=mes)
        
        # 1. Calcular fluxo do mês (considerando datas)
        fluxo_mes = 0
        for _, fluxo in fluxos.iterrows():
            if pd.isnull(fluxo['Data_Inicio']) or fluxo['Data_Inicio'].date() <= data_simulada:
                if pd.isnull(fluxo['Data_Fim']) or fluxo['Data_Fim'].date() >= data_simulada:
                    valor = float(fluxo['Valor'] or 0)
                    if fluxo['Tipo'] == 'Receita':
                        fluxo_mes += valor
                    else:  # Despesa
                        fluxo_mes -= valor
        
        # 2. Calcular rendimento dos investimentos (com inflação)
        rendimento_mes = patrimonio * (rendimento_padrao - inflacao_mensal)
        
        # 3. Atualizar patrimônio
        patrimonio += fluxo_mes + rendimento_mes
        
        # 4. Verificar se atingiu metas de sonhos
        for _, sonho in dados['sonhos_projetos'].iterrows():
            if sonho['Status'] != 'Concluído' and patrimonio >= float(sonho.get('Valor_Alvo', 0)):
                # Deduzir valor do sonho realizado
                patrimonio -= float(sonho.get('Valor_Alvo', 0))
        
        # 5. Armazenar resultados
        patrimonio_mensal.append(patrimonio)
        datas_mensais.append(data_simulada)
        fluxos_liquidos.append(fluxo_mes)
        rendimentos_mensais.append(rendimento_mes)
        
        # 6. Parar se atingiu meta final
        if patrimonio >= meta_final and mes > 12:  # Pelo menos 1 ano
            break
    
    # Criar DataFrame de resultados
    df_resultados = pd.DataFrame({
        'Data': datas_mensais,
        'Patrimonio': patrimonio_mensal,
        'Fluxo_Liquido': fluxos_liquidos,
        'Rendimento': rendimentos_mensais,
        'Acumulado_Rendimentos': np.cumsum(rendimentos_mensais)
    })
    
    # Calcular estatísticas
    meses_para_meta = None
    if patrimonio >= meta_final:
        meses_para_meta = len(df_resultados) - 1
    
    return df_resultados, meses_para_meta, patrimonio_atual

# ============================================================================
# 3. FUNÇÕES DE ANÁLISE
# ============================================================================
def analisar_gastos(dados):
    """Analisa gastos por categoria e responsável"""
    if dados['historico'].empty:
        return pd.DataFrame()
    
    df = dados['historico'].copy()
    df['Data'] = pd.to_datetime(df['Data'])
    df['Mes'] = df['Data'].dt.to_period('M').astype(str)
    
    # Gastos por categoria (apenas despesas)
    gastos_categoria = df[df['Tipo'] == 'Despesa'].groupby('Categoria')['Valor'].sum().reset_index()
    gastos_categoria = gastos_categoria.sort_values('Valor', ascending=False)
    
    # Gastos por responsável
    gastos_responsavel = df[df['Tipo'] == 'Despesa'].groupby('Responsavel')['Valor'].sum().reset_index()
    
    # Tendência mensal
    tendencia = df[df['Tipo'] == 'Despesa'].groupby('Mes')['Valor'].sum().reset_index()
    
    return {
        'por_categoria': gastos_categoria,
        'por_responsavel': gastos_responsavel,
        'tendencia': tendencia
    }

def calcular_saldos(dados):
    """Calcula saldos atuais e projeções"""
    total_investido = dados['investimentos']['Valor_Atual'].sum()
    
    # Receitas do mês atual
    hoje = date.today()
    mes_atual = hoje.strftime('%Y-%m')
    
    if not dados['historico'].empty:
        df_hist = dados['historico'].copy()
        df_hist['Data'] = pd.to_datetime(df_hist['Data'])
        df_hist['Mes'] = df_hist['Data'].dt.strftime('%Y-%m')
        
        receitas_mes = df_hist[(df_hist['Mes'] == mes_atual) & (df_hist['Tipo'] == 'Receita')]['Valor'].sum()
        despesas_mes = df_hist[(df_hist['Mes'] == mes_atual) & (df_hist['Tipo'] == 'Despesa')]['Valor'].sum()
        saldo_mes = receitas_mes - despesas_mes
    else:
        receitas_mes = despesas_mes = saldo_mes = 0
    
    # Valor total dos sonhos
    total_sonhos = dados['sonhos_projetos']['Valor_Alvo'].sum()
    realizado_sonhos = dados['sonhos_projetos']['Valor_Atual'].sum()
    
    return {
        'patrimonio': total_investido,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'total_sonhos': total_sonhos,
        'realizado_sonhos': realizado_sonhos,
        'progresso_sonhos': (realizado_sonhos / total_sonhos * 100) if total_sonhos > 0 else 0
    }

# ============================================================================
# 4. INTERFACE PRINCIPAL
# ============================================================================
def main():
    # Carregar dados
    dados, conn = carregar_dados()
    
    if dados is None:
        st.error("Não foi possível carregar os dados. Verifique a conexão.")
        return
    
    # ========================================================================
    # BARRA LATERAL
    # ========================================================================
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/money-bag.png", width=80)
        st.title("💎 Family Wealth Pro")
        st.markdown("---")
        
        # Menu de navegação
        menu = st.radio(
            "Navegação",
            ["🏠 Dashboard", "📊 Análise Detalhada", "📝 Lançamentos", 
             "🎯 Sonhos & Metas", "💰 Investimentos", "🏢 Fluxos Fixos", 
             "⚙️ Configurações"],
            index=0
        )
        
        st.markdown("---")
        
        # Resumo rápido na sidebar
        saldos = calcular_saldos(dados)
        st.metric("Patrimônio Atual", f"R$ {saldos['patrimonio']:,.2f}")
        st.metric("Saldo do Mês", f"R$ {saldos['saldo_mes']:,.2f}")
        
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
    
    # ========================================================================
    # DASHBOARD PRINCIPAL
    # ========================================================================
    if menu == "🏠 Dashboard":
        st.title("📊 Dashboard Financeiro")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Patrimônio Total", 
                     f"R$ {saldos['patrimonio']:,.2f}",
                     delta=f"R$ {saldos['saldo_mes']:,.2f}")
        
        with col2:
            st.metric("Receitas Mês", 
                     f"R$ {saldos['receitas_mes']:,.2f}")
        
        with col3:
            st.metric("Despesas Mês", 
                     f"R$ {saldos['despesas_mes']:,.2f}")
        
        with col4:
            st.metric("Progresso Sonhos", 
                     f"{saldos['progresso_sonhos']:.1f}%")
        
        st.markdown("---")
        
        # Gráfico de Projeção
        st.subheader("🚀 Projeção do Patrimônio")
        
        df_projecao, meses_meta, patrimonio_atual = calcular_projecao(dados)
        
        if not df_projecao.empty:
            # Criar gráfico interativo
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Linha do patrimônio
            fig.add_trace(
                go.Scatter(x=df_projecao['Data'], y=df_projecao['Patrimonio'],
                          name="Patrimônio", line=dict(color='#00CC96', width=3)),
                secondary_y=False
            )
            
            # Barras de fluxo líquido
            fig.add_trace(
                go.Bar(x=df_projecao['Data'], y=df_projecao['Fluxo_Liquido'],
                      name="Fluxo Mensal", marker_color='#636EFA', opacity=0.6),
                secondary_y=True
            )
            
            # Meta
            meta = float(dict(zip(dados['config']['Chave'], dados['config']['Valor'])).get('meta_patrimonio', 1000000))
            fig.add_hline(y=meta, line_dash="dash", line_color="red",
                         annotation_text=f"Meta: R$ {meta:,.0f}")
            
            # Configurar layout
            fig.update_layout(
                title="Evolução do Patrimônio (10 anos)",
                xaxis_title="Data",
                yaxis_title="Patrimônio (R$)",
                hovermode="x unified",
                height=500
            )
            
            fig.update_yaxes(title_text="Fluxo Mensal (R$)", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas da projeção
            if meses_meta:
                st.success(f"🎯 **Meta atingida em {meses_meta} meses!**")
            
            with st.expander("📈 Detalhes da Projeção"):
                st.dataframe(df_projecao.style.format({
                    'Patrimonio': 'R$ {:,.2f}',
                    'Fluxo_Liquido': 'R$ {:,.2f}',
                    'Rendimento': 'R$ {:,.2f}'
                }))
        
        # Distribuição dos Investimentos
        st.subheader("📊 Composição do Patrimônio")
        
        if not dados['investimentos'].empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.pie(dados['investimentos'], values='Valor_Atual', 
                            names='Categoria', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    dados['investimentos'][['Instituicao', 'Ativo', 'Valor_Atual', 'Categoria']]
                    .sort_values('Valor_Atual', ascending=False)
                    .style.format({'Valor_Atual': 'R$ {:,.2f}'})
                )
    
    # ========================================================================
    # ANÁLISE DETALHADA
    # ========================================================================
    elif menu == "📊 Análise Detalhada":
        st.title("📊 Análise Financeira Detalhada")
        
        analise = analisar_gastos(dados)
        
        if not dados['historico'].empty:
            tab1, tab2, tab3 = st.tabs(["Por Categoria", "Por Responsável", "Tendência Mensal"])
            
            with tab1:
                if not analise['por_categoria'].empty:
                    fig = px.bar(analise['por_categoria'], x='Categoria', y='Valor',
                                color='Valor', color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                if not analise['por_responsavel'].empty:
                    fig = px.pie(analise['por_responsavel'], values='Valor', 
                                names='Responsavel', hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                if not analise['tendencia'].empty:
                    fig = px.line(analise['tendencia'], x='Mes', y='Valor',
                                 markers=True, title="Evolução de Gastos")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Exportar dados
            with st.expander("📥 Exportar Dados"):
                st.download_button(
                    label="Baixar Histórico Completo",
                    data=dados['historico'].to_csv(index=False).encode('utf-8'),
                    file_name="historico_financeiro.csv",
                    mime="text/csv"
                )
        else:
            st.info("Nenhum dado de histórico disponível para análise.")
    
    # ========================================================================
    # LANÇAMENTOS DIÁRIOS
    # ========================================================================
    elif menu == "📝 Lançamentos":
        st.title("📝 Registro de Transações")
        
        # Formulário de novo lançamento
        with st.form("form_lancamento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                data_transacao = st.date_input("Data da Transação", date.today())
                tipo_transacao = st.selectbox("Tipo", 
                    ["Despesa", "Receita", "Transferência", "Investimento"])
                valor = st.number_input("Valor (R$)", 
                    min_value=0.0, format="%.2f", step=10.0)
            
            with col2:
                # Categorias dinâmicas
                categorias = dados['categorias']['Nome'].tolist() if not dados['categorias'].empty else [
                    "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", 
                    "Educação", "Vestuário", "Serviços", "Investimentos", "Outros"
                ]
                categoria = st.selectbox("Categoria", categorias)
                
                subcategorias = {
                    "Alimentação": ["Supermercado", "Restaurante", "Delivery"],
                    "Transporte": ["Combustível", "Manutenção", "Transporte Público"],
                    "Moradia": ["Aluguel", "Condomínio", "Energia", "Água", "Internet"],
                }
                subcategoria = st.selectbox("Subcategoria (Opcional)", 
                    [""] + subcategorias.get(categoria, []))
                
                responsavel = st.radio("Responsável", 
                    ["Reinaldo", "Raquel", "Compartilhado"], horizontal=True)
            
            descricao = st.text_input("Descrição Detalhada")
            fixo = st.checkbox("É uma despesa/receita fixa?")
            
            col_botoes = st.columns([3, 1, 1])
            with col_botoes[0]:
                if st.form_submit_button("💾 Salvar Transação", use_container_width=True):
                    novo_registro = pd.DataFrame([{
                        "Data": data_transacao,
                        "Tipo": tipo_transacao,
                        "Valor": valor,
                        "Categoria": categoria,
                        "Subcategoria": subcategoria if subcategoria else None,
                        "Descricao": descricao,
                        "Responsavel": responsavel,
                        "Fixo": "Sim" if fixo else "Não"
                    }])
                    
                    # Adicionar à planilha
                    df_historico = pd.concat([dados['historico'], novo_registro], ignore_index=True)
                    if salvar_dados(conn, "historico", df_historico):
                        st.success("Transação registrada com sucesso!")
                        if fixo:
                            st.info("Considere adicionar esta transação como fixa na aba 'Fluxos Fixos'")
            
            with col_botoes[2]:
                if st.form_submit_button("🔄 Limpar", type="secondary", use_container_width=True):
                    pass
        
        st.markdown("---")
        
        # Histórico de transações
        st.subheader("📋 Histórico Recente")
        
        if not dados['historico'].empty:
            # Filtros
            col_filtros1, col_filtros2, col_filtros3 = st.columns(3)
            
            with col_filtros1:
                filtro_tipo = st.multiselect("Tipo", 
                    dados['historico']['Tipo'].unique(), default=["Despesa", "Receita"])
            
            with col_filtros2:
                filtro_categoria = st.multiselect("Categoria",
                    dados['historico']['Categoria'].unique())
            
            with col_filtros3:
                filtro_responsavel = st.multiselect("Responsável",
                    dados['historico']['Responsavel'].unique())
            
            # Aplicar filtros
            df_filtrado = dados['historico'].copy()
            
            if filtro_tipo:
                df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(filtro_tipo)]
            if filtro_categoria:
                df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(filtro_categoria)]
            if filtro_responsavel:
                df_filtrado = df_filtrado[df_filtrado['Responsavel'].isin(filtro_responsavel)]
            
            # Ordenar por data
            df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data'])
            df_filtrado = df_filtrado.sort_values('Data', ascending=False)
            
            # Exibir tabela
            st.dataframe(
                df_filtrado.head(50).style.format({'Valor': 'R$ {:,.2f}'}),
                use_container_width=True,
                height=400
            )
            
            # Resumo
            total_despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
            total_receitas = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
            saldo = total_receitas - total_despesas
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
            col_res2.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
            col_res3.metric("Saldo", f"R$ {saldo:,.2f}", 
                           delta_color="inverse" if saldo < 0 else "normal")
        else:
            st.info("Nenhuma transação registrada ainda.")
    
    # ========================================================================
    # SONHOS & METAS
    # ========================================================================
    elif menu == "🎯 Sonhos & Metas":
        st.title("🎯 Nossos Sonhos e Metas")
        
        # Formulário para novo sonho
        with st.expander("➕ Adicionar Novo Sonho", expanded=False):
            with st.form("form_sonho"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome_sonho = st.text_input("Nome do Sonho")
                    valor_alvo = st.number_input("Valor Necessário (R$)", 
                        min_value=0.0, format="%.2f", step=1000.0)
                    categoria_sonho = st.selectbox("Categoria",
                        ["Viagem", "Imóvel", "Automóvel", "Educação", 
                         "Lazer", "Emergência", "Outros"])
                
                with col2:
                    data_alvo = st.date_input("Data Alvo", 
                        date.today() + timedelta(days=365))
                    prioridade = st.select_slider("Prioridade",
                        options=["Baixa", "Média", "Alta", "Máxima"])
                    valor_atual = st.number_input("Valor Já Economizado (R$)",
                        min_value=0.0, format="%.2f", step=100.0)
                
                descricao = st.text_area("Descrição Detalhada")
                
                if st.form_submit_button("🎯 Adicionar Sonho"):
                    novo_sonho = pd.DataFrame([{
                        "Nome": nome_sonho,
                        "Descricao": descricao,
                        "Valor_Alvo": valor_alvo,
                        "Valor_Atual": valor_atual,
                        "Data_Alvo": data_alvo,
                        "Prioridade": prioridade,
                        "Status": "Em Andamento",
                        "Categoria": categoria_sonho
                    }])
                    
                    df_sonhos = pd.concat([dados['sonhos_projetos'], novo_sonho], ignore_index=True)
                    if salvar_dados(conn, "sonhos_projetos", df_sonhos):
                        st.success("Sonho adicionado com sucesso!")
        
        # Visualização dos sonhos
        if not dados['sonhos_projetos'].empty:
            # Calcular progresso
            df_sonhos = dados['sonhos_projetos'].copy()
            df_sonhos['Progresso'] = (df_sonhos['Valor_Atual'] / df_sonhos['Valor_Alvo'] * 100).round(1)
            df_sonhos['Faltam'] = df_sonhos['Valor_Alvo'] - df_sonhos['Valor_Atual']
            df_sonhos['Data_Alvo'] = pd.to_datetime(df_sonhos['Data_Alvo'])
            df_sonhos['Dias_Restantes'] = (df_sonhos['Data_Alvo'] - pd.Timestamp.today()).dt.days
            
            # Ordenar por prioridade e progresso
            ordem_prioridade = {"Máxima": 0, "Alta": 1, "Média": 2, "Baixa": 3}
            df_sonhos['Ordem_Prioridade'] = df_sonhos['Prioridade'].map(ordem_prioridade)
            df_sonhos = df_sonhos.sort_values(['Ordem_Prioridade', 'Progresso'], ascending=[True, False])
            
            # Exibir cards dos sonhos
            st.subheader("📋 Lista de Sonhos")
            
            for idx, sonho in df_sonhos.iterrows():
                with st.container():
                    col_icon, col_content, col_progress = st.columns([1, 4, 2])
                    
                    with col_icon:
                        emoji = "🔥" if sonho['Prioridade'] == "Máxima" else \
                                "⭐" if sonho['Prioridade'] == "Alta" else \
                                "📌" if sonho['Prioridade'] == "Média" else "📝"
                        st.markdown(f"<h1>{emoji}</h1>", unsafe_allow_html=True)
                    
                    with col_content:
                        st.markdown(f"**{sonho['Nome']}**")
                        st.caption(f"{sonho['Descricao']}")
                        st.write(f"**Valor:** R$ {sonho['Valor_Alvo']:,.2f} | "
                                f"**Alvo:** {sonho['Data_Alvo'].strftime('%d/%m/%Y')} | "
                                f"**Prioridade:** {sonho['Prioridade']}")
                    
                    with col_progress:
                        progresso = int(sonho['Progresso'])
                        st.progress(min(progresso / 100, 1.0))
                        st.write(f"**{progresso}%** (R$ {sonho['Valor_Atual']:,.2f} / R$ {sonho['Valor_Alvo']:,.2f})")
                        
                        if sonho['Dias_Restantes'] > 0:
                            st.caption(f"⏳ {sonho['Dias_Restantes']} dias restantes")
                        else:
                            st.caption("⏰ Prazo expirado")
                    
                    st.markdown("---")
            
            # Gráfico de progresso
            st.subheader("📈 Progresso dos Sonhos")
            
            fig = px.bar(df_sonhos, x='Nome', y='Progresso',
                        color='Prioridade', text='Progresso',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(yaxis_title="Progresso (%)", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            
            # Editor para atualizar valores
            with st.expander("✏️ Editar Sonhos"):
                df_editado = st.data_editor(
                    df_sonhos[['Nome', 'Valor_Atual', 'Status', 'Prioridade']],
                    use_container_width=True,
                    num_rows="dynamic"
                )
                
                if st.button("💾 Salvar Alterações"):
                    # Atualizar apenas os campos editados
                    for idx, row in df_editado.iterrows():
                        mask = dados['sonhos_projetos']['Nome'] == row['Nome']
                        dados['sonhos_projetos'].loc[mask, 'Valor_Atual'] = row['Valor_Atual']
                        dados['sonhos_projetos'].loc[mask, 'Status'] = row['Status']
                        dados['sonhos_projetos'].loc[mask, 'Prioridade'] = row['Prioridade']
                    
                    if salvar_dados(conn, "sonhos_projetos", dados['sonhos_projetos']):
                        st.success("Sonhos atualizados!")
        else:
            st.info("Nenhum sonho cadastrado ainda. Comece adicionando seu primeiro sonho!")
    
    # ========================================================================
    # INVESTIMENTOS
    # ========================================================================
    elif menu == "💰 Investimentos":
        st.title("💰 Gestão de Investimentos")
        
        # Visão geral dos investimentos
        if not dados['investimentos'].empty:
            total_investido = dados['investimentos']['Valor_Atual'].sum()
            st.metric("Total Investido", f"R$ {total_investido:,.2f}")
            
            # Distribuição por instituição
            st.subheader("🏦 Distribuição por Instituição")
            
            dist_instituicao = dados['investimentos'].groupby('Instituicao')['Valor_Atual'].sum().reset_index()
            fig = px.pie(dist_instituicao, values='Valor_Atual', names='Instituicao', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        # Editor de investimentos
        st.subheader("📝 Gerenciar Investimentos")
        
        with st.form("form_investimento"):
            col1, col2 = st.columns(2)
            
            with col1:
                instituicao = st.text_input("Instituição/Corretora")
                ativo = st.text_input("Ativo/Nome do Investimento")
                tipo_invest = st.selectbox("Tipo",
                    ["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro Direto", "CDB", "LCI/LCA", "Outros"])
            
            with col2:
                valor_atual = st.number_input("Valor Atual (R$)", 
                    min_value=0.0, format="%.2f", step=100.0)
                rendimento_mensal = st.number_input("Rendimento Mensal Esperado (%)",
                    min_value=0.0, max_value=100.0, value=0.8, step=0.1, format="%.2f")
                categoria_invest = st.selectbox("Categoria",
                    ["Conservador", "Moderado", "Arrojado", "Longo Prazo", "Curto Prazo"])
            
            data_entrada = st.date_input("Data de Entrada", date.today())
            observacao = st.text_area("Observações")
            
            if st.form_submit_button("💾 Adicionar Investimento"):
                novo_invest = pd.DataFrame([{
                    "Instituicao": instituicao,
                    "Ativo": ativo,
                    "Tipo": tipo_invest,
                    "Valor_Atual": valor_atual,
                    "Data_Entrada": data_entrada,
                    "Rendimento_Mensal": rendimento_mensal / 100,  # Converter para decimal
                    "Categoria": categoria_invest,
                    "Observacao": observacao
                }])
                
                df_investimentos = pd.concat([dados['investimentos'], novo_invest], ignore_index=True)
                if salvar_dados(conn, "investimentos", df_investimentos):
                    st.success("Investimento cadastrado!")
        
        # Tabela de investimentos
        if not dados['investimentos'].empty:
            st.subheader("📋 Carteira de Investimentos")
            
            df_display = dados['investimentos'].copy()
            st.dataframe(
                df_display.style.format({
                    'Valor_Atual': 'R$ {:,.2f}',
                    'Rendimento_Mensal': '{:.2%}'
                }),
                use_container_width=True
            )
            
            # Opção para editar em massa
            with st.expander("✏️ Editar em Massa"):
                df_editado = st.data_editor(
                    dados['investimentos'],
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Valor_Atual": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Rendimento_Mensal": st.column_config.NumberColumn(format="%.2f%%")
                    }
                )
                
                if st.button("💾 Salvar Alterações nos Investimentos"):
                    if salvar_dados(conn, "investimentos", df_editado):
                        st.success("Investimentos atualizados!")
                        st.rerun()
    
    # ========================================================================
    # FLUXOS FIXOS
    # ========================================================================
    elif menu == "🏢 Fluxos Fixos":
        st.title("🏢 Gestão de Fluxos Fixos")
        
        # Resumo dos fluxos
        if not dados['fluxo_fixo'].empty:
            total_receitas = dados['fluxo_fixo'][dados['fluxo_fixo']['Tipo'] == 'Receita']['Valor'].sum()
            total_despesas = dados['fluxo_fixo'][dados['fluxo_fixo']['Tipo'] == 'Despesa']['Valor'].sum()
            saldo_fixo = total_receitas - total_despesas
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Receitas Fixas Mensais", f"R$ {total_receitas:,.2f}")
            col2.metric("Despesas Fixas Mensais", f"R$ {total_despesas:,.2f}")
            col3.metric("Saldo Fixo Mensal", f"R$ {saldo_fixo:,.2f}")
        
        # Formulário para novo fluxo fixo
        with st.form("form_fluxo_fixo"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_fluxo = st.text_input("Nome do Item")
                valor_fluxo = st.number_input("Valor Mensal (R$)", 
                    min_value=0.0, format="%.2f", step=10.0)
                tipo_fluxo = st.selectbox("Tipo", ["Receita", "Despesa"])
                categoria_fluxo = st.selectbox("Categoria",
                    ["Salário", "Aluguel", "Educação", "Transporte", 
                     "Saúde", "Lazer", "Investimento", "Outros"])
            
            with col2:
                data_inicio = st.date_input("Data de Início", date.today())
                data_fim = st.date_input("Data de Término (Opcional)", 
                    value=None, help="Deixe em branco se for permanente")
                recorrencia = st.selectbox("Recorrência",
                    ["Mensal", "Anual", "Trimestral", "Semestral"])
                observacao_fluxo = st.text_area("Observações")
            
            if st.form_submit_button("💾 Adicionar Fluxo Fixo"):
                novo_fluxo = pd.DataFrame([{
                    "Nome": nome_fluxo,
                    "Valor": valor_fluxo,
                    "Tipo": tipo_fluxo,
                    "Categoria": categoria_fluxo,
                    "Data_Inicio": data_inicio,
                    "Data_Fim": data_fim,
                    "Recorrencia": recorrencia,
                    "Observacao": observacao_fluxo
                }])
                
                df_fluxos = pd.concat([dados['fluxo_fixo'], novo_fluxo], ignore_index=True)
                if salvar_dados(conn, "fluxo_fixo", df_fluxos):
                    st.success("Fluxo fixo adicionado!")
        
        # Tabela de fluxos fixos
        if not dados['fluxo_fixo'].empty:
            st.subheader("📋 Lista de Fluxos Fixos")
            
            # Converter datas para exibição
            df_display = dados['fluxo_fixo'].copy()
            df_display['Data_Inicio'] = pd.to_datetime(df_display['Data_Inicio']).dt.date
            df_display['Data_Fim'] = pd.to_datetime(df_display['Data_Fim']).dt.date
            
            # Adicionar coluna de status
            hoje = date.today()
            def verificar_status(data_fim):
                if pd.isnull(data_fim):
                    return "Ativo"
                elif data_fim >= hoje:
                    return "Ativo"
                else:
                    return "Expirado"
            
            df_display['Status'] = df_display['Data_Fim'].apply(verificar_status)
            
            st.dataframe(
                df_display.style.format({'Valor': 'R$ {:,.2f}'}),
                use_container_width=True
            )
            
            # Editor para edição
            with st.expander("✏️ Editar Fluxos Fixos"):
                df_editado = st.data_editor(
                    dados['fluxo_fixo'],
                    use_container_width=True,
                    num_rows="dynamic"
                )
                
                if st.button("💾 Salvar Alterações nos Fluxos"):
                    if salvar_dados(conn, "fluxo_fixo", df_editado):
                        st.success("Fluxos fixos atualizados!")
                        st.rerun()
    
    # ========================================================================
    # CONFIGURAÇÕES
    # ========================================================================
    elif menu == "⚙️ Configurações":
        st.title("⚙️ Configurações do Sistema")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "⚙️ Parâmetros", "📁 Categorias", "🔄 Backup", "📊 Estatísticas"
        ])
        
        with tab1:
            st.subheader("Parâmetros do Sistema")
            
            # Configurações principais
            config_padrao = [
                ["meta_patrimonio", "1000000", "Meta de patrimônio total"],
                ["rendimento_mensal", "0.008", "Rendimento mensal esperado (0.8% = 0.008)"],
                ["inflacao_mensal", "0.004", "Inflação mensal esperada (0.4% = 0.004)"],
                ["orcamento_mensal_total", "5000", "Orçamento mensal total"],
                ["email_notificacao", "", "Email para notificações"],
                ["moeda", "BRL", "Moeda padrão (BRL, USD, EUR)"]
            ]
            
            # Se não houver configurações, criar padrão
            if dados['config'].empty:
                dados['config'] = pd.DataFrame(config_padrao, columns=["Chave", "Valor", "Descricao"])
            
            df_config_editado = st.data_editor(
                dados['config'],
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 Salvar Configurações"):
                if salvar_dados(conn, "config", df_config_editado):
                    st.success("Configurações salvas!")
        
        with tab2:
            st.subheader("Gerenciar Categorias")
            
            # Categorias padrão
            categorias_padrao = [
                {"Nome": "Alimentação", "Tipo": "Despesa", "Orcamento_Mensal": 1000, "Cor": "#1f77b4"},
                {"Nome": "Transporte", "Tipo": "Despesa", "Orcamento_Mensal": 500, "Cor": "#ff7f0e"},
                {"Nome": "Moradia", "Tipo": "Despesa", "Orcamento_Mensal": 2000, "Cor": "#2ca02c"},
                {"Nome": "Lazer", "Tipo": "Despesa", "Orcamento_Mensal": 300, "Cor": "#d62728"},
                {"Nome": "Saúde", "Tipo": "Despesa", "Orcamento_Mensal": 400, "Cor": "#9467bd"},
                {"Nome": "Educação", "Tipo": "Despesa", "Orcamento_Mensal": 600, "Cor": "#8c564b"},
                {"Nome": "Salário", "Tipo": "Receita", "Orcamento_Mensal": 0, "Cor": "#e377c2"},
                {"Nome": "Investimentos", "Tipo": "Receita", "Orcamento_Mensal": 0, "Cor": "#7f7f7f"},
            ]
            
            if dados['categorias'].empty:
                dados['categorias'] = pd.DataFrame(categorias_padrao)
            
            df_categorias_editado = st.data_editor(
                dados['categorias'],
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 Salvar Categorias"):
                if salvar_dados(conn, "categorias", df_categorias_editado):
                    st.success("Categorias salvas!")
        
        with tab3:
            st.subheader("Backup e Restauração")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📥 Exportar Dados")
                st.download_button(
                    label="Exportar Tudo (Excel)",
                    data=pd.ExcelWriter("backup_financeiro.xlsx", engine='openpyxl'),
                    file_name="backup_financeiro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                for aba in dados.keys():
                    st.download_button(
                        label=f"Exportar {aba} (CSV)",
                        data=dados[aba].to_csv(index=False).encode('utf-8'),
                        file_name=f"{aba}.csv",
                        mime="text/csv",
                        key=f"export_{aba}"
                    )
            
            with col2:
                st.markdown("### ⚠️ Limpar Dados")
                st.warning("Esta ação não pode ser desfeita!")
                
                if st.button("🗑️ Limpar Histórico", type="secondary"):
                    dados['historico'] = pd.DataFrame(columns=dados['historico'].columns)
                    if salvar_dados(conn, "historico", dados['historico']):
                        st.success("Histórico limpo!")
                
                if st.button("🔄 Restaurar Padrões", type="secondary"):
                    st.info("Funcionalidade em desenvolvimento")
        
        with tab4:
            st.subheader("Estatísticas do Sistema")
            
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.metric("Total de Transações", len(dados['historico']))
                st.metric("Total de Sonhos", len(dados['sonhos_projetos']))
                st.metric("Fluxos Fixos Ativos", 
                         len(dados['fluxo_fixo'][dados['fluxo_fixo']['Data_Fim'].isna() | 
                                               (pd.to_datetime(dados['fluxo_fixo']['Data_Fim']) >= pd.Timestamp.today())]))
            
            with col_stat2:
                st.metric("Categorias Definidas", len(dados['categorias']))
                st.metric("Investimentos Ativos", len(dados['investimentos']))
                st.metric("Primeiro Registro", 
                         pd.to_datetime(dados['historico']['Data']).min().strftime('%d/%m/%Y') 
                         if not dados['historico'].empty else "N/A")
            
            # Uso do sistema
            st.markdown("### 📈 Uso do Sistema")
            if not dados['historico'].empty:
                df_hist = dados['historico'].copy()
                df_hist['Data'] = pd.to_datetime(df_hist['Data'])
                df_hist['Mes'] = df_hist['Data'].dt.to_period('M').astype(str)
                
                uso_mensal = df_hist.groupby('Mes').size().reset_index(name='Transacoes')
                fig = px.line(uso_mensal, x='Mes', y='Transacoes', markers=True)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# EXECUÇÃO
# ============================================================================
if __name__ == "__main__":
    # Verificar dependências
    try:
        main()
    except Exception as e:
        st.error(f"Erro crítico: {e}")
        st.info("Verifique se todas as dependências estão instaladas:")
        st.code("""
        pip install streamlit pandas numpy plotly python-dateutil streamlit-gsheets
        """)
        
        if st.button("Tentar Novamente"):
            st.rerun()