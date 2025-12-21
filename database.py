import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

class DatabaseManager:

    # =====================
    # USERS
    # =====================
    @staticmethod
    def load_users():
        sb = get_supabase()
        res = sb.table("usuarios").select("*").execute()
        return pd.DataFrame(res.data)

    @staticmethod
    def save_users(df):
        sb = get_supabase()
        sb.table("usuarios").delete().neq("usuario", "").execute()
        sb.table("usuarios").insert(df.to_dict("records")).execute()

    # =====================
    # LOAD ALL
    # =====================
    @staticmethod
    def load_all(usuario):
        sb = get_supabase()
        tabelas = [
            "config", "historico", "investimentos",
            "sonhos_projetos", "fluxo_fixo",
            "categorias", "controle_gastos",
            "relatorios_historicos"
        ]

        dados = {}
        for t in tabelas:
            res = sb.table(t).select("*").eq("usuario", usuario).execute()
            dados[t] = pd.DataFrame(res.data)

        return dados

    @staticmethod
    def save(tabela, df, usuario):
        sb = get_supabase()
        sb.table(tabela).delete().eq("usuario", usuario).execute()
        sb.table(tabela).insert(df.to_dict("records")).execute()
