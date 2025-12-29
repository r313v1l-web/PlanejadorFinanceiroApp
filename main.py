import streamlit as st

import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px

from database import DatabaseManager
from dateutil.relativedelta import relativedelta

import io
import os
import bcrypt


# Adicione este CSS no início do arquivo, logo após os outros estilos

st.markdown("""
<style>
/* ====== ESTILOS COMPACTOS PARA LISTAS ====== */

/* Container compacto para itens */
.compact-item {
    border: 1px solid #1f2933;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    background-color: #111827;
    transition: all 0.2s;
}

.compact-item:hover {
    background-color: #1f2933;
    border-color: #3b82f6;
}

/* Layout de colunas mais compacto */
.compact-grid {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 2px 0;
}

/* Espaçamento reduzido entre itens */
.compact-divider {
    margin: 4px 0;
    border: none;
    border-top: 1px solid #1f2933;
}

/* Botões compactos */
.compact-button {
    padding: 2px 8px !important;
    margin: 0 !important;
    min-height: 28px !important;
}

/* Texto compacto */
.compact-text {
    font-size: 0.9em !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

/* Cabeçalhos compactos */
.compact-header {
    font-size: 1em !important;
    margin: 8px 0 4px 0 !important;
}

/* Contêiner sem margens extras */
.no-margin-container {
    padding: 0 !important;
    margin: 0 !important;
}

/* Linhas alternadas para melhor legibilidade */
.compact-row:nth-child(even) {
    background-color: #0f172a;
}

.compact-row:nth-child(odd) {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)



# =========================================================
# NORMALIZADOR
# =========================================================


def normalizar_df(df):
    if df is None or df.empty:
        return df
    df.columns = df.columns.str.lower()
    return df


# =========================================================
# AUTENTICAÇÃO
# =========================================================



def tela_login():
    import os
    import requests
    
    # Container principal centralizado
    col_esq, col_centro, col_dir = st.columns([1, 1.5, 1])
    
    with col_centro:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        
        # 🔥 LOGO - URL CORRETA do GitHub Raw
        github_logo_url = "https://raw.githubusercontent.com/r313v1l-web/PlanejadorFinanceiroApp/main/assets/images/logo.png"
        
        # Container especial para a logo
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        
        # Verificar se a URL funciona
        try:
            response = requests.head(github_logo_url, timeout=3)
            if response.status_code == 200:
                # URL funciona - mostrar logo
                st.markdown(f"""
                <div style="text-align: center; margin: 0 auto 20px auto;">
                    <img src="{github_logo_url}" 
                         style="width: 180px; height: 180px; 
                                object-fit: contain; 
                                border-radius: 50%;
                                padding: 10px;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                </div>
                """, unsafe_allow_html=True)
            else:
                # URL não funciona - usar placeholder
                st.markdown("""
                <div style="text-align: center; margin: 0 auto 20px auto;">
                    <div style="width: 180px; height: 180px; 
                                border-radius: 50%;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                margin: 0 auto;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                        <span style="color: white; font-size: 48px; font-weight: bold;">💎</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.info("Logo carregando...")
        except:
            # Erro na conexão
            st.markdown("""
            <div style="text-align: center; margin: 0 auto 20px auto;">
                <div style="width: 180px; height: 180px; 
                            border-radius: 50%;
                            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                            margin: 0 auto;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);">
                    <span style="color: white; font-size: 48px; font-weight: bold;">💰</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # TÍTULO
        st.markdown("""
        <h2 style="text-align: center; color: #ffffff !important; margin-bottom: 5px;">
            Gestão Financeira
        </h2>
        <p style="text-align: center; color: #e2e8f0 !important; margin-bottom: 25px;">
            Sistema de Controle Patrimonial
        </p>
        """, unsafe_allow_html=True)
        
        # CAMPOS DO FORMULÁRIO
        with st.container():
            usuario = st.text_input("👤 Usuário", key="login_user")
            senha = st.text_input("🔒 Senha", type="password", key="login_pass")
        
        # Espaçamento
        st.markdown("<br>", unsafe_allow_html=True)
        
        # BOTÃO DE LOGIN
        if st.button("🚀 Entrar no Sistema", type="primary", use_container_width=True):
            usuario_input = usuario.strip().lower()
            senha_input = senha.strip()
            
            # 🔥 MUDANÇA AQUI: Busca direto no banco apenas esse usuário
            user = DatabaseManager.get_user_by_username(usuario_input)
            
            if user.empty:
                st.error("❌ Usuário não encontrado.")
                return
            
            senha_hash = user.iloc[0]["senha"]
            
            if not bcrypt.checkpw(
                senha_input.encode("utf-8"),
                senha_hash.encode("utf-8")
            ):
                st.error("❌ Senha incorreta.")
                return
            
            if user.iloc[0]["ativo"] != "ativo":
                st.error("⛔ Usuário inativo. Contate o administrador.")
                return
            
            # LOGIN OK
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario_input
            st.session_state["nome"] = user.iloc[0]["nome"]
            st.session_state["perfil"] = str(user.iloc[0]["perfil"]).strip().lower()
            
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        
        # Rodapé do card
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 14px; margin-top: 20px;'>
            <hr style='margin: 20px 0; opacity: 0.3;'>
            <p>🔐 Sistema seguro • v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Fecha login-card



def tela_admin_usuarios():
    st.markdown("👥 Gestão de Usuários")

    df = DatabaseManager.list_all_users()

    # ===============================
    # ➕ CRIAR NOVO USUÁRIO
    # ===============================
    st.subheader("➕ Novo Usuário")

    with st.form("form_novo_usuario", clear_on_submit=True):
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            novo_usuario = st.text_input("Usuário").strip().lower()
        with col2:
            novo_nome = st.text_input("Nome")
        with col3:
            nova_senha = st.text_input("Senha Inicial", type="password")

        novo_perfil = st.selectbox("Perfil", ["user", "admin"])

        if st.form_submit_button("Criar Usuário"):
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

            # ✅ AQUI É O LUGAR CORRETO
            DatabaseManager.create_user(
                novo_usuario,
                novo_nome,
                senha_hash,
                novo_perfil
            )

            st.success("Usuário criado com sucesso.")
            st.rerun()

    st.divider()
    st.subheader("Usuários Existentes")

    # ===============================
    # EDIÇÃO DOS USUÁRIOS
    # ===============================
    senhas_para_reset = {}
    df_edit = df.copy()

    for i, row in df_edit.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2] , gap="large")

        with col1:
            st.write(f"**{row['usuario']}** ({row['nome']})")

        with col2:
            nova_senha = st.text_input(
                "Nova Senha",
                type="password",
                key=f"senha_{row['usuario']}"
            )
            if nova_senha:
                senhas_para_reset[row["usuario"]] = nova_senha
                st.warning("Senha será atualizada ao salvar.")

        with col3:
            df_edit.at[i, "perfil"] = st.selectbox(
                "Perfil",
                ["user", "admin"],
                index=0 if row["perfil"] == "user" else 1,
                key=f"perfil_{row['usuario']}"
            )

        with col4:
            df_edit.at[i, "ativo"] = st.selectbox(
                "status",
                ["ativo", "inativo"],
                index=0 if row["ativo"] == "ativo" else 1,
                key=f"ativo_{row['usuario']}"
            )

    if st.button("💾 Salvar Alterações"):

        for _, row in df_edit.iterrows():

            # Atualizar perfil e status
            DatabaseManager.update_user(
                usuario=row["usuario"],
                perfil=row["perfil"],
                ativo=row["ativo"]
            )

            # Atualizar senha (se houve reset)
            if row["usuario"] in senhas_para_reset:
                senha_hash = bcrypt.hashpw(
                    senhas_para_reset[row["usuario"]].encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                DatabaseManager.update_password(
                    usuario=row["usuario"],
                    senha_hash=senha_hash
                )

        st.success("Usuários atualizados.")
        st.rerun()



# =========================================================
# TELA DE ONBOARDING (PRIMEIRO ACESSO)
# =========================================================
def verificar_e_mostrar_onboarding(dados, usuario):
    # Verifica se existe configuração de "nome_familia"
    # Se já existir, entendemos que o usuário já fez o setup
    config_existente = False
    if not dados["config"].empty:
        if "nome_familia" in dados["config"]["chave"].values:
            config_existente = True
            
    if config_existente:
        return False  # Não precisa de onboarding, segue o baile

    # === SE CHEGOU AQUI, É UM NOVO USUÁRIO ===
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1>🚀 Bem-vindo ao Gestor Financeiro!</h1>
        <p style="color: #94a3b8; font-size: 18px;">
            Vamos configurar seu ambiente em menos de 1 minuto para você começar com o pé direito.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("### 1️⃣ Configurações Essenciais (Obrigatório)")
        
        with st.form("form_onboarding"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_familia = st.text_input("👨‍👩‍👧‍👦 Nome da Família / Perfil", placeholder="Ex: Família Silva")
                meta_patrimonio = st.number_input("🎯 Meta de Patrimônio (R$)", min_value=0.0, value=100000.0, step=1000.0)
            
            with col2:
                orcamento_mensal = st.number_input("💰 Renda Mensal Estimada (R$)", min_value=0.0, value=5000.0, step=100.0)
                reserva_gastos = st.number_input("💳 Limite para Gastos Variáveis (R$)", min_value=0.0, value=2000.0, step=100.0, help="Quanto você quer gastar no máximo com mercado, lazer, etc.")

            st.markdown("---")
            st.markdown("### 2️⃣ Vamos facilitar para você? (Sugestões)")
            st.caption("Podemos já criar alguns dados iniciais para você não começar do zero.")

            c1, c2 = st.columns(2)
            with c1:
                criar_categorias = st.checkbox("✅ Criar categorias padrão (Alimentação, Casa, Transporte...)", value=True)
                criar_salario = st.checkbox("✅ Adicionar minha renda como Receita Fixa", value=True)
            
            with c2:
                criar_despesas_exemplo = st.checkbox("✅ Adicionar despesas de exemplo (Aluguel/Energia)", value=False)

            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🚀 SALVAR E COMEÇAR", type="primary", use_container_width=True)

            if submitted:
                if not nome_familia:
                    st.error("Por favor, preencha o Nome da Família.")
                else:
                    # 1. Salvar Configurações
                    df_config = pd.DataFrame([
                        {"chave": "nome_familia", "valor": nome_familia},
                        {"chave": "meta_patrimonio", "valor": meta_patrimonio},
                        {"chave": "orcamento_mensal", "valor": orcamento_mensal},
                        {"chave": "reserva_gastos", "valor": reserva_gastos},
                        {"chave": "rendimento_mensal", "valor": 0.008},
                        {"chave": "inflacao_mensal", "valor": 0.004}
                    ])
                    DatabaseManager.save("config", df_config, usuario)

                    # 2. Criar Categorias Padrão
                    if criar_categorias:
                        cats = [
                            {"nome": "Alimentação", "tipo": "Despesa Variável", "ativa": True},
                            {"nome": "Transporte", "tipo": "Despesa Variável", "ativa": True},
                            {"nome": "Casa", "tipo": "Despesa Fixa", "ativa": True},
                            {"nome": "Lazer", "tipo": "Despesa Variável", "ativa": True},
                            {"nome": "Saúde", "tipo": "Despesa Variável", "ativa": True},
                            {"nome": "Educação", "tipo": "Despesa Fixa", "ativa": True},
                            {"nome": "Salário", "tipo": "Receita", "ativa": True},
                            {"nome": "Investimentos", "tipo": "Despesa Fixa", "ativa": True}
                        ]
                        df_cats = pd.DataFrame(cats)
                        DatabaseManager.save("categorias", df_cats, usuario)

                    # 3. Criar Fluxo Fixo (Salário e Despesas)
                    fluxos = []
                    if criar_salario and orcamento_mensal > 0:
                        fluxos.append({
                            "nome": "Salário Mensal",
                            "valor": orcamento_mensal,
                            "tipo": "Receita",
                            "categoria": "Salário",
                            "recorrencia": "Mensal",
                            "data_inicio": date.today().isoformat(),
                            "observacao": "Gerado automaticamente no onboarding"
                        })
                    
                    if criar_despesas_exemplo:
                        fluxos.append({
                            "nome": "Aluguel / Condomínio",
                            "valor": 1500.0,
                            "tipo": "Despesa",
                            "categoria": "Casa",
                            "recorrencia": "Mensal",
                            "data_inicio": date.today().isoformat(),
                            "observacao": "Exemplo gerado automaticamente"
                        })
                        fluxos.append({
                            "nome": "Energia Elétrica",
                            "valor": 200.0,
                            "tipo": "Despesa",
                            "categoria": "Casa",
                            "recorrencia": "Mensal",
                            "data_inicio": date.today().isoformat(),
                            "observacao": "Exemplo gerado automaticamente"
                        })

                    if fluxos:
                        df_fluxo = pd.DataFrame(fluxos)
                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)

                    # 🔥 A CORREÇÃO ESTÁ AQUI EMBAIXO 🔥
                    # Força o sistema a baixar os dados novos do banco antes de recarregar a página
                    st.session_state["dados"] = DatabaseManager.load_all(usuario)
                    # Normalizar os novos dados baixados para evitar erros
                    for chave in st.session_state["dados"]:
                        st.session_state["dados"][chave] = normalizar_df(st.session_state["dados"][chave])

                    st.success("Tudo pronto! Carregando seu painel...")
                    st.rerun()
    
    return True # Indica que mostrou o onboarding e deve parar o resto



# =========================================================
# FUNÇÃO: GERAR LANÇAMENTOS AUTOMÁTICOS
# =========================================================
def processar_lancamentos_automaticos(dados, usuario):
    # 1. Carregar dados
    df_fluxo = dados.get("fluxo_fixo", pd.DataFrame())
    df_historico = dados.get("historico", pd.DataFrame())
    
    if df_fluxo.empty:
        return False, "Não há contas mensais cadastradas para gerar."

    # Garantir datetime no histórico para comparação
    if not df_historico.empty:
        df_historico["data"] = pd.to_datetime(df_historico["data"], errors='coerce')

    hoje = date.today()
    mes_atual_str = hoje.strftime("%Y-%m") # Ex: "2023-10"
    
    novos_registros = []
    contagem = 0

    # 2. Percorrer cada conta fixa
    for _, row in df_fluxo.iterrows():
        nome = row.get("nome", "Sem nome")
        valor = float(row.get("valor", 0))
        tipo = row.get("tipo", "Despesa")
        categoria = row.get("categoria", "Outros")
        
        # Verificar validade (Data de início e fim)
        data_inicio = row.get("data_inicio")
        data_fim = row.get("data_fim")
        
        # Se tiver data de início no futuro, pula
        if data_inicio:
            dt_ini = pd.to_datetime(data_inicio).date()
            if dt_ini > hoje:
                continue
                
        # Se tiver data de fim e já passou, pula
        if data_fim:
            dt_fim = pd.to_datetime(data_fim).date()
            if dt_fim < hoje:
                continue

        # 3. VERIFICAÇÃO DE DUPLICIDADE INTELIGENTE
        # Verifica se já existe um lançamento com MESMO nome e MESMO mês no histórico
        ja_lancado = False
        if not df_historico.empty:
            filtro = (
                (df_historico["descricao"] == nome) & 
                (df_historico["data"].dt.strftime("%Y-%m") == mes_atual_str)
            )
            if not df_historico[filtro].empty:
                ja_lancado = True
        
        # 4. Se não foi lançado, cria o registro
        if not ja_lancado:
            novos_registros.append({
                "data": hoje.isoformat(), # Cria com a data de hoje
                "descricao": nome,
                "valor": valor,
                "tipo": tipo,
                "categoria": categoria,
                "responsavel": "Automático", # Marca como automático
                "fixo": "Sim"
            })
            contagem += 1

    # 5. Salvar se houver novidades
    if novos_registros:
        df_novos = pd.DataFrame(novos_registros)
        df_final = pd.concat([df_historico, df_novos], ignore_index=True)
        
        # Atualiza sessão e banco
        dados["historico"] = df_final
        st.session_state["dados"] = dados
        DatabaseManager.save("historico", df_final, usuario)
        
        return True, f"✅ {contagem} lançamentos gerados com sucesso para este mês!"
    else:
        return False, "👍 Todas as contas deste mês já foram lançadas!"
    

# =========================================================
# FUNÇÃO: SALVAR RELATÓRIO MENSAL
# =========================================================

def salvar_relatorio_mensal(
    dados,
    patrimonio,
    saldo_fixo,
    saldo_variavel,
    perc_meta,
    texto_exec,
    status="Rascunho"
):
    mes_ref = date.today().strftime("%Y-%m")

    df_hist = dados.get("relatorios_historicos", pd.DataFrame()).copy()

    # 🔒 Blindagem de colunas
    if "mes" not in df_hist.columns:
        df_hist["mes"] = ""
    if "status" not in df_hist.columns:
        df_hist["status"] = ""

    # Remover coluna 'id' se existir
    if "id" in df_hist.columns:
        df_hist = df_hist.drop(columns=["id"])

    # Se já existe FINALIZADO, não permite sobrescrever
    existente = df_hist[
        (df_hist["mes"] == mes_ref) &
        (df_hist["status"] == "Finalizado")
    ]

    if not existente.empty:
        return False, "Relatório já finalizado para este mês."

    # Remove rascunho anterior do mesmo mês
    df_hist = df_hist[df_hist["mes"] != mes_ref]

    novo = pd.DataFrame([{
        "mes": mes_ref,
        "patrimonio": patrimonio,
        "saldo_fixo": saldo_fixo,
        "saldo_variavel": saldo_variavel,
        "perc_meta": perc_meta,
        "status": status,
        "texto_executivo": texto_exec
    }])

    df_final = pd.concat([df_hist, novo], ignore_index=True)

    dados["relatorios_historicos"] = df_final
    st.session_state["dados"] = dados

    usuario = st.session_state["usuario"]
    DatabaseManager.save("relatorios_historicos", df_final, usuario)

    return True, f"Relatório salvo como {status}."

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Gestão Financeira",
    page_icon="assets/images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* ====== RESET BÁSICO ====== */
html, body, [class*="css"]  {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ====== FUNDO GERAL ====== */
.stApp {
    background-color: #0e1117;
    color: #e6e6e6;
}

/* ====== SIDEBAR ====== */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2933;
}

/* Título sidebar */
section[data-testid="stSidebar"] h2 {
    color: #f9fafb;
}

/* ====== CARDS (metric) ====== */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #0b1220);
    border: 1px solid #1f2933;
    padding: 16px;
    border-radius: 12px;
}

/* Valor do metric */
div[data-testid="metric-container"] > div:nth-child(2) {
    font-size: 24px;
    font-weight: 600;
}

/* ====== BOTÕES ====== */
button[kind="primary"] {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    border-radius: 8px;
    border: none;
}

button[kind="secondary"] {
    border-radius: 8px;
}

/* ====== INPUTS ====== */
input, textarea, select {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
    border: 1px solid #1f2933 !important;
}

/* ====== DATAFRAME ====== */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1f2933;
}

/* ====== EXPANDERS ====== */
details {
    border-radius: 10px;
    border: 1px solid #1f2933;
    padding: 8px;
}

/* ====== DIVISOR ====== */
hr {
    border: none;
    border-top: 1px solid #1f2933;
}

/* ====== TOAST / ALERTAS ====== */
.stAlert {
    border-radius: 10px;
}

/* ====== SCROLLBAR ====== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #1f2933;
    border-radius: 10px;
}
::-webkit-scrollbar-track {
    background: #020617;
}

</style>
""", unsafe_allow_html=True)


# ===============================
# CONTROLE DE LOGIN
# ===============================

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    tela_login()
    st.stop()

# ===============================
# A PARTIR DAQUI O USUÁRIO ESTÁ LOGADO
# ===============================

st.write(f"Bem-vindo, {st.session_state.get('nome', '')}")
usuario = st.session_state["usuario"]





# =========================================================
# USUÁRIO ATIVO (placeholder até existir login)
# =========================================================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = "default"

# =========================================================
# LOAD DATA
# =========================================================
if "dados" not in st.session_state:
    usuario = st.session_state["usuario"]
    st.session_state["dados"] = DatabaseManager.load_all(usuario)

dados = st.session_state["dados"]
for chave in dados:
    dados[chave] = normalizar_df(dados[chave])

# 🔥 NOVO BLOCO: VERIFICAR ONBOARDING 🔥
# Se a função retornar True, significa que está mostrando a tela de boas-vindas
# Então paramos o script aqui com st.stop() para não mostrar o menu lateral ainda
if verificar_e_mostrar_onboarding(dados, st.session_state["usuario"]):
    st.stop()


# =========================================================
# MENSAGENS GLOBAIS (toast / feedback)
# =========================================================
if "msg" not in st.session_state:
    st.session_state["msg"] = None

if "msg_tipo" not in st.session_state:
    st.session_state["msg_tipo"] = "success"


# =========================================================
# CALCULOS GERAIS (BLOCO 3) - CORREÇÃO
# =========================================================

hoje = date.today()
mes_atual = hoje.strftime("%Y-%m")

# ---------------- PATRIMÔNIO ----------------
patrimonio = dados["investimentos"]["valor_atual"].sum() if not dados["investimentos"].empty else 0

# ---------------- HISTÓRICO (VARIÁVEL) ----------------
if not dados["historico"].empty:
    hist = dados["historico"].copy()
    
    # 🔥 NORMALIZAR COLUNAS PRIMEIRO
    hist.columns = hist.columns.str.lower()
    
    # Converter data
    hist["data"] = pd.to_datetime(hist["data"])
    hist["mes"] = hist["data"].dt.strftime("%Y-%m")
    hist_mes = hist[hist["mes"] == mes_atual]

    # 🔥 BUSCAR COM VALORES EM MINÚSCULO
    receitas_variaveis = hist_mes[hist_mes["tipo"].str.lower() == "receita"]["valor"].sum()
    despesas_variaveis = hist_mes[hist_mes["tipo"].str.lower() == "despesa"]["valor"].sum()
else:
    receitas_variaveis = despesas_variaveis = 0


# ---------------- CONTROLE DE GASTOS (DESPESA VARIÁVEL) ----------------
if not dados.get("controle_gastos", pd.DataFrame()).empty:
    gastos_rapidos_mes = dados["controle_gastos"]["valor"].sum()
else:
    gastos_rapidos_mes = 0


# ---------------- SALDO VARIÁVEL FINAL ----------------
saldo_variavel = receitas_variaveis - despesas_variaveis - gastos_rapidos_mes

# ---------------- FLUXO FIXO ----------------
if not dados["fluxo_fixo"].empty:
    receitas_fixas = dados["fluxo_fixo"][dados["fluxo_fixo"]["tipo"] == "Receita"]["valor"].sum()
    despesas_fixas = dados["fluxo_fixo"][dados["fluxo_fixo"]["tipo"] == "Despesa"]["valor"].sum()
    saldo_fixo = receitas_fixas - despesas_fixas
else:
    receitas_fixas = despesas_fixas = saldo_fixo = 0

# ---------------- SONHOS - CORREÇÃO: FILTRAR APENAS SONHOS ATIVOS ----------------
if not dados["sonhos_projetos"].empty:
    # 🔥 FILTRAR: considerar apenas sonhos com status diferente de "Desistido"
    sonhos_ativos = dados["sonhos_projetos"][dados["sonhos_projetos"]["status"] != "Desistido"]
    
    if not sonhos_ativos.empty:
        total_sonhos = sonhos_ativos["valor_alvo"].sum()
        total_atual = sonhos_ativos["valor_atual"].sum()
        progresso_sonhos = (total_atual / total_sonhos * 100) if total_sonhos > 0 else 0
    else:
        total_sonhos = total_atual = progresso_sonhos = 0
else:
    total_sonhos = total_atual = progresso_sonhos = 0

# =========================================================
# CONFIGURAÇÕES (BLOCO 4)
# =========================================================

config_dict = {}

if not dados["config"].empty:
    for _, row in dados["config"].iterrows():
        config_dict[row["chave"]] = row["valor"]

# Valores com fallback seguro
meta_patrimonio = float(config_dict.get("meta_patrimonio", 0))
def normaliza_percentual(valor):
    try:
        v = float(valor)
        if v > 1:
            return v / 100
        return v
    except:
        return 0.0

rendimento_mensal = normaliza_percentual(config_dict.get("rendimento_mensal", 0))
inflacao_mensal = normaliza_percentual(config_dict.get("inflacao_mensal", 0))
orcamento_mensal = float(config_dict.get("orcamento_mensal", 0))
nome_familia = config_dict.get("nome_familia", "Família")


# =========================================================
# PROJEÇÃO DE PATRIMÔNIO (BLOCO 5)
# =========================================================

def projetar_patrimonio(
    patrimonio_inicial,
    saldo_fixo_mensal,
    rendimento_mensal,
    inflacao_mensal,
    meta_patrimonio,
    meses=120
):
    taxa_real = rendimento_mensal - inflacao_mensal
    taxa_real = max(taxa_real, -0.99)

    patrimonio = patrimonio_inicial
    resultados = []

    data_base = date.today().replace(day=1)

    for i in range(meses):
        data_ref = data_base + relativedelta(months=i)

        if i > 0:
            rendimento = patrimonio * taxa_real
            patrimonio += rendimento + saldo_fixo_mensal
        else:
            rendimento = 0

        resultados.append({
            "data": data_ref,
            "patrimonio": patrimonio,
            "rendimento": rendimento,
            "aporte_fixo": saldo_fixo_mensal if i > 0 else 0,
            "meta_atingida": patrimonio >= meta_patrimonio
        })

        if patrimonio >= meta_patrimonio and i >= 12:
            break

    return pd.DataFrame(resultados)

# =========================================================
# TEXTO EXECUTIVO AUTOMÁTICO
# =========================================================

def gerar_texto_executivo(
    patrimonio,
    saldo_variavel,
    saldo_fixo,
    perc_meta,
    status_meta,
    df_projecao
):
    texto = []

    # 1️⃣ Situação atual
    texto.append(
        f"No período analisado, o patrimônio consolidado da família é de "
        f"R$ {patrimonio:,.2f}, encontrando-se em status {status_meta.lower()} "
        f"em relação à meta financeira estabelecida."
    )

    # 2️⃣ Resultado mensal
    if saldo_variavel < 0:
        texto.append(
            "No mês corrente, observou-se pressão negativa nas despesas variáveis, "
            "indicando necessidade de maior controle sobre gastos não recorrentes."
        )
    else:
        texto.append(
            "O resultado mensal apresentou equilíbrio positivo nas despesas variáveis, "
            "refletindo bom controle financeiro no período."
        )

    if saldo_fixo < 0:
        texto.append(
            "A estrutura de custos fixos encontra-se deficitária, o que representa risco "
            "de consumo gradual do patrimônio caso não sejam realizados ajustes."
        )
    else:
        texto.append(
            "A estrutura fixa permanece sustentável, contribuindo positivamente para "
            "a preservação e crescimento patrimonial."
        )

    # 3️⃣ Projeção
    if not df_projecao.empty:
        meses = len(df_projecao)
        ultimo = df_projecao.iloc[-1]

        if ultimo["meta_atingida"]:
            texto.append(
                f"Mantidas as condições atuais, a projeção indica que a meta patrimonial "
                f"será atingida dentro de aproximadamente {meses} meses."
            )
        else:
            texto.append(
                "A projeção atual indica que a meta patrimonial não será atingida no "
                "horizonte previsto sem reforço de aportes ou ajustes na estrutura financeira."
            )

    # 4️⃣ Fechamento executivo
    if perc_meta >= 80:
        texto.append(
            "O cenário geral é positivo, com foco recomendado em disciplina e consistência."
        )
    elif perc_meta >= 50:
        texto.append(
            "O cenário é intermediário, exigindo atenção estratégica para aceleração do plano."
        )
    else:
        texto.append(
            "O cenário requer ações corretivas estruturais para evitar distanciamento da meta."
        )

    return " ".join(texto)

# =========================================================
# GERADOR DE RELATÓRIO HTML
# =========================================================

def gerar_relatorio_html(
    nome_familia,
    patrimonio,
    saldo_variavel,
    saldo_fixo,
    perc_meta,
    status_meta,
    texto_exec
):
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
            }}
            h2 {{
                margin-top: 30px;
                color: #34495e;
            }}
            .metric {{
                margin: 10px 0;
                font-size: 16px;
            }}
            .highlight {{
                background: #f4f6f7;
                padding: 15px;
                border-radius: 6px;
            }}
        </style>
    </head>
    <body>

        <h1>Relatório Financeiro Executivo</h1>
        <p><strong>Família:</strong> {nome_familia}</p>
        <p><strong>Data:</strong> {date.today().strftime("%d/%m/%Y")}</p>

        <h2>Resumo Executivo</h2>
        <div class="highlight">
            <div class="metric"><strong>Patrimônio Atual:</strong> R$ {patrimonio:,.2f}</div>
            <div class="metric"><strong>Saldo Fixo Mensal:</strong> R$ {saldo_fixo:,.2f}</div>
            <div class="metric"><strong>Status da Meta:</strong> {perc_meta:.1f}% • {status_meta}</div>
        </div>

        <h2>Análise Executiva</h2>
        <p>{texto_exec}</p>

    </body>
    </html>
    """
    return html

# =========================================================
# FUNÇÃO: FORMATAR TEMPO EM ANOS/MESES
# =========================================================
def formatar_tempo_meses(meses):
    """Converte meses para formato 'X anos e Y meses'"""
    if meses < 12:
        return f"{meses} meses"
    
    anos = meses // 12
    meses_restantes = meses % 12
    
    if meses_restantes == 0:
        return f"{anos} anos"
    elif anos == 0:
        return f"{meses_restantes} meses"
    else:
        return f"{anos} anos e {meses_restantes} meses"
    

# =========================================================
# FUNÇÃO: CALCULAR APORTE IDEAL PARA META
# =========================================================
def calcular_aporte_ideal_para_meta(
    patrimonio_atual,
    meta_patrimonio,
    rendimento_mensal,
    inflacao_mensal,
    tempo_desejado_anos
):
    """
    Calcula quanto precisa guardar por mês para atingir a meta no tempo desejado
    Retorna: aporte_mensal_sugerido, é_viável
    """
    if meta_patrimonio <= patrimonio_atual:
        return 0, True  # Meta já atingida
    
    taxa_real = rendimento_mensal - inflacao_mensal
    taxa_real = max(taxa_real, 0.001)  # Mínimo 0.1% para evitar divisão por zero
    
    meses_totais = tempo_desejado_anos * 12
    
    # Fórmula: PMT = (FV * i) / ((1 + i)^n - 1)
    # Onde: FV = meta - patrimônio atual (valor futuro necessário)
    fv_necessario = meta_patrimonio - patrimonio_atual
    
    if taxa_real <= 0 or meses_totais <= 0:
        # Se não há rendimento, divide igualmente
        aporte_mensal = fv_necessario / max(meses_totais, 1)
    else:
        # Cálculo com juros compostos
        fator = (1 + taxa_real) ** meses_totais
        aporte_mensal = (fv_necessario * taxa_real) / (fator - 1)
    
    # Verificar viabilidade (se aporte não é absurdamente alto)
    limite_razoavel = 0.5  # 50% da meta como aporte máximo mensal
    aporte_maximo_razoavel = meta_patrimonio * limite_razoavel / meses_totais
    
    é_viável = aporte_mensal <= aporte_maximo_razoavel
    
    return round(aporte_mensal, 2), é_viável


# =========================================================
# EXECUTA PROJEÇÃO (CRIAR df_projecao)
# =========================================================

df_projecao = projetar_patrimonio(
    patrimonio_inicial=patrimonio,
    saldo_fixo_mensal=saldo_fixo,
    rendimento_mensal=rendimento_mensal,
    inflacao_mensal=inflacao_mensal,
    meta_patrimonio=meta_patrimonio,
    meses=120
)


def mostrar_gasto_card(idx, row, df_original, unique_counter):
    """Função auxiliar para mostrar um card de gasto"""
    # Usar um contador único em vez do índice do DataFrame
    unique_key = f"del_btn_{unique_counter}"
    
    # Formatar data - APENAS DATA, SEM HORA
    if isinstance(row['data'], pd.Timestamp):
        data_str = row['data'].strftime("%d/%m")
        dia_semana = row['data'].strftime("%a")
        data_completa = row['data'].strftime("%d/%m/%Y")
    else:
        # Se for string, extrair apenas a parte da data
        data_str = str(row['data'])[:10] if row['data'] else ""
        dia_semana = ""
        data_completa = data_str
    
    # 🔥 SISTEMA DE CATEGORIAS AVANÇADO
    # Definir todas as categorias com palavras-chave
    CATEGORIAS_DETALHADAS = {
        # 🍔 ALIMENTAÇÃO
        "Alimentação - Restaurante": {
            "palavras": ['restaurante', 'lanche', 'fast food', 'pizza', 'hamburguer', 'mcdonald', 'bk', 'subway'],
            "cor": "#ef4444",
            "emoji": "🍔"
        },
        "Alimentação - Supermercado": {
            "palavras": ['mercado', 'supermercado', 'atacadão', 'atacadista', 'extra', 'carrefour', 'pão de açúcar'],
            "cor": "#dc2626",
            "emoji": "🛒"
        },
        "Alimentação - Café": {
            "palavras": ['café', 'cafeteria', 'starbucks', 'padaria', 'padoca', 'confeitaria'],
            "cor": "#92400e",
            "emoji": "☕"
        },
        "Alimentação - Açougue": {
            "palavras": ['açougue', 'carnes', 'frango', 'peixe', 'peixaria', 'frutos do mar'],
            "cor": "#b91c1c",
            "emoji": "🥩"
        },
        "Alimentação - Hortifruti": {
            "palavras": ['feira', 'hortifruti', 'fruta', 'legume', 'verdura', 'sacolão'],
            "cor": "#16a34a",
            "emoji": "🍎"
        },
        
        # 🚗 TRANSPORTE
        "Transporte - Combustível": {
            "palavras": ['gasolina', 'combustível', 'posto', 'shell', 'ipiranga', 'etanol', 'diesel'],
            "cor": "#3b82f6",
            "emoji": "⛽"
        },
        "Transporte - Táxi/Uber": {
            "palavras": ['uber', 'táxi', '99', 'cabify', 'corrida', 'transporte'],
            "cor": "#1d4ed8",
            "emoji": "🚕"
        },
        "Transporte - Público": {
            "palavras": ['ônibus', 'metro', 'trem', 'bilhete', 'passagem', 'recarga', 'cartão transporte'],
            "cor": "#1e40af",
            "emoji": "🚌"
        },
        "Transporte - Estacionamento": {
            "palavras": ['estacionamento', 'parking', 'garagem', 'zona azul'],
            "cor": "#0ea5e9",
            "emoji": "🅿️"
        },
        "Transporte - Manutenção": {
            "palavras": ['oficina', 'mecânico', 'troca de óleo', 'pneu', 'lavagem', 'manutenção carro'],
            "cor": "#6366f1",
            "emoji": "🛠️"
        },
        
        # 🏠 CASA
        "Casa - Aluguel": {
            "palavras": ['aluguel', 'condomínio', 'iptu', 'taxa condominial'],
            "cor": "#8b5cf6",
            "emoji": "🏠"
        },
        "Casa - Energia": {
            "palavras": ['luz', 'energia', 'conta de luz', 'energisa', 'enel', 'light'],
            "cor": "#f59e0b",
            "emoji": "💡"
        },
        "Casa - Água": {
            "palavras": ['água', 'conta de água', 'sabesp', 'cedae', 'caesb'],
            "cor": "#0ea5e9",
            "emoji": "💧"
        },
        "Casa - Gás": {
            "palavras": ['gás', 'botijão', 'gás natural', 'conta de gás'],
            "cor": "#ef4444",
            "emoji": "🔥"
        },
        "Casa - Internet/TV": {
            "palavras": ['internet', 'net', 'claro', 'vivo', 'oi', 'sky', 'tv a cabo'],
            "cor": "#8b5cf6",
            "emoji": "📡"
        },
        
        # 🛒 COMPRAS
        "Compras - Roupas": {
            "palavras": ['roupa', 'calçado', 'sapato', 'tenis', 'camiseta', 'loja de roupa', 'renner', 'c&a'],
            "cor": "#ec4899",
            "emoji": "👕"
        },
        "Compras - Eletrônicos": {
            "palavras": ['celular', 'notebook', 'tablet', 'tv', 'eletrônico', 'informática'],
            "cor": "#6b7280",
            "emoji": "📱"
        },
        "Compras - Beleza": {
            "palavras": ['farmácia', 'drogaria', 'perfume', 'maquiagem', 'cosmético', 'beleza'],
            "cor": "#f472b6",
            "emoji": "💄"
        },
        "Compras - Livros": {
            "palavras": ['livro', 'revista', 'jornal', 'leitura', 'livraria', 'saraiva', 'cultura'],
            "cor": "#84cc16",
            "emoji": "📚"
        },
        "Compras - Presentes": {
            "palavras": ['presente', 'aniversário', 'natal', 'dia das mães', 'dia dos pais'],
            "cor": "#a855f7",
            "emoji": "🎁"
        },
        
        # 🎯 LAZER
        "Lazer - Cinema": {
            "palavras": ['cinema', 'filme', 'ingresso', 'netflix', 'prime video', 'disney+'],
            "cor": "#a78bfa",
            "emoji": "🎬"
        },
        "Lazer - Bar": {
            "palavras": ['bar', 'boteco', 'cerveja', 'drink', 'happy hour', 'balada'],
            "cor": "#f59e0b",
            "emoji": "🍻"
        },
        "Lazer - Viagem": {
            "palavras": ['viagem', 'hotel', 'passagem', 'turismo', 'resort', 'pousada'],
            "cor": "#3b82f6",
            "emoji": "✈️"
        },
        "Lazer - Games": {
            "palavras": ['jogo', 'game', 'playstation', 'xbox', 'steam', 'nintendo'],
            "cor": "#8b5cf6",
            "emoji": "🎮"
        },
        "Lazer - Esportes": {
            "palavras": ['academia', 'ginásio', 'esporte', 'natação', 'futebol', 'personal trainer'],
            "cor": "#10b981",
            "emoji": "🏋️"
        },
        
        # 💼 TRABALHO
        "Trabalho - Material": {
            "palavras": ['material', 'escritório', 'caneta', 'papel', 'impressão', 'toner'],
            "cor": "#6b7280",
            "emoji": "📎"
        },
        "Trabalho - Software": {
            "palavras": ['software', 'assinatura', 'licença', 'app', 'aplicativo', 'programa'],
            "cor": "#3b82f6",
            "emoji": "💻"
        },
        "Trabalho - Telefone": {
            "palavras": ['telefone', 'celular empresa', 'recarga', 'plano empresarial'],
            "cor": "#10b981",
            "emoji": "📞"
        },
        
        # 🧑‍⚕️ SAÚDE
        "Saúde - Consulta": {
            "palavras": ['consulta', 'médico', 'dentista', 'psicólogo', 'terapia', 'clínica'],
            "cor": "#10b981",
            "emoji": "🏥"
        },
        "Saúde - Medicamento": {
            "palavras": ['remédio', 'medicamento', 'farmacia', 'drogaria'],
            "cor": "#ef4444",
            "emoji": "💊"
        },
        "Saúde - Plano": {
            "palavras": ['plano de saúde', 'unimed', 'amil', 'sulamerica'],
            "cor": "#dc2626",
            "emoji": "❤️"
        },
        
        # 🧾 FINANÇAS
        "Finanças - Taxa Bancária": {
            "palavras": ['taxa', 'tarifa', 'anuidade', 'banco', 'cartão', 'empréstimo'],
            "cor": "#059669",
            "emoji": "🏦"
        },
        "Finanças - Investimento": {
            "palavras": ['investimento', 'ações', 'fii', 'tesouro', 'cdb', 'bolsa'],
            "cor": "#84cc16",
            "emoji": "📈"
        },
        "Finanças - Seguro": {
            "palavras": ['seguro', 'apólice', 'previdência', 'resgate'],
            "cor": "#3b82f6",
            "emoji": "🛡️"
        },
        
        # 👨‍👩‍👧‍👦 FAMÍLIA
        "Família - Filhos": {
            "palavras": ['creche', 'escola', 'material escolar', 'uniforme', 'curso', 'aula'],
            "cor": "#f472b6",
            "emoji": "👶"
        },
        "Família - Pets": {
            "palavras": ['pet', 'veterinário', 'ração', 'gato', 'cachorro', 'animal'],
            "cor": "#f59e0b",
            "emoji": "🐕"
        },
        "Família - Eventos": {
            "palavras": ['festa', 'casamento', 'formatura', 'comemoração', 'confraternização'],
            "cor": "#8b5cf6",
            "emoji": "🎉"
        },
        
        # 💰 OUTROS
        "Outros - Assinaturas": {
            "palavras": ['assinatura', 'streaming', 'spotify', 'youtube premium'],
            "cor": "#6b7280",
            "emoji": "🎫"
        },
        "Outros - Variados": {
            "palavras": [],
            "cor": "#9ca3af",
            "emoji": "📝"
        }
    }
    
    # Determinar categoria automaticamente
    desc_lower = row['descricao'].lower()
    categoria_detectada = None
    
    for cat_nome, cat_info in CATEGORIAS_DETALHADAS.items():
        if any(palavra in desc_lower for palavra in cat_info["palavras"]):
            categoria_detectada = {
                "nome": cat_nome,
                "cor": cat_info["cor"],
                "emoji": cat_info["emoji"]
            }
            break
    
    # Se não detectou, usar "Outros"
    if not categoria_detectada:
        categoria_detectada = {
            "nome": "Outros - Variados",
            "cor": "#9ca3af",
            "emoji": "📝"
        }
    
    # Card para cada gasto
    with st.container():
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid {categoria_detectada['cor']};
            border: 1px solid #374151;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="
                            background: {categoria_detectada['cor']}20;
                            color: {categoria_detectada['cor']};
                            padding: 4px 12px;
                            border-radius: 20px;
                            font-size: 12px;
                            font-weight: bold;
                            margin-right: 12px;
                        ">
                            {categoria_detectada['emoji']} {categoria_detectada['nome'].split(' - ')[0]}
                        </div>
                        <div style="
                            background: #374151;
                            color: #d1d5db;
                            padding: 4px 10px;
                            border-radius: 6px;
                            font-size: 12px;
                            font-weight: bold;
                        ">
                            {data_str} • {dia_semana}
                        </div>
                    </div>
                    <div style="font-size: 16px; font-weight: bold; color: #f9fafb; margin-bottom: 4px;">
                        {row['descricao']}
                    </div>
                    <div style="font-size: 12px; color: #9ca3af; display: flex; align-items: center; gap: 8px;">
                        <span>{data_completa}</span>
                        <span style="color: {categoria_detectada['cor']};">
                            • {categoria_detectada['nome'].split(' - ')[1] if ' - ' in categoria_detectada['nome'] else categoria_detectada['nome']}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 20px; font-weight: bold; color: #f87171; margin-bottom: 8px;">
                        R$ {row['valor']:,.2f}
                    </div>
        """, unsafe_allow_html=True)
        
        # Botão de exclusão - usar chave única
        if st.button("🗑️", key=unique_key, help="Excluir este gasto"):
            st.session_state[f"confirm_delete_{unique_key}"] = True
            st.rerun()
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confirmação de exclusão (mantenha o mesmo código)
        if st.session_state.get(f"confirm_delete_{unique_key}", False):
            with st.container():
                st.warning(f"Excluir '{row['descricao'][:30]}...'?")
                col_conf1, col_conf2 = st.columns(2)
                with col_conf1:
                    if st.button("✅ Sim", key=f"confirm_yes_{unique_key}", use_container_width=True):
                        row_data = row['data']
                        
                        if isinstance(row_data, pd.Timestamp):
                            row_data_date = row_data.date()
                        elif isinstance(row_data, str):
                            row_data_date = pd.to_datetime(row_data).date()
                        else:
                            row_data_date = row_data
                        
                        for df_idx, df_row in df_original.iterrows():
                            df_row_data = df_row['data']
                            
                            if isinstance(df_row_data, pd.Timestamp):
                                df_row_data_date = df_row_data.date()
                            elif isinstance(df_row_data, str):
                                df_row_data_date = pd.to_datetime(df_row_data).date()
                            else:
                                df_row_data_date = df_row_data
                            
                            if (df_row_data_date == row_data_date and 
                                df_row['descricao'] == row['descricao'] and 
                                df_row['valor'] == row['valor']):
                                
                                df_novo = df_original.drop(df_idx).reset_index(drop=True)
                                dados["controle_gastos"] = df_novo
                                st.session_state["dados"] = dados
                                DatabaseManager.save("controle_gastos", df_novo, usuario)
                                
                                st.session_state[f"confirm_delete_{unique_key}"] = False
                                st.success("Gasto excluído!")
                                st.rerun()
                                break
                        
                        st.session_state[f"confirm_delete_{unique_key}"] = False
                        st.error("Não foi possível encontrar o gasto para exclusão.")
                        st.rerun()
                        
                with col_conf2:
                    if st.button("❌ Não", key=f"confirm_no_{unique_key}", use_container_width=True):
                        st.session_state[f"confirm_delete_{unique_key}"] = False
                        st.rerun()





