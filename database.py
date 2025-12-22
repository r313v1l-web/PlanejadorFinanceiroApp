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

        for table in tables:
            res = supabase.table(table) \
                .select("*") \
                .eq("usuario", usuario) \
                .execute()

            df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

            # 🔒 NORMALIZA SEMPRE
            if not df.empty:
                df.columns = df.columns.str.lower()
                
                # Normalização específica para fluxo_fixo
                if table == "fluxo_fixo" and "tipo" in df.columns:
                    df["tipo"] = df["tipo"].astype(str).str.strip().str.title()

            dados[table] = df

        return dados

    # ===============================
    # SAVE GENÉRICO (POR USUÁRIO) - VERSÃO DEFINITIVA
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

        # 🔥 FUNÇÃO AUXILIAR: Converte TODAS as datas para string
        def convert_dates_in_records(records_list):
            converted = []
            for record in records_list:
                new_record = {}
                for key, value in record.items():
                    if value is not None:
                        # Converter datas para string ISO
                        if hasattr(value, 'isoformat'):
                            new_record[key] = value.isoformat()
                        elif isinstance(value, pd.Timestamp):
                            new_record[key] = value.strftime('%Y-%m-%d')
                        else:
                            new_record[key] = value
                    else:
                        new_record[key] = value
                converted.append(new_record)
            return converted
        
        # 🔥 Converter TODAS as datas em TODOS os records
        records = convert_dates_in_records(records)

        # 🔥 CONFIG → UPSERT (usuario + chave)
        if table_name == "config":
            supabase.table("config") \
                .upsert(records, on_conflict="usuario,chave") \
                .execute()
            return True

        # 🔥 RELATORIOS_HISTORICOS → UPSERT (usuario + mes)
        if table_name == "relatorios_historicos":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            supabase.table("relatorios_historicos") \
                .upsert(records, on_conflict="usuario,mes") \
                .execute()
            return True

        # 🔥 CATEGORIAS → UPSERT (usuario + nome)
        if table_name == "categorias":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Garantir que temos as colunas necessárias para o upsert
            for record in records:
                if "nome" not in record:
                    record["nome"] = ""
            
            supabase.table("categorias") \
                .upsert(records, on_conflict="usuario,nome") \
                .execute()
            return True

        # 🔥 FLUXO_FIXO → DELETE + INSERT
        if table_name == "fluxo_fixo":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Primeiro deletar todos os fluxos do usuário
            supabase.table("fluxo_fixo") \
                .delete() \
                .eq("usuario", usuario) \
                .execute()
            
            # Depois inserir os novos
            supabase.table("fluxo_fixo") \
                .insert(records) \
                .execute()
            return True

        # 🔥 SONHOS_PROJETOS → DELETE + INSERT
        if table_name == "sonhos_projetos":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Primeiro deletar todos os sonhos do usuário
            supabase.table("sonhos_projetos") \
                .delete() \
                .eq("usuario", usuario) \
                .execute()
            
            # Depois inserir os novos
            supabase.table("sonhos_projetos") \
                .insert(records) \
                .execute()
            return True

        # 🔥 INVESTIMENTOS → DELETE + INSERT
        if table_name == "investimentos":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Primeiro deletar todos os investimentos do usuário
            supabase.table("investimentos") \
                .delete() \
                .eq("usuario", usuario) \
                .execute()
            
            # Depois inserir os novos
            supabase.table("investimentos") \
                .insert(records) \
                .execute()
            return True

        # 🔥 HISTORICO → DELETE + INSERT
        if table_name == "historico":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Primeiro deletar todo o histórico do usuário
            supabase.table("historico") \
                .delete() \
                .eq("usuario", usuario) \
                .execute()
            
            # Depois inserir os novos
            supabase.table("historico") \
                .insert(records) \
                .execute()
            return True

        # 🔥 CONTROLE_GASTOS → DELETE + INSERT
        if table_name == "controle_gastos":
            # Remover coluna id se existir
            for record in records:
                if "id" in record:
                    del record["id"]
            
            # Primeiro deletar todos os gastos do usuário
            supabase.table("controle_gastos") \
                .delete() \
                .eq("usuario", usuario) \
                .execute()
            
            # Depois inserir os novos
            supabase.table("controle_gastos") \
                .insert(records) \
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