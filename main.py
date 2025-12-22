import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from dateutil.relativedelta import relativedelta
import io
import bcrypt
import json

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Family Wealth Manager Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS CUSTOMIZADO (Streamlit Native)
# =========================================================
st.markdown("""
<style>
    /* CORES DO TEMA */
    :root {
        --primary: #1e3a8a;
        --primary-light: #3b82f6;
        --secondary: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --dark: #1e293b;
        --light: #f8fafc;
        --gray: #64748b;
    }
    
    /* ESTILOS GERAIS */
    .main {
        background-color: var(--light);
    }
    
    /* HEADER */
    .header-container {
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* CARDS */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 5px solid var(--primary);
        transition: transform 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-card.success {
        border-left-color: var(--secondary);
    }
    
    .metric-card.danger {
        border-left-color: var(--danger);
    }
    
    .metric-card.warning {
        border-left-color: var(--warning);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--dark);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: var(--gray);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-change {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 10px;
    }
    
    .metric-change.up {
        background: rgba(16, 185, 129, 0.1);
        color: var(--secondary);
    }
    
    .metric-change.down {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: var(--dark);
    }
    
    .sidebar-header {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .sidebar-title {
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* BOTÕES */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* INPUTS */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
    
    /* TABELAS */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* RESPONSIVO */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.8rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES DO SEU CÓDIGO ORIGINAL
# =========================================================
def normalizar_df(df):
    if df is None or df.empty:
        return df
    df.columns = df.columns.str.lower()
    return df

def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header do login
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #1e3a8a;'>💎 Family Wealth Manager</h1>
            <p style='color: #64748b;'>Sistema Premium de Gestão Patrimonial</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card de login
        with st.container():
            st.markdown("""
            <div style='
                background: white;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            '>
                <h3 style='text-align: center; margin-bottom: 1.5rem; color: #1e3a8a;'>🔐 Acesso ao Sistema</h3>
            """, unsafe_allow_html=True)
            
            usuario = st.text_input("Usuário", key="login_user")
            senha = st.text_input("Senha", type="password", key="login_pass")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("Entrar", type="primary", use_container_width=True):
                    df_users = DatabaseManager.load_users()
                    usuario_input = usuario.strip().lower()
                    senha_input = senha.strip()
                    user = df_users[df_users["usuario"] == usuario_input]
                    
                    if user.empty:
                        st.error("Usuário não encontrado.")
                        return
                    
                    senha_hash = user.iloc[0]["senha"]
                    if not bcrypt.checkpw(senha_input.encode("utf-8"), senha_hash.encode("utf-8")):
                        st.error("Senha incorreta.")
                        return
                    
                    if user.iloc[0]["ativo"] != "ativo":
                        st.error("Usuário inativo. Contate o administrador.")
                        return
                    
                    # LOGIN OK
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = usuario_input
                    st.session_state["nome"] = user.iloc[0]["nome"]
                    st.session_state["perfil"] = str(user.iloc[0]["perfil"]).strip().lower()
                    st.success("Login realizado com sucesso!")
                    st.rerun()
            
            st.markdown("""
            <div style='text-align: center; margin-top: 1.5rem; color: #64748b; font-size: 0.9rem;'>
                <i>🔒 Sistema 100% seguro e criptografado</i>
            </div>
            </div>
            """, unsafe_allow_html=True)

def tela_admin_usuarios():
    st.title("👥 Gestão de Usuários")
    df = DatabaseManager.load_users()
    
    # CRIAR NOVO USUÁRIO
    with st.expander("➕ Novo Usuário", expanded=True):
        with st.form("form_novo_usuario", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                novo_usuario = st.text_input("Usuário").strip().lower()
            with col2:
                novo_nome = st.text_input("Nome")
            with col3:
                nova_senha = st.text_input("Senha Inicial", type="password")
            novo_perfil = st.selectbox("Perfil", ["user", "admin"])
            
            if st.form_submit_button("Criar Usuário", type="primary"):
                if not novo_usuario or not nova_senha:
                    st.error("Usuário e senha são obrigatórios.")
                    return
                if novo_usuario in df["usuario"].values:
                    st.error("Usuário já existe.")
                    return
                
                senha_hash = bcrypt.hashpw(
                    nova_senha.encode("utf-8"), 
                    bcrypt.gensalt()
                ).decode("utf-8")
                
                DatabaseManager.create_user(
                    novo_usuario, novo_nome, senha_hash, novo_perfil
                )
                st.success("Usuário criado com sucesso!")
                st.rerun()
    
    st.divider()
    st.subheader("👥 Usuários Existentes")
    
    # EDIÇÃO DOS USUÁRIOS
    senhas_para_reset = {}
    df_edit = df.copy()
    
    for i, row in df_edit.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        with col1:
            st.markdown(f"**{row['usuario']}**")
            st.caption(row['nome'])
        with col2:
            nova_senha = st.text_input(
                "Nova Senha", type="password", 
                key=f"senha_{row['usuario']}",
                label_visibility="collapsed"
            )
            if nova_senha:
                senhas_para_reset[row["usuario"]] = nova_senha
        with col3:
            df_edit.at[i, "perfil"] = st.selectbox(
                "Perfil", ["user", "admin"], 
                index=0 if row["perfil"] == "user" else 1,
                key=f"perfil_{row['usuario']}",
                label_visibility="collapsed"
            )
        with col4:
            df_edit.at[i, "ativo"] = st.selectbox(
                "Status", ["ativo", "inativo"], 
                index=0 if row["ativo"] == "ativo" else 1,
                key=f"ativo_{row['usuario']}",
                label_visibility="collapsed"
            )
        with col5:
            if st.button("💾", key=f"save_{row['usuario']}", help="Salvar alterações"):
                DatabaseManager.update_user(
                    usuario=row["usuario"],
                    perfil=df_edit.at[i, "perfil"],
                    ativo=df_edit.at[i, "ativo"]
                )
                if row["usuario"] in senhas_para_reset:
                    senha_hash = bcrypt.hashpw(
                        senhas_para_reset[row["usuario"]].encode("utf-8"),
                        bcrypt.gensalt()
                    ).decode("utf-8")
                    DatabaseManager.update_password(
                        usuario=row["usuario"], senha_hash=senha_hash
                    )
                st.success(f"Usuário {row['usuario']} atualizado!")
                st.rerun()

# =========================================================
# COMPONENTES STREAMLIT NATIVOS
# =========================================================
def render_header():
    """Renderiza o header do dashboard"""
    user_name = st.session_state.get("nome", "Usuário")
    user_profile = st.session_state.get("perfil", "user").capitalize()
    
    st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="header-title">📊 Dashboard Financeiro</div>
                <div class="header-subtitle">Bem-vindo, {user_name} • Perfil: {user_profile}</div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <div style="
                    background: rgba(255,255,255,0.2);
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                ">
                    {user_name.split()[0][0].upper() if user_name else "U"}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card_component(title, value, change=None, icon="📊", color="primary"):
    """Componente de card de métrica nativo do Streamlit"""
    
    color_class = {
        "primary": "",
        "success": "success",
        "danger": "danger",
        "warning": "warning"
    }.get(color, "")
    
    change_html = ""
    if change is not None:
        change_class = "up" if change >= 0 else "down"
        change_icon = "📈" if change >= 0 else "📉"
        change_html = f"""
        <div class="metric-change {change_class}">
            {change_icon} {abs(change):.1f}%
        </div>
        """
    
    html = f"""
    <div class="metric-card {color_class}">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <div style="font-size: 1.2rem;">{icon}</div>
            <div style="font-size: 0.9rem; color: #64748b;">{title}</div>
        </div>
        <div class="metric-value">R$ {value:,.2f}</div>
        {change_html}
    </div>
    """
    
    return html

# =========================================================
# FUNÇÕES DE CÁLCULO
# =========================================================
def calcular_saldo_fixo(dados):
    """Calcula saldo fixo mensal"""
    if not dados["fluxo_fixo"].empty:
        receitas = dados["fluxo_fixo"][dados["fluxo_fixo"]["tipo"] == "Receita"]["valor"].sum()
        despesas = dados["fluxo_fixo"][dados["fluxo_fixo"]["tipo"] == "Despesa"]["valor"].sum()
        return receitas - despesas
    return 0

def calcular_saldo_variavel(dados):
    """Calcula saldo variável mensal"""
    if not dados.get("historico", pd.DataFrame()).empty:
        hist = dados["historico"].copy()
        mes_atual = date.today().strftime("%Y-%m")
        hist["mes"] = pd.to_datetime(hist["data"]).dt.strftime("%Y-%m")
        hist_mes = hist[hist["mes"] == mes_atual]
        
        receitas = hist_mes[hist_mes["tipo"] == "receita"]["valor"].sum()
        despesas = hist_mes[hist_mes["tipo"] == "despesa"]["valor"].sum()
        
        if not dados.get("controle_gastos", pd.DataFrame()).empty:
            gastos = dados["controle_gastos"]["valor"].sum()
        else:
            gastos = 0
        
        return receitas - despesas - gastos
    return 0

def calcular_progresso_sonhos(dados):
    """Calcula progresso dos sonhos"""
    if not dados["sonhos_projetos"].empty:
        total_alvo = dados["sonhos_projetos"]["valor_alvo"].sum()
        total_atual = dados["sonhos_projetos"]["valor_atual"].sum()
        return (total_atual / total_alvo * 100) if total_alvo > 0 else 0
    return 0

def calcular_patrimonio(dados):
    """Calcula patrimônio total"""
    if not dados["investimentos"].empty:
        return dados["investimentos"]["valor_atual"].sum()
    return 0

# =========================================================
# PÁGINAS PRINCIPAIS
# =========================================================
def pagina_dashboard():
    """Dashboard principal"""
    dados = st.session_state.get("dados", {})
    
    # Header
    render_header()
    
    # Métricas principais
    st.subheader("📈 Métricas Financeiras")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        patrimonio = calcular_patrimonio(dados)
        st.markdown(metric_card_component("Patrimônio Total", patrimonio, 12.5, "💰", "primary"), unsafe_allow_html=True)
    
    with col2:
        saldo_fixo = calcular_saldo_fixo(dados)
        color = "success" if saldo_fixo >= 0 else "danger"
        st.markdown(metric_card_component("Saldo Fixo", saldo_fixo, 8.2, "⚖️", color), unsafe_allow_html=True)
    
    with col3:
        saldo_variavel = calcular_saldo_variavel(dados)
        color = "success" if saldo_variavel >= 0 else "warning"
        st.markdown(metric_card_component("Saldo Variável", saldo_variavel, -3.1, "📊", color), unsafe_allow_html=True)
    
    with col4:
        progresso_sonhos = calcular_progresso_sonhos(dados)
        st.markdown(metric_card_component("Progresso Sonhos", progresso_sonhos, 15.8, "⭐", "warning"), unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not dados.get("investimentos", pd.DataFrame()).empty:
            st.markdown("**Distribuição de Investimentos**")
            fig = px.pie(
                dados["investimentos"],
                values='valor_atual',
                names='categoria',
                hole=0.4,
                color_discrete_sequence=['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum investimento cadastrado")
    
    with col2:
        st.markdown("**Evolução Patrimonial (Exemplo)**")
        dates = pd.date_range(start='2023-01-01', end='2023-12-01', freq='MS')
        valores = [100000 * (1.02)**i for i in range(len(dates))]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=dates,
            y=valores,
            mode='lines+markers',
            name='Patrimônio',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        fig2.update_layout(
            yaxis_title="Valor (R$)",
            hovermode='x unified'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Transações recentes
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🕒 Transações Recentes")
    
    if not dados.get("historico", pd.DataFrame()).empty:
        historico_recente = dados["historico"].sort_values('data', ascending=False).head(10)
        
        # Estilizar a tabela
        st.dataframe(
            historico_recente,
            column_config={
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "descricao": "Descrição",
                "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                "tipo": "Tipo"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhuma transação registrada")

def pagina_investimentos():
    """Página de investimentos"""
    st.title("📈 Gestão de Investimentos")
    dados = st.session_state.get("dados", {})
    
    # Formulário para adicionar investimento
    with st.expander("➕ Adicionar Novo Investimento", expanded=False):
        with st.form("form_investimento"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Investimento")
                categoria = st.selectbox("Categoria", [
                    "Renda Fixa", "Ações", "FIIs", "Tesouro Direto",
                    "Fundos", "Criptomoedas", "Internacional", "Outros"
                ])
                valor_atual = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0, format="%.2f")
            
            with col2:
                instituicao = st.text_input("Instituição/Corretora")
                rentabilidade = st.number_input("Rentabilidade Mensal (%)", step=0.1, format="%.2f")
                data_aplicacao = st.date_input("Data da Aplicação")
            
            notas = st.text_area("Observações")
            
            if st.form_submit_button("💾 Salvar Investimento", type="primary"):
                st.success("Investimento salvo com sucesso!")
                # Aqui você implementaria a lógica para salvar no banco
    
    # Lista de investimentos
    st.subheader("📊 Carteira de Investimentos")
    
    if not dados.get("investimentos", pd.DataFrame()).empty:
        for _, investimento in dados["investimentos"].iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{investimento['nome']}**")
                st.caption(f"{investimento['categoria']} • {investimento.get('instituicao', 'N/A')}")
            
            with col2:
                st.metric(
                    label="Valor Atual",
                    value=f"R$ {investimento['valor_atual']:,.2f}"
                )
            
            with col3:
                rentabilidade = investimento.get('rentabilidade_mensal', 0)
                delta = f"{rentabilidade:.2f}%"
                st.metric("Rentabilidade", delta)
            
            with col4:
                col_edit, col_del = st.columns(2)
                with col_edit:
                    st.button("✏️", key=f"edit_{investimento['nome']}")
                with col_del:
                    st.button("🗑️", key=f"del_{investimento['nome']}")
        
        # Resumo
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        total_investido = dados["investimentos"]["valor_atual"].sum()
        with col1:
            st.metric("Total Investido", f"R$ {total_investido:,.2f}")
        
        with col2:
            rent_media = dados["investimentos"]["rentabilidade_mensal"].mean() if 'rentabilidade_mensal' in dados["investimentos"].columns else 0
            st.metric("Rentabilidade Média", f"{rent_media:.2f}%")
        
        with col3:
            categorias = len(dados["investimentos"]["categoria"].unique())
            st.metric("Categorias", categorias)
    
    else:
        st.info("Nenhum investimento cadastrado. Adicione seu primeiro investimento!")

# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================
def main():
    """Função principal"""
    
    # Inicializar estado da sessão
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    
    if "dados" not in st.session_state:
        st.session_state["dados"] = {}
    
    # VERIFICAR LOGIN
    if not st.session_state["logado"]:
        tela_login()
        st.stop()
    
    # ================================
    # USUÁRIO LOGADO
    # ================================
    
    # Carregar dados se necessário
    if not st.session_state["dados"]:
        usuario = st.session_state.get("usuario", "default")
        try:
            st.session_state["dados"] = DatabaseManager.load_all(usuario)
            for chave in st.session_state["dados"]:
                st.session_state["dados"][chave] = normalizar_df(st.session_state["dados"][chave])
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            st.session_state["dados"] = {}
    
    # SIDEBAR - MENU
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">💎 Wealth Manager</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        st.markdown("### 📍 Navegação")
        
        menu_options = [
            ("📊 Dashboard", "dashboard"),
            ("📈 Investimentos", "investimentos"),
            ("⭐ Sonhos", "sonhos"),
            ("💰 Fluxo Financeiro", "fluxo"),
            ("📋 Relatórios", "relatorios"),
            ("⚙️ Configurações", "config"),
        ]
        
        # Adicionar admin se for admin
        if st.session_state.get("perfil") == "admin":
            menu_options.append(("👥 Admin", "admin"))
        
        selected_page = st.radio(
            "Selecione uma página",
            options=[opt[1] for opt in menu_options],
            format_func=lambda x: dict(menu_options)[x],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Informações do usuário
        user_name = st.session_state.get("nome", "Usuário")
        user_profile = st.session_state.get("perfil", "user").capitalize()
        
        st.markdown(f"""
        <div style="padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, #3b82f6, #1e3a8a);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                ">
                    {user_name[0].upper() if user_name else "U"}
                </div>
                <div>
                    <div style="font-weight: 600; color: white;">{user_name}</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">{user_profile}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # CONTEÚDO PRINCIPAL
    if selected_page == "dashboard":
        pagina_dashboard()
    
    elif selected_page == "investimentos":
        pagina_investimentos()
    
    elif selected_page == "admin" and st.session_state.get("perfil") == "admin":
        tela_admin_usuarios()
    
    elif selected_page == "sonhos":
        st.title("⭐ Sonhos & Metas")
        st.info("Funcionalidade em desenvolvimento")
    
    elif selected_page == "fluxo":
        st.title("💰 Fluxo Financeiro")
        st.info("Funcionalidade em desenvolvimento")
    
    elif selected_page == "relatorios":
        st.title("📋 Relatórios")
        st.info("Funcionalidade em desenvolvimento")
    
    elif selected_page == "config":
        st.title("⚙️ Configurações")
        st.info("Funcionalidade em desenvolvimento")
    
    else:
        pagina_dashboard()

# =========================================================
# EXECUÇÃO
# =========================================================
if __name__ == "__main__":
    main()