# =========================================================
# SIDEBAR (MENU ÚNICO DO SISTEMA) - VERSÃO ESTILIZADA
# =========================================================
with st.sidebar:
    # Cabeçalho estilizado com gradiente
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <div style="
            background: rgba(255, 255, 255, 0.15);
            border-radius: 50%;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
        ">
            <span style="font-size: 40px;">💸</span>
        </div>
        <h2 style="
            text-align: center; 
            letter-spacing: 1px;
            color: white;
            margin: 0 0 8px;
            font-size: 1.8em;
        ">
            GESTÃO FINANCEIRA
        </h2>
        <p style="
            text-align: center; 
            color: rgba(255, 255, 255, 0.9);
            margin: 0;
            font-size: 0.9em;
            font-weight: 300;
        ">
        Visão • Controle • Estratégia
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ===============================
    # MENU BASE ESTILIZADO
    # ===============================
    menu_data = [
        {
            "emoji": "🛒",
            "label": "Limite do Cartão/Mês",
            "color": "#3b82f6",
            "bg_color": "rgba(59, 130, 246, 0.1)"
        },
        {
            "emoji": "📊",
            "label": "Dashboard",
            "color": "#8b5cf6",
            "bg_color": "rgba(139, 92, 246, 0.1)"
        },
        {
            "emoji": "📄",
            "label": "Relatório Executivo",
            "color": "#6366f1",
            "bg_color": "rgba(99, 102, 241, 0.1)"
        },

        {
            "emoji": "🐷",
            "label": "Meu Dinheiro Guardado",
            "color": "#f59e0b",
            "bg_color": "rgba(245, 158, 11, 0.1)"
        },
        {
            "emoji": "🎯",
            "label": "Sonhos & Metas",
            "color": "#ef4444",
            "bg_color": "rgba(239, 68, 68, 0.1)"
        },
        {
            "emoji": "💸",
            "label": "Anotar Gasto",
            "color": "#10b981",
            "bg_color": "rgba(16, 185, 129, 0.1)"
        },
        {
            "emoji": "📅",
            "label": "Contas Mensais",
            "color": "#ec4899",
            "bg_color": "rgba(236, 72, 153, 0.1)"
        },
        {
            "emoji": "🏷️",
            "label": "Categorias",
            "color": "#14b8a6",
            "bg_color": "rgba(20, 184, 166, 0.1)"
        },

        {
            "emoji": "⚙️",
            "label": "Planejamento",
            "color": "#6b7280",
            "bg_color": "rgba(107, 114, 128, 0.1)"
        }
    ]

    # Adicionar menu ADMIN se necessário
    if st.session_state.get("perfil") == "admin":
        menu_data.append({
            "emoji": "👥",
            "label": "USUÁRIOS",
            "color": "#0ea5e9",
            "bg_color": "rgba(14, 165, 233, 0.1)"
        })

    # Criar seleção de menu com estilo personalizado
    st.markdown("""
    <style>
    /* Estilizar os radio buttons do MENU para parecerem cards */
    .sidebar-menu-container div[data-testid="stRadio"] > div {
        flex-direction: column;
        gap: 8px;
    }
    
    .sidebar-menu-container div[data-testid="stRadio"] > div > label {
        background: #1f2937 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        border: 1px solid #374151 !important;
        transition: all 0.3s ease !important;
        margin: 0 !important;
    }
    
    .sidebar-menu-container div[data-testid="stRadio"] > div > label:hover {
        background: #374151 !important;
        border-color: #4b5563 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar-menu-container div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background: linear-gradient(135deg, var(--selected-bg) 0%, rgba(0, 0, 0, 0.1) 100%) !important;
        border: 1px solid var(--selected-color) !important;
        box-shadow: 0 4px 12px var(--selected-shadow) !important;
    }
    
    /* REMOVIDO: Não esconder o radio button original */
    /* div[data-testid="stRadio"] > div > label > div:first-child {
        display: none !important;
    } */
    
    /* Estilizar o texto do menu */
    .sidebar-menu-container div[data-testid="stRadio"] > div > label > div:nth-child(2) {
        font-weight: 500 !important;
        font-size: 14px !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        color: #f9fafb !important;
    }
    
    /* Ícones do menu */
    .sidebar-menu-container .menu-icon {
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Criar opções de menu dinamicamente
    menu_options = []
    for item in menu_data:
        menu_options.append(f"{item['emoji']} {item['label']}")

    # Container para o menu com classe específica
    st.markdown('<div class="sidebar-menu-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom: 16px; color: #d1d5db; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
        NAVEGAÇÃO
    </div>
    """, unsafe_allow_html=True)
    
    # Inserir estilo dinâmico para cada opção (agora específico para o container do menu)
    css_vars = []
    for i, item in enumerate(menu_data):
        css_vars.append(f"""
        .sidebar-menu-container div[data-testid="stRadio"] > div > label:nth-child({i + 1}) {{
            --selected-color: {item['color']} !important;
            --selected-bg: {item['bg_color']} !important;
            --selected-shadow: rgba({int(item['color'][1:3], 16)}, {int(item['color'][3:5], 16)}, {int(item['color'][5:7], 16)}, 0.2) !important;
        }}
        
        .sidebar-menu-container div[data-testid="stRadio"] > div > label:nth-child({i + 1})[data-checked="true"] .menu-icon {{
            background: {item['color']} !important;
            color: white !important;
        }}
        """)
    
    st.markdown(f"<style>{''.join(css_vars)}</style>", unsafe_allow_html=True)
    
    # Radio button com as opções
    menu = st.radio(
        "Menu de Navegação",
        menu_options,
        label_visibility="collapsed",
        key="styled_menu"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ===============================
    # CARD DE STATUS DO USUÁRIO
    # ===============================
    with st.container():
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #374151;
            margin-top: 24px;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="
                    background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                    border-radius: 10px;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <span style="font-size: 20px;">👤</span>
                </div>
                <div>
                    <div style="font-size: 14px; color: #d1d5db; font-weight: 500;">
                        {usuario}
                    </div>
                    <div style="font-size: 12px; color: #9ca3af;">
                        {perfil}
                    </div>
                </div>
            </div>
            <div style="
                background: #111827;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: #9ca3af;
                border: 1px solid #374151;
            ">
                📅 {data_hoje}
            </div>
        </div>
        """.format(
            usuario=usuario,
            perfil=st.session_state.get("perfil", "Usuário").capitalize(),
            data_hoje=date.today().strftime("%d/%m/%Y")
        ), unsafe_allow_html=True)

    # ===============================
    # BOTÃO DE LOGOUT ESTILIZADO
    # ===============================
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_logout1, col_logout2, col_logout3 = st.columns([1, 2, 1])
    with col_logout2:
        if st.button(
            "🚪 Sair",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.clear()
            st.rerun()
# =========================================================
# 💸 Anotar Gasto - VERSÃO ESTILIZADA COMPLETA
# =========================================================

if menu == "💸 Anotar Gasto":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #10b981;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">📝</span>
            Registro de Transações
        </h1>
        <p style="color: #e5e7eb; margin: 0; opacity: 0.9;">
            Registre e gerencie todas as suas transações financeiras
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#3b82f6"
        }.get(msg_tipo, "#3b82f6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ================= RESUMO RÁPIDO =================
    # Calcular estatísticas do mês atual
    hoje = date.today()
    mes_atual = hoje.strftime("%Y-%m")
    
    if not dados["historico"].empty:
        df_historico = dados["historico"].copy()
        df_historico.columns = df_historico.columns.str.lower()
        
        # Converter data
        df_historico["data"] = pd.to_datetime(df_historico["data"], errors='coerce')
        df_historico["mes"] = df_historico["data"].dt.strftime("%Y-%m")
        
        # Filtrar mês atual
        historico_mes = df_historico[df_historico["mes"] == mes_atual]
        
        if not historico_mes.empty:
            receitas_mes = historico_mes[historico_mes["tipo"].str.lower() == "receita"]["valor"].sum()
            despesas_mes = historico_mes[historico_mes["tipo"].str.lower() == "despesa"]["valor"].sum()
            investimentos_mes = historico_mes[historico_mes["tipo"].str.lower() == "investimento"]["valor"].sum()
            total_mes = len(historico_mes)
        else:
            receitas_mes = despesas_mes = investimentos_mes = 0
            total_mes = 0
    else:
        receitas_mes = despesas_mes = investimentos_mes = 0
        total_mes = 0
    
    saldo_mes = receitas_mes - despesas_mes - investimentos_mes

    # Cards de métricas
    st.markdown("### 📊 Resumo do Mês")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Receitas</div>
                <div style="font-size: 24px; font-weight: bold;">R$ {receitas_mes:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Este mês</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c2d12 0%, #f97316 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📉 Despesas</div>
                <div style="font-size: 24px; font-weight: bold;">R$ {despesas_mes:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Este mês</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cor_saldo = "#10b981" if saldo_mes >= 0 else "#ef4444"
            icone_saldo = "🟢" if saldo_mes >= 0 else "🔴"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                border: 2px solid {cor_saldo};
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📊 Saldo</div>
                <div style="font-size: 24px; font-weight: bold; color: {cor_saldo};">{icone_saldo} R$ {abs(saldo_mes):,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>{"Superavit" if saldo_mes >= 0 else "Deficit"}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📋 Total Lançamentos</div>
                <div style="font-size: 28px; font-weight: bold;">{total_mes}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Este mês</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ================= FORMULÁRIO DE NOVO LANÇAMENTO =================
    st.markdown("### ➕ Novo Lançamento")
    
    with st.expander("📝 Clique para expandir o formulário", expanded=True):
        with st.container():

            
            with st.form("form_novo_lancamento", clear_on_submit=True):
                col1, col2, col3 = st.columns(3, gap="large")

                with col1:
                    st.markdown("#### 📅 Data e Tipo")
                    data = st.date_input(
                        "📅 **Data da Transação**",
                        date.today(),
                        help="Data em que a transação ocorreu"
                    )
                    
                    tipo = st.selectbox(
                        "📊 **Tipo de Transação**",
                        ["Despesa", "Receita", "Investimento"],
                        help="Despesa: Dinheiro que sai | Receita: Dinheiro que entra | Investimento: Aplicação financeira"
                    )
                    
                    valor = st.number_input(
                        "💰 **Valor (R$)**",
                        min_value=0.0,
                        step=10.0,
                        value=100.0,
                        format="%.2f",
                        help="Valor da transação"
                    )

                with col2:
                    st.markdown("#### 🏷️ Categorização")
                    
                    # Carregar categorias disponíveis
                    categorias_disponiveis = []
                    if not dados["categorias"].empty:
                        df_categorias = dados["categorias"].copy()
                        df_categorias.columns = df_categorias.columns.str.lower()
                        
                        if "ativa" in df_categorias.columns:
                            df_categorias["ativa"] = pd.to_numeric(df_categorias["ativa"], errors='coerce').fillna(1).astype(bool)
                            categorias_ativas = df_categorias[df_categorias["ativa"] == True]
                        else:
                            categorias_ativas = df_categorias
                        
                        if "nome" in categorias_ativas.columns:
                            categorias_disponiveis = categorias_ativas["nome"].dropna().unique().tolist()
                    
                    if not categorias_disponiveis:
                        categorias_disponiveis = ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Outros"]
                    
                    categoria = st.selectbox(
                        "📂 **Categoria**",
                        categorias_disponiveis,
                        help="Classifique a transação para facilitar a organização"
                    )
                    
                    subcategoria = st.text_input(
                        "🏷️ **Subcategoria (opcional)**",
                        placeholder="Ex: Supermercado, Combustível, Restaurante...",
                        help="Detalhe adicional sobre a transação"
                    )

                with col3:
                    st.markdown("#### 👥 Responsabilidade")
                    
                    responsavel = st.radio(
                        "👤 **Responsável pela Transação**",
                        ["🧔 Ele", "👩‍🦰 Ela", "👨‍👩‍👧‍👦 Compartilhado"],
                        horizontal=True,
                        help="Quem realizou ou é responsável por esta transação"
                    )
                    
                    fixo = st.checkbox(
                        "🔄 **É uma transação recorrente?**",
                        help="Marque se esta transação se repete mensalmente"
                    )
                    
                    # Espaçamento
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                descricao = st.text_input(
                    "📝 **Descrição da Transação**",
                    placeholder="Ex: Compra no supermercado, Salário mensal, Aporte em investimentos...",
                    help="Descreva brevemente a transação"
                )
                
                # Botão de envio
                col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                with col_submit2:
                    submitted = st.form_submit_button(
                        "💾 **REGISTRAR TRANSAÇÃO**",
                        type="primary",
                        use_container_width=True
                    )
                
                # No formulário de novo lançamento, na parte do submitted:
                if submitted:
                    if not descricao.strip():
                        st.error("❌ Por favor, informe uma descrição para a transação.")
                        st.stop()
                    
                    if valor <= 0:
                        st.error("❌ O valor deve ser maior que zero.")
                        st.stop()
                    
                    # CORREÇÃO: Garantir que a data seja salva como string ISO para consistência
                    data_iso = data.isoformat()  # Converte date para string no formato YYYY-MM-DD
                    
                    # Criar novo lançamento
                    nova = pd.DataFrame([{
                        "data": data_iso,  # Salva como string ISO
                        "tipo": tipo,
                        "valor": valor,
                        "categoria": categoria,
                        "subcategoria": subcategoria.strip() if subcategoria else "",
                        "descricao": descricao.strip(),
                        "responsavel": responsavel,
                        "fixo": "Sim" if fixo else "Não"
                    }])
                    
                    # Concatenar com dados existentes
                    df = dados["historico"].copy() if not dados["historico"].empty else pd.DataFrame()
                    df = pd.concat([df, nova], ignore_index=True)
                    
                    # Atualizar dados na sessão
                    dados["historico"] = df
                    st.session_state["dados"] = dados
                    
                    # Salvar no banco de dados
                    DatabaseManager.save("historico", df, usuario)
                    
                    # Mensagem de sucesso
                    tipo_icon = {
                        "Despesa": "📉",
                        "Receita": "💰",
                        "Investimento": "📈"
                    }.get(tipo, "📝")
                    
                    st.session_state["msg"] = f"{tipo_icon} Transação de {tipo} registrada com sucesso!"
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ================= HISTÓRICO DE LANÇAMENTOS =================
    st.markdown("### 📋 Histórico de Transações")

    if not dados["historico"].empty:
        df_historico_total = dados["historico"].copy()
        df_historico_total.columns = df_historico_total.columns.str.lower()
        
        # CORREÇÃO ROBUSTA: Função para converter QUALQUER formato de data para datetime
        def converter_data_para_datetime(data_value):
            """Converte qualquer formato de data para datetime pandas"""
            # Se for NaN ou None
            if pd.isna(data_value) or data_value is None:
                return pd.NaT
            
            # Se já for pandas Timestamp, retorna como está
            if isinstance(data_value, pd.Timestamp):
                return data_value
            
            # Se for datetime.datetime, converte para Timestamp
            if isinstance(data_value, datetime):  # CORREÇÃO AQUI: apenas datetime
                return pd.Timestamp(data_value)
            
            # Se for date object, converte
            if isinstance(data_value, date):
                return pd.Timestamp(data_value)
            
            # Se for string, tenta vários formatos
            if isinstance(data_value, str):
                # Remove espaços extras
                data_str = data_value.strip()
                
                # Se string vazia
                if not data_str:
                    return pd.NaT
                
                # Tenta diferentes formatos de data
                formatos = [
                    '%Y-%m-%d',      # 2024-01-26
                    '%d/%m/%Y',      # 26/01/2024
                    '%d-%m-%Y',      # 26-01-2024
                    '%Y/%m/%d',      # 2024/01/26
                    '%d.%m.%Y',      # 26.01.2024
                    '%Y-%m-%d %H:%M:%S',  # Com hora
                    '%d/%m/%Y %H:%M:%S',  # Com hora
                ]
                
                for formato in formatos:
                    try:
                        return pd.to_datetime(data_str, format=formato)
                    except:
                        continue
                
                # Se nenhum formato funcionar, tenta conversão genérica
                try:
                    return pd.to_datetime(data_str, errors='coerce')
                except:
                    return pd.NaT
            
            # Para qualquer outro tipo, tenta converter
            try:
                return pd.to_datetime(data_value, errors='coerce')
            except:
                return pd.NaT
        
        # Aplicar a conversão a TODAS as datas
        if "data" in df_historico_total.columns:
            df_historico_total["data"] = df_historico_total["data"].apply(converter_data_para_datetime)
            
            # Remover entradas com datas inválidas
            df_historico_total = df_historico_total.dropna(subset=["data"])
        
        # CORREÇÃO: Garantir que o tipo seja datetime64[ns]
        df_historico_total["data"] = pd.to_datetime(df_historico_total["data"])
        
        # Agora sim pode ordenar
        df_historico_total = df_historico_total.sort_values("data", ascending=False)
        
        # Filtros
        with st.expander("🔍 **Filtros e Busca**", expanded=False):
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3, gap="medium")
            
            with col_filtro1:
                filtro_tipo = st.selectbox(
                    "Filtrar por tipo",
                    ["Todos", "Despesa", "Receita", "Investimento"],
                    key="filtro_tipo_lanc"
                )
            
            with col_filtro2:
                # Filtro por período
                filtro_periodo = st.selectbox(
                    "Período",
                    ["Todos", "Últimos 7 dias", "Últimos 30 dias", "Este mês", "Este ano"],
                    key="filtro_periodo_lanc"
                )
            
            with col_filtro3:
                # Filtro por categoria
                categorias_disponiveis_filtro = ["Todas"] + categorias_disponiveis
                filtro_categoria = st.selectbox(
                    "Categoria",
                    categorias_disponiveis_filtro,
                    key="filtro_categoria_lanc"
                )
        
        # Aplicar filtros
        df_filtrado = df_historico_total.copy()
        
        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["tipo"] == filtro_tipo]
        
        if filtro_categoria != "Todas":
            df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_categoria]
        
        if filtro_periodo != "Todos":
            hoje = date.today()
            if filtro_periodo == "Últimos 7 dias":
                data_limite = hoje - timedelta(days=7)
                df_filtrado = df_filtrado[df_filtrado["data"] >= pd.Timestamp(data_limite)]
            elif filtro_periodo == "Últimos 30 dias":
                data_limite = hoje - timedelta(days=30)
                df_filtrado = df_filtrado[df_filtrado["data"] >= pd.Timestamp(data_limite)]
            elif filtro_periodo == "Este mês":
                df_filtrado = df_filtrado[df_filtrado["data"].dt.strftime("%Y-%m") == mes_atual]
            elif filtro_periodo == "Este ano":
                df_filtrado = df_filtrado[df_filtrado["data"].dt.year == hoje.year]
        
        # Contadores
        total_filtrado = len(df_filtrado)
        receitas_filtradas = df_filtrado[df_filtrado["tipo"] == "Receita"]["valor"].sum() if not df_filtrado.empty else 0
        despesas_filtradas = df_filtrado[df_filtrado["tipo"] == "Despesa"]["valor"].sum() if not df_filtrado.empty else 0
        
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 20px;
            border: 1px solid #374151;
        ">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div style="font-size: 14px; color: #9ca3af;">📋 Total filtrado</div>
                    <div style="font-size: 20px; font-weight: bold; color: #f9fafb;">{total_filtrado} transações</div>
                </div>
                <div>
                    <div style="font-size: 14px; color: #9ca3af;">💰 Receitas</div>
                    <div style="font-size: 18px; font-weight: bold; color: #10b981;">R$ {receitas_filtradas:,.2f}</div>
                </div>
                <div>
                    <div style="font-size: 14px; color: #9ca3af;">📉 Despesas</div>
                    <div style="font-size: 18px; font-weight: bold; color: #ef4444;">R$ {despesas_filtradas:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # CORREÇÃO: Definir total_paginas com valor padrão
        total_paginas = 1  # Valor padrão mínimo
        
        # CORREÇÃO: Verificar se há dados filtrados antes de mostrar paginação
        if total_filtrado > 0:
            # Paginação
            if "pagina_lancamentos" not in st.session_state:
                st.session_state["pagina_lancamentos"] = 1
            
            itens_por_pagina = 10
            total_paginas = max(1, (total_filtrado - 1) // itens_por_pagina + 1)  # Garantir no mínimo 1 página
            
            # Ajustar página atual se necessário
            if st.session_state["pagina_lancamentos"] > total_paginas:
                st.session_state["pagina_lancamentos"] = total_paginas
            
            # Controle de página
            col_pagina1, col_pagina2, col_pagina3 = st.columns([1, 2, 1])
            with col_pagina2:
                pagina_selecionada = st.number_input(
                    "📄 Página",
                    min_value=1,
                    max_value=total_paginas,
                    value=st.session_state["pagina_lancamentos"],
                    key="pagina_input_lanc"
                )
            
            # Atualizar se o usuário mudou manualmente
            if pagina_selecionada != st.session_state["pagina_lancamentos"]:
                st.session_state["pagina_lancamentos"] = pagina_selecionada
                st.rerun()
            
            inicio = (st.session_state["pagina_lancamentos"] - 1) * itens_por_pagina
            fim = min(inicio + itens_por_pagina, total_filtrado)
            
            # Mostrar transações da página atual
            df_pagina = df_filtrado.iloc[inicio:fim].reset_index(drop=True)
            
            # Mostrar cards das transações
            for idx, row in df_pagina.iterrows():
                # Encontrar o índice original correspondente
                idx_original = df_filtrado.iloc[inicio:fim].index[idx]
                
                # Dados da transação
                data_transacao = row['data']
                tipo_transacao = row['tipo']
                valor_transacao = row['valor']
                categoria_transacao = row['categoria']
                descricao_transacao = row['descricao']
                responsavel_transacao = row['responsavel']
                fixo_transacao = row.get('fixo', 'Não')
                subcategoria_transacao = row.get('subcategoria', '')
                
                # Formatar data
                if isinstance(data_transacao, pd.Timestamp):
                    data_formatada = data_transacao.strftime("%d/%m/%Y")
                    dia_semana = data_transacao.strftime("%a")
                else:
                    data_formatada = str(data_transacao)[:10]
                    dia_semana = ""
                
                # Cores baseadas no tipo
                if tipo_transacao == "Despesa":
                    cor_tipo = "#ef4444"
                    icone_tipo = "📉"
                    prefixo_valor = "-"
                elif tipo_transacao == "Receita":
                    cor_tipo = "#10b981"
                    icone_tipo = "💰"
                    prefixo_valor = "+"
                else:  # Investimento
                    cor_tipo = "#3b82f6"
                    icone_tipo = "📈"
                    prefixo_valor = "↗️"
                
                # Card para cada transação
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background: #1f2937;
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 16px;
                        border-left: 4px solid {cor_tipo};
                        border: 1px solid #374151;
                    ">
                    """, unsafe_allow_html=True)
                    
                    # Cabeçalho
                    col_header1, col_header2 = st.columns([3, 1])
                    
                    with col_header1:
                        st.markdown(f"""
                        <div style="
                            font-size: 18px;
                            font-weight: bold;
                            color: #f9fafb;
                            margin-bottom: 4px;
                        ">{icone_tipo} {descricao_transacao[:50]}{'...' if len(descricao_transacao) > 50 else ''}</div>
                        <div style="
                            font-size: 14px;
                            color: #9ca3af;
                            margin-bottom: 8px;
                        ">
                            📂 {categoria_transacao} • 👤 {responsavel_transacao} • 📅 {data_formatada} {f'({dia_semana})' if dia_semana else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_header2:
                        st.markdown(f"""
                        <div style="text-align: right;">
                            <div style="
                                font-size: 24px;
                                font-weight: bold;
                                color: {cor_tipo};
                                margin-bottom: 4px;
                            ">{prefixo_valor} R$ {valor_transacao:,.2f}</div>
                            <div style="
                                font-size: 12px;
                                color: #6b7280;
                            ">
                                {tipo_transacao} {'• 🔄 Recorrente' if fixo_transacao == 'Sim' else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Subcategoria se existir
                    if subcategoria_transacao:
                        st.markdown(f"""
                        <div style="
                            background: {cor_tipo}20;
                            border-radius: 6px;
                            padding: 8px 12px;
                            margin-top: 8px;
                            display: inline-block;
                        ">
                            <span style="font-size: 12px; color: {cor_tipo};">
                                🏷️ {subcategoria_transacao}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Ações
                    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                    
                    col_acoes1, col_acoes2, col_acoes3 = st.columns(3, gap="small")
                    
                    with col_acoes1:
                        # Botão para marcar como recorrente/não recorrente
                        if fixo_transacao == 'Sim':
                            if st.button("🔄 Não Recorrente", key=f"fixo_no_{idx_original}", use_container_width=True):
                                df_historico_total.at[idx_original, 'fixo'] = 'Não'
                                dados["historico"] = df_historico_total
                                st.session_state["dados"] = dados
                                DatabaseManager.save("historico", df_historico_total, usuario)
                                st.session_state["msg"] = "Transação marcada como não recorrente!"
                                st.session_state["msg_tipo"] = "success"
                                st.rerun()
                        else:
                            if st.button("🔄 Tornar Recorrente", key=f"fixo_sim_{idx_original}", use_container_width=True):
                                df_historico_total.at[idx_original, 'fixo'] = 'Sim'
                                dados["historico"] = df_historico_total
                                st.session_state["dados"] = dados
                                DatabaseManager.save("historico", df_historico_total, usuario)
                                st.session_state["msg"] = "Transação marcada como recorrente!"
                                st.session_state["msg_tipo"] = "success"
                                st.rerun()
                    
                    with col_acoes2:
                        # Botão de edição rápida
                        if st.button("✏️ Editar", key=f"edit_lanc_{idx_original}", use_container_width=True):
                            st.session_state[f"editing_lanc_{idx_original}"] = True
                            st.rerun()
                    
                    with col_acoes3:
                        # Botão de exclusão com confirmação
                        if st.button("🗑️ Excluir", key=f"del_lanc_{idx_original}", use_container_width=True, type="secondary"):
                            st.session_state[f"confirm_del_lanc_{idx_original}"] = True
                            st.rerun()
                    
                    # Confirmação de exclusão
                    if st.session_state.get(f"confirm_del_lanc_{idx_original}", False):

                        
                        col_confirm1, col_confirm2 = st.columns([2, 1])
                        
                        with col_confirm1:
                            st.warning(f"⚠️ **Confirmar exclusão da transação?**")
                            st.caption(f"'{descricao_transacao[:50]}...' • {data_formatada} • R$ {valor_transacao:,.2f}")
                        
                        with col_confirm2:
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Sim", key=f"yes_del_lanc_{idx_original}", use_container_width=True):
                                    # Excluir transação
                                    df_historico_total = df_historico_total.drop(idx_original).reset_index(drop=True)
                                    dados["historico"] = df_historico_total
                                    st.session_state["dados"] = dados
                                    DatabaseManager.save("historico", df_historico_total, usuario)
                                    st.session_state["msg"] = f"✅ Transação excluída com sucesso!"
                                    st.session_state["msg_tipo"] = "success"
                                    st.session_state[f"confirm_del_lanc_{idx_original}"] = False
                                    st.rerun()
                            with col_no:
                                if st.button("❌ Não", key=f"no_del_lanc_{idx_original}", use_container_width=True):
                                    st.session_state[f"confirm_del_lanc_{idx_original}"] = False
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Formulário de edição
                    if st.session_state.get(f"editing_lanc_{idx_original}", False):

                        
                        with st.form(f"form_edit_lanc_{idx_original}"):
                            st.markdown(f"### ✏️ Editando: {descricao_transacao[:30]}...")
                            
                            col_edit1, col_edit2 = st.columns(2, gap="small")
                            
                            with col_edit1:
                                edit_data = st.date_input(
                                    "Data",
                                    value=pd.to_datetime(data_transacao).date() if isinstance(data_transacao, pd.Timestamp) else date.today(),
                                    key=f"edit_data_lanc_{idx_original}"
                                )
                                
                                edit_tipo = st.selectbox(
                                    "Tipo",
                                    ["Despesa", "Receita", "Investimento"],
                                    index=["Despesa", "Receita", "Investimento"].index(tipo_transacao) if tipo_transacao in ["Despesa", "Receita", "Investimento"] else 0,
                                    key=f"edit_tipo_lanc_{idx_original}"
                                )
                                
                                edit_valor = st.number_input(
                                    "Valor (R$)",
                                    min_value=0.0,
                                    step=10.0,
                                    value=valor_transacao,
                                    key=f"edit_valor_lanc_{idx_original}"
                                )
                            
                            with col_edit2:
                                edit_categoria = st.selectbox(
                                    "Categoria",
                                    categorias_disponiveis,
                                    index=categorias_disponiveis.index(categoria_transacao) if categoria_transacao in categorias_disponiveis else 0,
                                    key=f"edit_cat_lanc_{idx_original}"
                                )
                                
                                edit_subcategoria = st.text_input(
                                    "Subcategoria",
                                    value=subcategoria_transacao,
                                    key=f"edit_subcat_lanc_{idx_original}"
                                )
                                
                                edit_responsavel = st.radio(
                                    "Responsável",
                                    ["🧔 Ele", "👩‍🦰 Ela", "👨‍👩‍👧‍👦 Compartilhado"],
                                    index=["🧔 Ele", "👩‍🦰 Ela", "👨‍👩‍👧‍👦 Compartilhado"].index(responsavel_transacao) if responsavel_transacao in ["🧔 Ele", "👩‍🦰 Ela", "👨‍👩‍👧‍👦 Compartilhado"] else 0,
                                    horizontal=True,
                                    key=f"edit_resp_lanc_{idx_original}"
                                )
                            
                            edit_descricao = st.text_input(
                                "Descrição",
                                value=descricao_transacao,
                                key=f"edit_desc_lanc_{idx_original}"
                            )
                            
                            edit_fixo = st.checkbox(
                                "Recorrente",
                                value=fixo_transacao == 'Sim',
                                key=f"edit_fixo_lanc_{idx_original}"
                            )
                            
                            col_save, col_cancel = st.columns(2, gap="medium")
                            with col_save:
                                if st.form_submit_button(
                                    "💾 Salvar Alterações",
                                    use_container_width=True,
                                    type="primary"
                                ):
                                    # Atualizar os dados
                                    df_historico_total.at[idx_original, 'data'] = edit_data
                                    df_historico_total.at[idx_original, 'tipo'] = edit_tipo
                                    df_historico_total.at[idx_original, 'valor'] = float(edit_valor)
                                    df_historico_total.at[idx_original, 'categoria'] = edit_categoria
                                    df_historico_total.at[idx_original, 'subcategoria'] = edit_subcategoria.strip()
                                    df_historico_total.at[idx_original, 'descricao'] = edit_descricao.strip()
                                    df_historico_total.at[idx_original, 'responsavel'] = edit_responsavel
                                    df_historico_total.at[idx_original, 'fixo'] = 'Sim' if edit_fixo else 'Não'
                                    
                                    dados["historico"] = df_historico_total
                                    st.session_state["dados"] = dados
                                    DatabaseManager.save("historico", df_historico_total, usuario)
                                    
                                    st.session_state[f"editing_lanc_{idx_original}"] = False
                                    st.session_state["msg"] = f"✅ Transação atualizada com sucesso!"
                                    st.session_state["msg_tipo"] = "success"
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button(
                                    "❌ Cancelar",
                                    use_container_width=True,
                                    type="secondary"
                                ):
                                    st.session_state[f"editing_lanc_{idx_original}"] = False
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # CORREÇÃO: Apenas mostrar a legenda de paginação se houver transações
            if total_filtrado > 0:
                st.caption(f"📄 Página {st.session_state['pagina_lancamentos']} de {total_paginas} • {total_filtrado} transações no total")
        else:
            # CORREÇÃO: Mensagem quando não há transações filtradas
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 40px 20px;
                text-align: center;
                border: 2px dashed #374151;
                margin: 20px 0;
            ">
                <div style="font-size: 48px; margin-bottom: 16px; color: #6b7280;">🔍</div>
                <h4 style="color: #9ca3af; margin-bottom: 8px;">Nenhuma transação encontrada</h4>
                <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                    Tente ajustar os filtros ou registre sua primeira transação acima.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Mensagem para quando não há lançamentos no histórico
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            border: 2px dashed #374151;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">📝</div>
            <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhum lançamento registrado</h3>
            <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                Use o formulário acima para registrar suas primeiras transações e começar a acompanhar suas finanças!
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.divider()

    # ================= ANÁLISE E EXPORTAÇÃO =================
    if not dados["historico"].empty:
        st.markdown("### 📊 Análise e Exportação")
        
        with st.container():
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #374151;
            ">
                <div style="color: #d1d5db; margin-bottom: 16px;">
                    Analise seus dados e exporte para uso externo.
                </div>
            """, unsafe_allow_html=True)
            
            col_analise1, col_analise2 = st.columns(2, gap="medium")
            
            with col_analise1:
                # Gráfico de distribuição por tipo
                st.markdown("#### 📈 Distribuição por Tipo")
                
                if not df_historico_total.empty:
                    # Agrupar por tipo
                    df_tipo = df_historico_total.groupby('tipo')['valor'].sum().reset_index()
                    
                    if not df_tipo.empty:
                        fig_tipo = px.pie(
                            df_tipo,
                            values="valor",
                            names="tipo",
                            hole=0.4,
                            color_discrete_map={
                                "Despesa": "#ef4444",
                                "Receita": "#10b981",
                                "Investimento": "#3b82f6"
                            }
                        )
                        fig_tipo.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                        )
                        fig_tipo.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            font=dict(color="#e5e7eb"),
                            showlegend=True,
                            height=300,
                            margin=dict(t=20, b=20, l=20, r=20)
                        )
                        st.plotly_chart(fig_tipo, use_container_width=True)
            
            with col_analise2:
                # Exportação de dados
                st.markdown("#### 📤 Exportar Dados")
                
                col_exp1, col_exp2 = st.columns(2, gap="small")
                
                with col_exp1:
                    # Exportar CSV completo
                    csv = df_historico_total.to_csv(index=False)
                    st.download_button(
                        label="📥 CSV Completo",
                        data=csv,
                        file_name=f"lancamentos_{date.today().strftime('%Y_%m_%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Baixe todos os lançamentos em formato CSV"
                    )
                
                with col_exp2:
                    # Exportar resumo
                    total_transacoes = len(df_historico_total)
                    receitas_total = df_historico_total[df_historico_total["tipo"] == "Receita"]["valor"].sum()
                    despesas_total = df_historico_total[df_historico_total["tipo"] == "Despesa"]["valor"].sum()
                    
                    resumo = f"""📋 RESUMO DE LANÇAMENTOS - {date.today().strftime('%d/%m/%Y')}

📊 Estatísticas Gerais:
• Total de Transações: {total_transacoes}
• Receitas Totais: R$ {receitas_total:,.2f}
• Despesas Totais: R$ {despesas_total:,.2f}
• Saldo Geral: R$ {receitas_total - despesas_total:,.2f}

📈 Últimas 10 Transações:
"""
                    
                    # Adicionar últimas 10 transações
                    ultimas = df_historico_total.head(10)
                    for _, row in ultimas.iterrows():
                        data_str = row['data'].strftime("%d/%m/%Y") if isinstance(row['data'], pd.Timestamp) else str(row['data'])[:10]
                        tipo_sigla = "DESP" if row['tipo'] == "Despesa" else "REC" if row['tipo'] == "Receita" else "INV"
                        resumo += f"• {data_str} [{tipo_sigla}] {row['descricao'][:30]}... R$ {row['valor']:,.2f}\n"
                    
                    st.download_button(
                        label="📄 Resumo (TXT)",
                        data=resumo,
                        file_name=f"resumo_lancamentos_{date.today().strftime('%Y_%m_%d')}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        help="Baixe um resumo executivo dos seus lançamentos"
                    )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ================= LISTA DE LANÇAMENTOS COMPACTA =================
    st.subheader("📋 Lançamentos Registrados")
    
    if not dados["historico"].empty:
        df_historico = dados["historico"].copy()
        
        # Ordenar por data (mais recente primeiro)
        df_historico = df_historico.sort_values("data", ascending=False)
        
        # Container para a lista
        lista_container = st.container()
        
        with lista_container:
            for idx, row in df_historico.iterrows():
                # Determinar cor baseada no tipo
                if row['tipo'] == "Despesa":
                    valor_color = "red"
                    valor_prefix = "-"
                elif row['tipo'] == "Receita":
                    valor_color = "green"
                    valor_prefix = "+"
                else:
                    valor_color = "white"
                    valor_prefix = ""
                
                # Formatar data
                if isinstance(row['data'], str):
                    data_str = row['data']
                else:
                    data_str = row['data'].strftime("%d/%m/%Y")
                
                # Criar item compacto
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1], gap="small")
                
                with col1:
                    st.markdown(f"**{row['descricao'][:30]}{'...' if len(row['descricao']) > 30 else ''}**")
                    st.caption(f"{row['categoria']} • {row['responsavel']} • {data_str}")
                
                with col2:
                    st.markdown(f"<span style='color: {valor_color}; font-weight: bold;'>{valor_prefix}R$ {row['valor']:,.2f}</span>", unsafe_allow_html=True)
                
                with col3:
                    st.caption(row['tipo'])
                
                with col4:
                    # Botão para excluir - mais compacto
                    if st.button("🗑️", key=f"del_hist_{idx}", help="Excluir"):
                        # Remover da lista
                        df_historico = df_historico.drop(idx).reset_index(drop=True)
                        dados["historico"] = df_historico
                        st.session_state["dados"] = dados
                        DatabaseManager.save("historico", df_historico, usuario)
                        st.success("Lançamento excluído!")
                        st.rerun()
                
                # Divisor fino
                st.markdown("<hr style='margin: 6px 0; border-color: #1f2933;'>", unsafe_allow_html=True)
    else:
        st.caption("Nenhum lançamento registrado.")



