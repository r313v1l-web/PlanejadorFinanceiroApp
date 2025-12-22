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
        df["perfil"] = df["perfil"].fillna("user")
        df["ativo"] = df["ativo"].astype(str).str.strip().str.lower()

        return df

    # ===============================
    # CREATE USER (🔥 ÚNICA FORMA CORRETA)
    # ===============================
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

    # ===============================
    # UPDATE USER
    # ===============================
    @staticmethod
    def update_user(usuario, data: dict):
        supabase = DatabaseManager._get_client()

        # remove campos nulos
        clean_data = {k: v for k, v in data.items() if v is not None}

        supabase.table("usuarios") \
            .update(clean_data) \
            .eq("usuario", usuario) \
            .execute()

        return True

    # ===============================
    # DADOS GERAIS
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

        for table in tables:
            res = supabase.table(table).select("*").execute()
            dados[table] = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        return dados
