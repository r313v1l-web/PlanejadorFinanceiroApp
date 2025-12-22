import streamlit as st
import pandas as pd
from supabase import create_client


class DatabaseManager:

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
        df["usuario"] = df["usuario"].astype(str).str.strip().str.lower()
        df["perfil"] = df["perfil"].fillna("user").astype(str).str.lower()
        df["ativo"] = df["ativo"].astype(str).str.strip().str.lower()

        return df

    @staticmethod
    def create_user(usuario, nome, senha_hash, perfil):
        supabase = DatabaseManager._get_client()

        payload = {
            "usuario": usuario.strip().lower(),
            "nome": nome.strip(),
            "senha": senha_hash,
            "perfil": perfil or "user",
            "ativo": "ativo"
        }

        supabase.table("usuarios").insert(payload).execute()
        return True

    @staticmethod
    def update_user(usuario, perfil=None, ativo=None):
        supabase = DatabaseManager._get_client()

        data = {}
        if perfil is not None:
            data["perfil"] = perfil
        if ativo is not None:
            data["ativo"] = ativo

        if data:
            supabase.table("usuarios") \
                .update(data) \
                .eq("usuario", usuario) \
                .execute()

        return True

    @staticmethod
    def update_password(usuario, senha_hash):
        supabase = DatabaseManager._get_client()

        supabase.table("usuarios") \
            .update({"senha": senha_hash}) \
            .eq("usuario", usuario) \
            .execute()

        return True

    # ===============================
    # LOAD DADOS (POR USUÁRIO)
    # ===============================
    @staticmethod
    def load_all(usuario):
        supabase = DatabaseManager._get_client()
        dados = {}

        tables = [
            "historico",
            "investimentos",
            "sonhos_projetos",
            "config",
            "categorias",
            "fluxo_fixo",
            "relatorios_historicos",
            "controle_gastos"
        ]

        @staticmethod
        def load_all(usuario):
            supabase = DatabaseManager._get_client()
            dados = {}

            tables = [
                "historico",
                "investimentos",
                "sonhos_projetos",
                "config",
                "categorias",
                "fluxo_fixo",
                "relatorios_historicos",
                "controle_gastos"
            ]

            for table in tables:
                res = supabase.table(table) \
                    .select("*") \
                    .eq("usuario", usuario) \
                    .execute()

                if res.data:
                    df = pd.DataFrame(res.data)
                    df.columns = df.columns.str.lower()   # 🔥 ESSENCIAL
                    dados[table] = df
                else:
                    dados[table] = pd.DataFrame()

            return dados

    # ===============================
    # SAVE GENÉRICO (POR USUÁRIO)
    # ===============================
    @staticmethod
    def save(table_name, df, usuario):
        supabase = DatabaseManager._get_client()

        if df is None or df.empty:
            return True

        df = df.copy()
        df.columns = df.columns.str.lower()

        # garantir coluna usuario
        df["usuario"] = usuario

        df = df.replace([float("inf"), float("-inf")], None)
        df = df.where(pd.notna(df), None)

        records = df.to_dict(orient="records")

        # 🔥 CONFIG → UPSERT (usuario + chave)
        if table_name == "config":
            supabase.table("config") \
                .upsert(records, on_conflict="usuario,chave") \
                .execute()
            return True

        # 🔥 OUTRAS TABELAS → DELETE DO USUÁRIO + INSERT
        supabase.table(table_name) \
            .delete() \
            .eq("usuario", usuario) \
            .execute()

        supabase.table(table_name) \
            .insert(records) \
            .execute()

        return True
