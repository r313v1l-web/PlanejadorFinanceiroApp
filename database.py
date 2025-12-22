import streamlit as st
import pandas as pd
from supabase import create_client


class DatabaseManager:

    TABLE_MAP = {
        "usuarios": "usuarios",
        "historico": "historico",
        "investimentos": "investimentos",
        "sonhos_projetos": "sonhos_projetos",
        "config": "config",
        "categorias": "categorias",
        "fluxo_fixo": "fluxo_fixo",
        "relatorios_historicos": "relatorios_historicos",
        "controle_gastos": "controle_gastos"
    }

    # ===============================
    # CONEXÃO SUPABASE
    # ===============================
    @staticmethod
    def _get_client():
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    # ===============================
    # USUÁRIOS
    # ===============================
    @staticmethod
    def load_users():
        supabase = DatabaseManager._get_client()

        res = supabase.table("usuarios").select("*").execute()
        if not res.data:
            return pd.DataFrame(
                columns=["usuario", "senha", "nome", "perfil", "ativo"]
            )

        df = pd.DataFrame(res.data)

        df["usuario"] = df["usuario"].str.strip().str.lower()
        df["perfil"] = df["perfil"].fillna("user")
        df["ativo"] = df["ativo"].str.strip().str.lower()

        return df

    @staticmethod
    def save_users(df):
        try:
            # ===============================
            # 1️⃣ LIMPEZA OBRIGATÓRIA (JSON SAFE)
            # ===============================
            df = df.replace([float("inf"), float("-inf")], None)
            df = df.where(pd.notna(df), None)

            # ===============================
            # 2️⃣ CONVERTE PARA LISTA DE DICTS
            # ===============================
            records = df.to_dict(orient="records")

            # ===============================
            # 3️⃣ SALVA NO SUPABASE
            # ===============================
            supabase.table("usuarios").insert(records).execute()

            return True

        except Exception as e:
            st.error(f"❌ Erro ao salvar usuários: {e}")
            return False


    # ===============================
    # DADOS GERAIS
    # ===============================
    @staticmethod
    def load_all(usuario):
        supabase = DatabaseManager._get_client()
        dados = {}

        for key, table in DatabaseManager.TABLE_MAP.items():
            if key == "usuarios":
                continue

            res = supabase.table(table).select("*").execute()
            dados[key] = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        return dados

    @staticmethod
    def save(table_name, df, usuario):
        table = DatabaseManager.TABLE_MAP.get(table_name)
        if not table:
            raise ValueError("Tabela inválida")

        supabase = DatabaseManager._get_client()

        supabase.table(table).delete().neq("id", "").execute()

        records = df.to_dict(orient="records")
        if records:
            supabase.table(table).insert(records).execute()

        return True
