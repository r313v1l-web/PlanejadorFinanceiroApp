import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px

from database import DatabaseManager
from dateutil.relativedelta import relativedelta

import io
import bcrypt





# =========================================================
# AUTENTICAÇÃO
# =========================================================

def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha")

    
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

            novo = pd.DataFrame([{
                "usuario": novo_usuario,
                "senha": senha_hash,
                "nome": novo_nome,
                "perfil": novo_perfil,
                "ativo": "ativo"   # 🔥 PADRÃO DO SEU SISTEMA
            }])

            df = pd.concat([df, novo], ignore_index=True)
            DatabaseManager.save_users(df)
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
                "Status",
                ["ativo", "inativo"],
                index=0 if row["ativo"] == "ativo" else 1,
                key=f"ativo_{row['usuario']}"
            )

    if st.button("💾 Salvar Alterações"):
        for usuario, nova_senha in senhas_para_reset.items():
            idx = df_edit[df_edit["usuario"] == usuario].index[0]
            df_edit.at[idx, "senha"] = bcrypt.hashpw(
                nova_senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

        DatabaseManager.save_users(df_edit)
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

    df_hist = dados.get("relatorios_historicos", pd.DataFrame())

    # Se já existe FINALIZADO, não permite sobrescrever
    if not df_hist.empty:
        existente = df_hist[df_hist["Mes"] == mes_ref]
        if not existente.empty and "Finalizado" in existente["Status"].values:
            return False, "Relatório já finalizado para este mês."

    novo = pd.DataFrame([{
        "Mes": mes_ref,
        "Patrimonio": patrimonio,
        "Saldo_Fixo": saldo_fixo,
        "Saldo_Variavel": saldo_variavel,
        "Perc_Meta": perc_meta,
        "Texto_Executivo": texto_exec,
        "Status": status
    }])

    # Remove rascunho anterior do mesmo mês
    df_hist = df_hist[df_hist["Mes"] != mes_ref]

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
    page_title="Family Wealth Manager Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "usuario" not in st.session_state:
    st.session_state["usuario"] = "default"

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
patrimonio = dados["investimentos"]["Valor_Atual"].sum() if not dados["investimentos"].empty else 0

# ---------------- HISTÓRICO (VARIÁVEL) ----------------
if not dados["historico"].empty:
    hist = dados["historico"].copy()
    hist["Data"] = pd.to_datetime(hist["Data"])
    hist["Mes"] = hist["Data"].dt.strftime("%Y-%m")
    hist_mes = hist[hist["Mes"] == mes_atual]

    receitas_variaveis = hist_mes[hist_mes["Tipo"] == "Receita"]["Valor"].sum()
    despesas_variaveis = hist_mes[hist_mes["Tipo"] == "Despesa"]["Valor"].sum()
else:
    receitas_variaveis = despesas_variaveis = 0


# ---------------- CONTROLE DE GASTOS (DESPESA VARIÁVEL) ----------------
if not dados.get("controle_gastos", pd.DataFrame()).empty:
    gastos_rapidos_mes = dados["controle_gastos"]["Valor"].sum()
else:
    gastos_rapidos_mes = 0


# ---------------- SALDO VARIÁVEL FINAL ----------------
saldo_variavel = receitas_variaveis - despesas_variaveis - gastos_rapidos_mes

# ---------------- FLUXO FIXO ----------------
if not dados["fluxo_fixo"].empty:
    receitas_fixas = dados["fluxo_fixo"][dados["fluxo_fixo"]["Tipo"] == "Receita"]["Valor"].sum()
    despesas_fixas = dados["fluxo_fixo"][dados["fluxo_fixo"]["Tipo"] == "Despesa"]["Valor"].sum()
    saldo_fixo = receitas_fixas - despesas_fixas
else:
    receitas_fixas = despesas_fixas = saldo_fixo = 0

# ---------------- SONHOS ----------------
if not dados["sonhos_projetos"].empty:
    total_sonhos = dados["sonhos_projetos"]["Valor_Alvo"].sum()
    total_atual = dados["sonhos_projetos"]["Valor_Atual"].sum()
    progresso_sonhos = (total_atual / total_sonhos * 100) if total_sonhos > 0 else 0
else:
    total_sonhos = total_atual = progresso_sonhos = 0



# =========================================================
# CONFIGURAÇÕES (BLOCO 4)
# =========================================================

config_dict = {}

if not dados["config"].empty:
    for _, row in dados["config"].iterrows():
        config_dict[row["Chave"]] = row["Valor"]

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
            "Data": data_ref,
            "Patrimonio": patrimonio,
            "Rendimento": rendimento,
            "Aporte_Fixo": saldo_fixo_mensal if i > 0 else 0,
            "Meta_Atingida": patrimonio >= meta_patrimonio
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

        if ultimo["Meta_Atingida"]:
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
            data = st.date_input("Data", date.today())
            tipo = st.selectbox("Tipo", ["Despesa", "Receita", "Investimento"])

        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
            categoria = st.selectbox(
                "Categoria",
                dados["categorias"]["Nome"].tolist() if not dados["categorias"].empty else []
            )

        with col3:
            responsavel = st.radio("Responsável", ["Reinaldo", "Raquel", "Compartilhado"], horizontal=True)
            fixo = st.checkbox("Recorrente")

        descricao = st.text_input("Descrição")

        submitted = st.form_submit_button("💾 SALVAR")

        if submitted:
            nova = pd.DataFrame([{
                "Data": data,
                "Tipo": tipo,
                "Valor": valor,
                "Categoria": categoria,
                "Subcategoria": "",
                "Descricao": descricao,
                "Responsavel": responsavel,
                "Fixo": "Sim" if fixo else "Não"
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

    # ---------------- HISTÓRICO ----------------
    st.subheader("📋 Histórico")

    if not dados["historico"].empty:
        df_hist = dados["historico"].copy()
        df_hist["Data"] = pd.to_datetime(df_hist["Data"])

        st.dataframe(
            df_hist.sort_values("Data", ascending=False).style.format({
                "Valor": "R$ {:,.2f}"
            }),
            use_container_width=True,
            height=450
        )
    else:
        st.caption("Nenhuma transação registrada.")

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
    total = dados["investimentos"]["Valor_Atual"].sum() if not dados["investimentos"].empty else 0
    st.metric("Total Investido", f"R$ {total:,.2f}")

    st.divider()

    # ---------------- TABELA ----------------
    if not dados["investimentos"].empty:
        st.dataframe(
            dados["investimentos"].style.format({
                "Valor_Atual": "R$ {:,.2f}",
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
            values="Valor_Atual",
            names="Categoria",
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
                    "Tipo",
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
                    "Tipo": tipo,
                    "Valor_Atual": valor_atual,
                    "Data_Entrada": data_entrada,
                    "Rendimento_Mensal": rendimento,
                    "Categoria": categoria,
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
        total_alvo = dados["sonhos_projetos"]["Valor_Alvo"].sum()
        total_atual = dados["sonhos_projetos"]["Valor_Atual"].sum()
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

            st.subheader(sonho["Nome"])
            st.caption(sonho.get("Descricao", ""))

            progresso = sonho["Valor_Atual"] / sonho["Valor_Alvo"] if sonho["Valor_Alvo"] > 0 else 0
            st.progress(progresso, text=f"R$ {sonho['Valor_Atual']:,.0f} / R$ {sonho['Valor_Alvo']:,.0f}")

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.caption(f"📅 {sonho['Data_Alvo']}")
            col_s2.caption(f"🔸 {sonho['Prioridade']}")
            col_s3.caption(f"📊 {sonho['Status']}")

            # --- adicionar valor ---
            with st.form(f"form_add_{i}", clear_on_submit=True):
                valor_add = st.number_input("Adicionar valor", min_value=0.0, step=100.0)
                if st.form_submit_button("💸 Adicionar"):
                    dados["sonhos_projetos"].loc[i, "Valor_Atual"] += valor_add
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
                    "Categoria",
                    ["Viagem", "Automóvel", "Reserva", "Imóvel", "Educação", "Outros"]
                )

            with col2:
                data_alvo = st.date_input("Data Alvo", date.today() + timedelta(days=365))
                prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
                valor_inicial = st.number_input("Valor Inicial (R$)", min_value=0.0, step=500.0)

            descricao = st.text_area("Descrição")

            if st.form_submit_button("🎯 Criar Sonho"):
                novo = pd.DataFrame([{
                    "Nome": nome,
                    "Descricao": descricao,
                    "Valor_Alvo": valor_alvo,
                    "Valor_Atual": valor_inicial,
                    "Data_Alvo": data_alvo,
                    "Prioridade": prioridade,
                    "Status": "Em Andamento",
                    "Categoria": categoria
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

    receitas = dados["fluxo_fixo"][dados["fluxo_fixo"]["Tipo"] == "Receita"]
    despesas = dados["fluxo_fixo"][dados["fluxo_fixo"]["Tipo"] == "Despesa"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas Fixas", f"R$ {receitas['Valor'].sum():,.2f}")
    col2.metric("Despesas Fixas", f"R$ {despesas['Valor'].sum():,.2f}")
    col3.metric("Saldo Fixo", f"R$ {(receitas['Valor'].sum() - despesas['Valor'].sum()):,.2f}")

    st.divider()

    tab1, tab2 = st.tabs(["📈 Receitas", "📉 Despesas"])

    with tab1:
        st.dataframe(
            receitas.style.format({"Valor": "R$ {:,.2f}"}),
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            despesas.style.format({"Valor": "R$ {:,.2f}"}),
            use_container_width=True
        )

    # ---------------- NOVO FLUXO ----------------
    with st.expander("➕ Adicionar Fluxo Fixo"):
        with st.form("form_fluxo", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome")
                valor = st.number_input("Valor Mensal (R$)", min_value=0.0, step=10.0)
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"])

            with col2:
                categoria = st.selectbox(
                    "Categoria",
                    dados["categorias"]["Nome"].tolist() if not dados["categorias"].empty else []
                )
                recorrencia = st.selectbox(
                    "Recorrência",
                    ["Mensal", "Anual", "Trimestral", "Semestral"]
                )

            data_inicio = st.date_input("Data de Início", date.today())
            data_fim = st.date_input("Data de Fim (opcional)", value=None)
            observacao = st.text_area("Observações")

            if st.form_submit_button("💾 Salvar Fluxo"):
                novo = pd.DataFrame([{
                    "Nome": nome,
                    "Valor": valor,
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Data_Inicio": data_inicio,
                    "Data_Fim": data_fim,
                    "Recorrencia": recorrencia,
                    "Observacao": observacao
                }])

                df_fluxo = dados["fluxo_fixo"].copy()
                df_fluxo = pd.concat([df_fluxo, novo], ignore_index=True)

                dados["fluxo_fixo"] = df_fluxo
                st.session_state["dados"] = dados
                DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)

                st.session_state["msg"] = "Fluxo fixo adicionado com sucesso."
                st.rerun()
    st.divider()
    st.subheader("🗑️ Excluir Fluxo Fixo")

    if not dados["fluxo_fixo"].empty:

        df_fluxo = dados["fluxo_fixo"].copy()
        df_fluxo["Label"] = (
            df_fluxo["Nome"] + " | " +
            df_fluxo["Tipo"] + " | R$ " +
            df_fluxo["Valor"].astype(str)
        )

        fluxo_sel = st.selectbox(
            "Selecione o fluxo para excluir",
            df_fluxo["Label"].tolist()
        )

        if st.button("❌ Excluir Fluxo Selecionado"):
            idx = df_fluxo[df_fluxo["Label"] == fluxo_sel].index[0]
            df_fluxo = df_fluxo.drop(idx)

            DatabaseManager.save("fluxo_fixo", df_fluxo, usuario)

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
        df_gastos = pd.DataFrame(columns=["Data", "Descricao", "Valor"])
    else:
        df_gastos = dados["controle_gastos"].copy()

    gasto_total = df_gastos["Valor"].sum() if not df_gastos.empty else 0
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
            descricao = st.text_input("Descrição", placeholder="Padaria, café, lanche...")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=1.0)

        if st.form_submit_button("💸 Registrar Gasto"):
            novo = pd.DataFrame([{
                "Data": date.today(),
                "Descricao": descricao,
                "Valor": valor
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
            df_gastos.sort_values("Data", ascending=False).style.format({
                "Valor": "R$ {:,.2f}"
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
        "Tipo": ["Receitas Fixas", "Despesas Fixas", "Saldo Variável"],
        "Valor": [receitas_fixas, despesas_fixas, saldo_variavel]
    })

    fig_comp = px.bar(
        df_comp,
        x="Tipo",
        y="Valor",
        text="Valor",
        color="Tipo"
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
            x="Data",
            y="Patrimonio",
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

        meta_df = df_projecao[df_projecao["Meta_Atingida"]]

        if not meta_df.empty:
            data_meta = meta_df.iloc[0]["Data"]

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
            xaxis_title="Data",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        ultimo = df_projecao.iloc[-1]
        meses_proj = len(df_projecao)

        colp1, colp2, colp3 = st.columns(3)

        colp1.metric("📅 Horizonte da Projeção", f"{meses_proj} meses")
        colp2.metric("📈 Patrimônio Projetado", f"R$ {ultimo['Patrimonio']:,.2f}")

        if ultimo["Meta_Atingida"]:
            colp3.metric(
                "🎯 Meta Atingida em",
                meta_df.iloc[0]["Data"].strftime("%m/%Y")
            )
        else:
            colp3.metric("🎯 Meta", "Ainda não atingida")

    else:
        st.caption("Dados insuficientes para projeção.")


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
        df_cat = pd.DataFrame(columns=["Nome", "Tipo", "Ativa"])
    else:
        df_cat = dados["categorias"].copy()

    # ---------------- LISTA ----------------
    st.subheader("📋 Categorias Cadastradas")

    if not df_cat.empty:
        st.dataframe(
            df_cat.style.applymap(
                lambda x: "color: gray;" if x is False else "",
                subset=["Ativa"]
            ),
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
                "Tipo",
                ["Despesa Variável", "Despesa Fixa", "Receita"]
            )

        with col3:
            ativa = st.checkbox("Ativa", value=True)

        submitted = st.form_submit_button("💾 Criar Categoria")

        if submitted:
            if nome.strip() == "":
                st.error("Informe o nome da categoria.")
            elif not df_cat[df_cat["Nome"].str.lower() == nome.lower()].empty:
                st.error("Categoria já existe.")
            else:
                nova = pd.DataFrame([{
                    "Nome": nome,
                    "Tipo": tipo,
                    "Ativa": ativa
                }])

                df_cat = pd.concat([df_cat, nova], ignore_index=True)
                dados["categorias"] = df_cat
                st.session_state["dados"] = dados
                DatabaseManager.save("categorias", df_cat, usuario)
                st.session_state["msg"] = "Salvo"
                st.session_state["msg_tipo"] = "success"
                st.rerun()

    st.divider()

    # ---------------- ATIVAR / DESATIVAR ----------------
    st.subheader("🔁 Ativar / Desativar Categoria")

    if not df_cat.empty:
        categoria_sel = st.selectbox(
            "Selecione a categoria",
            df_cat["Nome"].tolist()
        )

        status_atual = df_cat.loc[df_cat["Nome"] == categoria_sel, "Ativa"].values[0]

        if st.button("🔄 Alternar Status"):
            df_cat.loc[df_cat["Nome"] == categoria_sel, "Ativa"] = not status_atual
            dados["categorias"] = df_cat
            st.session_state["dados"] = dados
            DatabaseManager.save("categorias", df_cat, usuario)

            st.caption(
                f"Categoria {'ativada' if not status_atual else 'desativada'} com sucesso."
            )
            st.rerun()

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
                {"Chave": "meta_patrimonio", "Valor": meta, "Descricao": "Meta total de patrimônio"},
                {"Chave": "orcamento_mensal", "Valor": orcamento, "Descricao": "Orçamento mensal"},
                {"Chave": "nome_familia", "Valor": nome, "Descricao": "Nome da família"},
                {"Chave": "rendimento_mensal", "Valor": rendimento, "Descricao": "Rendimento mensal"},
                {"Chave": "inflacao_mensal", "Valor": inflacao, "Descricao": "Inflação mensal"},
                {"Chave": "reserva_gastos", "Valor": reserva, "Descricao": "Reserva mensal de gastos rápidos"}

            ])

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
            f"R$ {ultimo['Patrimonio']:,.2f} em aproximadamente "
            f"{meses_ate_meta} meses."
        )

        if ultimo["Meta_Atingida"]:
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
        x="Data",
        y="Patrimonio",
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
        xaxis_title="Data",
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

        df_hist = dados["relatorios_historicos"].sort_values("Mes", ascending=False)

        st.dataframe(
            df_hist[[
                "Mes",
                "Patrimonio",
                "Saldo_Fixo",
                "Saldo_Variavel",
                "Perc_Meta",
                "Status"
            ]].style.format({
                "Patrimonio": "R$ {:,.2f}",
                "Saldo_Fixo": "R$ {:,.2f}",
                "Saldo_Variavel": "R$ {:,.2f}",
                "Perc_Meta": "{:.1f}%"
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



