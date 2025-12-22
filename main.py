import streamlit as st

import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px

from database import DatabaseManager
from dateutil.relativedelta import relativedelta

import io
import bcrypt



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
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")  # ✅ AGORA COM TYPE

    
    df_users = DatabaseManager.load_users()

    if st.button("Entrar"):
        usuario_input = usuario.strip().lower()
        senha_input = senha.strip()

        user = df_users[df_users["usuario"] == usuario_input]

        if user.empty:
            st.error("Usuário não encontrado.")
            return

        senha_hash = user.iloc[0]["senha"]

        if not bcrypt.checkpw(
            senha_input.encode("utf-8"),
            senha_hash.encode("utf-8")
        ):
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

        st.success("Login realizado com sucesso.")
        st.rerun()



def tela_admin_usuarios():
    st.title("👥 Gestão de Usuários")

    df = DatabaseManager.load_users()

    # ===============================
    # ➕ CRIAR NOVO USUÁRIO
    # ===============================
    st.subheader("➕ Novo Usuário")

    with st.form("form_novo_usuario", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

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
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

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
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)




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
# CALCULOS GERAIS (BLOCO 3)
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

# ---------------- SONHOS ----------------
if not dados["sonhos_projetos"].empty:
    total_sonhos = dados["sonhos_projetos"]["valor_alvo"].sum()
    total_atual = dados["sonhos_projetos"]["valor_atual"].sum()
    progresso_sonhos = (total_atual / total_sonhos * 100) if total_sonhos > 0 else 0
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
# SIDEBAR (MENU ÚNICO DO SISTEMA)
# =========================================================
with st.sidebar:

    st.markdown(
        """
        <h1 style="text-align:center; font-size:80px;">💸</h1>
        <h2 style="text-align:center">Gestão Financeira</h2>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ===============================
    # MENU BASE
    # ===============================
    menu_itens = [
        "💸 CONTROLE DE GASTOS",
        "📊 DASHBOARD",
        "📝 LANÇAMENTOS",        
        "💰 INVESTIMENTOS",
        "🎯 SONHOS & METAS",
        "🏢 FLUXOS FIXOS",
        "🏷️ CATEGORIAS",
        "📄 RELATÓRIO EXECUTIVO",
        "⚙️ CONFIGURAÇÕES",
        
    ]

    # ===============================
    # MENU ADMIN
    # ===============================
    if st.session_state.get("perfil") == "admin":
        menu_itens.append("👥 USUÁRIOS")

    # ===============================
    # RADIO DE NAVEGAÇÃO
    # ===============================
    menu = st.radio(
        "NAVEGAÇÃO",
        menu_itens
    )

    st.divider()

    # ===============================
    # USUÁRIO LOGADO
    # ===============================
    st.caption(f"👤 {st.session_state.get('nome')}")

    # ===============================
    # LOGOUT
    # ===============================
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =========================================================
# 📝 LANÇAMENTOS
# =========================================================
if menu == "📝 LANÇAMENTOS":

    st.title("📝 Registro de Transações")
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
        col1, col2, col3 = st.columns(3)

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



# =========================================================
# 💰 INVESTIMENTOS
# =========================================================
elif menu == "💰 INVESTIMENTOS":

    st.title("💰 Carteira de Investimentos")
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

    # ---------------- TABELA ----------------
    if not dados["investimentos"].empty:
        st.dataframe(
            dados["investimentos"].style.format({
                "valor_atual": "R$ {:,.2f}",
                "Rendimento_Mensal": "{:.2%}"
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.caption("Nenhum investimento cadastrado.")

    # ---------------- GRÁFICO ----------------
    if not dados["investimentos"].empty:
        fig = px.pie(
            dados["investimentos"],
            values="valor_atual",
            names="categoria",
            hole=0.4,
            title="Distribuição por Perfil"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- FORM ----------------
    with st.expander("➕ Adicionar Investimento"):
        with st.form("form_investimento", clear_on_submit=True):
            col1, col2 = st.columns(2)

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
            observacao = st.text_area("Observações")

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


# =========================================================
# 🎯 SONHOS & METAS
# =========================================================
elif menu == "🎯 SONHOS & METAS":

    st.title("🎯 Sonhos & Metas")
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
        total_alvo = dados["sonhos_projetos"]["valor_alvo"].sum()
        total_atual = dados["sonhos_projetos"]["valor_atual"].sum()
        progresso = (total_atual / total_alvo * 100) if total_alvo > 0 else 0
    else:
        total_alvo = total_atual = progresso = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total em Metas", f"R$ {total_alvo:,.2f}")
    col2.metric("Economizado", f"R$ {total_atual:,.2f}")
    col3.metric("Progresso Geral", f"{progresso:.1f}%")

    st.divider()

    # ---------------- LISTA ----------------
    if not dados["sonhos_projetos"].empty:
        for i, sonho in dados["sonhos_projetos"].iterrows():

            st.subheader(sonho["nome"])
            st.caption(sonho.get("descricao", ""))

            progresso = sonho["valor_atual"] / sonho["valor_alvo"] if sonho["valor_alvo"] > 0 else 0
            st.progress(progresso, text=f"R$ {sonho['valor_atual']:,.0f} / R$ {sonho['valor_alvo']:,.0f}")

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.caption(f"📅 {sonho['data_alvo']}")
            col_s2.caption(f"🔸 {sonho['prioridade']}")
            col_s3.caption(f"📊 {sonho['status']}")

            # --- adicionar valor ---
            with st.form(f"form_add_{i}", clear_on_submit=True):
                valor_add = st.number_input("Adicionar valor", min_value=0.0, step=100.0)
                if st.form_submit_button("💸 Adicionar"):
                    dados["sonhos_projetos"].loc[i, "valor_atual"] += valor_add
                    st.session_state["dados"] = dados
                    DatabaseManager.save("sonhos_projetos", dados["sonhos_projetos"], usuario)
                    st.session_state["msg"] = "Salvo"
                    st.session_state["msg_tipo"] = "success"
                    st.rerun()

            st.divider()
    else:
        st.caption("Nenhum sonho cadastrado.")

    # ---------------- NOVO SONHO ----------------
    with st.expander("➕ Adicionar Novo Sonho"):
        with st.form("form_novo_sonho", clear_on_submit=True):
            col1, col2 = st.columns(2)

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

            descricao = st.text_area("descrição")

            if st.form_submit_button("🎯 Criar Sonho"):
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
                st.session_state["msg"] = "Salvo"
                st.session_state["msg_tipo"] = "success"
                st.rerun()

# =========================================================
# 🏢 FLUXOS FIXOS
# =========================================================
elif menu == "🏢 FLUXOS FIXOS":

    st.title("🏢 Fluxos Fixos Mensais")
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
        
        if "tipo" not in df_fluxo.columns:
            st.error("Erro: Coluna 'tipo' não encontrada")
            st.stop()
        
        df_fluxo["tipo"] = df_fluxo["tipo"].astype(str).str.strip().str.title()
    else:
        df_fluxo = pd.DataFrame(columns=["tipo", "valor", "nome", "categoria"])
    
    # FILTRAR
    receitas = df_fluxo[df_fluxo["tipo"] == "Receita"]
    despesas = df_fluxo[df_fluxo["tipo"] == "Despesa"]

    total_receitas = receitas["valor"].sum() if not receitas.empty and "valor" in receitas.columns else 0
    total_despesas = despesas["valor"].sum() if not despesas.empty and "valor" in despesas.columns else 0
    saldo_fixo = total_receitas - total_despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas Fixas", f"R$ {total_receitas:,.2f}")
    col2.metric("Despesas Fixas", f"R$ {total_despesas:,.2f}")
    col3.metric("Saldo Fixo", f"R$ {saldo_fixo:,.2f}")

    st.divider()

    tab1, tab2 = st.tabs(["📈 Receitas", "📉 Despesas"])

    with tab1:
        if not receitas.empty:
            st.dataframe(
                receitas.style.format({"valor": "R$ {:,.2f}"}),
                use_container_width=True
            )
        else:
            st.caption("Nenhuma receita fixa cadastrada.")

    with tab2:
        if not despesas.empty:
            st.dataframe(
                despesas.style.format({"valor": "R$ {:,.2f}"}),
                use_container_width=True
            )
        else:
            st.caption("Nenhuma despesa fixa cadastrada.")

    # ---------------- NOVO FLUXO ----------------
    with st.expander("➕ Adicionar Fluxo Fixo"):
        with st.form("form_fluxo", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome")
                valor = st.number_input("Valor Mensal (R$)", min_value=0.0, step=10.0)
                tipo = st.selectbox("tipo", ["Receita", "Despesa"])

            with col2:
                # 🔥 FILTRAR: Mostrar apenas categorias ATIVAS
                categorias_disponiveis = []
                if not dados["categorias"].empty:
                    df_categorias = dados["categorias"].copy()
                    df_categorias.columns = df_categorias.columns.str.lower()
                    
                    # Filtrar apenas categorias ativas
                    if "ativa" in df_categorias.columns:
                        # Converter para booleano se necessário
                        df_categorias["ativa"] = pd.to_numeric(df_categorias["ativa"], errors='coerce').fillna(1).astype(bool)
                        categorias_ativas = df_categorias[df_categorias["ativa"] == True]
                    else:
                        categorias_ativas = df_categorias
                    
                    if "nome" in categorias_ativas.columns:
                        categorias_disponiveis = categorias_ativas["nome"].dropna().unique().tolist()
                
                # Adicionar opção padrão se não houver categorias
                if not categorias_disponiveis:
                    categorias_disponiveis = ["Outros"]
                
                categoria = st.selectbox(
                    "categoria",
                    categorias_disponiveis
                )
                
                recorrencia = st.selectbox(
                    "Recorrência",
                    ["Mensal", "Anual", "Trimestral", "Semestral"]
                )

            data_inicio = st.date_input("Data de Início", date.today())
            data_fim = st.date_input("Data de Fim (opcional)", value=None)
            observacao = st.text_area("Observações")

            submitted = st.form_submit_button("💾 Salvar Fluxo")

            if submitted:
                # 🔥 CONVERTER DATAS PARA STRING (resolver TypeError)
                data_inicio_str = data_inicio.isoformat() if data_inicio else None
                data_fim_str = data_fim.isoformat() if data_fim else None
                
                novo = pd.DataFrame([{
                    "nome": nome.strip(),
                    "valor": float(valor),  # Garantir que é float
                    "tipo": tipo.strip().title(),
                    "categoria": categoria,
                    "data_inicio": data_inicio_str,  # 🔥 STRING, não date
                    "data_fim": data_fim_str,        # 🔥 STRING, não date
                    "recorrencia": recorrencia,
                    "observacao": observacao.strip()
                }])

                # Preparar DataFrame para salvar
                df_novo_fluxo = df_fluxo.copy() if not df_fluxo.empty else pd.DataFrame()
                
                # Garantir colunas
                colunas_base = ["nome", "valor", "tipo", "categoria", "data_inicio", 
                               "data_fim", "recorrencia", "observacao"]
                for col in colunas_base:
                    if col not in df_novo_fluxo.columns:
                        df_novo_fluxo[col] = None if df_novo_fluxo.empty else ""
                
                df_novo_fluxo = pd.concat([df_novo_fluxo, novo], ignore_index=True)
                df_novo_fluxo.columns = df_novo_fluxo.columns.str.lower()

                # 🔥 Converter quaisquer datas restantes para string
                for date_col in ["data_inicio", "data_fim"]:
                    if date_col in df_novo_fluxo.columns:
                        df_novo_fluxo[date_col] = df_novo_fluxo[date_col].apply(
                            lambda x: x.isoformat() if hasattr(x, 'isoformat') else x
                        )

                # Salvar
                dados["fluxo_fixo"] = df_novo_fluxo
                st.session_state["dados"] = dados
                DatabaseManager.save("fluxo_fixo", df_novo_fluxo, usuario)

                st.session_state["msg"] = "Fluxo fixo adicionado com sucesso."
                st.session_state["msg_tipo"] = "success"
                st.rerun()

    st.divider()
    st.subheader("🗑️ Excluir Fluxo Fixo")

    if not df_fluxo.empty:
        df_fluxo_excluir = df_fluxo.copy()
        
        if "nome" not in df_fluxo_excluir.columns:
            df_fluxo_excluir["nome"] = ""
        if "tipo" not in df_fluxo_excluir.columns:
            df_fluxo_excluir["tipo"] = ""
        if "valor" not in df_fluxo_excluir.columns:
            df_fluxo_excluir["valor"] = 0
        
        df_fluxo_excluir["Label"] = (
            df_fluxo_excluir["nome"].fillna("Sem nome") + " | " +
            df_fluxo_excluir["tipo"].fillna("Sem tipo") + " | R$ " +
            df_fluxo_excluir["valor"].astype(str)
        )

        fluxo_sel = st.selectbox(
            "Selecione o fluxo para excluir",
            df_fluxo_excluir["Label"].tolist()
        )

        if st.button("❌ Excluir Fluxo Selecionado"):
            idx = df_fluxo_excluir[df_fluxo_excluir["Label"] == fluxo_sel].index[0]
            df_fluxo_excluir = df_fluxo_excluir.drop(idx).reset_index(drop=True)
            
            if "Label" in df_fluxo_excluir.columns:
                df_fluxo_excluir = df_fluxo_excluir.drop(columns=["Label"])
            
            # 🔥 Converter datas para string antes de salvar
            for date_col in ["data_inicio", "data_fim"]:
                if date_col in df_fluxo_excluir.columns:
                    df_fluxo_excluir[date_col] = df_fluxo_excluir[date_col].apply(
                        lambda x: x.isoformat() if hasattr(x, 'isoformat') else x
                    )
            
            dados["fluxo_fixo"] = df_fluxo_excluir
            st.session_state["dados"] = dados
            DatabaseManager.save("fluxo_fixo", df_fluxo_excluir, usuario)

            st.success("Fluxo fixo excluído com sucesso.")
            st.rerun()
    else:
        st.caption("Nenhum fluxo fixo cadastrado.")            



# =========================================================
# 💸 CONTROLE DE GASTOS
# =========================================================

elif menu == "💸 CONTROLE DE GASTOS":

    st.title("💸 Controle de Gastos Mensais")
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

    gasto_total = df_gastos["valor"].sum() if not df_gastos.empty else 0
    saldo_restante = reserva_mensal - gasto_total

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Reserva Mensal", f"R$ {reserva_mensal:,.2f}")
    col2.metric("🧾 Total Gasto", f"R$ {gasto_total:,.2f}")
    col3.metric(
        "🟢 Saldo Disponível" if saldo_restante >= 0 else "🔴 Estouro",
        f"R$ {saldo_restante:,.2f}"
    )

    st.divider()

    # ---------- NOVO GASTO ----------
    st.subheader("➕ Registrar Gasto Rápido")

    with st.form("form_gasto_rapido", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            descricao = st.text_input("descrição", placeholder="Padaria, café, lanche...")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=1.0)

        if st.form_submit_button("💸 Registrar Gasto"):
            novo = pd.DataFrame([{
                "data": date.today(),
                "descricao": descricao,
                "valor": valor
            }])

            df_gastos = pd.concat([df_gastos, novo], ignore_index=True)
            dados["controle_gastos"] = df_gastos
            st.session_state["dados"] = dados
            DatabaseManager.save("controle_gastos", df_gastos, usuario)

            st.success("Gasto registrado com sucesso.")
            st.rerun()

    st.divider()

    # ---------- HISTÓRICO ----------
    st.subheader("📋 Gastos Registrados")

    if not df_gastos.empty:
        st.dataframe(
            df_gastos.sort_values("data", ascending=False).style.format({
                "valor": "R$ {:,.2f}"
            }),
            use_container_width=True,
            height=350
        )
    else:
        st.caption("Nenhum gasto registrado neste mês.")




# =========================================================
# 📊 DASHBOARD
# =========================================================

elif menu == "📊 DASHBOARD":

    st.title("📊 Dashboard Financeiro")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Patrimônio", f"R$ {patrimonio:,.2f}")

    col2.metric(
        "📈 Saldo Variável (Mês)",
        f"R$ {saldo_variavel:,.2f}",
        delta_color="inverse" if saldo_variavel < 0 else "normal"
    )

    col3.metric(
        "🏢 Saldo Fixo Mensal",
        f"R$ {saldo_fixo:,.2f}",
        delta_color="inverse" if saldo_fixo < 0 else "normal"
    )

    col4.metric("🎯 Progresso Sonhos", f"{progresso_sonhos:.1f}%")

    st.divider()

    # ================= COMPOSIÇÃO =================
    st.subheader("📊 Composição Financeira do Mês")

    df_comp = pd.DataFrame({
        "tipo": ["Receitas Fixas", "Despesas Fixas", "Saldo Variável"],
        "valor": [receitas_fixas, despesas_fixas, saldo_variavel]
    })

    fig_comp = px.bar(
        df_comp,
        x="tipo",
        y="valor",
        text="valor",
        color="tipo"
    )

    fig_comp.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()

    # ================= PROJEÇÃO =================
    st.subheader("🚀 Projeção de Patrimônio")

    if not df_projecao.empty:
        fig = px.line(
            df_projecao,
            x="data",
            y="patrimonio",
            title="Evolução do Patrimônio",
            markers=True
        )

        fig.add_hline(
            y=meta_patrimonio,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Meta: R$ {meta_patrimonio:,.0f}",
            annotation_position="top left"
        )

        meta_df = df_projecao[df_projecao["meta_atingida"]]

        if not meta_df.empty:
            data_meta = meta_df.iloc[0]["data"]

            # Garantir datetime puro
            data_meta = pd.to_datetime(data_meta)

            # Linha vertical (shape)
            fig.add_shape(
                type="line",
                x0=data_meta,
                x1=data_meta,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(
                    color="green",
                    width=2,
                    dash="dot"
                )
            )

            # Texto separado (annotation)
            fig.add_annotation(
                x=data_meta,
                y=1,
                xref="x",
                yref="paper",
                text=f"Meta atingida em {data_meta.strftime('%m/%Y')}",
                showarrow=False,
                yanchor="bottom",
                font=dict(color="green")
            )

        fig.update_layout(
            height=450,
            yaxis_title="Patrimônio (R$)",
            xaxis_title="data",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        ultimo = df_projecao.iloc[-1]
        meses_proj = len(df_projecao)

        colp1, colp2, colp3 = st.columns(3)

        tempo_formatado = formatar_tempo_meses(meses_proj)
        colp1.metric("📅 Horizonte da Projeção", tempo_formatado)
        colp2.metric("📈 Patrimônio Projetado", f"R$ {ultimo['patrimonio']:,.2f}")

        if ultimo["meta_atingida"]:
            colp3.metric(
                "🎯 Meta Atingida em",
                meta_df.iloc[0]["data"].strftime("%m/%Y")
            )
        else:
            colp3.metric("🎯 Meta", "Ainda não atingida")

    else:
        st.caption("Dados insuficientes para projeção.")

            
    
    # ================= SUGESTÃO DE APORTE =================
    st.subheader("🎯 Sugestão para Acelerar a Meta")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        tempo_desejado = st.number_input(
            "Em quantos anos quer atingir a meta?",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )
    
    if meta_patrimonio > patrimonio and tempo_desejado > 0:
        aporte_sugerido, é_viável = calcular_aporte_ideal_para_meta(
            patrimonio_atual=patrimonio,
            meta_patrimonio=meta_patrimonio,
            rendimento_mensal=rendimento_mensal,
            inflacao_mensal=inflacao_mensal,
            tempo_desejado_anos=tempo_desejado
        )
        
        with col_s2:
            st.metric(
                "💰 Aporte Mensal Sugerido",
                f"R$ {aporte_sugerido:,.2f}",
                delta_color="normal" if é_viável else "inverse"
            )
        
        with col_s3:
            if é_viável:
                st.success("✅ Meta viável com este aporte")
            else:
                st.warning("⚠️ Aporte muito alto - ajuste o prazo")
        
        # Comparação com saldo atual
        diferenca = aporte_sugerido - saldo_fixo
        if diferenca > 0:
            st.info(
                f"📊 Para atingir em **{tempo_desejado} anos**, você precisa guardar "
                f"**R$ {diferenca:,.2f} a mais por mês** "
                f"(atualmente guarda R$ {saldo_fixo:,.2f})"
            )
        else:
            st.success(
                f"🎉 Você já guarda o suficiente! Pode atingir a meta em "
                f"menos de {tempo_desejado} anos."
            )

            st.divider()
# =========================================================
# 🏷️ CATEGORIAS
# =========================================================

elif menu == "🏷️ CATEGORIAS":

    st.title("🏷️ Gestão de Categorias")
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

    # ---------------- CRIAR CATEGORIA ----------------
    st.subheader("➕ Nova Categoria")

    with st.form("form_categoria", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

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

# =========================================================
# ⚙️ CONFIGURAÇÕES
# =========================================================


elif menu == "⚙️ CONFIGURAÇÕES":

    st.title("⚙️ Configurações do Sistema")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None

    with st.form("form_config", clear_on_submit=False):

        col1, col2 = st.columns(2)

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
# 📄 RELATÓRIO EXECUTIVO
# =========================================================

elif menu == "📄 RELATÓRIO EXECUTIVO":

    st.title("📄 Relatório Financeiro Executivo")
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None
    st.caption("Visão consolidada para tomada de decisão")

    st.divider()

    st.subheader("📌 Resumo Executivo")

    col1, col2, col3, col4 = st.columns(4)

    # ================= RESUMO EXECUTIVO =================

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

    col1.metric(
        "💰 Patrimônio Atual",
        f"R$ {patrimonio:,.2f}"
    )

    col2.metric(
        "📈 Resultado do Mês",
        f"R$ {variacao_mensal:,.2f}",
        delta=f"{(variacao_mensal / patrimonio * 100):.1f}%" if patrimonio > 0 else None,
        delta_color="inverse" if variacao_mensal < 0 else "normal"
    )

    col3.metric(
        "🏢 Saldo Fixo",
        f"R$ {saldo_fixo:,.2f}",
        delta_color="inverse" if saldo_fixo < 0 else "normal"
    )

    col4.metric(
        "🎯 Status da Meta",
        f"{perc_meta:.1f}% • {status_meta}"
    )

    st.divider()


    st.subheader("📊 Diagnóstico do Mês")
    # ================= DIAGNÓSTICO =================

    if saldo_variavel < 0 and saldo_fixo < 0:
        diagnostico = "🔴 Mês financeiramente negativo. Atenção imediata ao controle de gastos."
    elif saldo_variavel < 0:
        diagnostico = "🟡 Gastos variáveis acima do esperado. Revisar despesas não recorrentes."
    elif saldo_fixo < 0:
        diagnostico = "🟠 Estrutura fixa deficitária. Ajuste de receitas ou redução de custos."
    else:
        diagnostico = "🟢 Fluxo financeiro saudável neste mês."

    if "🟢" in diagnostico:
        st.caption(diagnostico)
    else:
        st.caption(diagnostico)

    st.divider()

    st.subheader("🚀 Projeção e Cenário Base")
    # ================= PROJEÇÃO EXECUTIVA =================

    if not df_projecao.empty:
        ultimo = df_projecao.iloc[-1]
        meses_ate_meta = len(df_projecao)

        texto_proj = (
            f"📈 Mantido o cenário atual, o patrimônio projetado é de "
            f"R$ {ultimo['patrimonio']:,.2f} em aproximadamente "
            f"{meses_ate_meta} meses."
        )

        if ultimo["meta_atingida"]:
            texto_proj += " 🎯 A meta será atingida dentro do horizonte projetado."
        else:
            texto_proj += " ⚠️ A meta não será atingida sem ajustes no plano."

        st.caption(texto_proj)
    else:
        st.caption("Projeção indisponível por falta de dados.")

    st.divider()

    st.subheader("⚠️ Alertas & Recomendações")

    st.divider()
    st.subheader("📝 Análise Executiva Consolidada")

    texto_exec = gerar_texto_executivo(
        patrimonio=patrimonio,
        saldo_variavel=saldo_variavel,
        saldo_fixo=saldo_fixo,
        perc_meta=perc_meta,
        status_meta=status_meta,
        df_projecao=df_projecao
    )

    st.write(texto_exec)

    # ================= Recomendação Estratégica =================

    st.subheader("💡 Recomendação Estratégica")
    
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
        
        col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        
        with col_r1:
            st.metric(f"Prazo", f"{prazo} anos")
        
        with col_r2:
            if viavel:
                st.success(f"💰 Aporte mensal: R$ {aporte:,.2f}")
            else:
                st.error(f"💰 Aporte mensal: R$ {aporte:,.2f} (inviável)")
        
        with col_r3:
            diferenca = aporte - saldo_fixo
            if diferenca > 0:
                st.caption(f"+R$ {diferenca:,.2f}/mês")
            else:
                st.caption("✓ Dentro do atual")



    # ================= ALERTAS =================

    alertas = []

    if saldo_variavel < 0:
        alertas.append("⚠️ Despesas variáveis superaram receitas no mês.")

    if saldo_fixo < 0:
        alertas.append("⚠️ Estrutura fixa está consumindo patrimônio.")

    if perc_meta < 50:
        alertas.append("⚠️ Patrimônio distante da meta definida.")

    if not alertas:
        st.caption("✅ Nenhum alerta crítico identificado.")
    else:
        for alerta in alertas:
            st.error(alerta)

    st.divider()
    st.subheader("🧮 Simulador de Cenários")

    st.caption("Simule ajustes financeiros e veja o impacto no patrimônio ao longo do tempo.")

    with st.expander("⚙️ Configurar cenário de simulação"):
        col1, col2 = st.columns(2)

        with col1:
            aporte_extra = st.number_input(
                "➕ Aporte mensal adicional (R$)",
                min_value=0.0,
                step=100.0,
                value=0.0
            )

        with col2:
            ajuste_despesas = st.slider(
                "📉 Redução das despesas fixas (%)",
                min_value=0,
                max_value=50,
                value=0,
                step=5
            )




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

    st.divider()
    st.subheader("📊 Comparação de Cenários")

    if not df_projecao.empty and not df_projecao_simulada.empty:

        meses_base = len(df_projecao)
        meses_simulado = len(df_projecao_simulada)

        ganho_tempo = meses_base - meses_simulado

        colc1, colc2, colc3 = st.columns(3)

        colc1.metric(
            "⏱️ Tempo até Meta (Atual)",
            f"{meses_base} meses"
        )

        colc2.metric(
            "🚀 Tempo até Meta (Simulado)",
            f"{meses_simulado} meses",
            delta=f"-{ganho_tempo} meses" if ganho_tempo > 0 else None
        )

        colc3.metric(
            "💡 Impacto Mensal",
            f"R$ {saldo_fixo_simulado - saldo_fixo:,.2f}"
        )
    else:
        st.caption("Simulação indisponível.")


    st.divider()
    st.subheader("📈 Evolução do Patrimônio — Cenários Comparados")

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
        markers=True,
        title="Comparação de Crescimento Patrimonial"
    )

    # Linha da meta
    fig_comp.add_hline(
        y=meta_patrimonio,
        line_dash="dash",
        line_color="red",
        annotation_text="Meta",
        annotation_position="top left"
    )

    fig_comp.update_layout(
        height=450,
        yaxis_title="Patrimônio (R$)",
        xaxis_title="data",
        hovermode="x unified"
    )

    st.plotly_chart(fig_comp, use_container_width=True)


# =========================================================
# GERADOR DE PDF
# =========================================================



    st.divider()
    st.subheader("📥 Exportar Relatório")

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
        file_name="relatorio_financeiro_executivo.html",
        mime="text/html"
    )


    # =========================================================
    # 🗂️ CONTROLE DO RELATÓRIO MENSAL
    # =========================================================

    st.divider()
    st.subheader("🗂️ Controle do Relatório Mensal")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar como Rascunho"):
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
                st.caption(msg)
            else:
                st.caption(msg)

    with col2:
        if st.button("🔒 Finalizar Mês"):
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

            st.caption(msg) if ok else st.error(msg)

    # =========================================================
    # 📜 RELATÓRIOS ANTERIORES
    # =========================================================

    if not dados.get("relatorios_historicos", pd.DataFrame()).empty:
        st.divider()
        st.subheader("📜 Relatórios Anteriores")


        df_hist = dados.get("relatorios_historicos", pd.DataFrame()).copy()

        # 🔒 blindagem de schema
        for col in ["mes", "status", "patrimonio", "saldo_fixo", "saldo_variavel", "perc_meta"]:
            if col not in df_hist.columns:
                df_hist[col] = None

        df_hist = dados["relatorios_historicos"].sort_values("mes", ascending=False)

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
            }),
            use_container_width=True
        )

# =========================================================
# PLACEHOLDERS (não quebram)
# =========================================================
else:
    st.title(menu)
    if st.session_state.get("msg"):
        if st.session_state.get("msg_tipo") == "error":
            st.error(st.session_state["msg"])
        elif st.session_state.get("msg_tipo") == "warning":
            st.warning(st.session_state["msg"])
        else:
            st.success(st.session_state["msg"])

        st.session_state["msg"] = None
    st.caption("🚧 Esta aba será finalizada nos próximos blocos.")



