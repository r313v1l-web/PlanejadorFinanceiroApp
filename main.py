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
        df_users = DatabaseManager.load_users()
        
        if st.button("🚀 Entrar no Sistema", type="primary", use_container_width=True):
            usuario_input = usuario.strip().lower()
            senha_input = senha.strip()
            
            user = df_users[df_users["usuario"] == usuario_input]
            
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

    df = DatabaseManager.load_users()

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


# =========================================================
# FUNÇÕES AUXILIARES (colocar ANTES do menu)
# =========================================================

def mostrar_gasto_card(idx, row, df_original, unique_counter):
    """Função auxiliar para mostrar um card de gasto"""
    # Usar um contador único em vez do índice do DataFrame
    unique_key = f"del_btn_{unique_counter}"
    
    # Formatar data - APENAS DATA, SEM HORA
    if isinstance(row['data'], pd.Timestamp):
        data_str = row['data'].strftime("%d/%m")
        dia_semana = row['data'].strftime("%a")
        data_completa = row['data'].strftime("%d/%m/%Y")  # REMOVI A HORA
    else:
        # Se for string, extrair apenas a parte da data
        data_str = str(row['data'])[:10] if row['data'] else ""
        dia_semana = ""
        data_completa = data_str
    
    # Determinar categoria
    desc_lower = row['descricao'].lower()
    if any(word in desc_lower for word in ['comida', 'restaurante', 'lanche', 'almoço', 'jantar', 'café']):
        categoria = "🍔 Alimentação"
        cor_categoria = "#f87171"
    elif any(word in desc_lower for word in ['uber', 'táxi', 'gasolina', 'combustível', 'ônibus', 'metro']):
        categoria = "🚗 Transporte"
        cor_categoria = "#60a5fa"
    elif any(word in desc_lower for word in ['mercado', 'supermercado', 'feira', 'padaria']):
        categoria = "🛒 Compras"
        cor_categoria = "#34d399"
    elif any(word in desc_lower for word in ['cinema', 'shopping', 'parque', 'lazer', 'bar']):
        categoria = "🎯 Lazer"
        cor_categoria = "#a78bfa"
    else:
        categoria = "📝 Outros"
        cor_categoria = "#9ca3af"
    
    # Card para cada gasto
    with st.container():
        st.markdown(f"""
        <div style="
            background: #1f2937;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid {cor_categoria};
            border: 1px solid #374151;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="
                            background: {cor_categoria}20;
                            color: {cor_categoria};
                            padding: 4px 12px;
                            border-radius: 20px;
                            font-size: 12px;
                            font-weight: bold;
                            margin-right: 12px;
                        ">
                            {categoria}
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
                    <div style="font-size: 12px; color: #9ca3af;">
                        {data_completa}
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
        
        # Confirmação de exclusão - usar chave única
        if st.session_state.get(f"confirm_delete_{unique_key}", False):
            with st.container():
                st.warning(f"Excluir '{row['descricao'][:30]}...'?")
                col_conf1, col_conf2 = st.columns(2)
                with col_conf1:
                    if st.button("✅ Sim", key=f"confirm_yes_{unique_key}", use_container_width=True):
                        # CORREÇÃO: Comparar datas corretamente (apenas a parte da data)
                        row_data = row['data']
                        
                        if isinstance(row_data, pd.Timestamp):
                            row_data_date = row_data.date()
                        elif isinstance(row_data, str):
                            row_data_date = pd.to_datetime(row_data).date()
                        else:
                            row_data_date = row_data
                        
                        # Encontrar o índice real no DataFrame original
                        for df_idx, df_row in df_original.iterrows():
                            df_row_data = df_row['data']
                            
                            if isinstance(df_row_data, pd.Timestamp):
                                df_row_data_date = df_row_data.date()
                            elif isinstance(df_row_data, str):
                                df_row_data_date = pd.to_datetime(df_row_data).date()
                            else:
                                df_row_data_date = df_row_data
                            
                            # Comparar datas, descrição e valor
                            if (df_row_data_date == row_data_date and 
                                df_row['descricao'] == row['descricao'] and 
                                df_row['valor'] == row['valor']):
                                
                                # Encontrou o registro, excluir
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
            "emoji": "💸",
            "label": "CONTROLE DE GASTOS",
            "color": "#3b82f6",
            "bg_color": "rgba(59, 130, 246, 0.1)"
        },
        {
            "emoji": "📊",
            "label": "DASHBOARD",
            "color": "#8b5cf6",
            "bg_color": "rgba(139, 92, 246, 0.1)"
        },
        {
            "emoji": "📝",
            "label": "LANÇAMENTOS",
            "color": "#10b981",
            "bg_color": "rgba(16, 185, 129, 0.1)"
        },
        {
            "emoji": "💰",
            "label": "INVESTIMENTOS",
            "color": "#f59e0b",
            "bg_color": "rgba(245, 158, 11, 0.1)"
        },
        {
            "emoji": "🎯",
            "label": "SONHOS & METAS",
            "color": "#ef4444",
            "bg_color": "rgba(239, 68, 68, 0.1)"
        },
        {
            "emoji": "🏢",
            "label": "FLUXOS FIXOS",
            "color": "#ec4899",
            "bg_color": "rgba(236, 72, 153, 0.1)"
        },
        {
            "emoji": "🏷️",
            "label": "CATEGORIAS",
            "color": "#14b8a6",
            "bg_color": "rgba(20, 184, 166, 0.1)"
        },
        {
            "emoji": "📄",
            "label": "RELATÓRIO EXECUTIVO",
            "color": "#6366f1",
            "bg_color": "rgba(99, 102, 241, 0.1)"
        },
        {
            "emoji": "⚙️",
            "label": "CONFIGURAÇÕES",
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
# 📝 LANÇAMENTOS - VERSÃO COMPACTA
# =========================================================
if menu == "📝 LANÇAMENTOS":

    st.markdown("📝 Registro de Transações")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    # ---------------- FORM ----------------
    with st.form("form_lancamento", clear_on_submit=True):
        col1, col2, col3 = st.columns(3 , gap="large")

        with col1:
            data = st.date_input("data", date.today())
            tipo = st.selectbox("tipo", ["Despesa", "Receita", "Investimento"])

        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
            categoria = st.selectbox(
                "categoria",
                dados["categorias"]["nome"].tolist() if not dados["categorias"].empty else []
            )

        with col3:
            responsavel = st.radio("Responsável", ["🧔 Ele", "👩‍🦰 Ela", "Compartilhado"], horizontal=True)
            fixo = st.checkbox("Recorrente")

        descricao = st.text_input("descrição")
        
        submitted = st.form_submit_button("💾 SALVAR")
        
        if submitted:
            nova = pd.DataFrame([{
                "data": data,
                "tipo": tipo,
                "valor": valor,
                "categoria": categoria,
                "subcategoria": "",
                "descricao": descricao,
                "responsavel": responsavel,
                "fixo": "Sim" if fixo else "Não"
            }])
            

            df = dados["historico"].copy()
            df = pd.concat([df, nova], ignore_index=True)

            dados["historico"] = df
            st.session_state["dados"] = dados
            DatabaseManager.save("historico", df, usuario)
            st.session_state["msg"] = "Salvo"
            st.session_state["msg_tipo"] = "success"
            st.rerun()

    st.divider()
    
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
# 💰 INVESTIMENTOS - VERSÃO COMPACTA
# =========================================================

elif menu == "💰 INVESTIMENTOS":

    st.markdown("💰 Carteira de Investimentos")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    # ---------------- RESUMO ----------------
    total = dados["investimentos"]["valor_atual"].sum() if not dados["investimentos"].empty else 0
    st.metric("Total Investido", f"R$ {total:,.2f}")

    st.divider()

    # ---------------- FORM ADICIONAR ----------------
    with st.expander("➕ Adicionar Investimento", expanded=False):
        with st.form("form_investimento", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")

            with col1:
                instituicao = st.text_input("Instituição")
                ativo = st.text_input("Ativo")
                tipo = st.selectbox(
                    "tipo",
                    ["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro", "Outros"]
                )

            with col2:
                valor_atual = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0)
                rendimento = st.number_input(
                    "Rendimento Mensal (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.8,
                    step=0.1
                ) / 100
                categoria = st.selectbox(
                    "Perfil",
                    ["Conservador", "Moderado", "Arrojado", "Especulativo"]
                )

            data_entrada = st.date_input("Data de Entrada", date.today())
            observacao = st.text_area("Observações", height=60)

            submitted = st.form_submit_button("💾 SALVAR INVESTIMENTO")

            if submitted:
                novo = pd.DataFrame([{
                    "Instituicao": instituicao,
                    "Ativo": ativo,
                    "tipo": tipo,
                    "valor_atual": valor_atual,
                    "Data_Entrada": data_entrada,
                    "Rendimento_Mensal": rendimento,
                    "categoria": categoria,
                    "Observacao": observacao
                }])
                

                df = dados["investimentos"].copy()
                df = pd.concat([df, novo], ignore_index=True)

                dados["investimentos"] = df
                st.session_state["dados"] = dados
                DatabaseManager.save("investimentos", df, usuario)
                st.session_state["msg"] = "Salvo"
                st.session_state["msg_tipo"] = "success"
                st.rerun()

    # ---------------- LISTA DE INVESTIMENTOS COMPACTA ----------------
    st.subheader("📋 Meus Investimentos")
    
    if not dados["investimentos"].empty:
        df_investimentos = dados["investimentos"].copy()
        
        # Normalizar nomes das colunas
        df_investimentos.columns = df_investimentos.columns.str.lower()
        
        # Container para lista
        lista_container = st.container()
        
        with lista_container:
            for idx, row in df_investimentos.iterrows():
                # Formatar data de entrada
                data_str = ""
                if 'data_entrada' in row and row['data_entrada']:
                    if hasattr(row['data_entrada'], 'strftime'):
                        data_str = row['data_entrada'].strftime("%d/%m/%Y")
                    else:
                        data_str = str(row['data_entrada'])
                
                # Criar linha compacta
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1], gap="small")
                
                with col1:
                    st.markdown(f"**{row.get('ativo', 'Sem nome')}**")
                    st.caption(f"{row.get('instituicao', '')} • {row.get('tipo', '')}")
                
                with col2:
                    st.markdown(f"**R$ {row.get('valor_atual', 0):,.2f}**")
                    rendimento = row.get('rendimento_mensal', 0)
                    if isinstance(rendimento, (int, float)):
                        st.caption(f"{rendimento:.2%} ao mês")
                
                with col3:
                    st.caption(f"Perfil: {row.get('categoria', '')}")
                    if data_str:
                        st.caption(f"Entrada: {data_str}")
                
                with col4:
                    # Botões compactos
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("✏️", key=f"edit_{idx}", help="Editar"):
                            st.session_state[f"editing_{idx}"] = True
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("🗑️", key=f"del_{idx}", help="Excluir"):
                            # Confirmar exclusão rápida
                            confirm = st.checkbox(f"Confirmar exclusão de {row.get('ativo', 'este investimento')}", key=f"confirm_{idx}")
                            if confirm:
                                df_investimentos = df_investimentos.drop(idx).reset_index(drop=True)
                                dados["investimentos"] = df_investimentos
                                st.session_state["dados"] = dados
                                DatabaseManager.save("investimentos", df_investimentos, usuario)
                                st.success("Investimento excluído!")
                                st.rerun()
                
                # Formulário de edição (aparece apenas quando ativado)
                if st.session_state.get(f"editing_{idx}", False):
                    with st.expander(f"✏️ Editar {row.get('ativo', 'Investimento')}", expanded=True):
                        with st.form(f"form_edit_{idx}"):
                            col_e1, col_e2 = st.columns(2, gap="small")
                            
                            with col_e1:
                                edit_instituicao = st.text_input("Instituição", value=row.get('instituicao', ''), key=f"edit_inst_{idx}")
                                edit_ativo = st.text_input("Ativo", value=row.get('ativo', ''), key=f"edit_ativo_{idx}")
                                edit_tipo = st.selectbox(
                                    "tipo",
                                    ["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro", "Outros"],
                                    index=["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro", "Outros"].index(row.get('tipo', 'Renda Fixa')) 
                                    if row.get('tipo') in ["Renda Fixa", "Ações", "FIIs", "ETF", "Fundos", "Tesouro", "Outros"] else 0,
                                    key=f"edit_tipo_{idx}"
                                )
                            
                            with col_e2:
                                edit_valor = st.number_input(
                                    "Valor Atual (R$)", 
                                    min_value=0.0, 
                                    step=100.0, 
                                    value=float(row.get('valor_atual', 0)),
                                    key=f"edit_valor_{idx}"
                                )
                                edit_rendimento = st.number_input(
                                    "Rendimento Mensal (%)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=float(row.get('rendimento_mensal', 0.8) * 100),
                                    step=0.1,
                                    key=f"edit_rend_{idx}"
                                ) / 100
                                edit_categoria = st.selectbox(
                                    "Perfil",
                                    ["Conservador", "Moderado", "Arrojado", "Especulativo"],
                                    index=["Conservador", "Moderado", "Arrojado", "Especulativo"].index(row.get('categoria', 'Conservador')) 
                                    if row.get('categoria') in ["Conservador", "Moderado", "Arrojado", "Especulativo"] else 0,
                                    key=f"edit_cat_{idx}"
                                )
                            
                            edit_data_entrada = st.date_input(
                                "Data de Entrada", 
                                value=pd.to_datetime(row.get('data_entrada', date.today())),
                                key=f"edit_data_{idx}"
                            )
                            
                            edit_observacao = st.text_area(
                                "Observações", 
                                value=row.get('observacao', ''),
                                key=f"edit_obs_{idx}",
                                height=60
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Salvar"):
                                    # Atualizar os dados
                                    df_investimentos.at[idx, 'instituicao'] = edit_instituicao
                                    df_investimentos.at[idx, 'ativo'] = edit_ativo
                                    df_investimentos.at[idx, 'tipo'] = edit_tipo
                                    df_investimentos.at[idx, 'valor_atual'] = edit_valor
                                    df_investimentos.at[idx, 'data_entrada'] = edit_data_entrada
                                    df_investimentos.at[idx, 'rendimento_mensal'] = edit_rendimento
                                    df_investimentos.at[idx, 'categoria'] = edit_categoria
                                    df_investimentos.at[idx, 'observacao'] = edit_observacao
                                    
                                    dados["investimentos"] = df_investimentos
                                    st.session_state["dados"] = dados
                                    DatabaseManager.save("investimentos", df_investimentos, usuario)
                                    
                                    st.session_state[f"editing_{idx}"] = False
                                    st.success("Investimento atualizado!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"editing_{idx}"] = False
                                    st.rerun()
                
                # Divisor fino entre itens
                st.markdown("<hr style='margin: 6px 0; border-color: #1f2933;'>", unsafe_allow_html=True)
    else:
        st.caption("Nenhum investimento cadastrado.")

    # ---------------- GRÁFICOS ----------------
    if not dados["investimentos"].empty:
        st.divider()
        st.subheader("📊 Distribuição da Carteira")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                dados["investimentos"],
                values="valor_atual",
                names="categoria",
                hole=0.4,
                title="Por Perfil"
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e5e7eb", size=10),
                showlegend=True,
                legend=dict(font=dict(size=9))
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = px.pie(
                dados["investimentos"],
                values="valor_atual",
                names="tipo",
                hole=0.4,
                title="Por Tipo"
            )
            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font=dict(color="#e5e7eb", size=10),
                showlegend=True,
                legend=dict(font=dict(size=9))
            )
            st.plotly_chart(fig2, use_container_width=True)



# =========================================================
# 🎯 SONHOS & METAS - CORREÇÃO DA EXCLUSÃO
# =========================================================

elif menu == "🎯 SONHOS & METAS":

    st.markdown("🎯 Sonhos & Metas")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    # ---------------- RESUMO ----------------
    if not dados["sonhos_projetos"].empty:
        sonhos_ativos = dados["sonhos_projetos"][dados["sonhos_projetos"]["status"] != "Desistido"]
        
        if not sonhos_ativos.empty:
            total_alvo = sonhos_ativos["valor_alvo"].sum()
            total_atual = sonhos_ativos["valor_atual"].sum()
            progresso = (total_atual / total_alvo * 100) if total_alvo > 0 else 0
        else:
            total_alvo = total_atual = progresso = 0
    else:
        total_alvo = total_atual = progresso = 0

    col1, col2, col3 = st.columns(3, gap="small")
    col1.metric("Total em Metas", f"R$ {total_alvo:,.2f}")
    col2.metric("Economizado", f"R$ {total_atual:,.2f}")
    col3.metric("Progresso", f"{progresso:.1f}%")

    st.divider()

    # ---------------- NOVO SONHO ----------------
    with st.expander("➕ Novo Sonho", expanded=False):
        with st.form("form_novo_sonho", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="small")

            with col1:
                nome = st.text_input("Nome")
                valor_alvo = st.number_input("Valor Alvo (R$)", min_value=0.0, step=1000.0)
                categoria = st.selectbox(
                    "categoria",
                    ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"]
                )

            with col2:
                data_alvo = st.date_input("Data Alvo", date.today() + timedelta(days=365))
                prioridade = st.selectbox("prioridade", ["Baixa", "Média", "Alta"])
                valor_inicial = st.number_input("Valor Inicial (R$)", min_value=0.0, step=500.0)

            descricao = st.text_area("descrição", height=60)

            if st.form_submit_button("🎯 Criar"):
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
                st.success("Sonho criado com sucesso!")
                st.rerun()

    # ---------------- LISTA COMPACTA ----------------
    st.subheader("📋 Meus Sonhos")
    
    if not dados["sonhos_projetos"].empty:
        for i, sonho in dados["sonhos_projetos"].iterrows():
            # Inicializar estado para exclusão
            delete_key = f"delete_sonho_{i}"
            if delete_key not in st.session_state:
                st.session_state[delete_key] = False
            
            # Container para cada sonho
            is_desistido = sonho.get("status") == "Desistido"
            
            # Cabeçalho do sonho
            col1, col2, col3 = st.columns([3, 1, 1], gap="small")
            
            with col1:
                if is_desistido:
                    st.markdown(f"😢 **{sonho['nome']}** *(Desistido)*")
                else:
                    st.markdown(f"🎯 **{sonho['nome']}**")
                st.caption(f"{sonho.get('categoria', '')} • {sonho.get('prioridade', '')} • {sonho['data_alvo']}")
            
            with col2:
                progresso = sonho["valor_atual"] / sonho["valor_alvo"] if sonho["valor_alvo"] > 0 else 0
                if not is_desistido:
                    st.progress(min(progresso, 1.0))
            
            with col3:
                st.markdown(f"**R$ {sonho['valor_atual']:,.0f}** / R$ {sonho['valor_alvo']:,.0f}")
            
            # Barra de progresso fina
            if not is_desistido:
                st.caption(f"Progresso: {progresso:.1%}")
            
            # Ações rápidas
            col_a1, col_a2, col_a3, col_a4 = st.columns(4, gap="small")
            
            with col_a1:
                # Adicionar/retirar valor rápido
                with st.popover("💰 Movimentar", use_container_width=True):
                    valor_mov = st.number_input(
                        "Valor (+ para adicionar, - para retirar)", 
                        value=0.0, 
                        step=100.0,
                        key=f"mov_{i}"
                    )
                    if st.button("Aplicar", key=f"apply_{i}", use_container_width=True):
                        novo_valor = sonho["valor_atual"] + valor_mov
                        if novo_valor >= 0:
                            dados["sonhos_projetos"].loc[i, "valor_atual"] = novo_valor
                            st.session_state["dados"] = dados
                            DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                            st.success(f"{'Adicionado' if valor_mov > 0 else 'Retirado'} R$ {abs(valor_mov):,.2f}")
                            st.rerun()
                        else:
                            st.error("Valor não pode ser negativo!")
            
            with col_a2:
                if is_desistido:
                    if st.button("🔄 Reativar", key=f"reat_{i}", use_container_width=True):
                        dados["sonhos_projetos"].loc[i, "status"] = "Em Andamento"
                        st.session_state["dados"] = dados
                        DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                        st.success("Reativado!")
                        st.rerun()
                else:
                    if st.button("😢 Desistir", key=f"des_{i}", use_container_width=True):
                        dados["sonhos_projetos"].loc[i, "status"] = "Desistido"
                        st.session_state["dados"] = dados
                        DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                        st.success("Marcado como desistido")
                        st.rerun()
            
            with col_a3:
                if st.button("✏️ Editar", key=f"edit_sonho_{i}", use_container_width=True):
                    st.session_state[f"editing_sonho_{i}"] = not st.session_state.get(f"editing_sonho_{i}", False)
                    st.rerun()
            
            with col_a4:
                # CORREÇÃO: Sistema de exclusão em duas etapas
                if not st.session_state[delete_key]:
                    if st.button("🗑️ Excluir", key=f"del_btn_{i}", use_container_width=True, type="secondary"):
                        st.session_state[delete_key] = True
                        st.rerun()
                else:
                    # Modo de confirmação
                    st.warning(f"Excluir '{sonho['nome']}'?")
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("✅ Sim", key=f"confirm_yes_{i}", use_container_width=True):
                            # Excluir permanentemente
                            dados["sonhos_projetos"] = dados["sonhos_projetos"].drop(i).reset_index(drop=True)
                            st.session_state["dados"] = dados
                            DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                            st.session_state[delete_key] = False
                            st.error("Sonho excluído permanentemente!")
                            st.rerun()
                    with col_confirm2:
                        if st.button("❌ Não", key=f"confirm_no_{i}", use_container_width=True):
                            st.session_state[delete_key] = False
                            st.rerun()
            
            # Formulário de edição
            if st.session_state.get(f"editing_sonho_{i}", False):
                with st.expander("✏️ Editar Sonho", expanded=True):
                    with st.form(f"form_edit_sonho_{i}"):
                        col_e1, col_e2 = st.columns(2, gap="small")
                        
                        with col_e1:
                            edit_nome = st.text_input("Nome", value=sonho["nome"], key=f"edit_nome_{i}")
                            edit_valor_alvo = st.number_input("Valor Alvo", value=sonho["valor_alvo"], min_value=0.0, key=f"edit_alvo_{i}")
                            edit_categoria = st.selectbox(
                                "Categoria",
                                ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"],
                                index=["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"].index(sonho.get('categoria', 'Outros')) 
                                if sonho.get('categoria') in ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"] else 5,
                                key=f"edit_cat_{i}"
                            )
                        
                        with col_e2:
                            edit_data_alvo = st.date_input("Data Alvo", value=pd.to_datetime(sonho["data_alvo"]), key=f"edit_data_{i}")
                            edit_prioridade = st.selectbox(
                                "Prioridade",
                                ["Baixa", "Média", "Alta"],
                                index=["Baixa", "Média", "Alta"].index(sonho.get('prioridade', 'Média')),
                                key=f"edit_prio_{i}"
                            )
                            edit_valor_atual = st.number_input(
                                "Valor Atual",
                                value=sonho["valor_atual"],
                                min_value=0.0,
                                key=f"edit_atual_{i}"
                            )
                        
                        edit_descricao = st.text_area("Descrição", value=sonho.get("descricao", ""), height=60, key=f"edit_desc_{i}")
                        edit_status = st.selectbox(
                            "Status",
                            ["Em Andamento", "Desistido", "Concluído"],
                            index=["Em Andamento", "Desistido", "Concluído"].index(sonho.get('status', 'Em Andamento')),
                            key=f"edit_status_{i}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Salvar"):
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
                                st.success("Atualizado!")
                                st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state[f"editing_sonho_{i}"] = False
                                st.rerun()
            
            # Divisor fino
            st.markdown("<hr style='margin: 8px 0; border-color: #1f2933;'>", unsafe_allow_html=True)
    else:
        st.caption("Nenhum sonho cadastrado.")






# =========================================================
# 🏢 FLUXOS FIXOS - CORREÇÃO DA EDIÇÃO
# =========================================================
elif menu == "🏢 FLUXOS FIXOS":

    st.markdown("🏢 Fluxos Fixos Mensais")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    # 🔥 NORMALIZAR O DATAFRAME
    if not dados["fluxo_fixo"].empty:
        df_fluxo = dados["fluxo_fixo"].copy()
        df_fluxo.columns = df_fluxo.columns.str.lower()
        df_fluxo["tipo"] = df_fluxo["tipo"].astype(str).str.strip().str.title()
    else:
        df_fluxo = pd.DataFrame(columns=["tipo", "valor", "nome", "categoria"])
    
    # RESUMO
    receitas = df_fluxo[df_fluxo["tipo"] == "Receita"]
    despesas = df_fluxo[df_fluxo["tipo"] == "Despesa"]
    
    total_receitas = receitas["valor"].sum() if not receitas.empty else 0
    total_despesas = despesas["valor"].sum() if not despesas.empty else 0
    saldo_fixo = total_receitas - total_despesas

    col1, col2, col3 = st.columns(3, gap="small")
    col1.metric("Receitas", f"R$ {total_receitas:,.2f}")
    col2.metric("Despesas", f"R$ {total_despesas:,.2f}")
    col3.metric("Saldo", f"R$ {saldo_fixo:,.2f}")

    st.divider()

    # ---------------- ADICIONAR FLUXO ----------------
    with st.expander("➕ Novo Fluxo", expanded=False):
        with st.form("form_fluxo", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="small")

            with col1:
                nome = st.text_input("Nome")
                valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"])

            with col2:
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
                    categorias_disponiveis = ["Outros"]
                
                categoria = st.selectbox("Categoria", categorias_disponiveis)
                recorrencia = st.selectbox("Recorrência", ["Mensal", "Anual", "Trimestral", "Semestral"])

            data_inicio = st.date_input("Data de Início", date.today())
            data_fim = st.date_input("Data de Fim (opcional)", value=None)
            observacao = st.text_area("Observações", height=60)

            if st.form_submit_button("💾 Salvar"):
                data_inicio_str = data_inicio.isoformat() if data_inicio else None
                data_fim_str = data_fim.isoformat() if data_fim else None
                
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

                df_novo_fluxo = pd.concat([df_fluxo, novo], ignore_index=True) if not df_fluxo.empty else novo
                
                dados["fluxo_fixo"] = df_novo_fluxo
                st.session_state["dados"] = dados
                DatabaseManager.save("fluxo_fixo", df_novo_fluxo, usuario)

                st.success("Fluxo adicionado!")
                st.rerun()

    # ---------------- LISTA COMPACTA ----------------
    st.subheader("📋 Meus Fluxos")
    
    tab1, tab2 = st.tabs(["📈 Receitas", "📉 Despesas"])
    
    with tab1:
        if not receitas.empty:
            for idx, row in receitas.iterrows():
                # Inicializar estado para edição
                edit_key = f"editing_rec_{idx}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                
                # Linha principal
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1], gap="small")
                
                with col1:
                    st.markdown(f"**{row.get('nome', '')}**")
                    st.caption(f"{row.get('categoria', '')} • {row.get('recorrencia', 'Mensal')}")
                
                with col2:
                    st.markdown(f"**R$ {row.get('valor', 0):,.2f}**")
                    if row.get('observacao'):
                        st.caption(f"{row.get('observacao', '')[:30]}...")
                
                with col3:
                    if st.button("✏️", key=f"btn_edit_rec_{idx}", help="Editar"):
                        st.session_state[edit_key] = True
                        st.rerun()
                
                with col4:
                    if st.button("🗑️", key=f"btn_del_rec_{idx}", help="Excluir"):
                        df_fluxo = df_fluxo.drop(idx).reset_index(drop=True)
                        dados["fluxo_fixo"] = df_fluxo
                        st.session_state["dados"] = dados
                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                        st.success("Excluído!")
                        st.rerun()
                
                # Formulário de edição (aparece apenas quando ativado)
                if st.session_state[edit_key]:
                    with st.expander(f"✏️ Editar {row.get('nome', 'Receita')}", expanded=True):
                        with st.form(f"form_edit_rec_{idx}"):
                            col_e1, col_e2 = st.columns(2, gap="small")
                            
                            with col_e1:
                                edit_nome = st.text_input("Nome", value=row.get('nome', ''), key=f"edit_nome_rec_{idx}")
                                edit_valor = st.number_input(
                                    "Valor (R$)", 
                                    min_value=0.0, 
                                    step=10.0, 
                                    value=float(row.get('valor', 0)),
                                    key=f"edit_valor_rec_{idx}"
                                )
                                edit_tipo = st.selectbox(
                                    "Tipo", 
                                    ["Receita", "Despesa"],
                                    index=0 if row.get('tipo') == "Receita" else 1,
                                    key=f"edit_tipo_rec_{idx}"
                                )
                            
                            with col_e2:
                                # Categorias disponíveis
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
                                    categorias_disponiveis = ["Outros"]
                                
                                # Encontrar índice da categoria atual
                                categoria_atual = row.get('categoria', 'Outros')
                                categoria_index = categorias_disponiveis.index(categoria_atual) if categoria_atual in categorias_disponiveis else 0
                                
                                edit_categoria = st.selectbox(
                                    "Categoria",
                                    categorias_disponiveis,
                                    index=categoria_index,
                                    key=f"edit_cat_rec_{idx}"
                                )
                                
                                edit_recorrencia = st.selectbox(
                                    "Recorrência",
                                    ["Mensal", "Anual", "Trimestral", "Semestral"],
                                    index=["Mensal", "Anual", "Trimestral", "Semestral"].index(row.get('recorrencia', 'Mensal')),
                                    key=f"edit_rec_rec_{idx}"
                                )
                            
                            # Datas
                            edit_data_inicio = st.date_input(
                                "Data de Início", 
                                value=pd.to_datetime(row.get('data_inicio', date.today())),
                                key=f"edit_inicio_rec_{idx}"
                            )
                            
                            edit_data_fim = st.date_input(
                                "Data de Fim (opcional)", 
                                value=pd.to_datetime(row.get('data_fim')) if row.get('data_fim') else None,
                                key=f"edit_fim_rec_{idx}"
                            )
                            
                            edit_observacao = st.text_area(
                                "Observações", 
                                value=row.get('observacao', ''),
                                height=60,
                                key=f"edit_obs_rec_{idx}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Salvar Alterações"):
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
                                    
                                    st.session_state[edit_key] = False
                                    st.success("Receita atualizada!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[edit_key] = False
                                    st.rerun()
                
                st.markdown("<hr style='margin: 6px 0; border-color: #1f2933;'>", unsafe_allow_html=True)
        else:
            st.caption("Nenhuma receita fixa")
    
    with tab2:
        if not despesas.empty:
            for idx, row in despesas.iterrows():
                # Inicializar estado para edição
                edit_key = f"editing_desp_{idx}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                
                # Linha principal
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1], gap="small")
                
                with col1:
                    st.markdown(f"**{row.get('nome', '')}**")
                    st.caption(f"{row.get('categoria', '')} • {row.get('recorrencia', 'Mensal')}")
                
                with col2:
                    st.markdown(f"**R$ {row.get('valor', 0):,.2f}**")
                    if row.get('observacao'):
                        st.caption(f"{row.get('observacao', '')[:30]}...")
                
                with col3:
                    if st.button("✏️", key=f"btn_edit_desp_{idx}", help="Editar"):
                        st.session_state[edit_key] = True
                        st.rerun()
                
                with col4:
                    if st.button("🗑️", key=f"btn_del_desp_{idx}", help="Excluir"):
                        df_fluxo = df_fluxo.drop(idx).reset_index(drop=True)
                        dados["fluxo_fixo"] = df_fluxo
                        st.session_state["dados"] = dados
                        DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)
                        st.success("Excluído!")
                        st.rerun()
                
                # Formulário de edição (aparece apenas quando ativado)
                if st.session_state[edit_key]:
                    with st.expander(f"✏️ Editar {row.get('nome', 'Despesa')}", expanded=True):
                        with st.form(f"form_edit_desp_{idx}"):
                            col_e1, col_e2 = st.columns(2, gap="small")
                            
                            with col_e1:
                                edit_nome = st.text_input("Nome", value=row.get('nome', ''), key=f"edit_nome_desp_{idx}")
                                edit_valor = st.number_input(
                                    "Valor (R$)", 
                                    min_value=0.0, 
                                    step=10.0, 
                                    value=float(row.get('valor', 0)),
                                    key=f"edit_valor_desp_{idx}"
                                )
                                edit_tipo = st.selectbox(
                                    "Tipo", 
                                    ["Receita", "Despesa"],
                                    index=0 if row.get('tipo') == "Receita" else 1,
                                    key=f"edit_tipo_desp_{idx}"
                                )
                            
                            with col_e2:
                                # Categorias disponíveis
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
                                    categorias_disponiveis = ["Outros"]
                                
                                # Encontrar índice da categoria atual
                                categoria_atual = row.get('categoria', 'Outros')
                                categoria_index = categorias_disponiveis.index(categoria_atual) if categoria_atual in categorias_disponiveis else 0
                                
                                edit_categoria = st.selectbox(
                                    "Categoria",
                                    categorias_disponiveis,
                                    index=categoria_index,
                                    key=f"edit_cat_desp_{idx}"
                                )
                                
                                edit_recorrencia = st.selectbox(
                                    "Recorrência",
                                    ["Mensal", "Anual", "Trimestral", "Semestral"],
                                    index=["Mensal", "Anual", "Trimestral", "Semestral"].index(row.get('recorrencia', 'Mensal')),
                                    key=f"edit_rec_desp_{idx}"
                                )
                            
                            # Datas
                            edit_data_inicio = st.date_input(
                                "Data de Início", 
                                value=pd.to_datetime(row.get('data_inicio', date.today())),
                                key=f"edit_inicio_desp_{idx}"
                            )
                            
                            edit_data_fim = st.date_input(
                                "Data de Fim (opcional)", 
                                value=pd.to_datetime(row.get('data_fim')) if row.get('data_fim') else None,
                                key=f"edit_fim_desp_{idx}"
                            )
                            
                            edit_observacao = st.text_area(
                                "Observações", 
                                value=row.get('observacao', ''),
                                height=60,
                                key=f"edit_obs_desp_{idx}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Salvar Alterações"):
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
                                    
                                    st.session_state[edit_key] = False
                                    st.success("Despesa atualizada!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[edit_key] = False
                                    st.rerun()
                
                st.markdown("<hr style='margin: 6px 0; border-color: #1f2933;'>", unsafe_allow_html=True)
        else:
            st.caption("Nenhuma despesa fixa")
       



# =========================================================
# 💸 CONTROLE DE GASTOS - VERSÃO COM CARDS
# =========================================================

elif menu == "💸 CONTROLE DE GASTOS":

    st.markdown("💸 Controle de Gastos Mensais")
    
    # Mensagens de feedback
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])
        st.session_state["msg"] = None
    
    st.caption("Reserva mensal para gastos do dia a dia")

    # ---------- RESERVA ----------
    reserva_mensal = float(config_dict.get("reserva_gastos", 0))

    if reserva_mensal == 0:
        st.warning("⚠️ Defina a reserva mensal em Configurações.")
        st.stop()

    # ---------- CARREGAR GASTOS ----------
    if "controle_gastos" not in dados or dados["controle_gastos"].empty:
        df_gastos = pd.DataFrame(columns=["data", "descricao", "valor"])
    else:
        df_gastos = dados["controle_gastos"].copy()
        
        # Converter 'data' para datetime
        if "data" in df_gastos.columns and not df_gastos.empty:
            df_gastos["data"] = pd.to_datetime(df_gastos["data"], errors='coerce')
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
                

                        

        
        with tab4:
            # Análise por categorias
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
                border-radius: 12px;
                padding: 16px;
                color: #7c3aed;
                margin-bottom: 20px;
                border: 1px solid #a78bfa;
            ">
                <div style="font-size: 16px; font-weight: bold;">🏷️ Análise por Categorias</div>
                <div style="font-size: 14px;">Distribuição dos seus gastos</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detectar categorias automaticamente
            categorias = {
                "🍔 Alimentação": 0,
                "🚗 Transporte": 0,
                "🛒 Compras": 0,
                "🎯 Lazer": 0,
                "🏠 Casa": 0,
                "📱 Serviços": 0,
                "📝 Outros": 0
            }
            
            palavras_chave = {
                "🍔 Alimentação": ['comida', 'restaurante', 'lanche', 'almoço', 'jantar', 'café', 'padaria', 'pizza', 'hamburguer', 'sorvete'],
                "🚗 Transporte": ['uber', 'táxi', 'gasolina', 'combustível', 'ônibus', 'metro', 'estacionamento', 'pedágio'],
                "🛒 Compras": ['mercado', 'supermercado', 'feira', 'shopping', 'roupa', 'calçado', 'eletrônico', 'livro'],
                "🎯 Lazer": ['cinema', 'parque', 'bar', 'show', 'viagem', 'hotel', 'play', 'jogo', 'streaming'],
                "🏠 Casa": ['aluguel', 'condomínio', 'luz', 'água', 'gás', 'internet', 'manutenção', 'reforma'],
                "📱 Serviços": ['celular', 'assinatura', 'plano', 'conserto', 'serviço', 'taxa', 'assinatura']
            }
            
            for idx, row in df_gastos.iterrows():
                desc_lower = row['descricao'].lower()
                categoria_encontrada = False
                
                for categoria, palavras in palavras_chave.items():
                    if any(palavra in desc_lower for palavra in palavras):
                        categorias[categoria] += row['valor']
                        categoria_encontrada = True
                        break
                
                if not categoria_encontrada:
                    categorias["📝 Outros"] += row['valor']
            
            # Mostrar gráfico de pizza
            df_categorias = pd.DataFrame({
                'Categoria': list(categorias.keys()),
                'Valor': list(categorias.values())
            })
            df_categorias = df_categorias[df_categorias['Valor'] > 0]
            
            if not df_categorias.empty:
                col_graf1, col_graf2 = st.columns([2, 1])
                
                with col_graf1:
                    fig = px.pie(
                        df_categorias,
                        values='Valor',
                        names='Categoria',
                        title='Distribuição por Categoria',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(
                        height=400,
                        showlegend=True,
                        plot_bgcolor='#0e1117',
                        paper_bgcolor='#0e1117',
                        font=dict(color='#e5e7eb')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_graf2:
                    # Tabela de resumo
                    st.markdown("**📊 Resumo por Categoria**")
                    
                    for categoria, valor in categorias.items():
                        if valor > 0:
                            percentual = (valor / df_gastos['valor'].sum()) * 100
                            st.markdown(f"""
                            <div style="
                                background: #1f2937;
                                border-radius: 8px;
                                padding: 10px;
                                margin-bottom: 8px;
                                border-left: 4px solid #3b82f6;
                            ">
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="font-weight: bold;">{categoria}</span>
                                    <span style="color: #f87171;">R$ {valor:,.2f}</span>
                                </div>
                                <div style="font-size: 12px; color: #9ca3af;">
                                    {percentual:.1f}% do total
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Gastos por categoria específica
            categoria_selecionada = st.selectbox(
                "Ver gastos por categoria",
                [cat for cat, valor in categorias.items() if valor > 0],
                key="categoria_selecionada"
            )
            
            if categoria_selecionada:
                # Filtrar gastos por categoria
                gastos_categoria = []
                for idx, row in df_gastos.iterrows():
                    desc_lower = row['descricao'].lower()
                    palavras = palavras_chave.get(categoria_selecionada, [])
                    
                    if any(palavra in desc_lower for palavra in palavras) or \
                    (categoria_selecionada == "📝 Outros" and not any(
                        any(p in desc_lower for p in palavras_chave[cat]) 
                        for cat in palavras_chave.keys()
                    )):
                        gastos_categoria.append((idx, row))
                
                if gastos_categoria:
                    st.markdown(f"### Gastos em {categoria_selecionada}")
                    for i, (idx, row) in enumerate(gastos_categoria):
                        mostrar_gasto_card(idx, row, df_gastos, unique_counter=f"cat_{categoria_selecionada}_{i}")
                else:
                    st.info(f"Nenhum gasto encontrado na categoria {categoria_selecionada}")

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
# 📊 DASHBOARD - VERSÃO ESTILIZADA CORRIGIDA
# =========================================================

elif menu == "📊 DASHBOARD":

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
# 🏷️ CATEGORIAS
# =========================================================

elif menu == "🏷️ CATEGORIAS":

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
# ⚙️ CONFIGURAÇÕES
# =========================================================


elif menu == "⚙️ CONFIGURAÇÕES":

    st.markdown("⚙️ Configurações do Sistema")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    with st.form("form_config", clear_on_submit=False):

        col1, col2 = st.columns(2, gap="large")

        with col1:
            meta = st.number_input(
                "💰 Meta de Patrimônio (R$)",
                min_value=0.0,
                value=meta_patrimonio,
                step=10000.0
            )

            orcamento = st.number_input(
                "📊 Orçamento Mensal (R$)",
                min_value=0.0,
                value=orcamento_mensal,
                step=500.0
            )

            nome = st.text_input(
                "👨‍👩‍👧 Nome da Família",
                value=nome_familia
            )

        with col2:
            rendimento = st.number_input(
                "📈 Rendimento Mensal Esperado (%)",
                min_value=0.0,
                max_value=100.0,
                value=rendimento_mensal * 100,
                step=0.1
            ) / 100

            inflacao = st.number_input(
                "💸 Inflação Mensal Esperada (%)",
                min_value=0.0,
                max_value=100.0,
                value=inflacao_mensal * 100,
                step=0.1
            ) / 100
            reserva = st.number_input(
                "💸 Reserva mensal para gastos rápidos (R$)",
                min_value=0.0,
                value=float(config_dict.get("reserva_gastos", 0)),
                step=50.0
            )

        submitted = st.form_submit_button("💾 SALVAR CONFIGURAÇÕES")

        if submitted:
            df_config = pd.DataFrame([
                {"chave": "meta_patrimonio", "valor": meta, "descricao": "Meta total de patrimônio"},
                {"chave": "orcamento_mensal", "valor": orcamento, "descricao": "Orçamento mensal"},
                {"chave": "nome_familia", "valor": nome, "descricao": "Nome da família"},
                {"chave": "rendimento_mensal", "valor": rendimento, "descricao": "Rendimento mensal"},
                {"chave": "inflacao_mensal", "valor": inflacao, "descricao": "Inflação mensal"},
                {"chave": "reserva_gastos", "valor": reserva, "descricao": "Reserva mensal de gastos rápidos"}
            ])

            # Normaliza colunas ANTES de salvar
            df_config.columns = df_config.columns.str.lower()

            dados["config"] = df_config
            st.session_state["dados"] = dados

            DatabaseManager.save("config", df_config, st.session_state["usuario"])

            st.session_state["msg"] = "Salvo"
            st.session_state["msg_tipo"] = "success"
            st.rerun()

# =========================================================
# 📄 USUÁRIOS
# =========================================================

elif menu == "👥 USUÁRIOS":
    if st.session_state.get("perfil") != "admin":
        st.error("Acesso restrito.")
        st.stop()

    tela_admin_usuarios()


# =========================================================
# 📄 RELATÓRIO EXECUTIVO - VERSÃO ESTILIZADA
# =========================================================

elif menu == "📄 RELATÓRIO EXECUTIVO":
    
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



