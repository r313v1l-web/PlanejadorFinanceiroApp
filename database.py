# database.py
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

ABAS_BASE = [
    "config",
    "investimentos",
    "historico",
    "sonhos_projetos",
    "fluxo_fixo",
    "categorias",
    "controle_gastos",
    "relatorios_historicos"
]


class DatabaseManager:

    # ===============================
    # USERS (SEM CACHE + STATUS TEXTO)
    # ===============================
    @staticmethod
    def load_users():
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 🔥 bypass real de cache
        df = conn.read(worksheet="usuarios", ttl=0)
        df = df.dropna(how="all")

        df.columns = df.columns.astype(str).str.strip().str.lower()

        for col in ["usuario", "senha", "nome", "perfil", "ativo"]:
            if col not in df.columns:
                df[col] = ""

        df["usuario"] = df["usuario"].astype(str).str.strip().str.lower()
        df["senha"] = df["senha"].astype(str).str.strip()
        df["nome"] = df["nome"].astype(str).str.strip()

        df["perfil"] = (
            df["perfil"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace("", "user")
        )

        # 🔐 status CONTROLADO
        df["ativo"] = (
            df["ativo"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return df

    @staticmethod
    def save_users(df):
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(worksheet="usuarios", data=df)

    # ===============================
    # DADOS DO SISTEMA (CACHE OK)
    # ===============================
    @staticmethod
    @st.cache_data(ttl=60)
    def load_all(usuario: str = "default"):
        conn = st.connection("gsheets", type=GSheetsConnection)
        dados = {}

        for aba in ABAS_BASE:
            aba_real = DatabaseManager._aba_usuario(aba, usuario)

            try:
                df = conn.read(worksheet=aba_real)
                df = df.dropna(how="all")

                if df.empty:
                    dados[aba] = DatabaseManager.fallback(aba)
                else:
                    dados[aba] = DatabaseManager.normalize(df)

            except Exception:
                dados[aba] = DatabaseManager.fallback(aba)

        return dados

    @staticmethod
    def save(aba, df, usuario):
        conn = st.connection("gsheets", type=GSheetsConnection)
        aba_real = f"{aba}_{usuario}"

        try:
            conn.update(worksheet=aba_real, data=df)
        except Exception:
            conn.create(worksheet=aba_real, data=df)

    # ===============================
    # UTILIDADES
    # ===============================
    @staticmethod
    def _aba_usuario(aba: str, usuario: str) -> str:
        return f"{aba}_{usuario.lower().strip()}"

    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for col in df.columns:
            if "data" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

            if col.lower() in ["valor", "valor_atual", "valor_alvo"]:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            if col.lower() == "rendimento_mensal":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    @staticmethod
    def fallback(aba: str) -> pd.DataFrame:
        SCHEMAS = {
            "fluxo_fixo": [
                "Nome", "Valor", "Tipo", "Categoria",
                "Data_Inicio", "Data_Fim", "Recorrencia", "Observacao"
            ],
            "historico": [
                "Data", "Tipo", "Valor", "Categoria",
                "Subcategoria", "Descricao", "Responsavel", "Fixo"
            ],
            "investimentos": [
                "Instituicao", "Ativo", "Tipo", "Valor_Atual",
                "Data_Entrada", "Rendimento_Mensal", "Categoria", "Observacao"
            ],
            "sonhos_projetos": [
                "Nome", "Descricao", "Valor_Alvo", "Valor_Atual",
                "Data_Alvo", "Prioridade", "Status", "Categoria"
            ],
            "categorias": [
                "Nome", "Tipo", "Orcamento_Mensal", "Cor"
            ],
            "config": [
                "Chave", "Valor", "Descricao"
            ],
            "relatorios_historicos": [
                "Mes", "Patrimonio", "Saldo_Fixo",
                "Saldo_Variavel", "Perc_Meta",
                "Texto_Executivo", "Status"
            ],
            "controle_gastos": [
                "Data", "Descricao", "Valor"
            ]
        }

        return pd.DataFrame(columns=SCHEMAS.get(aba, []))
