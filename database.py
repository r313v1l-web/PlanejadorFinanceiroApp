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

    # ===============================
    # CREATE USER  ✅ (INSERÇÃO PONTUAL)
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
    # UPDATE USER (perfil / ativo)
    # ===============================
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

    # ===============================
    # UPDATE PASSWORD
    # ===============================
    @staticmethod
    def update_password(usuario, senha_hash):
        supabase = DatabaseManager._get_client()

        supabase.table("usuarios") \
            .update({"senha": senha_hash}) \
            .eq("usuario", usuario) \
            .execute()

        return True

    # ===============================
    # LOAD DADOS DO SISTEMA
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
            res = supabase.table("config") \
                .select("*") \
                .eq("usuario", usuario) \
                .execute()

            dados[table] = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        return dados

    # ===============================
    # SAVE GENÉRICO (NÃO USAR PARA USUÁRIOS)
    # ===============================
    @staticmethod
    def save(table_name, df, usuario):
        supabase = DatabaseManager._get_client()

        # limpeza JSON-safe
        df = df.replace([float("inf"), float("-inf")], None)
        df = df.where(pd.notna(df), None)

        records = df.to_dict(orient="records")

        if not records:
            return True

        # 🔥 CONFIG usa UPSERT
        if table_name == "config":
            supabase.table("config") \
                .upsert(records, on_conflict="chave") \
                .execute()
            return True

        # 🔥 DEMAIS TABELAS (operacionais)
        supabase.table(table_name).delete().execute()

        supabase.table(table_name).insert(records).execute()

        return True

