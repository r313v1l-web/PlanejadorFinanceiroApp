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
# FUNÇÕES DO SEU CÓDIGO ORIGINAL (MANTIDAS)
# =========================================================
def normalizar_df(df):
    if df is None or df.empty:
        return df
    df.columns = df.columns.str.lower()
    return df

def tela_login():
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    df_users = DatabaseManager.load_users()
    
    if st.button("Entrar"):
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
        st.success("Login realizado com sucesso.")
        st.rerun()

def tela_admin_usuarios():
    st.title("👥 Gestão de Usuários")
    df = DatabaseManager.load_users()
    
    # CRIAR NOVO USUÁRIO
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
            
            DatabaseManager.create_user(
                novo_usuario, novo_nome, senha_hash, novo_perfil
            )
            st.success("Usuário criado com sucesso.")
            st.rerun()
    
    st.divider()
    st.subheader("Usuários Existentes")
    
    # EDIÇÃO DOS USUÁRIOS
    senhas_para_reset = {}
    df_edit = df.copy()
    
    for i, row in df_edit.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.write(f"**{row['usuario']}** ({row['nome']})")
        with col2:
            nova_senha = st.text_input(
                "Nova Senha", type="password", key=f"senha_{row['usuario']}"
            )
            if nova_senha:
                senhas_para_reset[row["usuario"]] = nova_senha
                st.warning("Senha será atualizada ao salvar.")
        with col3:
            df_edit.at[i, "perfil"] = st.selectbox(
                "Perfil", ["user", "admin"], 
                index=0 if row["perfil"] == "user" else 1,
                key=f"perfil_{row['usuario']}"
            )
        with col4:
            df_edit.at[i, "ativo"] = st.selectbox(
                "status", ["ativo", "inativo"], 
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
                    usuario=row["usuario"], senha_hash=senha_hash
                )
        st.success("Usuários atualizados.")
        st.rerun()