# =========================================================
# 🐷 Meu Dinheiro Guardado - VERSÃO ESTILIZADA CORRIGIDA
# =========================================================

elif menu == "🐷 Meu Dinheiro Guardado":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #10b981;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">💰</span>
            Carteira de Investimentos
        </h1>
        <p style="color: #e5e7eb; margin: 0; opacity: 0.9;">
            Gerencie e acompanhe seus investimentos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#3b82f6"
        }.get(msg_tipo, "#3b82f6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ---------------- RESUMO ESTILIZADO ----------------
    # Criar uma cópia segura dos dados
    df_investimentos = dados["investimentos"].copy() if not dados["investimentos"].empty else pd.DataFrame()
    
    # Normalizar nomes das colunas para minúsculas
    if not df_investimentos.empty:
        df_investimentos.columns = df_investimentos.columns.str.lower()
    
    total = df_investimentos["valor_atual"].sum() if not df_investimentos.empty and "valor_atual" in df_investimentos.columns else 0
    total_formatado = f"R$ {total:,.2f}"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        margin-bottom: 24px;
        text-align: center;
    ">
        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Total Investido</div>
        <div style="font-size: 32px; font-weight: bold;">{total_formatado}</div>
        <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
            <i>Valor atual da sua carteira</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ---------------- FORM ADICIONAR SIMPLIFICADO ----------------
    with st.expander("➕ Adicionar Novo Investimento", expanded=False):
        with st.container():
            
            # Texto explicativo simples
            st.caption("Preencha apenas o básico. O resto nós configuramos para você.")

            with st.form("form_investimento", clear_on_submit=True):
                # 1. O BÁSICO (O que todo mundo sabe)
                col_basico1, col_basico2 = st.columns(2, gap="medium")
                
                with col_basico1:
                    instituicao = st.text_input("🏦 Onde está o dinheiro?", placeholder="Ex: Nubank, Caixa, Debaixo do colchão", help="O banco ou corretora onde o dinheiro está guardado.")
                    ativo = st.text_input("📝 Nome do Investimento", placeholder="Ex: Guardadinho, Poupança, CDB", help="Um nome para você identificar depois.")
                
                with col_basico2:
                    valor_atual = st.number_input(
                        "💰 Quanto tem lá hoje? (R$)", 
                        min_value=0.0, 
                        step=100.0,
                        value=1000.0,
                        help="O saldo atual bruto."
                    )
                    tipo = st.selectbox(
                        "📊 Tipo (Se não souber, escolha 'Outros')",
                        ["Renda Fixa", "Poupança", "Ações", "FIIs", "Tesouro Direto", "Criptomoedas", "Outros"],
                        help="Tenta classificar. Se for conta corrente ou Nubank, pode por 'Renda Fixa' ou 'Poupança'."
                    )

                # 2. O AVANÇADO (Escondido num expander dentro do form)
                with st.expander("⚙️ Detalhes Avançados (Opcional)", expanded=False):
                    st.caption("Só mexa aqui se você souber o que está fazendo. Senão, deixe como está.")
                    
                    col_adv1, col_adv2 = st.columns(2)
                    with col_adv1:
                        # Padrão: 0.8% ao mês (média da renda fixa hoje)
                        rendimento = st.number_input(
                            "📈 Rendimento Mensal (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=0.8, 
                            step=0.1,
                            help="Quanto rende por mês? Se não sabe, deixe 0.8% (média aproximada)."
                        ) / 100
                        
                        data_entrada = st.date_input("📅 Quando você aplicou?", date.today())

                    with col_adv2:
                        categoria = st.selectbox(
                            "🎯 Perfil de Risco",
                            ["Conservador", "Moderado", "Arrojado", "Especulativo"],
                            help="Conservador: Não quer perder dinheiro nunca. Arrojado: Aceita risco para ganhar mais."
                        )
                        observacao = st.text_area("📝 Notas", height=80, placeholder="Ex: Dinheiro da reserva de emergência")

                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(
                    "💾 SALVAR MEU DINHEIRO",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:
                    # Lógica de salvamento (igual a anterior, mas adaptada ao layout novo)
                    novo = pd.DataFrame([{
                        "instituicao": instituicao,
                        "ativo": ativo,
                        "tipo": tipo,
                        "valor_atual": valor_atual,
                        "data_entrada": data_entrada,
                        "rendimento_mensal": rendimento,
                        "categoria": categoria,
                        "observacao": observacao
                    }])
                    
                    if df_investimentos.empty:
                        df_atualizado = novo
                    else:
                        for col in novo.columns:
                            if col not in df_investimentos.columns:
                                df_investimentos[col] = None
                        
                        # Converter tipos para evitar erros
                        df_investimentos = df_investimentos.astype({
                            'valor_atual': 'float64', 
                            'rendimento_mensal': 'float64'
                        }, errors='ignore')
                        
                        df_atualizado = pd.concat([df_investimentos, novo], ignore_index=True)
                    
                    dados["investimentos"] = df_atualizado
                    st.session_state["dados"] = dados
                    DatabaseManager.save("investimentos", df_atualizado, usuario)
                    
                    st.session_state["msg"] = "✅ Dinheiro guardado com sucesso!"
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()

    # ---------------- LISTA DE INVESTIMENTOS ESTILIZADA ----------------
    st.markdown("### 📋 Meus Investimentos")
    
    if not df_investimentos.empty:
        # Container para lista
        with st.container():
            for idx, row in df_investimentos.iterrows():
                # Formatar data de entrada com segurança
                data_str = ""
                if 'data_entrada' in row and pd.notna(row['data_entrada']):
                    try:
                        if hasattr(row['data_entrada'], 'strftime'):
                            data_str = row['data_entrada'].strftime("%d/%m/%Y")
                        else:
                            # Tentar converter para datetime
                            data_dt = pd.to_datetime(row['data_entrada'], errors='coerce')
                            if pd.notna(data_dt):
                                data_str = data_dt.strftime("%d/%m/%Y")
                    except:
                        data_str = str(row['data_entrada'])
                
                # Obter valores com valores padrão
                ativo_nome = row.get('ativo', 'Sem nome') if pd.notna(row.get('ativo')) else 'Sem nome'
                instituicao_nome = row.get('instituicao', 'N/A') if pd.notna(row.get('instituicao')) else 'N/A'
                tipo_nome = row.get('tipo', 'N/A') if pd.notna(row.get('tipo')) else 'N/A'
                categoria_nome = row.get('categoria', 'Conservador') if pd.notna(row.get('categoria')) else 'Conservador'
                
                # Converter valores numéricos
                valor_atual_val = float(row.get('valor_atual', 0)) if pd.notna(row.get('valor_atual')) else 0
                rendimento_val = float(row.get('rendimento_mensal', 0)) if pd.notna(row.get('rendimento_mensal')) else 0
                
                # Definir cores baseadas no perfil
                cor_perfil = {
                    "Conservador": "#10b981",
                    "Moderado": "#3b82f6",
                    "Arrojado": "#f59e0b",
                    "Especulativo": "#ef4444"
                }.get(categoria_nome, "#6b7280")
                
                # Criar card para cada investimento
                with st.container():

                    
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1.5], gap="small")
                    
                    with col1:
                        # Nome do ativo com destaque
                        st.markdown(f"""
                        <div style="
                            font-size: 18px;
                            font-weight: bold;
                            color: white;
                            margin-bottom: 4px;
                        ">{ativo_nome}</div>
                        <div style="
                            font-size: 12px;
                            color: #9ca3af;
                        ">🏦 {instituicao_nome} • 📊 {tipo_nome}</div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Valor e rendimento
                        valor_formatado = f"R$ {valor_atual_val:,.2f}"
                        rend_formatado = f"{rendimento_val:.2%} ao mês" if rendimento_val != 0 else "N/A"
                        
                        st.markdown(f"""
                        <div style="
                            font-size: 16px;
                            font-weight: bold;
                            color: #10b981;
                            margin-bottom: 4px;
                        ">{valor_formatado}</div>
                        <div style="
                            font-size: 12px;
                            color: #6b7280;
                        ">📈 {rend_formatado}</div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        # Perfil e data
                        perfil_emoji = {
                            "Conservador": "🛡️",
                            "Moderado": "⚖️",
                            "Arrojado": "🚀",
                            "Especulativo": "🎲"
                        }.get(categoria_nome, "📊")
                        
                        st.markdown(f"""
                        <div style="
                            font-size: 12px;
                            color: {cor_perfil};
                            margin-bottom: 4px;
                            display: flex;
                            align-items: center;
                            gap: 4px;
                        ">
                            {perfil_emoji} <strong>{categoria_nome}</strong>
                        </div>
                        <div style="
                            font-size: 11px;
                            color: #6b7280;
                        ">📅 Entrada: {data_str if data_str else 'N/A'}</div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        # Botões de ação
                        btn_container = st.container()
                        with btn_container:
                            col_btn1, col_btn2 = st.columns(2, gap="small")
                            
                            with col_btn1:
                                if st.button(
                                    "✏️", 
                                    key=f"edit_{idx}",
                                    help="Editar investimento",
                                    use_container_width=True
                                ):
                                    st.session_state[f"editing_{idx}"] = True
                                    st.rerun()
                            
                            with col_btn2:
                                if st.button(
                                    "🗑️", 
                                    key=f"del_{idx}",
                                    help="Excluir investimento",
                                    use_container_width=True,
                                    type="secondary"
                                ):
                                    st.session_state[f"delete_confirm_{idx}"] = True
                    
                    # Modal de confirmação de exclusão
                    if st.session_state.get(f"delete_confirm_{idx}", False):

                        
                        col_confirm1, col_confirm2 = st.columns([3, 1])
                        with col_confirm1:
                            st.warning(f"⚠️ **Confirmar exclusão de {ativo_nome}?**")
                        
                        with col_confirm2:
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Sim", key=f"yes_{idx}", use_container_width=True):
                                    # Remover o investimento
                                    df_atualizado = df_investimentos.drop(idx).reset_index(drop=True)
                                    dados["investimentos"] = df_atualizado
                                    st.session_state["dados"] = dados
                                    DatabaseManager.save("investimentos", df_atualizado, usuario)
                                    st.session_state["msg"] = "✅ Investimento excluído com sucesso!"
                                    st.session_state["msg_tipo"] = "success"
                                    st.session_state[f"delete_confirm_{idx}"] = False
                                    st.rerun()
                            with col_no:
                                if st.button("❌ Não", key=f"no_{idx}", use_container_width=True):
                                    st.session_state[f"delete_confirm_{idx}"] = False
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Formulário de edição (aparece apenas quando ativado)
                    if st.session_state.get(f"editing_{idx}", False):

                        
                        with st.form(f"form_edit_{idx}"):
                            st.markdown(f"### ✏️ Editando: {ativo_nome}")
                            
                            col_e1, col_e2 = st.columns(2, gap="small")
                            
                            with col_e1:
                                edit_instituicao = st.text_input(
                                    "🏦 Instituição", 
                                    value=instituicao_nome,
                                    key=f"edit_inst_{idx}"
                                )
                                edit_ativo = st.text_input(
                                    "📈 Ativo", 
                                    value=ativo_nome,
                                    key=f"edit_ativo_{idx}"
                                )
                                
                                # Tipo com valor padrão seguro
                                tipo_options = ["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro", "Outros"]
                                tipo_index = 0
                                if tipo_nome in tipo_options:
                                    tipo_index = tipo_options.index(tipo_nome)
                                
                                edit_tipo = st.selectbox(
                                    "📊 Tipo",
                                    tipo_options,
                                    index=tipo_index,
                                    key=f"edit_tipo_{idx}"
                                )
                            
                            with col_e2:
                                edit_valor = st.number_input(
                                    "💰 Valor Atual (R$)", 
                                    min_value=0.0, 
                                    step=100.0, 
                                    value=valor_atual_val,
                                    key=f"edit_valor_{idx}"
                                )
                                edit_rendimento = st.number_input(
                                    "📈 Rendimento Mensal (%)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=rendimento_val * 100,
                                    step=0.1,
                                    key=f"edit_rend_{idx}"
                                ) / 100
                                
                                # Categoria com valor padrão seguro
                                cat_options = ["Conservador", "Moderado", "Arrojado", "Especulativo"]
                                cat_index = 0
                                if categoria_nome in cat_options:
                                    cat_index = cat_options.index(categoria_nome)
                                
                                edit_categoria = st.selectbox(
                                    "🎯 Perfil",
                                    cat_options,
                                    index=cat_index,
                                    key=f"edit_cat_{idx}"
                                )
                            
                            # Data com tratamento de erro
                            edit_data_entrada = date.today()
                            try:
                                if 'data_entrada' in row and pd.notna(row['data_entrada']):
                                    edit_data_entrada = pd.to_datetime(row['data_entrada']).date()
                            except:
                                pass
                            
                            edit_data_entrada = st.date_input(
                                "📅 Data de Entrada", 
                                value=edit_data_entrada,
                                key=f"edit_data_{idx}"
                            )
                            
                            edit_observacao = st.text_area(
                                "📝 Observações", 
                                value=row.get('observacao', '') if pd.notna(row.get('observacao')) else '',
                                key=f"edit_obs_{idx}",
                                height=80
                            )
                            
                            col_save, col_cancel = st.columns(2, gap="medium")
                            with col_save:
                                if st.form_submit_button(
                                    "💾 Salvar Alterações",
                                    use_container_width=True,
                                    type="primary"
                                ):
                                    # Atualizar os dados na cópia
                                    df_investimentos.at[idx, 'instituicao'] = edit_instituicao
                                    df_investimentos.at[idx, 'ativo'] = edit_ativo
                                    df_investimentos.at[idx, 'tipo'] = edit_tipo
                                    df_investimentos.at[idx, 'valor_atual'] = edit_valor
                                    df_investimentos.at[idx, 'data_entrada'] = edit_data_entrada
                                    df_investimentos.at[idx, 'rendimento_mensal'] = edit_rendimento
                                    df_investimentos.at[idx, 'categoria'] = edit_categoria
                                    df_investimentos.at[idx, 'observacao'] = edit_observacao
                                    
                                    # Atualizar dados na sessão
                                    dados["investimentos"] = df_investimentos
                                    st.session_state["dados"] = dados
                                    
                                    # Salvar no banco
                                    DatabaseManager.save("investimentos", df_investimentos, usuario)
                                    
                                    # Limpar estado e mostrar mensagem
                                    st.session_state[f"editing_{idx}"] = False
                                    st.session_state["msg"] = "✅ Investimento atualizado com sucesso!"
                                    st.session_state["msg_tipo"] = "success"
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button(
                                    "❌ Cancelar",
                                    use_container_width=True,
                                    type="secondary"
                                ):
                                    st.session_state[f"editing_{idx}"] = False
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Espaçamento entre cards
                st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            border: 2px dashed #374151;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">💰</div>
            <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhum investimento cadastrado</h3>
            <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                Clique em "➕ Adicionar Novo Investimento" para começar a construir sua carteira.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- GRÁFICOS ESTILIZADOS ----------------
    if not df_investimentos.empty and not df_investimentos.empty:
        st.divider()
        st.markdown("### 📊 Análise da Carteira")
        
        with st.container():

            
            # Preparar dados para gráficos
            # Garantir que temos as colunas necessárias
            for col in ['categoria', 'tipo', 'valor_atual', 'rendimento_mensal']:
                if col not in df_investimentos.columns:
                    df_investimentos[col] = None if col == 'categoria' or col == 'tipo' else 0
            
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                st.markdown("#### 🎯 Distribuição por Perfil")
                if 'categoria' in df_investimentos.columns and df_investimentos['categoria'].notna().any():
                    fig = px.pie(
                        df_investimentos,
                        values="valor_atual",
                        names="categoria",
                        hole=0.4,
                        color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#0e1117",
                        plot_bgcolor="#0e1117",
                        font=dict(color="#e5e7eb"),
                        showlegend=True,
                        height=350,
                        margin=dict(t=30, b=30, l=30, r=30),
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="right",
                            x=1.2,
                            font=dict(size=11)
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("⚠️ Sem dados de perfil disponíveis")
            
            with col2:
                st.markdown("#### 📊 Distribuição por Tipo")
                if 'tipo' in df_investimentos.columns and df_investimentos['tipo'].notna().any():
                    fig2 = px.pie(
                        df_investimentos,
                        values="valor_atual",
                        names="tipo",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig2.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                    )
                    fig2.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#0e1117",
                        plot_bgcolor="#0e1117",
                        font=dict(color="#e5e7eb"),
                        showlegend=True,
                        height=350,
                        margin=dict(t=30, b=30, l=30, r=30),
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="right",
                            x=1.2,
                            font=dict(size=11)
                        )
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("⚠️ Sem dados de tipo disponíveis")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Cards de estatísticas com tratamento de erros
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Calcular estatísticas com segurança
            num_investimentos = len(df_investimentos)
            
            avg_rendimento = 0
            if 'rendimento_mensal' in df_investimentos.columns:
                rendimentos = pd.to_numeric(df_investimentos['rendimento_mensal'], errors='coerce')
                if rendimentos.notna().any():
                    avg_rendimento = rendimentos.mean() * 100
            
            maior_investimento = 0
            if 'valor_atual' in df_investimentos.columns:
                valores = pd.to_numeric(df_investimentos['valor_atual'], errors='coerce')
                if valores.notna().any():
                    maior_investimento = valores.max()
            
            col_stats1, col_stats2, col_stats3 = st.columns(3, gap="medium")
            
            with col_stats1:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📈 Total de Investimentos</div>
                    <div style="font-size: 24px; font-weight: bold;">{num_investimentos}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Ativos na carteira</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stats2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📊 Rendimento Médio</div>
                    <div style="font-size: 24px; font-weight: bold; color: #10b981;">{avg_rendimento:.2f}%</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Mensal</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stats3:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Maior Investimento</div>
                    <div style="font-size: 24px; font-weight: bold; color: #3b82f6;">R$ {maior_investimento:,.0f}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Valor individual</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# =========================================================
# 🎯 Sonhos & Metas - VERSÃO ESTILIZADA COMPLETA
# =========================================================

elif menu == "🎯 Sonhos & Metas":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #a78bfa;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">🎯</span>
            Sonhos & Metas
        </h1>
        <p style="color: #e5e7eb; margin: 0; opacity: 0.9;">
            Transforme seus sonhos em realidade
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#8b5cf6"
        }.get(msg_tipo, "#8b5cf6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ---------------- RESUMO ESTILIZADO ----------------
    # Calcular métricas
    if not dados["sonhos_projetos"].empty:
        sonhos_ativos = dados["sonhos_projetos"][dados["sonhos_projetos"]["status"] != "Desistido"]
        
        if not sonhos_ativos.empty:
            total_alvo = sonhos_ativos["valor_alvo"].sum()
            total_atual = sonhos_ativos["valor_atual"].sum()
            progresso = (total_atual / total_alvo * 100) if total_alvo > 0 else 0
            num_sonhos = len(sonhos_ativos)
        else:
            total_alvo = total_atual = progresso = 0
            num_sonhos = 0
    else:
        total_alvo = total_atual = progresso = 0
        num_sonhos = 0
    
    # Cards de métricas
    st.markdown("### 📊 Visão Geral dos Sonhos")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🎯 Total de Sonhos</div>
                <div style="font-size: 28px; font-weight: bold;">{num_sonhos}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Ativos</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Economizado</div>
                <div style="font-size: 24px; font-weight: bold;">R$ {total_atual:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Valor acumulado</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #78350f 0%, #f59e0b 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🏆 Total em Metas</div>
                <div style="font-size: 24px; font-weight: bold;">R$ {total_alvo:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Valor necessário</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Cor baseada no progresso
            cor_progresso = "#ef4444" if progresso < 30 else "#f59e0b" if progresso < 70 else "#10b981"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                border: 2px solid {cor_progresso};
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📈 Progresso Geral</div>
                <div style="font-size: 28px; font-weight: bold; color: {cor_progresso};">{progresso:.1f}%</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Conclusão total</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ---------------- NOVO SONHO ESTILIZADO ----------------
    with st.expander("➕ Adicionar Novo Sonho", expanded=False):
        with st.container():

            
            with st.form("form_novo_sonho", clear_on_submit=True):
                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown("#### 📋 Informações Básicas")
                    nome = st.text_input("🎯 Nome do Sonho", placeholder="Ex: Viagem para Europa")
                    valor_alvo = st.number_input(
                        "💰 Valor Alvo (R$)", 
                        min_value=0.0, 
                        step=1000.0,
                        value=10000.0
                    )
                    categoria = st.selectbox(
                        "📂 Categoria",
                        ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"]
                    )

                with col2:
                    st.markdown("#### 📅 Planejamento")
                    data_alvo = st.date_input("📅 Data Alvo", date.today() + timedelta(days=365))
                    prioridade = st.selectbox("⚡ Prioridade", ["Baixa", "Média", "Alta"])
                    valor_inicial = st.number_input(
                        "💰 Valor Inicial (R$)", 
                        min_value=0.0, 
                        step=500.0,
                        value=0.0
                    )

                descricao = st.text_area(
                    "📝 Descrição", 
                    placeholder="Descreva seu sonho...",
                    height=80
                )

                submitted = st.form_submit_button(
                    "🎯 CRIAR SONHO",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:
                    novo = pd.DataFrame([{
                        "nome": nome,
                        "descricao": descricao,
                        "valor_alvo": valor_alvo,
                        "valor_atual": valor_inicial,
                        "data_alvo": data_alvo,
                        "prioridade": prioridade,
                        "status": "Em Andamento",
                        "categoria": categoria
                    }])

                    df = pd.concat([dados["sonhos_projetos"], novo], ignore_index=True)
                    dados["sonhos_projetos"] = df
                    st.session_state["dados"] = dados
                    DatabaseManager.save("sonhos_projetos", df, usuario)
                    
                    st.session_state["msg"] = "✅ Sonho criado com sucesso!"
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------- LISTA DE SONHOS ESTILIZADA ----------------
    st.markdown("### 📋 Meus Sonhos & Metas")
    
    if not dados["sonhos_projetos"].empty:
        for i, sonho in dados["sonhos_projetos"].iterrows():
            # Inicializar estado para exclusão
            delete_key = f"delete_sonho_{i}"
            if delete_key not in st.session_state:
                st.session_state[delete_key] = False
            
            # Dados do sonho
            is_desistido = sonho.get("status") == "Desistido"
            progresso_val = sonho["valor_atual"] / sonho["valor_alvo"] if sonho["valor_alvo"] > 0 else 0
            progresso_percent = min(progresso_val * 100, 100)
            
            # Cores baseadas no status
            cor_status = {
                "Em Andamento": "#3b82f6",
                "Concluído": "#10b981",
                "Desistido": "#6b7280"
            }.get(sonho.get('status', 'Em Andamento'), "#6b7280")
            
            # Cor da barra de progresso
            cor_barra = "#ef4444" if progresso_percent < 30 else "#f59e0b" if progresso_percent < 70 else "#10b981"
            
            # Container principal do sonho
            with st.container():
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 16px;
                    border-left: 4px solid {cor_status};
                    border: 1px solid #374151;
                ">
                """, unsafe_allow_html=True)
                
                # Cabeçalho
                col_title, col_status = st.columns([3, 1])
                
                with col_title:
                    status_emoji = "😢" if is_desistido else "🎯"
                    status_text = " (Desistido)" if is_desistido else ""
                    
                    st.markdown(f"""
                    <div style="
                        font-size: 20px;
                        font-weight: bold;
                        color: white;
                        margin-bottom: 4px;
                    ">{status_emoji} {sonho['nome']}<span style="color: {cor_status};">{status_text}</span></div>
                    <div style="
                        font-size: 14px;
                        color: #9ca3af;
                        margin-bottom: 8px;
                    ">
                        📂 {sonho.get('categoria', '')} • ⚡ {sonho.get('prioridade', '')} • 📅 {sonho['data_alvo']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_status:
                    st.markdown(f"""
                    <div style="
                        background: {cor_status}20;
                        border: 1px solid {cor_status};
                        border-radius: 20px;
                        padding: 6px 12px;
                        text-align: center;
                        color: {cor_status};
                        font-size: 12px;
                        font-weight: bold;
                    ">
                        {sonho.get('status', 'Em Andamento')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Barra de progresso
                if not is_desistido:
                    st.markdown(f"""
                    <div style="
                        background: #374151;
                        border-radius: 10px;
                        height: 12px;
                        margin: 12px 0;
                        overflow: hidden;
                    ">
                        <div style="
                            background: {cor_barra};
                            width: {progresso_percent}%;
                            height: 100%;
                            border-radius: 10px;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Métricas
                col_met1, col_met2, col_met3 = st.columns(3, gap="small")
                
                with col_met1:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 12px; color: #9ca3af;">💰 Economizado</div>
                        <div style="font-size: 18px; font-weight: bold; color: #10b981;">R$ {sonho['valor_atual']:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_met2:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 12px; color: #9ca3af;">🏆 Meta</div>
                        <div style="font-size: 18px; font-weight: bold; color: #3b82f6;">R$ {sonho['valor_alvo']:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_met3:
                    if not is_desistido:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="font-size: 12px; color: #9ca3af;">📈 Progresso</div>
                            <div style="font-size: 18px; font-weight: bold; color: {cor_barra};">{progresso_val:.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Ações rápidas
                st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                
                col_acoes1, col_acoes2, col_acoes3, col_acoes4 = st.columns(4, gap="small")
                
                with col_acoes1:
                    # Movimentar valor
                    with st.popover("💰 Movimentar", use_container_width=True):
                        
                        valor_mov = st.number_input(
                            "Valor (+ para adicionar, - para retirar)", 
                            value=0.0, 
                            step=100.0,
                            key=f"mov_{i}"
                        )
                        
                        if st.button("💾 Aplicar", key=f"apply_{i}", use_container_width=True):
                            novo_valor = sonho["valor_atual"] + valor_mov
                            if novo_valor >= 0:
                                dados["sonhos_projetos"].loc[i, "valor_atual"] = novo_valor
                                st.session_state["dados"] = dados
                                DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                                
                                acao = "adicionado" if valor_mov > 0 else "retirado"
                                st.session_state["msg"] = f"✅ {acao.capitalize()} R$ {abs(valor_mov):,.2f} no sonho '{sonho['nome']}'!"
                                st.session_state["msg_tipo"] = "success"
                                st.rerun()
                            else:
                                st.error("❌ Valor não pode ser negativo!")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with col_acoes2:
                    if is_desistido:
                        if st.button("🔄 Reativar", key=f"reat_{i}", use_container_width=True, type="secondary"):
                            dados["sonhos_projetos"].loc[i, "status"] = "Em Andamento"
                            st.session_state["dados"] = dados
                            DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                            
                            st.session_state["msg"] = f"✅ Sonho '{sonho['nome']}' reativado!"
                            st.session_state["msg_tipo"] = "success"
                            st.rerun()
                    else:
                        if st.button("😢 Desistir", key=f"des_{i}", use_container_width=True, type="secondary"):
                            dados["sonhos_projetos"].loc[i, "status"] = "Desistido"
                            st.session_state["dados"] = dados
                            DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                            
                            st.session_state["msg"] = f"⚠️ Sonho '{sonho['nome']}' marcado como desistido"
                            st.session_state["msg_tipo"] = "warning"
                            st.rerun()
                
                with col_acoes3:
                    if st.button("✏️ Editar", key=f"edit_sonho_{i}", use_container_width=True):
                        st.session_state[f"editing_sonho_{i}"] = not st.session_state.get(f"editing_sonho_{i}", False)
                        st.rerun()
                
                with col_acoes4:
                    # Sistema de exclusão em duas etapas
                    if not st.session_state[delete_key]:
                        if st.button("🗑️ Excluir", key=f"del_btn_{i}", use_container_width=True, type="secondary"):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        # Modo de confirmação
                        st.markdown(f"""
                        <div style="
                            background: #7f1d1d;
                            border-radius: 8px;
                            padding: 8px;
                            border: 1px solid #ef4444;
                            text-align: center;
                        ">
                            <div style="color: #ef4444; font-size: 12px; font-weight: bold;">
                                Excluir '{sonho['nome']}'?
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button("✅ Sim", key=f"confirm_yes_{i}", use_container_width=True):
                                # Excluir permanentemente
                                dados["sonhos_projetos"] = dados["sonhos_projetos"].drop(i).reset_index(drop=True)
                                st.session_state["dados"] = dados
                                DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                                st.session_state[delete_key] = False
                                
                                st.session_state["msg"] = f"❌ Sonho '{sonho['nome']}' excluído permanentemente!"
                                st.session_state["msg_tipo"] = "error"
                                st.rerun()
                        
                        with col_confirm2:
                            if st.button("❌ Não", key=f"confirm_no_{i}", use_container_width=True):
                                st.session_state[delete_key] = False
                                st.rerun()
                
                # Formulário de edição
                if st.session_state.get(f"editing_sonho_{i}", False):

                    
                    with st.form(f"form_edit_sonho_{i}"):
                        st.markdown(f"### ✏️ Editando: {sonho['nome']}")
                        
                        col_e1, col_e2 = st.columns(2, gap="small")
                        
                        with col_e1:
                            edit_nome = st.text_input(
                                "🎯 Nome", 
                                value=sonho["nome"], 
                                key=f"edit_nome_{i}"
                            )
                            edit_valor_alvo = st.number_input(
                                "💰 Valor Alvo", 
                                value=sonho["valor_alvo"], 
                                min_value=0.0, 
                                key=f"edit_alvo_{i}"
                            )
                            
                            # Categoria com valor padrão seguro
                            cat_options = ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"]
                            cat_index = 0
                            if sonho.get('categoria') in cat_options:
                                cat_index = cat_options.index(sonho.get('categoria'))
                            
                            edit_categoria = st.selectbox(
                                "📂 Categoria",
                                cat_options,
                                index=cat_index,
                                key=f"edit_cat_{i}"
                            )
                        
                        with col_e2:
                            edit_data_alvo = st.date_input(
                                "📅 Data Alvo", 
                                value=pd.to_datetime(sonho["data_alvo"]), 
                                key=f"edit_data_{i}"
                            )
                            
                            # Prioridade com valor padrão seguro
                            prio_options = ["Baixa", "Média", "Alta"]
                            prio_index = 1  # Default para Média
                            if sonho.get('prioridade') in prio_options:
                                prio_index = prio_options.index(sonho.get('prioridade'))
                            
                            edit_prioridade = st.selectbox(
                                "⚡ Prioridade",
                                prio_options,
                                index=prio_index,
                                key=f"edit_prio_{i}"
                            )
                            edit_valor_atual = st.number_input(
                                "💰 Valor Atual",
                                value=sonho["valor_atual"],
                                min_value=0.0,
                                key=f"edit_atual_{i}"
                            )
                        
                        edit_descricao = st.text_area(
                            "📝 Descrição", 
                            value=sonho.get("descricao", ""), 
                            height=80, 
                            key=f"edit_desc_{i}"
                        )
                        
                        # Status com valor padrão seguro
                        status_options = ["Em Andamento", "Desistido", "Concluído"]
                        status_index = 0  # Default para Em Andamento
                        if sonho.get('status') in status_options:
                            status_index = status_options.index(sonho.get('status'))
                        
                        edit_status = st.selectbox(
                            "📊 Status",
                            status_options,
                            index=status_index,
                            key=f"edit_status_{i}"
                        )
                        
                        col_save, col_cancel = st.columns(2, gap="medium")
                        
                        with col_save:
                            save_btn = st.form_submit_button(
                                "💾 Salvar Alterações",
                                use_container_width=True,
                                type="primary"
                            )
                        
                        with col_cancel:
                            cancel_btn = st.form_submit_button(
                                "❌ Cancelar",
                                use_container_width=True,
                                type="secondary"
                            )
                        
                        # Processar ações
                        if save_btn:
                            dados["sonhos_projetos"].loc[i, "nome"] = edit_nome
                            dados["sonhos_projetos"].loc[i, "valor_alvo"] = edit_valor_alvo
                            dados["sonhos_projetos"].loc[i, "categoria"] = edit_categoria
                            dados["sonhos_projetos"].loc[i, "data_alvo"] = edit_data_alvo
                            dados["sonhos_projetos"].loc[i, "prioridade"] = edit_prioridade
                            dados["sonhos_projetos"].loc[i, "valor_atual"] = edit_valor_atual
                            dados["sonhos_projetos"].loc[i, "descricao"] = edit_descricao
                            dados["sonhos_projetos"].loc[i, "status"] = edit_status
                            
                            st.session_state["dados"] = dados
                            DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                            st.session_state[f"editing_sonho_{i}"] = False
                            
                            st.session_state["msg"] = f"✅ Sonho '{edit_nome}' atualizado com sucesso!"
                            st.session_state["msg_tipo"] = "success"
                            st.rerun()
                        
                        if cancel_btn:
                            st.session_state[f"editing_sonho_{i}"] = False
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Espaçamento entre cards
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    else:
        # Mensagem para quando não há sonhos
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            border: 2px dashed #374151;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">🎯</div>
            <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhum sonho cadastrado</h3>
            <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                Crie seu primeiro sonho clicando em "➕ Adicionar Novo Sonho" acima!
            </p>
        </div>
        """, unsafe_allow_html=True)



# =========================================================
# 📅 Contas Mensais - VERSÃO ESTILIZADA COMPLETA (ANTIGO FLUXO FIXO)
# =========================================================

elif menu == "📅 Contas Mensais":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #a78bfa;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">🏢</span>
            Contas Mensais
        </h1>
        <p style="color: #e5e7eb; margin: 0; opacity: 0.9;">
            Controle suas receitas e despesas recorrentes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#8b5cf6"
        }.get(msg_tipo, "#8b5cf6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ================= CARREGAR E NORMALIZAR DADOS =================
    # 🔥 NORMALIZAR O DATAFRAME
    if not dados["fluxo_fixo"].empty:
        df_fluxo = dados["fluxo_fixo"].copy()
        df_fluxo.columns = df_fluxo.columns.str.lower()
        df_fluxo["tipo"] = df_fluxo["tipo"].astype(str).str.strip().str.title()
    else:
        df_fluxo = pd.DataFrame(columns=["tipo", "valor", "nome", "categoria", "recorrencia", "data_inicio", "data_fim", "observacao"])
    # ================= BOTÃO DE AUTOMAÇÃO =================
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #1e3a8a 0%, #172554 100%);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #3b82f6;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        ">
            <div style="color: white;">
                <div style="font-weight: bold; font-size: 16px;">⚡ Automação Mensal</div>
                <div style="font-size: 12px; opacity: 0.8;">Lançar todas as contas ativas no histórico deste mês</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_auto1, col_auto2 = st.columns([3, 1])
        with col_auto2:
            if st.button("🚀 Gerar Agora", use_container_width=True):
                sucesso, mensagem = processar_lancamentos_automaticos(dados, usuario)
                if sucesso:
                    st.success(mensagem)
                    st.balloons() # Efeito visual legal!
                    # Força recarregamento dos dados para atualizar os gráficos
                    st.session_state["dados"] = DatabaseManager.load_all(usuario)
                    st.rerun()
                else:
                    st.info(mensagem)
        
        st.markdown("</div>", unsafe_allow_html=True)
    # ======================================================
    # ================= RESUMO ESTILIZADO =================
    # Separar receitas e despesas
    receitas = df_fluxo[df_fluxo["tipo"] == "Receita"] if not df_fluxo.empty else pd.DataFrame()
    despesas = df_fluxo[df_fluxo["tipo"] == "Despesa"] if not df_fluxo.empty else pd.DataFrame()
    
    # Calcular totais
    total_receitas = receitas["valor"].sum() if not receitas.empty else 0
    total_despesas = despesas["valor"].sum() if not despesas.empty else 0
    saldo_fixo = total_receitas - total_despesas

    # Cards de métricas
    st.markdown("### 📊 Resumo dos Fluxos Fixos")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Receitas Fixas</div>
                <div style="font-size: 28px; font-weight: bold;">R$ {total_receitas:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Valor mensal recorrente</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c2d12 0%, #f97316 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📉 Despesas Fixas</div>
                <div style="font-size: 28px; font-weight: bold;">R$ {total_despesas:,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>Valor mensal obrigatório</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            cor_saldo = "#10b981" if saldo_fixo >= 0 else "#ef4444"
            icone_saldo = "🟢" if saldo_fixo >= 0 else "🔴"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                border: 2px solid {cor_saldo};
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📊 Saldo Líquido</div>
                <div style="font-size: 28px; font-weight: bold; color: {cor_saldo};">{icone_saldo} R$ {abs(saldo_fixo):,.0f}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>{"Superavit" if saldo_fixo >= 0 else "Deficit"}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_fluxos = len(df_fluxo) if not df_fluxo.empty else 0
            receitas_count = len(receitas) if not receitas.empty else 0
            despesas_count = len(despesas) if not despesas.empty else 0
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
            ">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📋 Total de Fluxos</div>
                <div style="font-size: 28px; font-weight: bold;">{total_fluxos}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                    <i>{receitas_count} receitas • {despesas_count} despesas</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ================= FORMULÁRIO PARA NOVO FLUXO =================
    st.markdown("### ➕ Adicionar Novo Fluxo")
    
    with st.expander("📝 Clique para expandir o formulário", expanded=False):
        with st.container():
            
            with st.form("form_novo_fluxo", clear_on_submit=True):
                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown("#### 📋 O que é isso?")
                    nome = st.text_input(
                        "🏷️ **Nome da Conta**",
                        placeholder="Ex: Aluguel, Netflix, Salário, Academia...",
                        help="Dê um nome fácil de lembrar. Ex: 'Faculdade' ou 'Salário da Esposa'."
                    )
                    
                    valor = st.number_input(
                        "💰 **Valor Mensal (R$)**",
                        min_value=0.0,
                        step=10.0,
                        value=1000.0,
                        format="%.2f",
                        help="Qual o valor dessa conta? Se variar um pouco (como luz), coloque uma média."
                    )
                    
                    tipo = st.selectbox(
                        "📊 **É dinheiro que entra ou sai?**",
                        ["Receita", "Despesa"],
                        help="Receita: Salário, Vendas, Pensão (Dinheiro entrando).\nDespesa: Contas a pagar (Dinheiro saindo)."
                    )

                with col2:
                    st.markdown("#### 🏷️ Detalhes")
                    
                    # Carregar categorias disponíveis
                    categorias_disponiveis = []
                    if not dados["categorias"].empty:
                        df_categorias = dados["categorias"].copy()
                        df_categorias.columns = df_categorias.columns.str.lower()
                        
                        if "ativa" in df_categorias.columns:
                            df_categorias["ativa"] = pd.to_numeric(df_categorias["ativa"], errors='coerce').fillna(1).astype(bool)
                            categorias_ativas = df_categorias[df_categorias["ativa"] == True]
                        else:
                            categorias_ativas = df_categorias
                        
                        if "nome" in categorias_ativas.columns:
                            categorias_disponiveis = categorias_ativas["nome"].dropna().unique().tolist()
                    
                    if not categorias_disponiveis:
                        categorias_disponiveis = ["Salário", "Aluguel", "Energia", "Água", "Internet", "Outros"]
                    
                    categoria = st.selectbox(
                        "📂 **Categoria**",
                        categorias_disponiveis, # Certifique-se que a variável existe como no código anterior
                        help="Agrupar ajuda a saber onde você gasta mais. Ex: 'Casa', 'Lazer'."
                    )
                    
                    recorrencia = st.selectbox(
                        "🔄 **Repete quando?**",
                        ["Mensal", "Anual", "Trimestral", "Semestral"],
                        help="Mensal: Todo mês tem (Aluguel, Luz).\nAnual: Uma vez por ano (IPTU, IPVA)."
                    )

                st.markdown("#### 📅 Período de Vigência")
                col_data1, col_data2 = st.columns(2, gap="large")
                
                with col_data1:
                    data_inicio = st.date_input(
                        "📅 **Data de Início**",
                        date.today(),
                        help="Data a partir da qual este fluxo começa a valer"
                    )
                
                with col_data2:
                    data_fim = st.date_input(
                        "⏰ **Data de Fim (opcional)**",
                        value=None,
                        help="Data em que este fluxo deixa de valer (deixe em branco para permanente)"
                    )

                observacao = st.text_area(
                    "📝 **Observações**",
                    placeholder="Adicione notas importantes sobre este fluxo...",
                    height=80,
                    help="Informações adicionais que possam ser úteis"
                )

                submitted = st.form_submit_button(
                    "💾 **SALVAR FLUXO**",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:
                    if not nome.strip():
                        st.error("❌ Por favor, informe um nome para o fluxo.")
                        st.stop()
                    
                    if valor <= 0:
                        st.error("❌ O valor deve ser maior que zero.")
                        st.stop()
                    
                    # Preparar datas para salvar
                    data_inicio_str = data_inicio.isoformat() if data_inicio else None
                    data_fim_str = data_fim.isoformat() if data_fim else None
                    
                    # Criar novo fluxo
                    novo = pd.DataFrame([{
                        "nome": nome.strip(),
                        "valor": float(valor),
                        "tipo": tipo.strip().title(),
                        "categoria": categoria,
                        "data_inicio": data_inicio_str,
                        "data_fim": data_fim_str,
                        "recorrencia": recorrencia,
                        "observacao": observacao.strip()
                    }])

                    # Concatenar com dados existentes
                    if df_fluxo.empty:
                        df_novo_fluxo = novo
                    else:
                        # Garantir que todas as colunas existam
                        for col in novo.columns:
                            if col not in df_fluxo.columns:
                                df_fluxo[col] = None
                        
                        df_novo_fluxo = pd.concat([df_fluxo, novo], ignore_index=True)
                    
                    # Atualizar dados na sessão
                    dados["fluxo_fixo"] = df_novo_fluxo
                    st.session_state["dados"] = dados
                    
                    # Salvar no banco de dados
                    DatabaseManager.save("fluxo_fixo", df_novo_fluxo, usuario)
                    
                    # Mensagem de sucesso
                    st.session_state["msg"] = f"✅ {tipo} '{nome}' salvo com sucesso!"
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ================= LISTA DE FLUXOS ESTILIZADA =================
    st.markdown("### 📋 Meus Fluxos Fixos")
    
    if not df_fluxo.empty:
        # Ordenar por tipo (receitas primeiro) e valor (maiores primeiro)
        df_fluxo = df_fluxo.sort_values(["tipo", "valor"], ascending=[True, False])
        
        # Criar abas para organização
        tab1, tab2 = st.tabs(["💰 **Receitas**", "📉 **Despesas**"])
        
        with tab1:
            if not receitas.empty:
                # Resumo das receitas
                receitas_ordenadas = receitas.sort_values("valor", ascending=False)
                
                for idx, row in receitas_ordenadas.iterrows():
                    # Dados do fluxo
                    nome_fluxo = row.get('nome', 'Sem nome')
                    valor_fluxo = row.get('valor', 0)
                    categoria_fluxo = row.get('categoria', 'Sem categoria')
                    recorrencia_fluxo = row.get('recorrencia', 'Mensal')
                    observacao_fluxo = row.get('observacao', '')
                    
                    # Formatar datas
                    data_inicio_format = ""
                    data_fim_format = ""
                    
                    if row.get('data_inicio'):
                        try:
                            data_inicio_format = pd.to_datetime(row['data_inicio']).strftime("%d/%m/%Y")
                        except:
                            data_inicio_format = str(row['data_inicio'])
                    
                    if row.get('data_fim'):
                        try:
                            data_fim_format = pd.to_datetime(row['data_fim']).strftime("%d/%m/%Y")
                        except:
                            data_fim_format = str(row['data_fim'])
                    
                    # Card para cada receita
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                            border-radius: 12px;
                            padding: 20px;
                            margin-bottom: 16px;
                            border: 1px solid #10b981;
                        ">
                        """, unsafe_allow_html=True)
                        
                        # Cabeçalho
                        col_header1, col_header2 = st.columns([3, 1])
                        
                        with col_header1:
                            st.markdown(f"""
                            <div style="
                                font-size: 20px;
                                font-weight: bold;
                                color: white;
                                margin-bottom: 4px;
                            ">💰 {nome_fluxo}</div>
                            <div style="
                                font-size: 14px;
                                color: rgba(255, 255, 255, 0.9);
                                margin-bottom: 8px;
                            ">
                                📂 {categoria_fluxo} • 🔄 {recorrencia_fluxo}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_header2:
                            st.markdown(f"""
                            <div style="
                                text-align: right;
                            ">
                                <div style="
                                    font-size: 24px;
                                    font-weight: bold;
                                    color: white;
                                    margin-bottom: 4px;
                                ">R$ {valor_fluxo:,.2f}</div>
                                <div style="
                                    font-size: 12px;
                                    color: rgba(255, 255, 255, 0.8);
                                ">por mês</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Detalhes
                        if observacao_fluxo or data_inicio_format or data_fim_format:
                            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                            
                            if observacao_fluxo:
                                st.markdown(f"""
                                <div style="
                                    font-size: 13px;
                                    color: rgba(255, 255, 255, 0.8);
                                    margin-bottom: 4px;
                                ">📝 {observacao_fluxo}</div>
                                """, unsafe_allow_html=True)
                            
                            col_detalhes1, col_detalhes2 = st.columns(2)
                            
                            with col_detalhes1:
                                if data_inicio_format:
                                    st.markdown(f"""
                                    <div style="
                                        font-size: 12px;
                                        color: rgba(255, 255, 255, 0.7);
                                    ">📅 Início: {data_inicio_format}</div>
                                    """, unsafe_allow_html=True)
                            
                            with col_detalhes2:
                                if data_fim_format:
                                    st.markdown(f"""
                                    <div style="
                                        font-size: 12px;
                                        color: rgba(255, 255, 255, 0.7);
                                    ">⏰ Fim: {data_fim_format}</div>
                                    """, unsafe_allow_html=True)
                        
                        # Ações
                        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                        
                        col_acoes1, col_acoes2, col_acoes3 = st.columns(3, gap="small")
                        
                        with col_acoes1:
                            # Botão de edição
                            if st.button("✏️ Editar", key=f"edit_rec_{idx}", use_container_width=True):
                                st.session_state[f"editing_rec_{idx}"] = True
                                st.rerun()
                        
                        with col_acoes2:
                            # Status (ativa/inativa)
                            status_fluxo = "Ativo"
                            if data_fim_format and pd.to_datetime(data_fim_format) < pd.Timestamp.now():
                                status_fluxo = "Expirado"
                            
                            st.markdown(f"""
                            <div style="
                                background: {'#10b981' if status_fluxo == 'Ativo' else '#6b7280'};
                                border-radius: 6px;
                                padding: 8px;
                                text-align: center;
                                color: white;
                                font-size: 12px;
                                font-weight: bold;
                            ">{status_fluxo}</div>
                            """, unsafe_allow_html=True)
                        
                        with col_acoes3:
                            # Botão de exclusão com confirmação
                            if st.button("🗑️ Excluir", key=f"del_rec_{idx}", use_container_width=True, type="secondary"):
                                st.session_state[f"confirm_del_rec_{idx}"] = True
                                st.rerun()
                        
                        # Confirmação de exclusão
                        if st.session_state.get(f"confirm_del_rec_{idx}", False):
                            st.markdown("""
                            <div style="
                                background: #7f1d1d;
                                border-radius: 8px;
                                padding: 16px;
                                margin-top: 12px;
                                border: 1px solid #ef4444;
                            ">
                            """, unsafe_allow_html=True)
                            
                            col_confirm1, col_confirm2 = st.columns([2, 1])
                            
                            with col_confirm1:
                                st.warning(f"⚠️ **Confirmar exclusão de '{nome_fluxo}'?**")
                                st.caption("Esta ação não pode ser desfeita.")
                            
                            with col_confirm2:
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("✅ Sim", key=f"yes_del_rec_{idx}", use_container_width=True):
                                        # Excluir fluxo
                                        df_fluxo = df_fluxo.drop(idx).reset_index(drop=True)
                                        dados["fluxo_fixo"] = df_fluxo
                                        st.session_state["dados"] = dados
                                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                                        st.session_state["msg"] = f"✅ Receita '{nome_fluxo}' excluída!"
                                        st.session_state["msg_tipo"] = "success"
                                        st.session_state[f"confirm_del_rec_{idx}"] = False
                                        st.rerun()
                                with col_no:
                                    if st.button("❌ Não", key=f"no_del_rec_{idx}", use_container_width=True):
                                        st.session_state[f"confirm_del_rec_{idx}"] = False
                                        st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Formulário de edição
                        if st.session_state.get(f"editing_rec_{idx}", False):
                            st.markdown("""
                            <div style="
                                background: rgba(16, 185, 129, 0.1);
                                border: 2px solid #10b981;
                                border-radius: 12px;
                                padding: 20px;
                                margin-top: 12px;
                            ">
                            """, unsafe_allow_html=True)
                            
                            with st.form(f"form_edit_rec_{idx}"):
                                st.markdown(f"### ✏️ Editando: {nome_fluxo}")
                                
                                col_edit1, col_edit2 = st.columns(2, gap="small")
                                
                                with col_edit1:
                                    edit_nome = st.text_input(
                                        "Nome", 
                                        value=nome_fluxo,
                                        key=f"edit_nome_rec_{idx}"
                                    )
                                    edit_valor = st.number_input(
                                        "Valor (R$)", 
                                        min_value=0.0, 
                                        step=10.0, 
                                        value=valor_fluxo,
                                        key=f"edit_valor_rec_{idx}"
                                    )
                                    edit_tipo = st.selectbox(
                                        "Tipo", 
                                        ["Receita", "Despesa"],
                                        index=0,  # Receita
                                        key=f"edit_tipo_rec_{idx}"
                                    )
                                
                                with col_edit2:
                                    # Categorias disponíveis
                                    edit_categoria = st.selectbox(
                                        "Categoria",
                                        categorias_disponiveis,
                                        index=categorias_disponiveis.index(categoria_fluxo) if categoria_fluxo in categorias_disponiveis else 0,
                                        key=f"edit_cat_rec_{idx}"
                                    )
                                    
                                    edit_recorrencia = st.selectbox(
                                        "Recorrência",
                                        ["Mensal", "Anual", "Trimestral", "Semestral"],
                                        index=["Mensal", "Anual", "Trimestral", "Semestral"].index(recorrencia_fluxo) if recorrencia_fluxo in ["Mensal", "Anual", "Trimestral", "Semestral"] else 0,
                                        key=f"edit_rec_rec_{idx}"
                                    )
                                
                                # Datas
                                edit_data_inicio = None
                                if row.get('data_inicio'):
                                    try:
                                        edit_data_inicio = pd.to_datetime(row['data_inicio']).date()
                                    except:
                                        edit_data_inicio = date.today()
                                else:
                                    edit_data_inicio = date.today()
                                
                                edit_data_inicio = st.date_input(
                                    "Data de Início", 
                                    value=edit_data_inicio,
                                    key=f"edit_inicio_rec_{idx}"
                                )
                                
                                edit_data_fim = None
                                if row.get('data_fim'):
                                    try:
                                        edit_data_fim = pd.to_datetime(row['data_fim']).date()
                                    except:
                                        edit_data_fim = None
                                
                                edit_data_fim = st.date_input(
                                    "Data de Fim (opcional)", 
                                    value=edit_data_fim,
                                    key=f"edit_fim_rec_{idx}"
                                )
                                
                                edit_observacao = st.text_area(
                                    "Observações", 
                                    value=observacao_fluxo,
                                    height=60,
                                    key=f"edit_obs_rec_{idx}"
                                )
                                
                                col_save, col_cancel = st.columns(2, gap="medium")
                                with col_save:
                                    if st.form_submit_button(
                                        "💾 Salvar Alterações",
                                        use_container_width=True,
                                        type="primary"
                                    ):
                                        # Atualizar os dados
                                        data_inicio_str = edit_data_inicio.isoformat() if edit_data_inicio else None
                                        data_fim_str = edit_data_fim.isoformat() if edit_data_fim else None
                                        
                                        df_fluxo.at[idx, 'nome'] = edit_nome
                                        df_fluxo.at[idx, 'valor'] = float(edit_valor)
                                        df_fluxo.at[idx, 'tipo'] = edit_tipo
                                        df_fluxo.at[idx, 'categoria'] = edit_categoria
                                        df_fluxo.at[idx, 'data_inicio'] = data_inicio_str
                                        df_fluxo.at[idx, 'data_fim'] = data_fim_str
                                        df_fluxo.at[idx, 'recorrencia'] = edit_recorrencia
                                        df_fluxo.at[idx, 'observacao'] = edit_observacao
                                        
                                        dados["fluxo_fixo"] = df_fluxo
                                        st.session_state["dados"] = dados
                                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                                        
                                        st.session_state[f"editing_rec_{idx}"] = False
                                        st.session_state["msg"] = f"✅ Receita '{edit_nome}' atualizada!"
                                        st.session_state["msg_tipo"] = "success"
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button(
                                        "❌ Cancelar",
                                        use_container_width=True,
                                        type="secondary"
                                    ):
                                        st.session_state[f"editing_rec_{idx}"] = False
                                        st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Mensagem para quando não há receitas
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 60px 20px;
                    text-align: center;
                    border: 2px dashed #374151;
                    margin: 20px 0;
                ">
                    <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">💰</div>
                    <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhuma receita fixa cadastrada</h3>
                    <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                        Adicione suas receitas recorrentes (salário, aluguéis, investimentos, etc.) usando o formulário acima.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            if not despesas.empty:
                # Resumo das despesas
                despesas_ordenadas = despesas.sort_values("valor", ascending=False)
                
                for idx, row in despesas_ordenadas.iterrows():
                    # Dados do fluxo
                    nome_fluxo = row.get('nome', 'Sem nome')
                    valor_fluxo = row.get('valor', 0)
                    categoria_fluxo = row.get('categoria', 'Sem categoria')
                    recorrencia_fluxo = row.get('recorrencia', 'Mensal')
                    observacao_fluxo = row.get('observacao', '')
                    
                    # Formatar datas
                    data_inicio_format = ""
                    data_fim_format = ""

                    if row.get('data_inicio'):
                        try:
                            # Se for string no formato YYYY-MM-DD, converter corretamente
                            if isinstance(row['data_inicio'], str):
                                # Remover hora se existir
                                data_str = row['data_inicio'].split(' ')[0] if ' ' in row['data_inicio'] else row['data_inicio']
                                # Converter para datetime
                                data_dt = pd.to_datetime(data_str, format='%Y-%m-%d', errors='coerce')
                                if pd.notna(data_dt):
                                    data_inicio_format = data_dt.strftime("%d/%m/%Y")
                                else:
                                    data_inicio_format = data_str
                            elif isinstance(row['data_inicio'], pd.Timestamp):
                                data_inicio_format = row['data_inicio'].strftime("%d/%m/%Y")
                            elif hasattr(row['data_inicio'], 'strftime'):
                                data_inicio_format = row['data_inicio'].strftime("%d/%m/%Y")
                            else:
                                data_inicio_format = str(row['data_inicio'])
                        except Exception as e:
                            data_inicio_format = str(row['data_inicio'])

                    if row.get('data_fim'):
                        try:
                            # Se for string no formato YYYY-MM-DD, converter corretamente
                            if isinstance(row['data_fim'], str):
                                # Remover hora se existir
                                data_str = row['data_fim'].split(' ')[0] if ' ' in row['data_fim'] else row['data_fim']
                                # Converter para datetime
                                data_dt = pd.to_datetime(data_str, format='%Y-%m-%d', errors='coerce')
                                if pd.notna(data_dt):
                                    data_fim_format = data_dt.strftime("%d/%m/%Y")
                                else:
                                    data_fim_format = data_str
                            elif isinstance(row['data_fim'], pd.Timestamp):
                                data_fim_format = row['data_fim'].strftime("%d/%m/%Y")
                            elif hasattr(row['data_fim'], 'strftime'):
                                data_fim_format = row['data_fim'].strftime("%d/%m/%Y")
                            else:
                                data_fim_format = str(row['data_fim'])
                        except Exception as e:
                            data_fim_format = str(row['data_fim'])
                    
                    # Card para cada despesa
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #7c2d12 0%, #f97316 100%);
                            border-radius: 12px;
                            padding: 20px;
                            margin-bottom: 16px;
                            border: 1px solid #f97316;
                        ">
                        """, unsafe_allow_html=True)
                        
                        # Cabeçalho
                        col_header1, col_header2 = st.columns([3, 1])
                        
                        with col_header1:
                            st.markdown(f"""
                            <div style="
                                font-size: 20px;
                                font-weight: bold;
                                color: white;
                                margin-bottom: 4px;
                            ">📉 {nome_fluxo}</div>
                            <div style="
                                font-size: 14px;
                                color: rgba(255, 255, 255, 0.9);
                                margin-bottom: 8px;
                            ">
                                📂 {categoria_fluxo} • 🔄 {recorrencia_fluxo}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_header2:
                            st.markdown(f"""
                            <div style="
                                text-align: right;
                            ">
                                <div style="
                                    font-size: 24px;
                                    font-weight: bold;
                                    color: white;
                                    margin-bottom: 4px;
                                ">R$ {valor_fluxo:,.2f}</div>
                                <div style="
                                    font-size: 12px;
                                    color: rgba(255, 255, 255, 0.8);
                                ">por mês</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Detalhes
                        if observacao_fluxo or data_inicio_format or data_fim_format:
                            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                            
                            if observacao_fluxo:
                                st.markdown(f"""
                                <div style="
                                    font-size: 13px;
                                    color: rgba(255, 255, 255, 0.8);
                                    margin-bottom: 4px;
                                ">📝 {observacao_fluxo}</div>
                                """, unsafe_allow_html=True)
                            
                            col_detalhes1, col_detalhes2 = st.columns(2)
                            
                            with col_detalhes1:
                                if data_inicio_format:
                                    st.markdown(f"""
                                    <div style="
                                        font-size: 12px;
                                        color: rgba(255, 255, 255, 0.7);
                                    ">📅 Início: {data_inicio_format}</div>
                                    """, unsafe_allow_html=True)
                            
                            with col_detalhes2:
                                if data_fim_format:
                                    st.markdown(f"""
                                    <div style="
                                        font-size: 12px;
                                        color: rgba(255, 255, 255, 0.7);
                                    ">⏰ Fim: {data_fim_format}</div>
                                    """, unsafe_allow_html=True)
                        
                        # Ações
                        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                        
                        col_acoes1, col_acoes2, col_acoes3 = st.columns(3, gap="small")
                        
                        with col_acoes1:
                            # Botão de edição
                            if st.button("✏️ Editar", key=f"edit_desp_{idx}", use_container_width=True):
                                st.session_state[f"editing_desp_{idx}"] = True
                                st.rerun()
                        
                        with col_acoes2:
                            # Status (ativa/inativa)
                            status_fluxo = "Ativo"
                            if data_fim_format and pd.to_datetime(data_fim_format) < pd.Timestamp.now():
                                status_fluxo = "Expirado"
                            
                            st.markdown(f"""
                            <div style="
                                background: {'#f97316' if status_fluxo == 'Ativo' else '#6b7280'};
                                border-radius: 6px;
                                padding: 8px;
                                text-align: center;
                                color: white;
                                font-size: 12px;
                                font-weight: bold;
                            ">{status_fluxo}</div>
                            """, unsafe_allow_html=True)
                        
                        with col_acoes3:
                            # Botão de exclusão com confirmação
                            if st.button("🗑️ Excluir", key=f"del_desp_{idx}", use_container_width=True, type="secondary"):
                                st.session_state[f"confirm_del_desp_{idx}"] = True
                                st.rerun()
                        
                        # Confirmação de exclusão
                        if st.session_state.get(f"confirm_del_desp_{idx}", False):
                            st.markdown("""
                            <div style="
                                background: #7f1d1d;
                                border-radius: 8px;
                                padding: 16px;
                                margin-top: 12px;
                                border: 1px solid #ef4444;
                            ">
                            """, unsafe_allow_html=True)
                            
                            col_confirm1, col_confirm2 = st.columns([2, 1])
                            
                            with col_confirm1:
                                st.warning(f"⚠️ **Confirmar exclusão de '{nome_fluxo}'?**")
                                st.caption("Esta ação não pode ser desfeita.")
                            
                            with col_confirm2:
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("✅ Sim", key=f"yes_del_desp_{idx}", use_container_width=True):
                                        # Excluir fluxo
                                        df_fluxo = df_fluxo.drop(idx).reset_index(drop=True)
                                        dados["fluxo_fixo"] = df_fluxo
                                        st.session_state["dados"] = dados
                                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                                        st.session_state["msg"] = f"✅ Despesa '{nome_fluxo}' excluída!"
                                        st.session_state["msg_tipo"] = "success"
                                        st.session_state[f"confirm_del_desp_{idx}"] = False
                                        st.rerun()
                                with col_no:
                                    if st.button("❌ Não", key=f"no_del_desp_{idx}", use_container_width=True):
                                        st.session_state[f"confirm_del_desp_{idx}"] = False
                                        st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Formulário de edição (estrutura similar às receitas)
                        # Formulário de edição
                        if st.session_state.get(f"editing_desp_{idx}", False):
                            st.markdown("""
                            <div style="
                                background: rgba(249, 115, 22, 0.1);
                                border: 2px solid #f97316;
                                border-radius: 12px;
                                padding: 20px;
                                margin-top: 12px;
                            ">
                            """, unsafe_allow_html=True)
                            
                            with st.form(f"form_edit_desp_{idx}"):
                                st.markdown(f"### ✏️ Editando: {nome_fluxo}")
                                
                                col_edit1, col_edit2 = st.columns(2, gap="small")
                                
                                with col_edit1:
                                    edit_nome = st.text_input(
                                        "Nome", 
                                        value=nome_fluxo,
                                        key=f"edit_nome_desp_{idx}"
                                    )
                                    edit_valor = st.number_input(
                                        "Valor (R$)", 
                                        min_value=0.0, 
                                        step=10.0, 
                                        value=valor_fluxo,
                                        key=f"edit_valor_desp_{idx}"
                                    )
                                    edit_tipo = st.selectbox(
                                        "Tipo", 
                                        ["Receita", "Despesa"],
                                        index=1,  # Despesa
                                        key=f"edit_tipo_desp_{idx}"
                                    )
                                
                                with col_edit2:
                                    # Categorias disponíveis
                                    edit_categoria = st.selectbox(
                                        "Categoria",
                                        categorias_disponiveis,
                                        index=categorias_disponiveis.index(categoria_fluxo) if categoria_fluxo in categorias_disponiveis else 0,
                                        key=f"edit_cat_desp_{idx}"
                                    )
                                    
                                    edit_recorrencia = st.selectbox(
                                        "Recorrência",
                                        ["Mensal", "Anual", "Trimestral", "Semestral"],
                                        index=["Mensal", "Anual", "Trimestral", "Semestral"].index(recorrencia_fluxo) if recorrencia_fluxo in ["Mensal", "Anual", "Trimestral", "Semestral"] else 0,
                                        key=f"edit_rec_desp_{idx}"
                                    )
                                
                                # Datas com tratamento correto
                                edit_data_inicio = None
                                if row.get('data_inicio'):
                                    try:
                                        if isinstance(row['data_inicio'], str):
                                            # Remover hora se existir
                                            data_str = row['data_inicio'].split(' ')[0] if ' ' in row['data_inicio'] else row['data_inicio']
                                            edit_data_inicio = pd.to_datetime(data_str, format='%Y-%m-%d', errors='coerce').date()
                                        elif isinstance(row['data_inicio'], pd.Timestamp):
                                            edit_data_inicio = row['data_inicio'].date()
                                        elif hasattr(row['data_inicio'], 'date'):
                                            edit_data_inicio = row['data_inicio'].date()
                                    except:
                                        edit_data_inicio = date.today()
                                else:
                                    edit_data_inicio = date.today()
                                
                                edit_data_inicio = st.date_input(
                                    "Data de Início", 
                                    value=edit_data_inicio,
                                    key=f"edit_inicio_desp_{idx}"
                                )
                                
                                edit_data_fim = None
                                if row.get('data_fim'):
                                    try:
                                        if isinstance(row['data_fim'], str):
                                            # Remover hora se existir
                                            data_str = row['data_fim'].split(' ')[0] if ' ' in row['data_fim'] else row['data_fim']
                                            edit_data_fim = pd.to_datetime(data_str, format='%Y-%m-%d', errors='coerce').date()
                                        elif isinstance(row['data_fim'], pd.Timestamp):
                                            edit_data_fim = row['data_fim'].date()
                                        elif hasattr(row['data_fim'], 'date'):
                                            edit_data_fim = row['data_fim'].date()
                                    except:
                                        edit_data_fim = None
                                
                                edit_data_fim = st.date_input(
                                    "Data de Fim (opcional)", 
                                    value=edit_data_fim,
                                    key=f"edit_fim_desp_{idx}"
                                )
                                
                                edit_observacao = st.text_area(
                                    "Observações", 
                                    value=observacao_fluxo,
                                    height=60,
                                    key=f"edit_obs_desp_{idx}"
                                )
                                
                                col_save, col_cancel = st.columns(2, gap="medium")
                                with col_save:
                                    if st.form_submit_button(
                                        "💾 Salvar Alterações",
                                        use_container_width=True,
                                        type="primary"
                                    ):
                                        # Atualizar os dados
                                        data_inicio_str = edit_data_inicio.isoformat() if edit_data_inicio else None
                                        data_fim_str = edit_data_fim.isoformat() if edit_data_fim else None
                                        
                                        df_fluxo.at[idx, 'nome'] = edit_nome
                                        df_fluxo.at[idx, 'valor'] = float(edit_valor)
                                        df_fluxo.at[idx, 'tipo'] = edit_tipo
                                        df_fluxo.at[idx, 'categoria'] = edit_categoria
                                        df_fluxo.at[idx, 'data_inicio'] = data_inicio_str
                                        df_fluxo.at[idx, 'data_fim'] = data_fim_str
                                        df_fluxo.at[idx, 'recorrencia'] = edit_recorrencia
                                        df_fluxo.at[idx, 'observacao'] = edit_observacao
                                        
                                        dados["fluxo_fixo"] = df_fluxo
                                        st.session_state["dados"] = dados
                                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                                        
                                        st.session_state[f"editing_desp_{idx}"] = False
                                        st.session_state["msg"] = f"✅ Despesa '{edit_nome}' atualizada!"
                                        st.session_state["msg_tipo"] = "success"
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button(
                                        "❌ Cancelar",
                                        use_container_width=True,
                                        type="secondary"
                                    ):
                                        st.session_state[f"editing_desp_{idx}"] = False
                                        st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Mensagem para quando não há despesas
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 60px 20px;
                    text-align: center;
                    border: 2px dashed #374151;
                    margin: 20px 0;
                ">
                    <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">📉</div>
                    <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhuma despesa fixa cadastrada</h3>
                    <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                        Adicione suas despesas recorrentes (aluguel, contas, financiamentos, etc.) usando o formulário acima.
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Mensagem para quando não há fluxos
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            border: 2px dashed #374151;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">🏢</div>
            <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhum fluxo fixo cadastrado</h3>
            <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                Comece adicionando suas receitas e despesas fixas para ter uma visão completa das suas finanças recorrentes.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ================= GRÁFICOS DE ANÁLISE =================
    if not df_fluxo.empty:
        st.markdown("### 📊 Análise dos Fluxos")
        
        with st.container():
            
            # Gráfico de pizza por categoria
            col_graf1, col_graf2 = st.columns(2, gap="medium")
            
            with col_graf1:
                st.markdown("#### 🏷️ Distribuição por Categoria")
                if not df_fluxo.empty and 'categoria' in df_fluxo.columns:
                    # Agrupar por categoria
                    df_categorias = df_fluxo.groupby('categoria')['valor'].sum().reset_index()
                    
                    if not df_categorias.empty:
                        fig_cat = px.pie(
                            df_categorias,
                            values="valor",
                            names="categoria",
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig_cat.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                        )
                        fig_cat.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            font=dict(color="#e5e7eb"),
                            showlegend=True,
                            height=350,
                            margin=dict(t=30, b=30, l=30, r=30)
                        )
                        st.plotly_chart(fig_cat, use_container_width=True)
                    else:
                        st.info("Sem dados de categorias para análise.")
            
            with col_graf2:
                st.markdown("#### 📅 Distribuição por Recorrência")
                if not df_fluxo.empty and 'recorrencia' in df_fluxo.columns:
                    # Agrupar por recorrência
                    df_recorrencia = df_fluxo.groupby('recorrencia')['valor'].sum().reset_index()
                    
                    if not df_recorrencia.empty:
                        fig_rec = px.bar(
                            df_recorrencia,
                            x="recorrencia",
                            y="valor",
                            color="recorrencia",
                            text="valor"
                        )
                        fig_rec.update_traces(
                            texttemplate="R$ %{text:,.0f}",
                            textposition="outside",
                            marker=dict(
                                line=dict(width=2, color="#1f2937")
                            )
                        )
                        fig_rec.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            font=dict(color="#e5e7eb"),
                            showlegend=False,
                            xaxis=dict(title=""),
                            yaxis=dict(title="Valor (R$)", gridcolor="#374151"),
                            height=350
                        )
                        st.plotly_chart(fig_rec, use_container_width=True)
                    else:
                        st.info("Sem dados de recorrência para análise.")
            
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ================= EXPORTAÇÃO DE DADOS =================
    st.markdown("### 📤 Exportar Dados")
    
    with st.container():
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #374151;
        ">
            <div style="color: #d1d5db; margin-bottom: 16px;">
                Exporte seus fluxos fixos para análise externa ou backup.
            </div>
        """, unsafe_allow_html=True)
        
        col_exp1, col_exp2 = st.columns(2, gap="medium")
        
        with col_exp1:
            # Exportar para CSV
            if not df_fluxo.empty:
                csv = df_fluxo.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar CSV Completo",
                    data=csv,
                    file_name=f"fluxos_fixos_{date.today().strftime('%Y_%m_%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Baixe todos os dados em formato CSV"
                )
        
        with col_exp2:
            # Exportar resumo
            if not df_fluxo.empty:
                # Calcular valores ANTES de formatar (forma mais segura)
                receita_media = total_receitas / len(receitas) if not receitas.empty else 0
                despesa_media = total_despesas / len(despesas) if not despesas.empty else 0
                margem_seguranca = ((total_receitas - total_despesas) / total_receitas * 100) if total_receitas > 0 else 0
                
                resumo = f"""📋 RESUMO DE FLUXOS FIXOS - {date.today().strftime('%d/%m/%Y')}

        🏢 Total de Fluxos: {len(df_fluxo)}
        💰 Receitas Fixas: R$ {total_receitas:,.2f} ({len(receitas) if not receitas.empty else 0} itens)
        📉 Despesas Fixas: R$ {total_despesas:,.2f} ({len(despesas) if not despesas.empty else 0} itens)
        📊 Saldo Líquido: R$ {saldo_fixo:,.2f} ({"Superavit" if saldo_fixo >= 0 else "Deficit"})

        💡 Análise:
        - Receita média: R$ {receita_media:,.2f}
        - Despesa média: R$ {despesa_media:,.2f}
        - Margem de segurança: {margem_seguranca:.1f}%
        """
                
                st.download_button(
                    label="📄 Baixar Resumo (TXT)",
                    data=resumo,
                    file_name=f"resumo_fluxos_{date.today().strftime('%Y_%m_%d')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    help="Baixe um resumo executivo dos seus fluxos"
                )
        
        st.markdown("</div>", unsafe_allow_html=True)



# =========================================================
# 🛒 Limite do Cartão/Mês - VERSÃO COM CARDS
# =========================================================

elif menu == "🛒 Limite do Cartão/Mês":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #7c3aed;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">💸</span>
            Controle de Gastos Mensais
        </h1>
        <p style="color: #e5e7eb; margin: 0; opacity: 0.9;">
            Reserva mensal para gastos do dia a dia
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#8b5cf6"
        }.get(msg_tipo, "#8b5cf6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ---------- RESERVA ----------
    reserva_mensal = float(config_dict.get("reserva_gastos", 0))

    if reserva_mensal == 0:
        st.warning("⚠️ Defina a reserva mensal em Configurações.")
        st.stop()

    # ---------- CARREGAR GASTOS ----------
    if "controle_gastos" not in dados or dados["controle_gastos"].empty:
        df_gastos = pd.DataFrame(columns=["data", "descricao", "valor"])
        # Criar coluna datetime mesmo vazia
        df_gastos["data"] = pd.to_datetime(df_gastos["data"], errors='coerce')
    else:
        df_gastos = dados["controle_gastos"].copy()
        
        # Converter 'data' para datetime SEMPRE
        df_gastos["data"] = pd.to_datetime(df_gastos["data"], errors='coerce')
        
        # Remover valores NaT (datas inválidas)
        if not df_gastos.empty:
            df_gastos = df_gastos.dropna(subset=["data"])

    # Cálculos
    gasto_total = df_gastos["valor"].sum() if not df_gastos.empty else 0
    saldo_restante = reserva_mensal - gasto_total
    percentual_gasto = (gasto_total / reserva_mensal * 100) if reserva_mensal > 0 else 0
    total_gastos = len(df_gastos)
    media_gasto = df_gastos["valor"].mean() if not df_gastos.empty else 0
    
    # Gastos de hoje
    hoje = date.today()
    df_gastos_hoje = df_gastos[df_gastos["data"].dt.date == hoje]
    gastos_hoje = df_gastos_hoje["valor"].sum() if not df_gastos_hoje.empty else 0
    qtd_gastos_hoje = len(df_gastos_hoje)

    # ---------- CARDS DE RESUMO ----------
    st.markdown("### 📊 Resumo do Mês")
    
    # Container para os cards
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            # Card 1: Reserva Mensal
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                margin-bottom: 10px;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        <span style="font-size: 20px;">💰</span>
                    </div>
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">Reserva Mensal</div>
                        <div style="font-size: 24px; font-weight: bold;">R$ {reserva:,.0f}</div>
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Valor disponível para gastos do mês</i>
                </div>
            </div>
            """.format(reserva=reserva_mensal), unsafe_allow_html=True)
        
        with col2:
            # Card 2: Total Gasto
            cor_gasto = "#f87171" if percentual_gasto > 80 else "#fbbf24" if percentual_gasto > 50 else "#60a5fa"
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                margin-bottom: 10px;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="
                        background: {cor};
                        border-radius: 10px;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        <span style="font-size: 20px;">🧾</span>
                    </div>
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">Total Gasto</div>
                        <div style="font-size: 24px; font-weight: bold;">R$ {gasto:,.0f}</div>
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>{percentual:.1f}% da reserva utilizada</i>
                </div>
            </div>
            """.format(cor=cor_gasto, gasto=gasto_total, percentual=percentual_gasto), unsafe_allow_html=True)
        
        with col3:
            # Card 3: Saldo Disponível
            cor_saldo = "#34d399" if saldo_restante >= 0 else "#f87171"
            icone_saldo = "🟢" if saldo_restante >= 0 else "🔴"
            texto_saldo = "Saldo Disponível" if saldo_restante >= 0 else "Estouro"
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                margin-bottom: 10px;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        <span style="font-size: 20px;">{icone}</span>
                    </div>
                    <div>
                        <div style="font-size: 14px; opacity: 0.9;">{texto}</div>
                        <div style="font-size: 24px; font-weight: bold;">R$ {saldo:,.0f}</div>
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>{status}</i>
                </div>
            </div>
            """.format(
                icone=icone_saldo,
                texto=texto_saldo,
                saldo=abs(saldo_restante),
                status="Dentro do orçamento" if saldo_restante >= 0 else "Acima do limite"
            ), unsafe_allow_html=True)
        
        with col4:
            # Card 4: Estatísticas
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
                margin-bottom: 10px;
            ">
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 14px; opacity: 0.9;">📊 Estatísticas</div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: bold;">{total}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Gastos</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: bold;">R$ {media:,.0f}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Média</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: bold;">{hoje}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Hoje</div>
                    </div>
                </div>
            </div>
            """.format(total=total_gastos, media=media_gasto, hoje=qtd_gastos_hoje), unsafe_allow_html=True)
    
    # Barra de progresso estilizada
    st.markdown("""
    <div style="
        background: #1f2937;
        border-radius: 10px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid #374151;
    ">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #d1d5db; font-size: 14px;">Utilização da Reserva</span>
            <span style="color: #60a5fa; font-weight: bold; font-size: 14px;">{percentual:.1f}%</span>
        </div>
        <div style="
            background: #374151;
            border-radius: 20px;
            height: 10px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #3b82f6, #60a5fa);
                width: {percentual}%;
                height: 100%;
                border-radius: 20px;
                transition: width 0.5s ease;
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px;">
            <span style="color: #9ca3af;">R$ 0</span>
            <span style="color: #9ca3af;">R$ {reserva:,.0f}</span>
        </div>
    </div>
    """.format(percentual=min(percentual_gasto, 100), reserva=reserva_mensal), unsafe_allow_html=True)

    st.divider()

    # ---------- CARD PARA NOVO GASTO ----------
    st.markdown("### ➕ Registrar Novo Gasto")
    
    with st.container():
        
        
        with st.form("form_gasto_rapido", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
            
            with col1:
                descricao = st.text_input(
                    "📝 Descrição",
                    placeholder="Ex: Café da manhã, Combustível, Farmácia...",
                    help="Descreva brevemente o gasto"
                )
            
            with col2:
                valor = st.number_input(
                    "💰 Valor (R$)",
                    min_value=0.01,
                    step=1.0,
                    value=10.0,
                    format="%.2f"
                )
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento para alinhar
                submitted = st.form_submit_button(
                    "💸 Registrar Gasto",
                    type="primary",
                    use_container_width=True
                )

            if submitted and descricao.strip():
                novo = pd.DataFrame([{
                    "data": date.today(),
                    "descricao": descricao.strip(),
                    "valor": valor
                }])

                df_gastos = pd.concat([df_gastos, novo], ignore_index=True)
                dados["controle_gastos"] = df_gastos
                st.session_state["dados"] = dados
                DatabaseManager.save("controle_gastos", df_gastos, usuario)
                
                st.success(f"✅ Gasto de **R$ {valor:,.2f}** registrado com sucesso!")
                st.rerun()
            elif submitted:
                st.error("❌ Por favor, informe uma descrição para o gasto")
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ---------- CARDS PARA HISTÓRICO DE GASTOS COM ABAS ----------
    st.markdown("### 📋 Histórico de Gastos")
        
    if not df_gastos.empty:
        # Ordenar por data (mais recente primeiro)
        df_gastos = df_gastos.sort_values("data", ascending=False)
        
        # Criar abas para organização
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Hoje", "📊 Este Mês", "📈 Todos", "🏷️ Categorias"])
        
        with tab1:
            # Gastos de hoje
            df_hoje = df_gastos[df_gastos["data"].dt.date == hoje]
            
            if not df_hoje.empty:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    border-radius: 12px;
                    padding: 16px;
                    color: #92400e;
                    margin-bottom: 20px;
                    border: 1px solid #fbbf24;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 16px; font-weight: bold;">📅 Resumo de Hoje</div>
                            <div style="font-size: 14px;">{len(df_hoje)} gastos registrados</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 20px; font-weight: bold;">R$ {df_hoje['valor'].sum():,.2f}</div>
                            <div style="font-size: 12px;">Total gasto hoje</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar gastos de hoje - usar enumerate para obter um contador único
                for i, (idx, row) in enumerate(df_hoje.iterrows()):
                    mostrar_gasto_card(idx, row, df_gastos, unique_counter=i)
            else:
                st.info("Nenhum gasto registrado hoje.")
        
        with tab2:
            # Gastos deste mês
            mes_atual = hoje.strftime("%Y-%m")
            df_mes = df_gastos[df_gastos["data"].dt.strftime("%Y-%m") == mes_atual]
            
            if not df_mes.empty:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border-radius: 12px;
                    padding: 16px;
                    color: #1e40af;
                    margin-bottom: 20px;
                    border: 1px solid #60a5fa;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 16px; font-weight: bold;">📊 Resumo do Mês</div>
                            <div style="font-size: 14px;">{len(df_mes)} gastos em {hoje.strftime('%B')}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 20px; font-weight: bold;">R$ {df_mes['valor'].sum():,.2f}</div>
                            <div style="font-size: 12px;">Total do mês</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Paginação para gastos do mês - usando session_state para controle
                if "pagina_mes_atual" not in st.session_state:
                    st.session_state["pagina_mes_atual"] = 1
                
                itens_por_pagina = 10
                total_paginas = (len(df_mes) - 1) // itens_por_pagina + 1
                
                # Ajustar página atual se necessário
                if st.session_state["pagina_mes_atual"] > total_paginas:
                    st.session_state["pagina_mes_atual"] = 1
                
                # Exibir seleção de página
                pagina_mes_selecionada = st.number_input(
                    "Página",
                    min_value=1,
                    max_value=total_paginas,
                    value=st.session_state["pagina_mes_atual"],
                    key="pagina_mes_input"
                )
                
                # Atualizar se o usuário mudou manualmente
                if pagina_mes_selecionada != st.session_state["pagina_mes_atual"]:
                    st.session_state["pagina_mes_atual"] = pagina_mes_selecionada
                    st.rerun()
                
                inicio = (st.session_state["pagina_mes_atual"] - 1) * itens_por_pagina
                fim = inicio + itens_por_pagina
                
                # Mostrar gastos da página atual - resetar índices para garantir unicidade
                df_mes_pagina = df_mes.iloc[inicio:fim].reset_index(drop=True)
                for i, (idx, row) in enumerate(df_mes_pagina.iterrows()):
                    # Encontrar o índice original correspondente
                    idx_original = df_mes.iloc[inicio:fim].index[i]
                    mostrar_gasto_card(idx_original, row, df_gastos, unique_counter=f"mes_{st.session_state['pagina_mes_atual']}_{i}")
                

                
                # Informação sobre total de páginas
                st.caption(f"Página {st.session_state['pagina_mes_atual']} de {total_paginas} • {len(df_mes)} gastos no total")
            else:
                st.info("Nenhum gasto registrado este mês.")
        
        with tab3:
            # Todos os gastos com paginação
            if not df_gastos.empty:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
                    border-radius: 12px;
                    padding: 16px;
                    color: #374151;
                    margin-bottom: 20px;
                    border: 1px solid #9ca3af;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 16px; font-weight: bold;">📈 Todos os Gastos</div>
                            <div style="font-size: 14px;">{len(df_gastos)} gastos registrados</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 20px; font-weight: bold;">R$ {df_gastos['valor'].sum():,.2f}</div>
                            <div style="font-size: 12px;">Total geral</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Filtros
                col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
                
                with col_filtro1:
                    ordenar_por = st.selectbox(
                        "Ordenar por",
                        ["Data (recente)", "Data (antigo)", "Valor (maior)", "Valor (menor)"],
                        key="ordenar_gastos"
                    )
                
                with col_filtro2:
                    # Filtro por período
                    periodo = st.selectbox(
                        "Período",
                        ["Todos", "Últimos 7 dias", "Últimos 30 dias", "Este ano", "Ano passado"],
                        key="periodo_gastos"
                    )
                
                with col_filtro3:
                    # Filtro por valor mínimo
                    valor_min = st.number_input(
                        "Valor mínimo (R$)",
                        min_value=0.0,
                        value=0.0,
                        step=10.0,
                        key="valor_min_gastos"
                    )
                
                # Aplicar filtros
                df_filtrado = df_gastos.copy()
                
                # Filtrar por período
                if periodo == "Últimos 7 dias":
                    data_limite = hoje - timedelta(days=7)
                    df_filtrado = df_filtrado[df_filtrado["data"] >= pd.Timestamp(data_limite)]
                elif periodo == "Últimos 30 dias":
                    data_limite = hoje - timedelta(days=30)
                    df_filtrado = df_filtrado[df_filtrado["data"] >= pd.Timestamp(data_limite)]
                elif periodo == "Este ano":
                    df_filtrado = df_filtrado[df_filtrado["data"].dt.year == hoje.year]
                elif periodo == "Ano passado":
                    df_filtrado = df_filtrado[df_filtrado["data"].dt.year == hoje.year - 1]
                
                # Filtrar por valor mínimo
                df_filtrado = df_filtrado[df_filtrado["valor"] >= valor_min]
                
                # Ordenar
                if ordenar_por == "Data (recente)":
                    df_filtrado = df_filtrado.sort_values("data", ascending=False)
                elif ordenar_por == "Data (antigo)":
                    df_filtrado = df_filtrado.sort_values("data", ascending=True)
                elif ordenar_por == "Valor (maior)":
                    df_filtrado = df_filtrado.sort_values("valor", ascending=False)
                elif ordenar_por == "Valor (menor)":
                    df_filtrado = df_filtrado.sort_values("valor", ascending=True)
                
                # Paginação - usar session_state para manter o estado
                if "pagina_total_atual" not in st.session_state:
                    st.session_state["pagina_total_atual"] = 1
                
                if "itens_por_pagina_total" not in st.session_state:
                    st.session_state["itens_por_pagina_total"] = 15
                
                # Controle de itens por página
                itens_por_pagina_total = st.slider(
                    "Itens por página",
                    min_value=5,
                    max_value=50,
                    value=st.session_state["itens_por_pagina_total"],
                    step=5,
                    key="itens_por_pagina_slider"
                )
                
                # Atualizar se o usuário mudou
                if itens_por_pagina_total != st.session_state["itens_por_pagina_total"]:
                    st.session_state["itens_por_pagina_total"] = itens_por_pagina_total
                    st.session_state["pagina_total_atual"] = 1  # Resetar para primeira página
                    st.rerun()
                
                total_paginas_total = (len(df_filtrado) - 1) // itens_por_pagina_total + 1
                
                # Ajustar página atual se necessário
                if st.session_state["pagina_total_atual"] > total_paginas_total:
                    st.session_state["pagina_total_atual"] = 1
                
                # Exibir seleção de página
                pagina_selecionada = st.number_input(
                    "Página",
                    min_value=1,
                    max_value=total_paginas_total,
                    value=st.session_state["pagina_total_atual"],
                    key="pagina_total_input"
                )
                
                # Atualizar se o usuário mudou manualmente
                if pagina_selecionada != st.session_state["pagina_total_atual"]:
                    st.session_state["pagina_total_atual"] = pagina_selecionada
                    st.rerun()
                
                inicio_total = (st.session_state["pagina_total_atual"] - 1) * itens_por_pagina_total
                fim_total = inicio_total + itens_por_pagina_total
                
                # Mostrar resultados
                st.caption(f"Mostrando {min(len(df_filtrado), itens_por_pagina_total)} de {len(df_filtrado)} gastos")
                
                # Resetar índices para garantir unicidade
                df_filtrado_pagina = df_filtrado.iloc[inicio_total:fim_total].reset_index(drop=True)
                for i, (idx, row) in enumerate(df_filtrado_pagina.iterrows()):
                    # Encontrar o índice original correspondente
                    idx_original = df_filtrado.iloc[inicio_total:fim_total].index[i]
                    mostrar_gasto_card(idx_original, row, df_gastos, unique_counter=f"todos_{st.session_state['pagina_total_atual']}_{i}")
                

                        

        
        # Substitua TODO o conteúdo da aba 4 (🏷️ Categorias) por:

        with tab4:
            # Análise por categorias AVANÇADA
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
                border-radius: 12px;
                padding: 16px;
                color: #7c3aed;
                margin-bottom: 20px;
                border: 1px solid #a78bfa;
            ">
                <div style="font-size: 16px; font-weight: bold;">🏷️ Análise Detalhada por Categorias</div>
                <div style="font-size: 14px;">Visualize como seu dinheiro está sendo distribuído</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Sistema de categorias hierárquico
            CATEGORIAS_HIERARQUICAS = {
                "🍔 Alimentação": {
                    "subcategorias": {
                        "🍔 Alimentação - Restaurante": "#ef4444",
                        "🍎 Alimentação - Supermercado": "#dc2626",
                        "☕ Alimentação - Café": "#92400e",
                        "🥩 Alimentação - Açougue": "#b91c1c",
                        "🍎 Alimentação - Hortifruti": "#16a34a"
                    },
                    "cor": "#ef4444"
                },
                "🚗 Transporte": {
                    "subcategorias": {
                        "🚗 Transporte - Combustível": "#3b82f6",
                        "🚕 Transporte - Táxi/Uber": "#1d4ed8",
                        "🚌 Transporte - Público": "#1e40af",
                        "🅿️ Transporte - Estacionamento": "#0ea5e9",
                        "🛠️ Transporte - Manutenção": "#6366f1"
                    },
                    "cor": "#3b82f6"
                },
                "🏠 Casa": {
                    "subcategorias": {
                        "🏠 Casa - Aluguel": "#8b5cf6",
                        "💡 Casa - Energia": "#f59e0b",
                        "💧 Casa - Água": "#0ea5e9",
                        "🔥 Casa - Gás": "#ef4444",
                        "📡 Casa - Internet/TV": "#8b5cf6"
                    },
                    "cor": "#8b5cf6"
                },
                "🛒 Compras": {
                    "subcategorias": {
                        "🛍️ Compras - Roupas": "#ec4899",
                        "📱 Compras - Eletrônicos": "#6b7280",
                        "💄 Compras - Beleza": "#f472b6",
                        "📚 Compras - Livros": "#84cc16",
                        "🎁 Compras - Presentes": "#a855f7"
                    },
                    "cor": "#ec4899"
                },
                "🎯 Lazer": {
                    "subcategorias": {
                        "🎬 Lazer - Cinema": "#a78bfa",
                        "🍻 Lazer - Bar": "#f59e0b",
                        "✈️ Lazer - Viagem": "#3b82f6",
                        "🎮 Lazer - Games": "#8b5cf6",
                        "🏋️ Lazer - Esportes": "#10b981"
                    },
                    "cor": "#a78bfa"
                },
                "🧑‍⚕️ Saúde": {
                    "subcategorias": {
                        "🏥 Saúde - Consulta": "#10b981",
                        "💊 Saúde - Medicamento": "#ef4444",
                        "❤️ Saúde - Plano": "#dc2626"
                    },
                    "cor": "#10b981"
                },
                "💼 Trabalho": {
                    "subcategorias": {
                        "💼 Trabalho - Material": "#6b7280",
                        "💻 Trabalho - Software": "#3b82f6",
                        "📞 Trabalho - Telefone": "#10b981"
                    },
                    "cor": "#6b7280"
                },
                "🧾 Finanças": {
                    "subcategorias": {
                        "🏦 Finanças - Taxa Bancária": "#059669",
                        "📊 Finanças - Investimento": "#84cc16",
                        "🧾 Finanças - Seguro": "#3b82f6"
                    },
                    "cor": "#059669"
                },
                "👨‍👩‍👧‍👦 Família": {
                    "subcategorias": {
                        "👶 Família - Filhos": "#f472b6",
                        "🐕 Família - Pets": "#f59e0b",
                        "🎉 Família - Eventos": "#8b5cf6"
                    },
                    "cor": "#f472b6"
                },
                "💰 Outros": {
                    "subcategorias": {
                        "🎫 Outros - Assinaturas": "#6b7280",
                        "📝 Outros - Variados": "#9ca3af"
                    },
                    "cor": "#6b7280"
                }
            }
            
            # Detectar categorias automaticamente
            categorias_detalhadas = {}
            palavras_chave_detalhadas = {
                "🍔 Alimentação - Restaurante": ['restaurante', 'lanche', 'fast food', 'pizza', 'hamburguer'],
                "🍎 Alimentação - Supermercado": ['mercado', 'supermercado', 'atacadão'],
                "☕ Alimentação - Café": ['café', 'cafeteria', 'starbucks', 'padaria'],
                "🥩 Alimentação - Açougue": ['açougue', 'carnes', 'frango', 'peixe'],
                "🍎 Alimentação - Hortifruti": ['feira', 'hortifruti', 'fruta', 'legume'],
                "🚗 Transporte - Combustível": ['gasolina', 'combustível', 'posto'],
                "🚕 Transporte - Táxi/Uber": ['uber', 'táxi', '99', 'cabify'],
                "🚌 Transporte - Público": ['ônibus', 'metro', 'trem', 'bilhete'],
                "🅿️ Transporte - Estacionamento": ['estacionamento', 'parking', 'garagem'],
                "🛠️ Transporte - Manutenção": ['oficina', 'mecânico', 'troca de óleo'],
                "🏠 Casa - Aluguel": ['aluguel', 'condomínio', 'iptu'],
                "💡 Casa - Energia": ['luz', 'energia', 'conta de luz'],
                "💧 Casa - Água": ['água', 'conta de água', 'sabesp'],
                "🔥 Casa - Gás": ['gás', 'botijão', 'gás natural'],
                "📡 Casa - Internet/TV": ['internet', 'net', 'claro', 'vivo'],
                "🛍️ Compras - Roupas": ['roupa', 'calçado', 'sapato', 'tenis'],
                "📱 Compras - Eletrônicos": ['celular', 'notebook', 'tablet', 'tv'],
                "💄 Compras - Beleza": ['farmácia', 'drogaria', 'perfume', 'maquiagem'],
                "📚 Compras - Livros": ['livro', 'revista', 'jornal', 'leitura'],
                "🎁 Compras - Presentes": ['presente', 'aniversário', 'natal'],
                "🎬 Lazer - Cinema": ['cinema', 'filme', 'ingresso', 'netflix'],
                "🍻 Lazer - Bar": ['bar', 'boteco', 'cerveja', 'drink'],
                "✈️ Lazer - Viagem": ['viagem', 'hotel', 'passagem', 'turismo'],
                "🎮 Lazer - Games": ['jogo', 'game', 'playstation', 'xbox'],
                "🏋️ Lazer - Esportes": ['academia', 'ginásio', 'esporte', 'natação'],
                "💼 Trabalho - Material": ['material', 'escritório', 'caneta', 'papel'],
                "💻 Trabalho - Software": ['software', 'assinatura', 'licença', 'app'],
                "📞 Trabalho - Telefone": ['telefone', 'celular empresa', 'recarga'],
                "🏥 Saúde - Consulta": ['consulta', 'médico', 'dentista', 'psicólogo'],
                "💊 Saúde - Medicamento": ['remédio', 'medicamento', 'farmacia'],
                "❤️ Saúde - Plano": ['plano de saúde', 'unimed', 'amil'],
                "🏦 Finanças - Taxa Bancária": ['taxa', 'tarifa', 'anuidade', 'banco'],
                "📊 Finanças - Investimento": ['investimento', 'ações', 'fii', 'tesouro'],
                "🧾 Finanças - Seguro": ['seguro', 'apólice', 'previdência'],
                "👶 Família - Filhos": ['creche', 'escola', 'material escolar', 'uniforme'],
                "🐕 Família - Pets": ['pet', 'veterinário', 'ração', 'gato'],
                "🎉 Família - Eventos": ['festa', 'casamento', 'formatura', 'comemoração'],
                "🎫 Outros - Assinaturas": ['assinatura', 'streaming', 'spotify', 'youtube'],
                "📝 Outros - Variados": []
            }
            
            # Processar todos os gastos
            for idx, row in df_gastos.iterrows():
                desc_lower = row['descricao'].lower()
                categoria_encontrada = False
                
                for categoria, palavras in palavras_chave_detalhadas.items():
                    if any(palavra in desc_lower for palavra in palavras):
                        if categoria not in categorias_detalhadas:
                            categorias_detalhadas[categoria] = 0
                        categorias_detalhadas[categoria] += row['valor']
                        categoria_encontrada = True
                        break
                
                if not categoria_encontrada:
                    if "📝 Outros - Variados" not in categorias_detalhadas:
                        categorias_detalhadas["📝 Outros - Variados"] = 0
                    categorias_detalhadas["📝 Outros - Variados"] += row['valor']
            
            # Criar abas para navegação entre categorias principais
            categorias_principais = list(CATEGORIAS_HIERARQUICAS.keys())
            
            if categorias_detalhadas:
                # Seção 1: Visão Geral
                st.markdown("#### 📊 Visão Geral por Categoria Principal")
                
                # Agrupar por categoria principal
                totais_principais = {}
                for cat_detalhada, valor in categorias_detalhadas.items():
                    # Encontrar categoria principal
                    for cat_principal, info in CATEGORIAS_HIERARQUICAS.items():
                        if cat_detalhada in info["subcategorias"]:
                            if cat_principal not in totais_principais:
                                totais_principais[cat_principal] = 0
                            totais_principais[cat_principal] += valor
                            break
                
                # Gráfico de pizza por categoria principal
                if totais_principais:
                    df_principais = pd.DataFrame({
                        'Categoria': list(totais_principais.keys()),
                        'Valor': list(totais_principais.values())
                    })
                    
                    # Adicionar cores
                    df_principais['Cor'] = df_principais['Categoria'].apply(
                        lambda x: CATEGORIAS_HIERARQUICAS[x]["cor"]
                    )
                    
                    fig1 = px.pie(
                        df_principais,
                        values='Valor',
                        names='Categoria',
                        title='Distribuição por Categoria Principal',
                        color='Cor',
                        color_discrete_map={row['Cor']: row['Cor'] for _, row in df_principais.iterrows()}
                    )
                    fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                    )
                    fig1.update_layout(
                        height=500,
                        showlegend=True,
                        plot_bgcolor='#0e1117',
                        paper_bgcolor='#0e1117',
                        font=dict(color='#e5e7eb'),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                # Seção 2: Navegação Detalhada
                st.markdown("#### 🔍 Análise Detalhada por Subcategoria")
                
                # Seletor de categoria principal
                categoria_selecionada = st.selectbox(
                    "Selecione uma categoria para detalhar:",
                    categorias_principais,
                    key="categoria_principal"
                )
                
                if categoria_selecionada:
                    # Filtrar subcategorias da categoria selecionada
                    subcategorias_info = CATEGORIAS_HIERARQUICAS[categoria_selecionada]["subcategorias"]
                    cor_principal = CATEGORIAS_HIERARQUICAS[categoria_selecionada]["cor"]
                    
                    # Card da categoria principal
                    st.markdown(f"""
                    <div style="
                        background: {cor_principal}20;
                        border: 2px solid {cor_principal};
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 20px;
                    ">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <span style="font-size: 32px;">{categoria_selecionada.split(' ')[0]}</span>
                            <div>
                                <div style="font-size: 18px; font-weight: bold; color: {cor_principal};">
                                    {categoria_selecionada}
                                </div>
                                <div style="color: #d1d5db;">
                                    {len(subcategorias_info)} subcategorias disponíveis
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Calcular totais por subcategoria
                    subcategorias_totais = {}
                    for subcat in subcategorias_info.keys():
                        if subcat in categorias_detalhadas:
                            subcategorias_totais[subcat] = categorias_detalhadas[subcat]
                    
                    if subcategorias_totais:
                        # Gráfico de barras por subcategoria
                        df_subcategorias = pd.DataFrame({
                            'Subcategoria': list(subcategorias_totais.keys()),
                            'Valor': list(subcategorias_totais.values())
                        })
                        
                        # Extrair nome curto para exibição
                        df_subcategorias['Nome Curto'] = df_subcategorias['Subcategoria'].apply(
                            lambda x: x.split(' - ')[1] if ' - ' in x else x
                        )
                        
                        fig2 = px.bar(
                            df_subcategorias.sort_values('Valor', ascending=False),
                            x='Nome Curto',
                            y='Valor',
                            color='Subcategoria',
                            color_discrete_map=subcategorias_info,
                            title=f'Distribuição em {categoria_selecionada}',
                            text='Valor'
                        )
                        fig2.update_traces(
                            texttemplate='R$ %{text:,.0f}',
                            textposition='outside',
                            marker=dict(
                                line=dict(width=2, color='#1f2937')
                            )
                        )
                        fig2.update_layout(
                            height=400,
                            showlegend=False,
                            plot_bgcolor='#0e1117',
                            paper_bgcolor='#0e1117',
                            font=dict(color='#e5e7eb'),
                            xaxis=dict(
                                title="",
                                tickfont=dict(size=12),
                                tickangle=45
                            ),
                            yaxis=dict(
                                title="Valor (R$)",
                                tickfont=dict(size=12),
                                gridcolor="#374151"
                            )
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Tabela detalhada
                        st.markdown("##### 📋 Detalhamento por Subcategoria")
                        
                        for subcat, valor in sorted(subcategorias_totais.items(), key=lambda x: x[1], reverse=True):
                            subcat_nome = subcat.split(' - ')[1] if ' - ' in subcat else subcat
                            percentual = (valor / sum(subcategorias_totais.values())) * 100
                            cor_sub = subcategorias_info[subcat]
                            
                            st.markdown(f"""
                            <div style="
                                background: #1f2937;
                                border-radius: 10px;
                                padding: 16px;
                                margin-bottom: 10px;
                                border-left: 4px solid {cor_sub};
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="display: flex; align-items: center; gap: 12px;">
                                        <div style="
                                            background: {cor_sub}20;
                                            width: 40px;
                                            height: 40px;
                                            border-radius: 8px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                        ">
                                            <span style="font-size: 20px;">{subcat[0]}</span>
                                        </div>
                                        <div>
                                            <div style="font-weight: bold; color: #f9fafb;">{subcat_nome}</div>
                                            <div style="font-size: 12px; color: #9ca3af;">{subcat}</div>
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 18px; font-weight: bold; color: #f87171;">
                                            R$ {valor:,.2f}
                                        </div>
                                        <div style="font-size: 12px; color: #9ca3af;">
                                            {percentual:.1f}% da categoria
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Gastos específicos da subcategoria selecionada
                        subcategoria_selecionada = st.selectbox(
                            "Ver gastos específicos de:",
                            [f"{subcat} (R$ {valor:,.2f})" for subcat, valor in subcategorias_totais.items()],
                            key=f"subcat_{categoria_selecionada}"
                        )
                        
                        if subcategoria_selecionada:
                            # Extrair nome da subcategoria
                            subcat_nome = subcategoria_selecionada.split(' (R$')[0]
                            
                            # Filtrar gastos por subcategoria
                            gastos_subcategoria = []
                            for idx, row in df_gastos.iterrows():
                                desc_lower = row['descricao'].lower()
                                palavras = palavras_chave_detalhadas.get(subcat_nome, [])
                                
                                if any(palavra in desc_lower for palavra in palavras) or \
                                (subcat_nome == "📝 Outros - Variados" and not any(
                                    any(p in desc_lower for p in palavras_chave_detalhadas[cat]) 
                                    for cat in palavras_chave_detalhadas.keys()
                                )):
                                    gastos_subcategoria.append((idx, row))
                            
                            if gastos_subcategoria:
                                st.markdown(f"### 💸 Gastos em {subcat_nome}")
                                for i, (idx, row) in enumerate(gastos_subcategoria):
                                    mostrar_gasto_card(idx, row, df_gastos, unique_counter=f"subcat_{subcat_nome}_{i}")
                            else:
                                st.info(f"Nenhum gasto encontrado em {subcat_nome}")
                    else:
                        st.info(f"Nenhum gasto registrado em {categoria_selecionada}")
                
                # Seção 3: Insights e Recomendações
                st.markdown("#### 💡 Insights e Recomendações")
                
                # Encontrar categoria com maior gasto
                if categorias_detalhadas:
                    maior_categoria = max(categorias_detalhadas.items(), key=lambda x: x[1])
                    categoria_maior = maior_categoria[0]
                    valor_maior = maior_categoria[1]
                    percentual_maior = (valor_maior / gasto_total * 100) if gasto_total > 0 else 0
                    
                    # Encontrar categoria principal do maior gasto
                    categoria_principal_maior = ""
                    for cat_principal, info in CATEGORIAS_HIERARQUICAS.items():
                        if categoria_maior in info["subcategorias"]:
                            categoria_principal_maior = cat_principal
                            break
                    
                    col_insight1, col_insight2 = st.columns(2)
                    
                    with col_insight1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                            border-radius: 12px;
                            padding: 20px;
                            color: white;
                            height: 100%;
                        ">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 12px;">📌 Maior Gasto</div>
                            <div style="font-size: 20px; font-weight: bold; color: #f87171; margin-bottom: 8px;">
                                {categoria_maior.split(' - ')[1] if ' - ' in categoria_maior else categoria_maior}
                            </div>
                            <div style="font-size: 24px; font-weight: bold;">R$ {valor_maior:,.2f}</div>
                            <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                                {percentual_maior:.1f}% do total • {categoria_principal_maior}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_insight2:
                        # Recomendação baseada no maior gasto
                        recomendacao = ""
                        if percentual_maior > 30:
                            recomendacao = "Considere reduzir gastos nesta categoria"
                        elif percentual_maior > 20:
                            recomendacao = "Monitorar gastos nesta área"
                        else:
                            recomendacao = "Gastos equilibrados nesta categoria"
                        
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                            border-radius: 12px;
                            padding: 20px;
                            color: white;
                            height: 100%;
                        ">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 12px;">💡 Recomendação</div>
                            <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">
                                {recomendacao}
                            </div>
                            <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                                Baseado na distribuição atual dos gastos
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Distribuição saudável sugerida
                    st.markdown("##### 📊 Distribuição Saudável Sugerida")
                    
                    distribuicao_saudavel = {
                        "🍔 Alimentação": "25-35%",
                        "🏠 Casa": "25-35%",
                        "🚗 Transporte": "10-15%",
                        "🧑‍⚕️ Saúde": "5-10%",
                        "🎯 Lazer": "5-10%",
                        "💰 Outros": "10-15%"
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    cols = [col1, col2, col3]
                    
                    for idx, (cat, percentual) in enumerate(distribuicao_saudavel.items()):
                        with cols[idx % 3]:
                            st.markdown(f"""
                            <div style="
                                background: #1f2937;
                                border-radius: 10px;
                                padding: 16px;
                                text-align: center;
                                border: 1px solid #374151;
                            ">
                                <div style="font-size: 24px; margin-bottom: 8px;">{cat.split(' ')[0]}</div>
                                <div style="font-size: 14px; color: #9ca3af; margin-bottom: 4px;">{cat}</div>
                                <div style="font-size: 16px; font-weight: bold; color: #10b981;">{percentual}</div>
                                <div style="font-size: 11px; color: #6b7280;">do orçamento</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("Nenhum gasto registrado para análise de categorias.")
    else:
        # Card para estado vazio
        with st.container():
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                border-radius: 12px;
                padding: 60px 20px;
                text-align: center;
                border: 2px dashed #374151;
                margin: 20px 0;
            ">
                <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">📭</div>
                <h3 style="color: #9ca3af; margin-bottom: 12px;">Nenhum gasto registrado</h3>
                <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                    Use o formulário acima para registrar seus primeiros gastos e começar seu controle financeiro!
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Card de dicas
        with st.expander("💡 Dicas para um bom controle de gastos", expanded=True):
            col_tip1, col_tip2, col_tip3 = st.columns(3)
            
            with col_tip1:
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    height: 100%;
                    border: 1px solid #374151;
                ">
                    <div style="font-size: 24px; margin-bottom: 12px;">⏰</div>
                    <div style="font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Registre imediatamente</div>
                    <div style="font-size: 14px; color: #9ca3af;">
                        Anote cada gasto logo após ocorrer para não esquecer
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_tip2:
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    height: 100%;
                    border: 1px solid #374151;
                ">
                    <div style="font-size: 24px; margin-bottom: 12px;">🏷️</div>
                    <div style="font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Categorize seus gastos</div>
                    <div style="font-size: 14px; color: #9ca3af;">
                        Use descrições claras para identificar padrões de consumo
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_tip3:
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    height: 100%;
                    border: 1px solid #374151;
                ">
                    <div style="font-size: 24px; margin-bottom: 12px;">📈</div>
                    <div style="font-weight: bold; color: #f9fafb; margin-bottom: 8px;">Revise semanalmente</div>
                    <div style="font-size: 14px; color: #9ca3af;">
                        Analise seus gastos regularmente para ajustar hábitos
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---------- CARDS PARA ESTATÍSTICAS AVANÇADAS ----------
    if not df_gastos.empty and len(df_gastos) > 5:
        st.divider()
        st.markdown("### 📈 Análise de Gastos")
        
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            # Card de média diária
            dias_com_gastos = df_gastos["data"].dt.date.nunique()
            media_diaria = gasto_total / dias_com_gastos if dias_com_gastos > 0 else 0
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📅 Média Diária</div>
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 4px;">R$ {media:,.2f}</div>
                    <div style="font-size: 12px; opacity: 0.8;">
                        Baseado em {dias} dias com gastos
                    </div>
                </div>
            </div>
            """.format(media=media_diaria, dias=dias_com_gastos), unsafe_allow_html=True)
        
        with col_stat2:
            # Card de projeção mensal
            dias_no_mes = 30
            projecao_mensal = media_diaria * dias_no_mes
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #7c2d12 0%, #f97316 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📊 Projeção Mensal</div>
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 4px;">R$ {proj:,.0f}</div>
                    <div style="font-size: 12px; opacity: 0.8;">
                        {status} da reserva
                    </div>
                </div>
            </div>
            """.format(
                proj=projecao_mensal,
                status="Dentro" if projecao_mensal <= reserva_mensal else "Acima"
            ), unsafe_allow_html=True)

    # ---------- BOTÃO PARA EXPORTAR ----------
    if not df_gastos.empty:
        st.divider()
        
        with st.container():
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #374151;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 16px; color: #d1d5db; margin-bottom: 16px;">
                        📤 Exportar Dados
                    </div>
                    <div style="display: flex; gap: 12px; justify-content: center;">
            """, unsafe_allow_html=True)
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                if st.button("📋 Copiar Resumo", use_container_width=True):
                    resumo = f"""💸 RESUMO DE GASTOS - {date.today().strftime('%d/%m/%Y')}

💰 Reserva Mensal: R$ {reserva_mensal:,.2f}
🧾 Total Gasto: R$ {gasto_total:,.2f}
🟢 Saldo Disponível: R$ {saldo_restante:,.2f}
📊 Percentual Utilizado: {percentual_gasto:.1f}%
📈 Total de Gastos: {total_gastos}
📅 Média por Gasto: R$ {media_gasto:,.2f}
📅 Gastos Hoje: {qtd_gastos_hoje} (R$ {gastos_hoje:,.2f})
"""
                    st.code(resumo)
            
            with col_exp2:
                # Download CSV
                csv = df_gastos.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar CSV Completo",
                    data=csv,
                    file_name=f"gastos_{date.today().strftime('%Y_%m')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("""
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# 📊 Dashboard - VERSÃO ESTILIZADA CORRIGIDA
# =========================================================

elif menu == "📊 Dashboard":

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #334155;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: #3b82f6;
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">📊</span>
            Dashboard Financeiro
        </h1>
        <p style="color: #94a3b8; margin: 0;">
            Visão completa da sua saúde financeira em tempo real
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#3b82f6"
        }.get(msg_tipo, "#3b82f6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ================= CARDS DE MÉTRICAS PRINCIPAIS =================
    st.markdown("### 📈 Métricas Principais")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            # Card 1: Patrimônio
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">💰</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Patrimônio Total</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {patrimonio:,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Seu patrimônio atual consolidado</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Card 2: Saldo Variável
            cor_saldo_var = "#f87171" if saldo_variavel < 0 else "#34d399"
            icone_saldo_var = "🔴" if saldo_variavel < 0 else "🟢"
            texto_var = "Deficit" if saldo_variavel < 0 else "Superavit"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: {cor_saldo_var};
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">{icone_saldo_var}</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Saldo Variável (Mês)</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {abs(saldo_variavel):,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>{texto_var} mensal do orçamento</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Card 3: Saldo Fixo
            cor_saldo_fixo = "#f87171" if saldo_fixo < 0 else "#60a5fa"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">🏢</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Saldo Fixo Mensal</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {saldo_fixo:,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Para investimentos e metas</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Card 4: Progresso Sonhos
            cor_progresso = "#fbbf24" if progresso_sonhos < 50 else "#34d399" if progresso_sonhos < 90 else "#10b981"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: {cor_progresso};
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">🎯</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Progresso Sonhos</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        {progresso_sonhos:.1f}%
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Conclusão das suas metas</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ================= COMPOSIÇÃO FINANCEIRA =================
    st.markdown("### 📊 Composição Financeira do Mês")
    
    with st.container():
        
        
        df_comp = pd.DataFrame({
            "tipo": ["Receitas Fixas", "Despesas Fixas", "Saldo Variável"],
            "valor": [receitas_fixas, despesas_fixas, saldo_variavel],
            "cor": ["#10b981", "#ef4444", "#3b82f6"]
        })

        fig_comp = px.bar(
            df_comp,
            x="tipo",
            y="valor",
            color="tipo",
            color_discrete_sequence=df_comp["cor"].tolist(),
            text="valor"
        )

        fig_comp.update_traces(
            texttemplate="R$ %{text:,.0f}",
            textposition="outside",
            textfont=dict(size=14, color="#e5e7eb"),
            marker=dict(
                line=dict(width=2, color="#1f2937")
            )
        )

        fig_comp.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="#e5e7eb"),
            showlegend=False,
            xaxis=dict(
                title="",
                tickfont=dict(size=14),
                gridcolor="#374151"
            ),
            yaxis=dict(
                title="Valor (R$)",
                tickfont=dict(size=12),
                gridcolor="#374151",
                tickprefix="R$ "
            ),
            height=400,
            margin=dict(t=40, b=80, l=80, r=40)
        )

        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ================= PROJEÇÃO DE PATRIMÔNIO =================
    st.markdown("### 🚀 Projeção de Patrimônio")
    
    with st.container():
        if not df_projecao.empty:
            
            
            fig = px.line(
                df_projecao,
                x="data",
                y="patrimonio",
                markers=True,
                line_shape="spline"
            )

            fig.update_traces(
                line=dict(width=4, color="#3b82f6"),
                marker=dict(size=8, color="#60a5fa"),
                hovertemplate="<b>%{x|%b/%Y}</b><br>R$ %{y:,.0f}<extra></extra>"
            )

            # Linha da meta - usando add_hline com annotation separada
            fig.add_hline(
                y=meta_patrimonio,
                line_dash="dash",
                line_color="#10b981",
                line_width=2,
                annotation_text=f"Meta: R$ {meta_patrimonio:,.0f}",
                annotation_position="top left",
                annotation_font=dict(color="#10b981", size=12)
            )

            meta_df = df_projecao[df_projecao["meta_atingida"]]

            if not meta_df.empty:
                data_meta = pd.to_datetime(meta_df.iloc[0]["data"])
                
                # Converter para string para evitar problemas com datetime
                data_meta_str = data_meta.strftime('%Y-%m-%d')
                
                # Adicionar linha vertical
                fig.add_vline(
                    x=data_meta,
                    line_dash="dot",
                    line_color="#10b981",
                    line_width=2
                )
                
                # Adicionar anotação separadamente usando add_annotation
                fig.add_annotation(
                    x=data_meta,
                    y=1,
                    xref="x",
                    yref="paper",
                    text=f"Meta atingida em {data_meta.strftime('%m/%Y')}",
                    showarrow=False,
                    yanchor="bottom",
                    font=dict(color="#10b981", size=10),
                    bgcolor="rgba(16, 185, 129, 0.1)",
                    bordercolor="#10b981",
                    borderwidth=1,
                    borderpad=4,
                    xanchor="left"
                )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e5e7eb"),
                hovermode="x unified",
                title=dict(
                    text="Evolução do Patrimônio",
                    font=dict(size=20, color="white"),
                    x=0.05
                ),
                xaxis=dict(
                    title="",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="Patrimônio (R$)",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12),
                    tickprefix="R$ "
                ),
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Cards de estatísticas da projeção
            ultimo = df_projecao.iloc[-1]
            meses_proj = len(df_projecao)
            
            col_stat1, col_stat2, col_stat3 = st.columns(3, gap="medium")
            
            with col_stat1:
                tempo_formatado = formatar_tempo_meses(meses_proj)
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📅 Horizonte da Projeção</div>
                    <div style="font-size: 24px; font-weight: bold;">{tempo_formatado}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Período projetado</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">📈 Patrimônio Projetado</div>
                    <div style="font-size: 24px; font-weight: bold;">R$ {ultimo['patrimonio']:,.0f}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Valor final estimado</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                if ultimo["meta_atingida"]:
                    data_meta = meta_df.iloc[0]["data"].strftime("%m/%Y")
                    status_html = f"""
                    <div style="
                        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                        border-radius: 12px;
                        padding: 20px;
                        color: white;
                        text-align: center;
                    ">
                        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🎯 Meta Atingida</div>
                        <div style="font-size: 24px; font-weight: bold;">{data_meta}</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                            <i>Parabéns! 🎉</i>
                        </div>
                    </div>
                    """
                else:
                    status_html = f"""
                    <div style="
                        background: linear-gradient(135deg, #78350f 0%, #f59e0b 100%);
                        border-radius: 12px;
                        padding: 20px;
                        color: white;
                        text-align: center;
                    ">
                        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🎯 Meta</div>
                        <div style="font-size: 24px; font-weight: bold;">Em progresso</div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                            <i>Ainda não atingida</i>
                        </div>
                    </div>
                    """
                st.markdown(status_html, unsafe_allow_html=True)

        else:
            # Card para dados insuficientes
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 60px 20px;
                text-align: center;
                border: 2px dashed #374151;
                margin: 20px 0;
            ">
                <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">📊</div>
                <h3 style="color: #9ca3af; margin-bottom: 12px;">Dados insuficientes para projeção</h3>
                <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                    Continue registrando seus lançamentos para ver projeções detalhadas.
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ================= SUGESTÃO DE APORTE =================
    st.markdown("### 🎯 Sugestão para Acelerar a Meta")
    
    with st.container():
        
        
        col_s1, col_s2, col_s3 = st.columns(3, gap="medium")
        
        with col_s1:
            st.markdown("""
            <div style="
                background: #111827;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #374151;
            ">
                <div style="font-size: 14px; color: #d1d5db; margin-bottom: 12px;">
                    ⏳ Prazo Desejado
                </div>
            """, unsafe_allow_html=True)
            
            tempo_desejado = st.number_input(
                "Em quantos anos quer atingir a meta?",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                label_visibility="collapsed"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        if meta_patrimonio > patrimonio and tempo_desejado > 0:
            aporte_sugerido, é_viável = calcular_aporte_ideal_para_meta(
                patrimonio_atual=patrimonio,
                meta_patrimonio=meta_patrimonio,
                rendimento_mensal=rendimento_mensal,
                inflacao_mensal=inflacao_mensal,
                tempo_desejado_anos=tempo_desejado
            )
            
            with col_s2:
                cor_aporte = "#10b981" if é_viável else "#f59e0b"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                    border: 2px solid {cor_aporte};
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💰 Aporte Mensal Sugerido</div>
                    <div style="font-size: 28px; font-weight: bold;">R$ {aporte_sugerido:,.0f}</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Para atingir em {tempo_desejado} anos</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_s3:
                if é_viável:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                        border-radius: 12px;
                        padding: 20px;
                        color: white;
                        text-align: center;
                    ">
                        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">✅ Status</div>
                        <div style="font-size: 20px; font-weight: bold; margin-bottom: 4px;">Meta viável</div>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Com este aporte
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #78350f 0%, #f59e0b 100%);
                        border-radius: 12px;
                        padding: 20px;
                        color: white;
                        text-align: center;
                    ">
                        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">⚠️ Status</div>
                        <div style="font-size: 20px; font-weight: bold; margin-bottom: 4px;">Aporte muito alto</div>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Ajuste o prazo
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Comparação com saldo atual
            st.markdown("<br>", unsafe_allow_html=True)
            
            diferenca = aporte_sugerido - saldo_fixo
            if diferenca > 0:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    margin-top: 16px;
                ">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="font-size: 32px;">📊</div>
                        <div>
                            <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px;">
                                Para atingir em <strong>{tempo_desejado} anos</strong>
                            </div>
                            <div style="font-size: 14px; opacity: 0.9;">
                                Você precisa guardar <strong>R$ {diferenca:,.0f} a mais por mês</strong>
                                (atualmente guarda R$ {saldo_fixo:,.0f})
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    margin-top: 16px;
                ">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="font-size: 32px;">🎉</div>
                        <div>
                            <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px;">
                                Excelente notícia!
                            </div>
                            <div style="font-size: 14px; opacity: 0.9;">
                                Você já guarda o suficiente! Pode atingir a meta em menos de <strong>{tempo_desejado} anos</strong>.
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # ================= RESUMO RÁPIDO =================
    st.markdown("### 📋 Resumo Rápido")
    
    col_r1, col_r2, col_r3 = st.columns(3, gap="medium")
    
    with col_r1:
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #374151;
        ">
            <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">💼 Receitas Fixas</div>
            <div style="font-size: 20px; font-weight: bold; color: #10b981;">R$ {receitas_fixas:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r2:
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #374151;
        ">
            <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">📉 Despesas Fixas</div>
            <div style="font-size: 20px; font-weight: bold; color: #ef4444;">R$ {despesas_fixas:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r3:
        margem_seguranca = ((receitas_fixas - despesas_fixas) / receitas_fixas * 100) if receitas_fixas > 0 else 0
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #374151;
        ">
            <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">📊 Margem de Segurança</div>
            <div style="font-size: 20px; font-weight: bold; color: #3b82f6;">{margem_seguranca:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
# =========================================================
# 🏷️ Categorias
# =========================================================

elif menu == "🏷️ Categorias":

    st.markdown("🏷️ Gestão de Categorias")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None
    st.caption("Centralize e organize todas as categorias do sistema")

    # Garantir DataFrame
    if "categorias" not in dados or dados["categorias"].empty:
        df_cat = pd.DataFrame(columns=["nome", "tipo", "ativa"])
    else:
        df_cat = dados["categorias"].copy()

        # 🔒 NORMALIZAÇÃO OBRIGATÓRIA
        df_cat.columns = df_cat.columns.str.lower()

        # 🔒 blindagem obrigatória
        for col in ["nome", "tipo", "ativa"]:
            if col not in df_cat.columns:
                df_cat[col] = True if col == "ativa" else ""



    # ---------------- CRIAR CATEGORIA ----------------
    st.subheader("➕ Nova Categoria")

    with st.form("form_categoria", clear_on_submit=True):
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            nome = st.text_input("Nome da Categoria")

        with col2:
            tipo = st.selectbox(
                "tipo",
                ["Despesa Variável", "Despesa Fixa", "Receita"]
            )

        with col3:
            ativa = st.checkbox("ativa", value=True)

        submitted = st.form_submit_button("💾 Criar Categoria")

        if submitted:
            if nome.strip() == "":
                st.error("Informe o nome da categoria.")
                st.stop()
            
            # Verificar se categoria já existe (case-insensitive)
            if not df_cat.empty:
                nome_exists = df_cat["nome"].astype(str).str.lower().str.contains(nome.lower()).any()
                if nome_exists:
                    st.error("Categoria já existe.")
                    st.stop()
            
            # Criar nova categoria
            nova = pd.DataFrame([{
                "nome": nome.strip(),
                "tipo": tipo,
                "ativa": ativa
            }])

            # Concatenar e normalizar
            df_cat = pd.concat([df_cat, nova], ignore_index=True)
            
            # 🔥 Garantir normalização antes de salvar
            df_cat.columns = df_cat.columns.str.lower()
            dados["categorias"] = df_cat
            st.session_state["dados"] = dados
            
            # Salvar no banco
            DatabaseManager.save("categorias", df_cat, usuario)
            
            st.session_state["msg"] = "Categoria criada com sucesso."
            st.session_state["msg_tipo"] = "success"
            st.rerun()

    st.divider()

    # ---------------- ATIVAR / DESATIVAR ----------------
    st.subheader("🔁 Ativar / Desativar Categoria")

    if not df_cat.empty:
        # 🔥 SOLUÇÃO: Primeiro remover colunas duplicadas para acessar 'nome' como Series
        df_cat_unique = df_cat.loc[:, ~df_cat.columns.duplicated()]
        
        # Garantir que temos a coluna 'nome'
        if "nome" not in df_cat_unique.columns:
            st.error("Coluna 'nome' não encontrada.")
            st.stop()
        
        # Agora podemos acessar como Series
        categorias_lista = df_cat_unique["nome"].dropna().tolist()
        
        # Remover duplicados da lista (caso ainda existam)
        categorias_lista = list(dict.fromkeys(categorias_lista))  # Mantém ordem
        
        if categorias_lista:
            categoria_sel = st.selectbox(
                "Selecione a categoria",
                categorias_lista,
                key="select_categoria"
            )

            # 🔥 Encontrar status atual CORRETAMENTE
            # Primeiro garantir que estamos usando o df sem colunas duplicadas
            mask = df_cat_unique["nome"] == categoria_sel
            
            if mask.any():  # Se encontrou a categoria
                status_atual = df_cat_unique.loc[mask, "ativa"].iloc[0]
                
                # Converter para booleano se necessário
                if isinstance(status_atual, str):
                    status_atual = status_atual.lower() in ['true', '1', 'yes', 'sim', 'ativo']
                elif pd.isna(status_atual):
                    status_atual = True
            else:
                status_atual = True

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Ativar Categoria", use_container_width=True):
                    # Atualizar no df original (com duplicatas)
                    df_cat.loc[df_cat["nome"] == categoria_sel, "ativa"] = True
                    dados["categorias"] = df_cat
                    st.session_state["dados"] = dados
                    DatabaseManager.save("categorias", df_cat, usuario)
                    st.success(f"Categoria '{categoria_sel}' ativada.")
                    st.rerun()
            
            with col_btn2:
                if st.button("❌ Desativar Categoria", use_container_width=True):
                    # Atualizar no df original (com duplicatas)
                    df_cat.loc[df_cat["nome"] == categoria_sel, "ativa"] = False
                    dados["categorias"] = df_cat
                    st.session_state["dados"] = dados
                    DatabaseManager.save("categorias", df_cat, usuario)
                    st.warning(f"Categoria '{categoria_sel}' desativada.")
                    st.rerun()
            
            # Mostrar status atual
            status_text = "✅ Ativa" if status_atual else "❌ Inativa"
            st.caption(f"Status atual: {status_text}")
        else:
            st.caption("Nenhuma categoria disponível para alteração.")
    else:
        st.caption("Nenhuma categoria cadastrada.")

    # ---------------- LISTA ----------------
    st.subheader("📋 Categorias Cadastradas")

    if not df_cat.empty:
        # 🔥 SOLUÇÃO: Criar uma cópia com índice resetado e remover colunas duplicadas
        df_display = df_cat.copy()
        
        # 1. Remover colunas duplicadas
        df_display = df_display.loc[:, ~df_display.columns.duplicated()]
        
        # 2. Resetar índice para garantir unicidade
        df_display = df_display.reset_index(drop=True)
        
        # 3. Garantir que 'ativa' é booleana para a formatação
        if "ativa" in df_display.columns:
            df_display["ativa"] = df_display["ativa"].astype(bool)
        
        # 4. Aplicar estilo CORRETAMENTE
        def highlight_inactive(row):
            styles = [''] * len(row)
            if 'ativa' in df_display.columns and not row['ativa']:
                styles[df_display.columns.get_loc('ativa')] = 'color: gray;'
            return styles
        
        # Usar apply (não applymap) para estilo condicional por linha
        styled_df = df_display.style.apply(
            highlight_inactive, 
            axis=1,  # Aplicar por linha
            subset=None
        )
        
        # Adicionar formatação básica
        styled_df = styled_df.format(None)  # Formatação padrão
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=350
        )
    else:
        st.caption("Nenhuma categoria cadastrada.")

    st.divider()

# =========================================================
# ⚙️ Planejamento - VERSÃO PASSO A PASSO EXPLICATIVA
# =========================================================
elif menu == "⚙️ Planejamento":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #334155;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: #f59e0b;
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">⚙️</span>
            Configurações do Sistema
        </h1>
        <p style="color: #94a3b8; margin: 0;">
            Configure seu planejamento financeiro passo a passo
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Mensagens de feedback
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {"error": "❌", "warning": "⚠️", "success": "✅", "info": "ℹ️"}.get(msg_tipo, "ℹ️")
        msg_color = {"error": "#ef4444", "warning": "#f59e0b", "success": "#10b981", "info": "#3b82f6"}.get(msg_tipo, "#3b82f6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None

    # ================= PASSO A PASSO DE CONFIGURAÇÃO =================
    st.markdown("### 🚀 Configuração Guiada do Seu Planejamento")
    
    # Barra de progresso
    total_passos = 6
    passo_atual = 1
    
    # Contêiner principal
    with st.container():
        
        # =========== PASSO 1: NOME DA FAMÍLIA ===========
        with st.expander(f"📝 **PASSO {passo_atual}/6 - Nome da Família**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #3b82f6;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #3b82f6;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">1</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Comece com um nome para sua família
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    Este nome será usado em todos os relatórios e dashboard. Pode ser seu sobrenome, 
                    um apelido familiar ou qualquer nome que represente seu grupo familiar.
                </div>
            """, unsafe_allow_html=True)
            
            col_nome1, col_nome2 = st.columns([2, 1])
            with col_nome1:
                nome_familia = st.text_input(
                    "👨‍👩‍👧‍👦 **Nome da Família**",
                    value=nome_familia,
                    placeholder="Ex: Família Silva, Casa do João, Nossa Família...",
                    help="Escolha um nome que represente seu grupo familiar"
                )
            
            with col_nome2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Salvar Nome", key="salvar_nome", use_container_width=True):
                    if nome_familia.strip():
                        # Salvar nome no config
                        st.session_state["config_nome_salvo"] = nome_familia
                        st.success(f"Nome '{nome_familia}' salvo!")
                        passo_atual = 2
                    else:
                        st.error("Por favor, informe um nome válido")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # =========== PASSO 2: META DE PATRIMÔNIO ===========
        passo_atual = 2
        with st.expander(f"🎯 **PASSO {passo_atual}/6 - Meta de Patrimônio**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #8b5cf6;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #8b5cf6;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">2</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Defina sua meta financeira
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    **Por que definir uma meta?**<br>
                    Uma meta clara de patrimônio ajuda a manter o foco, medir progresso e tomar 
                    decisões financeiras mais conscientes. É o seu objetivo financeiro de longo prazo.
                </div>
            """, unsafe_allow_html=True)
            
            # Exemplos de metas
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                if st.button("💰 R$ 500 mil", use_container_width=True):
                    st.session_state["meta_sugerida"] = 500000
            with col_meta2:
                if st.button("🏡 R$ 1 milhão", use_container_width=True):
                    st.session_state["meta_sugerida"] = 1000000
            with col_meta3:
                if st.button("🚀 R$ 2 milhões", use_container_width=True):
                    st.session_state["meta_sugerida"] = 2000000
            
            meta_sugerida = st.session_state.get("meta_sugerida", meta_patrimonio)
            
            col_meta_input1, col_meta_input2 = st.columns([2, 1])
            with col_meta_input1:
                meta = st.number_input(
                    "**💰 Qual é sua meta de patrimônio? (R$)**",
                    min_value=0.0,
                    value=float(meta_sugerida),
                    step=10000.0,
                    format="%.2f",
                    help="Quanto dinheiro você quer ter acumulado no futuro para se sentir seguro ou rico? Ex: R$ 100.000 para começar."
                )
            
            with col_meta_input2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🎯 Definir Meta", key="salvar_meta", use_container_width=True):
                    if meta > 0:
                        st.session_state["config_meta_salva"] = meta
                        st.success(f"Meta de R$ {meta:,.2f} definida!")
                        passo_atual = 3
                    else:
                        st.error("A meta deve ser maior que zero")
            
            # Card explicativo
            st.markdown("""
            <div style="
                background: rgba(139, 92, 246, 0.1);
                border: 1px solid #8b5cf6;
                border-radius: 10px;
                padding: 16px;
                margin-top: 16px;
            ">
                <div style="font-size: 14px; color: #a78bfa; font-weight: bold; margin-bottom: 8px;">
                    💡 Dica sobre metas
                </div>
                <div style="font-size: 13px; color: #d1d5db;">
                    Considere fatores como: idade atual, tempo até a aposentadoria, 
                    estilo de vida desejado e objetivos pessoais (casa própria, educação dos filhos, viagens).
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # =========== PASSO 3: ORÇAMENTO MENSAL ===========
        passo_atual = 3
        with st.expander(f"📊 **PASSO {passo_atual}/6 - Orçamento Mensal**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #10b981;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #10b981;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">3</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Estabeleça seu orçamento mensal
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    **O que é orçamento mensal?**<br>
                    É o valor total que sua família recebe (ou planeja receber) por mês. 
                    Esta informação é fundamental para calcular quanto pode ser poupado e investido.
                </div>
            """, unsafe_allow_html=True)
            
            col_orc1, col_orc2 = st.columns([2, 1])
            with col_orc1:
                orcamento = st.number_input(
                    "**📊 Qual é a renda TOTAL da família? (R$)**",
                    min_value=0.0,
                    value=orcamento_mensal,
                    step=500.0,
                    format="%.2f",
                    help="Some todos os salários líquidos, vales, rendas extras e pensões que caem na conta todo mês."
                )
            
            with col_orc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💼 Definir Orçamento", key="salvar_orcamento", use_container_width=True):
                    if orcamento > 0:
                        st.session_state["config_orcamento_salvo"] = orcamento
                        st.success(f"Orçamento de R$ {orcamento:,.2f} definido!")
                        passo_atual = 4
                    else:
                        st.error("O orçamento deve ser maior que zero")
            
            # Calculadora de porcentagem da meta
            if meta > 0 and orcamento > 0:
                meses_para_meta = meta / orcamento if orcamento > 0 else 0
                anos_para_meta = meses_para_meta / 12
                
                st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid #10b981;
                    border-radius: 10px;
                    padding: 16px;
                    margin-top: 16px;
                ">
                    <div style="font-size: 14px; color: #34d399; font-weight: bold; margin-bottom: 8px;">
                    📈 Projeção com base no orçamento
                    </div>
                    <div style="font-size: 13px; color: #d1d5db;">
                    Com este orçamento mensal, você atingiria sua meta em aproximadamente:<br>
                    <strong>{meses_para_meta:,.0f} meses</strong> ({anos_para_meta:,.1f} anos)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # =========== PASSO 4: RENDIMENTO ESPERADO ===========
        passo_atual = 4
        with st.expander(f"📈 **PASSO {passo_atual}/6 - Rendimento dos Investimentos**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #f59e0b;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #f59e0b;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">4</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Estime o rendimento dos seus investimentos
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    **Por que isso é importante?**<br>
                    O rendimento real (acima da inflação) determina quanto seu dinheiro cresce ao longo do tempo. 
                    Este valor é usado nas projeções de patrimônio.
                </div>
            """, unsafe_allow_html=True)
            
            # Opções pré-definidas
            st.markdown("**💡 Escolha um perfil de investidor:**")
            
            col_perfil1, col_perfil2, col_perfil3 = st.columns(3)
            with col_perfil1:
                if st.button("🛡️ Conservador", use_container_width=True):
                    st.session_state["rendimento_sugerido"] = 0.5
                    st.session_state["perfil_selecionado"] = "Conservador"
            with col_perfil2:
                if st.button("⚖️ Moderado", use_container_width=True):
                    st.session_state["rendimento_sugerido"] = 0.8
                    st.session_state["perfil_selecionado"] = "Moderado"
            with col_perfil3:
                if st.button("🚀 Arrojado", use_container_width=True):
                    st.session_state["rendimento_sugerido"] = 1.2
                    st.session_state["perfil_selecionado"] = "Arrojado"
            
            rendimento_sugerido = st.session_state.get("rendimento_sugerido", rendimento_mensal * 100)
            
            col_rend1, col_rend2 = st.columns([2, 1])
            with col_rend1:
                rendimento = st.number_input(
                    "**📈 Qual rendimento mensal REAL você espera? (%)**",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(rendimento_sugerido),
                    step=0.1,
                    help="Rendimento mensal acima da inflação (líquido de impostos e taxas)"
                ) / 100
            
            with col_rend2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💰 Definir Rendimento", key="salvar_rendimento", use_container_width=True):
                    if rendimento > 0:
                        st.session_state["config_rendimento_salvo"] = rendimento
                        st.success(f"Rendimento de {rendimento*100:.1f}% ao mês definido!")
                        passo_atual = 5
                    else:
                        st.error("O rendimento deve ser maior que zero")
            
            # Explicação sobre rendimento real vs nominal
            st.markdown("""
            <div style="
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid #f59e0b;
                border-radius: 10px;
                padding: 16px;
                margin-top: 16px;
            ">
                <div style="font-size: 14px; color: #fbbf24; font-weight: bold; margin-bottom: 8px;">
                    📚 Entenda o rendimento REAL
                </div>
                <div style="font-size: 13px; color: #d1d5db;">
                    <strong>Rendimento REAL = Rendimento Nominal - Inflação</strong><br>
                    Exemplo: Se seus investimentos rendem 1% ao mês e a inflação é 0.3%, 
                    seu rendimento real é de 0.7% ao mês.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # =========== PASSO 5: RESERVA PARA GASTOS ===========
        passo_atual = 5
        with st.expander(f"💸 **PASSO {passo_atual}/6 - Reserva para Gastos**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #ec4899;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #ec4899;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">5</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Defina sua reserva para gastos do dia a dia
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    **O que é esta reserva?**<br>
                    É o valor mensal que você separa para gastos variáveis (alimentação, transporte, 
                    lazer, etc.). O sistema ajudará a controlar para não ultrapassar este limite.
                </div>
            """, unsafe_allow_html=True)
            
            # Sugestão baseada no orçamento
            if orcamento > 0:
                sugestao_reserva = orcamento * 0.3  # 30% do orçamento
                st.info(f"💡 **Sugestão:** Reserve cerca de 30% do seu orçamento para gastos variáveis: **R$ {sugestao_reserva:,.2f}**")
            
            col_res1, col_res2 = st.columns([2, 1])
            with col_res1:
                reserva = st.number_input(
                    "**💸 Limite para 'Gastar Vivendo' (R$)**",
                    min_value=0.0,
                    value=float(config_dict.get("reserva_gastos", sugestao_reserva if orcamento > 0 else 1000)),
                    step=50.0,
                    format="%.2f",
                    help="Tirando as contas fixas (aluguel, luz), quanto sobra para você gastar com mercado, Uber, iFood e lazer? Esse será seu limite mensal."
                )
            
            with col_res2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💳 Definir Reserva", key="salvar_reserva", use_container_width=True):
                    if reserva > 0:
                        st.session_state["config_reserva_salva"] = reserva
                        st.success(f"Reserva de R$ {reserva:,.2f} definida!")
                        passo_atual = 6
                    else:
                        st.error("A reserva deve ser maior que zero")
            
            # Explicação sobre categorias de gastos
            st.markdown("""
            <div style="
                background: rgba(236, 72, 153, 0.1);
                border: 1px solid #ec4899;
                border-radius: 10px;
                padding: 16px;
                margin-top: 16px;
            ">
                <div style="font-size: 14px; color: #f472b6; font-weight: bold; margin-bottom: 8px;">
                    🏷️ Como usar esta reserva
                </div>
                <div style="font-size: 13px; color: #d1d5db;">
                    Na aba <strong>"🛒 Limite do Cartão/Mês"</strong> você poderá registrar cada gasto e 
                    o sistema mostrará quanto ainda pode gastar no mês, organizando por categorias como:
                    Alimentação, Transporte, Lazer, Saúde, etc.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # =========== PASSO 6: REVISÃO E CONFIRMAÇÃO ===========
        passo_atual = 6
        with st.expander(f"✅ **PASSO {passo_atual}/6 - Revisão e Confirmação**", expanded=True):
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border-left: 4px solid #10b981;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="
                        background: #10b981;
                        border-radius: 8px;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <span style="color: white; font-weight: bold;">6</span>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">
                        Revise e confirme suas configurações
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                    **Última etapa!**<br>
                    Confira todas as informações abaixo e salve para começar a usar o sistema.
                </div>
            """, unsafe_allow_html=True)
            
            # Resumo das configurações
            st.markdown("### 📋 Resumo do Seu Planejamento")
            
            col_resumo1, col_resumo2 = st.columns(2)
            
            with col_resumo1:
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border: 1px solid #374151;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">👨‍👩‍👧‍👦</span>
                        <div style="font-size: 14px; color: #d1d5db;">Nome da Família</div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f9fafb;">{nome_familia}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border: 1px solid #374151;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🎯</span>
                        <div style="font-size: 14px; color: #d1d5db;">Meta de Patrimônio</div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #8b5cf6;">R$ {meta:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border: 1px solid #374151;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">📈</span>
                        <div style="font-size: 14px; color: #d1d5db;">Rendimento Esperado</div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #f59e0b;">{rendimento*100:.1f}% ao mês</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_resumo2:
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border: 1px solid #374151;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">💼</span>
                        <div style="font-size: 14px; color: #d1d5db;">Orçamento Mensal</div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #10b981;">R$ {orcamento:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 10px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border: 1px solid #374151;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">💸</span>
                        <div style="font-size: 14px; color: #d1d5db;">Reserva para Gastos</div>
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #ec4899;">R$ {reserva:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Projeção rápida
                if meta > 0 and orcamento > 0 and rendimento > 0:
                    # Cálculo simplificado
                    poupanca_mensal = orcamento * 0.3  # Supondo 30% de poupança
                    patrimonio_projetado = 0
                    meses = 0
                    
                    while patrimonio_projetado < meta and meses < 600:  # 50 anos máximo
                        patrimonio_projetado = (patrimonio_projetado + poupanca_mensal) * (1 + rendimento)
                        meses += 1
                    
                    anos = meses / 12
                    
                    st.markdown(f"""
                    <div style="
                        background: #1f2937;
                        border-radius: 10px;
                        padding: 16px;
                        border: 1px solid #374151;
                    ">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <span style="font-size: 20px;">⏱️</span>
                            <div style="font-size: 14px; color: #d1d5db;">Projeção da Meta</div>
                        </div>
                        <div style="font-size: 16px; font-weight: bold; color: #3b82f6;">
                            {meses} meses ({anos:.1f} anos)
                        </div>
                        <div style="font-size: 12px; color: #9ca3af;">
                            Tempo estimado para atingir sua meta
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Botão final para salvar tudo
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_save1, col_save2, col_save3 = st.columns([1, 2, 1])
            with col_save2:
                if st.button("🚀 **SALVAR TODAS AS CONFIGURAÇÕES**", 
                           type="primary", 
                           use_container_width=True,
                           key="salvar_tudo"):
                    
                    # Inflação padrão (pode ser ajustada depois)
                    inflacao = 0.003  # 0.3% ao mês (padrão)
                    
                    df_config = pd.DataFrame([
                        {"chave": "meta_patrimonio", "valor": meta, "descricao": "Meta total de patrimônio"},
                        {"chave": "orcamento_mensal", "valor": orcamento, "descricao": "Orçamento mensal"},
                        {"chave": "nome_familia", "valor": nome_familia, "descricao": "Nome da família"},
                        {"chave": "rendimento_mensal", "valor": rendimento, "descricao": "Rendimento mensal real"},
                        {"chave": "inflacao_mensal", "valor": inflacao, "descricao": "Inflação mensal esperada"},
                        {"chave": "reserva_gastos", "valor": reserva, "descricao": "Reserva mensal de gastos rápidos"}
                    ])

                    # Normalizar colunas
                    df_config.columns = df_config.columns.str.lower()

                    dados["config"] = df_config
                    st.session_state["dados"] = dados

                    DatabaseManager.save("config", df_config, st.session_state["usuario"])

                    st.session_state["msg"] = "✅ Configurações salvas com sucesso! Seu planejamento está pronto."
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # ================= CONFIGURAÇÕES AVANÇADAS =================
    with st.expander("⚙️ **Configurações Avançadas**", expanded=False):
        st.markdown("""
        <div style="
            background: #1f2937;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #374151;
        ">
            <div style="color: #d1d5db; font-size: 14px; margin-bottom: 16px;">
                Ajustes técnicos e configurações específicas do sistema.
            </div>
        """, unsafe_allow_html=True)
        
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            inflacao = st.number_input(
                "💸 Inflação Mensal Esperada (%)",
                min_value=0.0,
                max_value=100.0,
                value=inflacao_mensal * 100,
                step=0.1
            ) / 100
        
        with col_adv2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Configurações Avançadas", use_container_width=True):
                # Atualizar apenas a inflação no config existente
                if not dados["config"].empty:
                    df_config = dados["config"].copy()
                    df_config.loc[df_config["chave"] == "inflacao_mensal", "valor"] = inflacao
                    
                    dados["config"] = df_config
                    st.session_state["dados"] = dados
                    DatabaseManager.save("config", df_config, st.session_state["usuario"])
                    
                    st.success("Configurações avançadas salvas!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📄 USUÁRIOS
# =========================================================

elif menu == "👥 USUÁRIOS":
    if st.session_state.get("perfil") != "admin":
        st.error("Acesso restrito.")
        st.stop()

    tela_admin_usuarios()


# =========================================================
# 📄 Relatório Executivo - VERSÃO ESTILIZADA
# =========================================================

elif menu == "📄 Relatório Executivo":
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #334155;
    ">
        <h1 style="
            color: white;
            margin: 0 0 8px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="
                background: #8b5cf6;
                border-radius: 10px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">📄</span>
            Relatório Executivo Financeiro
        </h1>
        <p style="color: #94a3b8; margin: 0;">
            Visão consolidada para tomada de decisão estratégica
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensagens de feedback estilizadas
    if st.session_state.get("msg"):
        msg_tipo = st.session_state.get("msg_tipo", "info")
        msg_icon = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }.get(msg_tipo, "ℹ️")
        
        msg_color = {
            "error": "#ef4444",
            "warning": "#f59e0b",
            "success": "#10b981",
            "info": "#3b82f6"
        }.get(msg_tipo, "#3b82f6")
        
        st.markdown(f"""
        <div style="
            background: {msg_color}15;
            border: 1px solid {msg_color}30;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            color: #e5e7eb;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">{msg_icon}</span>
                <div>{st.session_state["msg"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["msg"] = None
    
    st.divider()

    # ================= RESUMO EXECUTIVO =================
    st.markdown("### 📌 Resumo Executivo")
    
    variacao_mensal = saldo_variavel + saldo_fixo
    
    if meta_patrimonio > 0:
        perc_meta = patrimonio / meta_patrimonio * 100
    else:
        perc_meta = 0
    
    status_meta = (
        "🟢 Atingida" if perc_meta >= 100 else
        "🟡 Em progresso" if perc_meta >= 60 else
        "🔴 Crítica"
    )
    
    # Cards de métricas principais
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            # Card 1: Patrimônio
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">💰</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Patrimônio Atual</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {patrimonio:,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Valor total acumulado</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Card 2: Resultado do Mês
            delta_color = "normal" if variacao_mensal >= 0 else "inverse"
            cor_card = "#10b981" if variacao_mensal >= 0 else "#ef4444"
            icone = "📈" if variacao_mensal >= 0 else "📉"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {cor_card}80 0%, {cor_card} 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px {cor_card}30;
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">{icone}</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Resultado do Mês</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {abs(variacao_mensal):,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>{"Lucro" if variacao_mensal >= 0 else "Prejuízo"} mensal</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Card 3: Saldo Fixo
            cor_saldo_fixo = "#60a5fa" if saldo_fixo >= 0 else "#f87171"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">🏢</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Saldo Fixo</div>
                    <div style="font-size: 28px; font-weight: bold; margin: 8px 0;">
                        R$ {saldo_fixo:,.0f}
                    </div>
                </div>
                <div style="font-size: 12px; opacity: 0.8;">
                    <i>Para investimentos</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Card 4: Status da Meta
            cor_meta = "#10b981" if perc_meta >= 100 else "#f59e0b" if perc_meta >= 60 else "#ef4444"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
                border-radius: 16px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
                height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="
                        background: {cor_meta};
                        border-radius: 10px;
                        width: 48px;
                        height: 48px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 12px;
                    ">
                        <span style="font-size: 24px;">🎯</span>
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">Status da Meta</div>
                    <div style="font-size: 20px; font-weight: bold; margin: 8px 0;">
                        {perc_meta:.1f}%
                    </div>
                    <div style="font-size: 12px;">
                        {status_meta}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

    # ================= DIAGNÓSTICO DO MÊS =================
    st.markdown("### 📊 Diagnóstico do Mês")
    
    with st.container():
        
        # Determinar diagnóstico
        if saldo_variavel < 0 and saldo_fixo < 0:
            diagnostico = "Mês financeiramente negativo. Atenção imediata ao controle de gastos."
            cor_diag = "#ef4444"
            icone_diag = "🔴"
        elif saldo_variavel < 0:
            diagnostico = "Gastos variáveis acima do esperado. Revisar despesas não recorrentes."
            cor_diag = "#f59e0b"
            icone_diag = "🟡"
        elif saldo_fixo < 0:
            diagnostico = "Estrutura fixa deficitária. Ajuste de receitas ou redução de custos."
            cor_diag = "#f97316"
            icone_diag = "🟠"
        else:
            diagnostico = "Fluxo financeiro saudável neste mês."
            cor_diag = "#10b981"
            icone_diag = "🟢"
        
        st.markdown(f"""
        <div style="
            background: {cor_diag}15;
            border: 1px solid {cor_diag}30;
            border-radius: 12px;
            padding: 20px;
            color: #e5e7eb;
            margin-top: 20px;
        ">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="font-size: 32px;">{icone_diag}</span>
                <div>
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px;">
                        {diagnostico}
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">
                        Última análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= PROJEÇÃO E CENÁRIO BASE =================
    st.markdown("### 🚀 Projeção e Cenário Base")
    
    with st.container():
        
        if not df_projecao.empty:
            ultimo = df_projecao.iloc[-1]
            meses_ate_meta = len(df_projecao)
            
            if ultimo["meta_atingida"]:
                texto_proj = f"✅ Meta será atingida em aproximadamente {meses_ate_meta} meses."
                cor_proj = "#10b981"
                icone_proj = "✅"
            else:
                texto_proj = f"⚠️ Meta não será atingida sem ajustes no plano."
                cor_proj = "#f59e0b"
                icone_proj = "⚠️"
            
            st.markdown(f"""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #374151;
                margin-bottom: 20px;
            ">
                <div style="display: flex; align-items: flex-start; gap: 16px;">
                    <span style="font-size: 24px; color: {cor_proj};">{icone_proj}</span>
                    <div>
                        <div style="font-size: 16px; color: #e5e7eb; font-weight: bold; margin-bottom: 8px;">
                            Mantido o cenário atual:
                        </div>
                        <div style="color: #d1d5db;">
                            Patrimônio projetado: <strong>R$ {ultimo['patrimonio']:,.2f}</strong><br>
                            Tempo estimado: <strong>{meses_ate_meta} meses</strong>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de projeção
            st.markdown("#### 📈 Evolução Projetada")
            
            fig_proj = px.line(
                df_projecao,
                x="data",
                y="patrimonio",
                markers=True,
                line_shape="spline"
            )
            
            fig_proj.update_traces(
                line=dict(width=4, color="#3b82f6"),
                marker=dict(size=8, color="#60a5fa"),
                hovertemplate="<b>%{x|%b/%Y}</b><br>R$ %{y:,.0f}<extra></extra>"
            )
            
            # Linha da meta
            fig_proj.add_hline(
                y=meta_patrimonio,
                line_dash="dash",
                line_color="#10b981",
                line_width=2,
                annotation_text=f"Meta: R$ {meta_patrimonio:,.0f}",
                annotation_position="top left",
                annotation_font=dict(color="#10b981", size=12)
            )
            
            fig_proj.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e5e7eb"),
                hovermode="x unified",
                xaxis=dict(
                    title="",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="Patrimônio (R$)",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12),
                    tickprefix="R$ "
                ),
                height=400,
                margin=dict(t=40, b=40, l=60, r=40)
            )
            
            st.plotly_chart(fig_proj, use_container_width=True)
            
        else:
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 60px 20px;
                text-align: center;
                border: 2px dashed #374151;
                margin: 20px 0;
            ">
                <div style="font-size: 64px; margin-bottom: 20px; color: #6b7280;">📊</div>
                <h3 style="color: #9ca3af; margin-bottom: 12px;">Projeção indisponível</h3>
                <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                    Dados insuficientes para gerar projeção.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= ANÁLISE EXECUTIVA CONSOLIDADA =================
    st.markdown("### 📝 Análise Executiva Consolidada")
    
    with st.container():
        
        texto_exec = gerar_texto_executivo(
            patrimonio=patrimonio,
            saldo_variavel=saldo_variavel,
            saldo_fixo=saldo_fixo,
            perc_meta=perc_meta,
            status_meta=status_meta,
            df_projecao=df_projecao
        )
        
        
        
        st.write(texto_exec)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= RECOMENDAÇÃO ESTRATÉGICA =================
    st.markdown("### 💡 Recomendação Estratégica")
    
    with st.container():
        
        st.markdown("#### 🎯 Aporte Ideal por Prazo")
        
        # Calcular sugestão para 5, 10 e 15 anos
        prazos = [5, 10, 15]
        
        for prazo in prazos:
            aporte, viavel = calcular_aporte_ideal_para_meta(
                patrimonio_atual=patrimonio,
                meta_patrimonio=meta_patrimonio,
                rendimento_mensal=rendimento_mensal,
                inflacao_mensal=inflacao_mensal,
                tempo_desejado_anos=prazo
            )
            
            cor_card_rec = "#10b981" if viavel else "#f59e0b"
            status_rec = "✅ Viável" if viavel else "⚠️ Ajustar"
            
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1], gap="medium")
            
            with col_r1:
                st.markdown(f"""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    border: 1px solid #374151;
                ">
                    <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">⏳ Prazo</div>
                    <div style="font-size: 20px; font-weight: bold; color: #e5e7eb;">{prazo} anos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_r2:
                st.markdown(f"""
                <div style="
                    background: {cor_card_rec}20;
                    border-radius: 12px;
                    padding: 16px;
                    border: 2px solid {cor_card_rec};
                    text-align: center;
                ">
                    <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">💰 Aporte Mensal</div>
                    <div style="font-size: 20px; font-weight: bold; color: {cor_card_rec};">R$ {aporte:,.0f}</div>
                    <div style="font-size: 12px; color: {cor_card_rec}; margin-top: 4px;">{status_rec}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_r3:
                diferenca = aporte - saldo_fixo
                if diferenca > 0:
                    st.markdown(f"""
                    <div style="
                        background: #1f2937;
                        border-radius: 12px;
                        padding: 16px;
                        text-align: center;
                        border: 1px solid #374151;
                    ">
                        <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">📊 Diferença</div>
                        <div style="font-size: 16px; font-weight: bold; color: #f59e0b;">
                            +R$ {diferenca:,.0f}
                        </div>
                        <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">a mais/mês</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: #1f2937;
                        border-radius: 12px;
                        padding: 16px;
                        text-align: center;
                        border: 1px solid #374151;
                    ">
                        <div style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">📊 Diferença</div>
                        <div style="font-size: 16px; font-weight: bold; color: #10b981;">
                            ✓ Dentro
                        </div>
                        <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">do atual</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= SIMULADOR DE CENÁRIOS =================
    st.markdown("### 🧮 Simulador de Cenários")
    
    with st.container():
        
        st.markdown("Simule ajustes financeiros e veja o impacto no patrimônio ao longo do tempo.")
        
        with st.expander("⚙️ Configurar cenário de simulação", expanded=False):
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid #374151;
                    margin-bottom: 20px;
                ">
                    <div style="font-size: 14px; color: #d1d5db; margin-bottom: 12px;">
                        ➕ Aporte mensal adicional
                    </div>
                """, unsafe_allow_html=True)
                
                aporte_extra = st.number_input(
                    "Valor em R$",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    label_visibility="collapsed"
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="
                    background: #1f2937;
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid #374151;
                    margin-bottom: 20px;
                ">
                    <div style="font-size: 14px; color: #d1d5db; margin-bottom: 12px;">
                        📉 Redução das despesas fixas
                    </div>
                """, unsafe_allow_html=True)
                
                ajuste_despesas = st.slider(
                    "Percentual de redução",
                    min_value=0,
                    max_value=50,
                    value=0,
                    step=5,
                    label_visibility="collapsed"
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # ================= CÁLCULO DO CENÁRIO SIMULADO =================
        saldo_fixo_simulado = saldo_fixo + aporte_extra
        
        if ajuste_despesas > 0:
            reducao = despesas_fixas * (ajuste_despesas / 100)
            saldo_fixo_simulado += reducao
        
        # 🔹 A PROJEÇÃO SIMULADA SEMPRE EXISTE
        df_projecao_simulada = projetar_patrimonio(
            patrimonio_inicial=patrimonio,
            saldo_fixo_mensal=saldo_fixo_simulado,
            rendimento_mensal=rendimento_mensal,
            inflacao_mensal=inflacao_mensal,
            meta_patrimonio=meta_patrimonio,
            meses=120
        )
        
        # ================= COMPARAÇÃO DE CENÁRIOS =================
        st.markdown("#### 📊 Comparação de Cenários")
        
        if not df_projecao.empty and not df_projecao_simulada.empty:
            meses_base = len(df_projecao)
            meses_simulado = len(df_projecao_simulada)
            ganho_tempo = meses_base - meses_simulado
            
            colc1, colc2, colc3 = st.columns(3, gap="medium")
            
            with colc1:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">⏱️ Cenário Atual</div>
                    <div style="font-size: 24px; font-weight: bold;">{meses_base} meses</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>Tempo até meta</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with colc2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🚀 Cenário Simulado</div>
                    <div style="font-size: 24px; font-weight: bold;">{meses_simulado} meses</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>{f"-{ganho_tempo} meses" if ganho_tempo > 0 else "Sem alteração"}</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with colc3:
                impacto = saldo_fixo_simulado - saldo_fixo
                cor_impacto = "#10b981" if impacto >= 0 else "#ef4444"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border-radius: 12px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">💡 Impacto Mensal</div>
                    <div style="font-size: 24px; font-weight: bold; color: {cor_impacto};">
                        R$ {impacto:+,.0f}
                    </div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 8px;">
                        <i>{"Aporte adicional" if impacto > 0 else "Redução"}</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ================= GRÁFICO COMPARATIVO =================
            st.markdown("#### 📈 Evolução do Patrimônio — Comparativo")
            
            # Preparar dados para o gráfico
            df_base = df_projecao.copy()
            df_base["Cenário"] = "Atual"
            
            df_sim = df_projecao_simulada.copy()
            df_sim["Cenário"] = "Simulado"
            
            df_plot = pd.concat([df_base, df_sim], ignore_index=True)
            
            fig_comp = px.line(
                df_plot,
                x="data",
                y="patrimonio",
                color="Cenário",
                color_discrete_map={"Atual": "#3b82f6", "Simulado": "#10b981"},
                markers=True,
                line_shape="spline"
            )
            
            fig_comp.update_traces(
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate="<b>%{x|%b/%Y}</b><br>%{data.name}: R$ %{y:,.0f}<extra></extra>"
            )
            
            # Linha da meta
            fig_comp.add_hline(
                y=meta_patrimonio,
                line_dash="dash",
                line_color="#8b5cf6",
                line_width=2,
                annotation_text="Meta",
                annotation_position="top left",
                annotation_font=dict(color="#8b5cf6", size=12)
            )
            
            fig_comp.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e5e7eb"),
                hovermode="x unified",
                xaxis=dict(
                    title="",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="Patrimônio (R$)",
                    gridcolor="#374151",
                    showgrid=True,
                    tickfont=dict(size=12),
                    tickprefix="R$ "
                ),
                height=450,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.markdown("""
            <div style="
                background: #1f2937;
                border-radius: 12px;
                padding: 40px 20px;
                text-align: center;
                border: 2px dashed #374151;
                margin: 20px 0;
            ">
                <div style="font-size: 48px; margin-bottom: 16px; color: #6b7280;">📊</div>
                <h4 style="color: #9ca3af; margin-bottom: 8px;">Simulação indisponível</h4>
                <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                    Configure o cenário de simulação para ver resultados.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= ALERTAS E CONTROLE =================
    st.markdown("### ⚠️ Alertas Críticos")
    
    with st.container():
        
        alertas = []
        
        if saldo_variavel < 0:
            alertas.append("Despesas variáveis superaram receitas no mês.")
        
        if saldo_fixo < 0:
            alertas.append("Estrutura fixa está consumindo patrimônio.")
        
        if perc_meta < 50:
            alertas.append("Patrimônio distante da meta definida.")
        
        if not alertas:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
                border-radius: 12px;
                padding: 20px;
                color: white;
                text-align: center;
            ">
                <div style="display: flex; align-items: center; justify-content: center; gap: 16px;">
                    <span style="font-size: 32px;">✅</span>
                    <div style="text-align: left;">
                        <div style="font-size: 18px; font-weight: bold; margin-bottom: 4px;">
                            Nenhum alerta crítico
                        </div>
                        <div style="font-size: 14px; opacity: 0.9;">
                            Sua saúde financeira está sob controle.
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for alerta in alertas:
                st.markdown(f"""
                <div style="
                    background: #7f1d1d20;
                    border: 1px solid #ef4444;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                    color: #e5e7eb;
                ">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 20px; color: #ef4444;">⚠️</span>
                        <div>{alerta}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= CONTROLE DO RELATÓRIO =================
    st.markdown("### 📥 Controle e Exportação")
    
    with st.container():
        
        col_controle1, col_controle2 = st.columns(2, gap="medium")
        
        with col_controle1:

            
            if st.button("💾 Salvar Rascunho", use_container_width=True):
                texto_exec = gerar_texto_executivo(
                    patrimonio=patrimonio,
                    saldo_variavel=saldo_variavel,
                    saldo_fixo=saldo_fixo,
                    perc_meta=perc_meta,
                    status_meta=status_meta,
                    df_projecao=df_projecao
                )
                
                ok, msg = salvar_relatorio_mensal(
                    dados=dados,
                    patrimonio=patrimonio,
                    saldo_fixo=saldo_fixo,
                    saldo_variavel=saldo_variavel,
                    perc_meta=perc_meta,
                    texto_exec=texto_exec,
                    status="Rascunho"
                )
                
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_controle2:

            
            if st.button("🔒 Finalizar Mês", use_container_width=True):
                texto_exec = gerar_texto_executivo(
                    patrimonio=patrimonio,
                    saldo_variavel=saldo_variavel,
                    saldo_fixo=saldo_fixo,
                    perc_meta=perc_meta,
                    status_meta=status_meta,
                    df_projecao=df_projecao
                )
                
                ok, msg = salvar_relatorio_mensal(
                    dados=dados,
                    patrimonio=patrimonio,
                    saldo_fixo=saldo_fixo,
                    saldo_variavel=saldo_variavel,
                    perc_meta=perc_meta,
                    texto_exec=texto_exec,
                    status="Finalizado"
                )
                
                st.success(msg) if ok else st.error(msg)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Botão de exportação
        st.markdown("<br>", unsafe_allow_html=True)
        
        texto_exec = gerar_texto_executivo(
            patrimonio=patrimonio,
            saldo_variavel=saldo_variavel,
            saldo_fixo=saldo_fixo,
            perc_meta=perc_meta,
            status_meta=status_meta,
            df_projecao=df_projecao
        )
        
        html = gerar_relatorio_html(
            nome_familia=nome_familia,
            patrimonio=patrimonio,
            saldo_variavel=saldo_variavel,
            saldo_fixo=saldo_fixo,
            perc_meta=perc_meta,
            status_meta=status_meta,
            texto_exec=texto_exec
        )
        
        st.download_button(
            label="⬇️ Baixar Relatório Executivo (HTML)",
            data=html,
            file_name=f"relatorio_executivo_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # ================= HISTÓRICO DE RELATÓRIOS =================
    if not dados.get("relatorios_historicos", pd.DataFrame()).empty:
        st.markdown("### 📜 Relatórios Anteriores")
        
        with st.container():
            
            df_hist = dados.get("relatorios_historicos", pd.DataFrame()).copy()
            
            # 🔒 blindagem de schema
            for col in ["mes", "status", "patrimonio", "saldo_fixo", "saldo_variavel", "perc_meta"]:
                if col not in df_hist.columns:
                    df_hist[col] = None
            
            df_hist = dados["relatorios_historicos"].sort_values("mes", ascending=False)
            
            # Estilizar o dataframe
            def color_status(val):
                if val == "Finalizado":
                    return "background-color: #065f46; color: white;"
                elif val == "Rascunho":
                    return "background-color: #78350f; color: white;"
                return ""
            
            st.dataframe(
                df_hist[[
                    "mes",
                    "patrimonio",
                    "saldo_fixo",
                    "saldo_variavel",
                    "perc_meta",
                    "status"
                ]].style.format({
                    "patrimonio": "R$ {:,.2f}",
                    "saldo_fixo": "R$ {:,.2f}",
                    "saldo_variavel": "R$ {:,.2f}",
                    "perc_meta": "{:.1f}%"
                }).applymap(color_status, subset=["status"]),
                use_container_width=True,
                height=300
            )
            
            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PLACEHOLDERS (não quebram)
# =========================================================
else:
    st.markdown(menu)
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None
    st.caption("🚧 Esta aba será finalizada nos próximos blocos.")