def salvar_relatorio_mensal(dados, patrimonio, saldo_fixo, saldo_variavel, perc_meta, texto_exec, status="Rascunho"):
    mes_ref = date.today().strftime("%Y-%m")
    df_hist = dados.get("relatorios_historicos", pd.DataFrame()).copy()
    
    # Blindagem de colunas
    if "mes" not in df_hist.columns:
        df_hist["mes"] = ""
    if "status" not in df_hist.columns:
        df_hist["status"] = ""
    
    # Se já existe FINALIZADO, não permite sobrescrever
    existente = df_hist[
        (df_hist["mes"] == mes_ref) & (df_hist["status"] == "Finalizado")
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

def gerar_texto_executivo(patrimonio, saldo_variavel, saldo_fixo, perc_meta, status_meta, df_projecao):
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
        texto.append("O cenário geral é positivo, com foco recomendado em disciplina e consistência.")
    elif perc_meta >= 50:
        texto.append("O cenário é intermediário, exigindo atenção estratégica para aceleração do plano.")
    else:
        texto.append("O cenário requer ações corretivas estruturais para evitar distanciamento da meta.")
    
    return " ".join(texto)

# =========================================================
# NOVAS FUNÇÕES COM BOOTSTRAP
# =========================================================
def setup_bootstrap():
    """Configura Bootstrap 5 e CSS customizado"""
    
    st.markdown("""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Family Wealth Manager Pro</title>
            
            <!-- Bootstrap 5 CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css" rel="stylesheet">
            
            <!-- Google Fonts -->
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            
            <!-- Custom CSS -->
            <link href="assets/css/finance-dashboard.css" rel="stylesheet">
            
            <style>
                /* Overrides para Streamlit */
                .stApp {
                    font-family: 'Inter', sans-serif;
                    background-color: #f8fafc;
                }
                
                .main .block-container {
                    padding-top: 0;
                    padding-bottom: 0;
                    max-width: 100%;
                }
                
                /* Esconde sidebar original do Streamlit */
                [data-testid="stSidebar"] {
                    display: none;
                }
                
                /* Customiza botões do Streamlit */
                .stButton > button {
                    border-radius: 0.75rem;
                    font-weight: 600;
                    border: none;
                    transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .stButton > button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
                }
                
                /* Customiza inputs */
                .stTextInput > div > div > input {
                    border-radius: 0.75rem;
                    border: 2px solid #e2e8f0;
                    padding: 0.75rem 1rem;
                    font-size: 0.875rem;
                }
                
                .stSelectbox > div > div > select {
                    border-radius: 0.75rem;
                    border: 2px solid #e2e8f0;
                    padding: 0.75rem 1rem;
                    font-size: 0.875rem;
                }
                
                /* Remove margens padrão do Streamlit */
                .st-emotion-cache-1r6slb0 {
                    padding: 0;
                }
            </style>
        </head>
        <body>
    """, unsafe_allow_html=True)

def render_navbar():
    """Renderiza navbar premium"""
    
    user_name = st.session_state.get("nome", "Usuário")
    user_profile = st.session_state.get("perfil", "user").capitalize()
    user_initials = user_name[0].upper() if user_name else "U"
    
    navbar_html = f"""
        <nav class="navbar navbar-expand-lg navbar-finance">
            <div class="container-fluid">
                <!-- Brand Logo -->
                <a class="navbar-brand" href="#">
                    <i class="bi bi-gem navbar-brand-icon"></i>
                    <span class="d-none d-md-inline">Wealth Manager</span>
                </a>
                
                <!-- Main Navigation -->
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav mx-auto">
                        <li class="nav-item">
                            <a class="nav-link active" href="#" onclick="window.location.href='?page=dashboard'">
                                <i class="bi bi-speedometer2"></i>
                                <span class="d-none d-md-inline">Dashboard</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="window.location.href='?page=investimentos'">
                                <i class="bi bi-graph-up"></i>
                                <span class="d-none d-md-inline">Investimentos</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="window.location.href='?page=sonhos'">
                                <i class="bi bi-stars"></i>
                                <span class="d-none d-md-inline">Sonhos</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="window.location.href='?page=fluxo'">
                                <i class="bi bi-arrow-left-right"></i>
                                <span class="d-none d-md-inline">Fluxo</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="window.location.href='?page=relatorios'">
                                <i class="bi bi-file-earmark-text"></i>
                                <span class="d-none d-md-inline">Relatórios</span>
                            </a>
                        </li>
                        {'''<li class="nav-item">
                            <a class="nav-link" href="#" onclick="window.location.href='?page=admin'">
                                <i class="bi bi-shield-check"></i>
                                <span class="d-none d-md-inline">Admin</span>
                            </a>
                        </li>''' if st.session_state.get("perfil") == "admin" else ""}
                    </ul>
                    
                    <!-- User Menu -->
                    <div class="dropdown">
                        <a href="#" class="d-flex align-items-center text-white text-decoration-none dropdown-toggle" 
                           data-bs-toggle="dropdown">
                            <div class="avatar me-2">{user_initials}</div>
                            <div class="d-none d-md-block">
                                <strong>{user_name}</strong>
                                <small class="d-block opacity-75">{user_profile}</small>
                            </div>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end user-dropdown">
                            <li class="user-dropdown-header">
                                <div class="d-flex align-items-center">
                                    <div class="avatar-lg me-3">{user_initials}</div>
                                    <div>
                                        <h6 class="mb-0">{user_name}</h6>
                                        <small class="text-muted">{user_profile}</small>
                                    </div>
                                </div>
                            </li>
                            <li><a class="user-dropdown-item" href="#" onclick="window.location.href='?page=perfil'">
                                <i class="bi bi-person"></i>Meu Perfil
                            </a></li>
                            <li><a class="user-dropdown-item" href="#" onclick="window.location.href='?page=config'">
                                <i class="bi bi-gear"></i>Configurações
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="user-dropdown-item text-danger" href="#" onclick="logout()">
                                <i class="bi bi-box-arrow-right"></i>Sair
                            </a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>
        
        <script>
        function logout() {{
            // Remove session state via URL parameter
            window.location.href = '?logout=true';
        }}
        </script>
    """
    
    st.markdown(navbar_html, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza sidebar luxury"""
    
    sidebar_html = """
        <!-- Sidebar -->
        <div class="sidebar-luxury">
            <div class="sidebar-header">
                <h5 class="text-white mb-0">MENU PRINCIPAL</h5>
            </div>
            
            <nav class="mt-4">
                <h6 class="sidebar-title">DASHBOARD</h6>
                <ul class="sidebar-menu">
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link active" onclick="window.location.href='?page=dashboard'">
                            <i class="bi bi-house"></i>
                            <span>Visão Geral</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=analytics'">
                            <i class="bi bi-bar-chart"></i>
                            <span>Análises</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=performance'">
                            <i class="bi bi-trophy"></i>
                            <span>Performance</span>
                        </a>
                    </li>
                </ul>
                
                <h6 class="sidebar-title mt-4">GESTÃO</h6>
                <ul class="sidebar-menu">
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=investimentos'">
                            <i class="bi bi-piggy-bank"></i>
                            <span>Carteira</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=transacoes'">
                            <i class="bi bi-cash-stack"></i>
                            <span>Transações</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=categorias'">
                            <i class="bi bi-tags"></i>
                            <span>Categorias</span>
                        </a>
                    </li>
                </ul>
                
                <h6 class="sidebar-title mt-4">PLANEJAMENTO</h6>
                <ul class="sidebar-menu">
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=metas'">
                            <i class="bi bi-flag"></i>
                            <span>Metas</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=orcamento'">
                            <i class="bi bi-wallet2"></i>
                            <span>Orçamento</span>
                        </a>
                    </li>
                    <li class="sidebar-menu-item">
                        <a href="#" class="sidebar-menu-link" onclick="window.location.href='?page=projecoes'">
                            <i class="bi bi-graph-up-arrow"></i>
                            <span>Projeções</span>
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
    """
    
    st.markdown(sidebar_html, unsafe_allow_html=True)

def finance_card(title, value, change, icon, color="primary", subtitle=""):
    """Componente de card financeiro premium"""
    
    colors = {
        "primary": {"class": ""},
        "success": {"class": "success"},
        "danger": {"class": "danger"},
        "warning": {"class": "warning"},
        "premium": {"class": "premium"}
    }
    
    change_class = "positive" if change >= 0 else "negative"
    change_icon = "bi-arrow-up" if change >= 0 else "bi-arrow-down"
    
    return f"""
        <div class="card card-finance {colors.get(color, {}).get('class', '')} h-100">
            <div class="card-body-finance">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="card-icon {colors.get(color, {}).get('class', '')}">
                        <i class="bi {icon}"></i>
                    </div>
                    <span class="card-change {change_class}">
                        <i class="bi {change_icon}"></i>
                        {abs(change):.1f}%
                    </span>
                </div>
                
                <h3 class="card-value">R$ {value:,.2f}</h3>
                <h6 class="text-muted mb-0">{title}</h6>
                {f'<small class="text-muted">{subtitle}</small>' if subtitle else ''}
            </div>
        </div>
    """

def metric_card(title, value, trend, trend_value, icon, color="primary"):
    """Card de métrica compacto"""
    
    trend_class = "trend-up" if trend == "up" else "trend-down"
    trend_icon = "bi-arrow-up" if trend == "up" else "bi-arrow-down"
    
    return f"""
        <div class="metric-card">
            <div class="metric-header">
                <span class="metric-title">{title}</span>
                <i class="bi {icon} text-{color} fs-5"></i>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-trend {trend_class}">
                <i class="bi {trend_icon}"></i>
                <span>{trend_value}</span>
            </div>
        </div>
    """

def create_chart_container(title, chart_id, height=400):
    """Container para gráficos com controles"""
    
    return f"""
        <div class="chart-container">
            <div class="chart-header">
                <h5 class="chart-title">{title}</h5>
                <div class="chart-actions">
                    <button class="btn btn-sm btn-finance-outline" onclick="downloadChart('{chart_id}')">
                        <i class="bi bi-download"></i>
                    </button>
                </div>
            </div>
            <div id="{chart_id}" style="height: {height}px;"></div>
        </div>
    """

# =========================================================
# PÁGINAS DO SISTEMA (ATUALIZADAS)
# =========================================================
def pagina_dashboard_premium(dados):
    """Dashboard com Bootstrap 5 premium"""
    
    # Header da página
    st.markdown("""
        <div class="main-content">
            <!-- Page Header -->
            <div class="content-header">
                <div class="d-flex justify-content-between align-items-end">
                    <div>
                        <h1 class="content-title">📊 Dashboard Financeiro</h1>
                        <p class="content-subtitle">Visão completa da sua saúde financeira e patrimônio</p>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-finance btn-finance-outline" onclick="window.location.href='?page=export'">
                            <i class="bi bi-download me-2"></i>
                            Exportar
                        </button>
                        <button class="btn btn-finance btn-finance-primary" onclick="window.location.href='?page=relatorio'">
                            <i class="bi bi-plus-circle me-2"></i>
                            Novo Relatório
                        </button>
                    </div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    
    # Grid de métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        patrimonio = dados["investimentos"]["valor_atual"].sum() if not dados["investimentos"].empty else 0
        st.markdown(finance_card(
            "Patrimônio Total", 
            patrimonio, 
            12.5, 
            "bi-bank", 
            "primary",
            "Valor consolidado"
        ), unsafe_allow_html=True)
    
    with col2:
        saldo_fixo = calcular_saldo_fixo(dados)
        st.markdown(finance_card(
            "Saldo Fixo", 
            saldo_fixo, 
            8.2, 
            "bi-arrow-left-right", 
            "success" if saldo_fixo >= 0 else "danger",
            "Receitas - Despesas Fixas"
        ), unsafe_allow_html=True)
    
    with col3:
        saldo_variavel = calcular_saldo_variavel(dados)
        st.markdown(finance_card(
            "Saldo Variável", 
            saldo_variavel, 
            -3.1, 
            "bi-graph-up", 
            "warning" if saldo_variavel >= 0 else "danger",
            "Receitas - Despesas Variáveis"
        ), unsafe_allow_html=True)
    
    with col4:
        progresso_sonhos = calcular_progresso_sonhos(dados)
        st.markdown(finance_card(
            "Progresso Sonhos", 
            progresso_sonhos, 
            15.8, 
            "bi-stars", 
            "premium",
            "% das metas alcançadas"
        ), unsafe_allow_html=True)
    
    # Segunda linha - Métricas rápidas
    st.markdown("""
        <div class="row g-3 mb-4">
    """, unsafe_allow_html=True)
    
    metrics = [
        ("Rentabilidade Mensal", "4.8%", "up", "+0.5%", "bi-arrow-up-right", "success"),
        ("Inflação Projetada", "3.2%", "down", "-0.2%", "bi-arrow-down-right", "warning"),
        ("Taxa de Poupança", "28%", "up", "+3%", "bi-percent", "primary"),
        ("Score Financeiro", "A+", "stable", "Excelente", "bi-award", "premium")
    ]
    
    for i, (title, value, trend, trend_value, icon, color) in enumerate(metrics):
        col = st.columns(4)[i % 4]
        with col:
            st.markdown(metric_card(title, value, trend, trend_value, icon, color), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição de investimentos
        if not dados["investimentos"].empty:
            fig = px.pie(
                dados["investimentos"],
                values='valor_atual',
                names='categoria',
                hole=0.4,
                color_discrete_sequence=['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe']
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}'
            )
            fig.update_layout(
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            st.markdown(create_chart_container("Distribuição de Investimentos", "chart1"), unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # Gráfico de evolução patrimonial
        st.markdown(create_chart_container("Evolução Patrimonial", "chart2"), unsafe_allow_html=True)
        
        # Dados de exemplo para o gráfico
        dates = pd.date_range(start='2023-01-01', end='2023-12-01', freq='MS')
        valores = [100000 * (1.02)**i for i in range(len(dates))]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=dates,
            y=valores,
            mode='lines+markers',
            name='Patrimônio',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        fig2.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            yaxis=dict(
                tickformat='R$,.0f',
                gridcolor='rgba(0,0,0,0.05)'
            ),
            xaxis=dict(
                gridcolor='rgba(0,0,0,0.05)'
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
    # Tabela de transações recentes
    st.markdown("""
        <div class="mt-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">🕒 Transações Recentes</h5>
                <button class="btn btn-sm btn-finance-outline" onclick="window.location.href='?page=transacoes'">
                    Ver Todas <i class="bi bi-arrow-right ms-1"></i>
                </button>
            </div>
    """, unsafe_allow_html=True)
    
    if not dados.get("historico", pd.DataFrame()).empty:
        historico_recente = dados["historico"].sort_values('data', ascending=False).head(8)
        
        # Estilizar a tabela com Bootstrap
        st.markdown("""
            <div class="table-responsive">
            <table class="table table-finance">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Descrição</th>
                        <th>Categoria</th>
                        <th class="text-end">Valor</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)
        
        for _, row in historico_recente.iterrows():
            valor_class = "text-success" if row['tipo'] == 'receita' else "text-danger"
            valor_icon = "bi-arrow-up" if row['tipo'] == 'receita' else "bi-arrow-down"
            
            st.markdown(f"""
                <tr>
                    <td>{row['data']}</td>
                    <td>{row['descricao']}</td>
                    <td><span class="badge badge-info">{row.get('categoria', 'Não categorizada')}</span></td>
                    <td class="text-end {valor_class}">
                        <i class="bi {valor_icon} me-1"></i>
                        R$ {row['valor']:,.2f}
                    </td>
                </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </tbody>
            </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="text-center py-5">
                <i class="bi bi-receipt fs-1 text-muted mb-3"></i>
                <p class="text-muted">Nenhuma transação registrada</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Fecha main-content

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

# =========================================================
# FUNÇÃO PRINCIPAL ATUALIZADA
# =========================================================
def main():
    """Função principal integrando Bootstrap"""
    
    # Configuração da página
    st.set_page_config(
        page_title="Gestão Financeira",
        page_icon="💎",
        layout="wide",
        initial_sidebar_state="collapsed"  # Esconde sidebar do Streamlit
    )
    
    # Setup do Bootstrap (sempre executar primeiro)
    setup_bootstrap()
    
    # Controle de login
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    
    # Verifica logout via URL
    if "logout" in st.query_params and st.query_params["logout"] == "true":
        st.session_state["logado"] = False
        st.query_params.clear()
        st.rerun()
    
    if not st.session_state["logado"]:
        # Tela de login estilizada com Bootstrap
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
                <div class="text-center mb-5">
                    <i class="bi bi-gem fs-1 text-primary"></i>
                    <h1 class="mt-3">Family Wealth Manager</h1>
                    <p class="text-muted">Sistema Premium de Gestão Patrimonial</p>
                </div>
                
                <div class="card border-0 shadow-lg">
                    <div class="card-body p-5">
                        <h4 class="card-title text-center mb-4">🔐 Acesso ao Sistema</h4>
            """, unsafe_allow_html=True)
            
            # Usar a função de login original (mas com styling)
            tela_login()
            
            st.markdown("""
                        <div class="text-center mt-4">
                            <small class="text-muted">
                                <i class="bi bi-shield-check"></i>
                                Sistema 100% seguro e criptografado
                            </small>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Bootstrap JS
        st.markdown("""
            <!-- Bootstrap JS Bundle -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
        """, unsafe_allow_html=True)
        
        st.stop()
    
    # =========================================================
    # USUÁRIO LOGADO - RENDERIZAR INTERFACE COMPLETA
    # =========================================================
    
    # Renderizar navbar
    render_navbar()
    
    # Layout principal com sidebar e conteúdo
    col_sidebar, col_content = st.columns([2, 10])
    
    with col_sidebar:
        render_sidebar()
    
    with col_content:
        # Determinar página atual
        current_page = st.query_params.get("page", ["dashboard"])[0]
        
        # Carregar dados
        if "dados" not in st.session_state:
            usuario = st.session_state.get("usuario", "default")
            st.session_state["dados"] = DatabaseManager.load_all(usuario)
        
        dados = st.session_state["dados"]
        
        # Normalizar dados
        for chave in dados:
            dados[chave] = normalizar_df(dados[chave])
        
        # Navegação entre páginas
        if current_page == "dashboard":
            pagina_dashboard_premium(dados)
            
        elif current_page == "admin":
            if st.session_state.get("perfil") == "admin":
                tela_admin_usuarios()
            else:
                st.error("Acesso não autorizado")
                pagina_dashboard_premium(dados)
                
        elif current_page == "investimentos":
            st.markdown("""
                <div class="main-content">
                    <div class="content-header">
                        <h1 class="content-title">📈 Gestão de Investimentos</h1>
                        <p class="content-subtitle">Carteira de investimentos e rentabilidade</p>
                    </div>
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Página de investimentos em desenvolvimento
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        elif current_page == "sonhos":
            st.markdown("""
                <div class="main-content">
                    <div class="content-header">
                        <h1 class="content-title">⭐ Sonhos & Metas</h1>
                        <p class="content-subtitle">Planejamento e acompanhamento de objetivos</p>
                    </div>
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Página de sonhos em desenvolvimento
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        elif current_page == "relatorios":
            st.markdown("""
                <div class="main-content">
                    <div class="content-header">
                        <h1 class="content-title">📋 Relatórios</h1>
                        <p class="content-subtitle">Relatórios financeiros e análises</p>
                    </div>
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Página de relatórios em desenvolvimento
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            pagina_dashboard_premium(dados)
    
    # Bootstrap JS no final
    st.markdown("""
        <!-- Bootstrap JS Bundle -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        
        <!-- Custom JS -->
        <script>
        // Inicializar tooltips do Bootstrap
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // Inicializar dropdowns
            var dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
            var dropdownList = dropdownTriggerList.map(function (dropdownTriggerEl) {
                return new bootstrap.Dropdown(dropdownTriggerEl);
            });
        });
        
        function downloadChart(chartId) {
            alert('Funcionalidade de download em desenvolvimento');
        }
        </script>
        </body>
        </html>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()