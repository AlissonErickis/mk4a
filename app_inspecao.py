import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load or initialize data
def load_data():
    if os.path.exists("inspecoes.xlsx"):
        inspecoes = pd.read_excel("inspecoes.xlsx", sheet_name="Inspecoes", engine="openpyxl")
        posicoes = pd.read_excel("inspecoes.xlsx", sheet_name="Posicoes_Inspecionadas", engine="openpyxl")
        rechecks = pd.read_excel("inspecoes.xlsx", sheet_name="Rechecks", engine="openpyxl")
    else:
        inspecoes = pd.DataFrame(columns=["ID", "Data", "Hora_Inicio", "Hora_Fim", "Numero_Pa", "Molde", "Modelo", "Responsavel"])
        posicoes = pd.DataFrame(columns=["Inspecao_ID", "Posicao", "Regiao", "Tipo_Defeito", "Sub_Outros"])
        rechecks = pd.DataFrame(columns=["Inspecao_ID", "Posicao", "Corrigido", "Observacoes", "Responsavel_Recheck"])
    return inspecoes, posicoes, rechecks

def save_data(inspecoes, posicoes, rechecks):
    with pd.ExcelWriter("inspecoes.xlsx", engine="openpyxl") as writer:
        inspecoes.to_excel(writer, sheet_name="Inspecoes", index=False)
        posicoes.to_excel(writer, sheet_name="Posicoes_Inspecionadas", index=False)
        rechecks.to_excel(writer, sheet_name="Rechecks", index=False)

# Load data
inspecoes_df, posicoes_df, rechecks_df = load_data()

# Tipos de defeitos
tipos_defeitos = ["Arranhões", "Bolhas", "Escorrimento", "Falha de Pintura", "Marca de Rolo", "Olho de Peixe", "Ondulação", "Poros", "Rugosidade", "Sujeira", "Outros"]
sub_outros = ["Mancha", "Descoloração", "Contaminação"]

# Interface
st.title("Inspeção Visual de Pintura - MK4A")
menu = st.sidebar.selectbox("Menu", ["Nova Inspeção", "Recheck", "Histórico"])

if menu == "Nova Inspeção":
    st.header("Nova Inspeção")
    with st.form("form_inspecao"):
        data = st.date_input("Data", datetime.today())
        hora_inicio = st.time_input("Hora de Início")
        hora_fim = st.time_input("Hora de Fim")
        numero_pa = st.text_input("Número da Pá")
        molde = st.text_input("Molde")
        modelo = st.text_input("Modelo")
        responsavel = st.text_input("Responsável")
        st.markdown("### Posições Inspecionadas")
        posicoes = []
        for i in range(1, 82):
            st.markdown(f"**Posição {i}**")
            regiao = st.text_input(f"Região {i}", key=f"regiao_{i}")
            tipo_defeito = st.selectbox(f"Tipo de Defeito {i}", tipos_defeitos, key=f"defeito_{i}")
            sub_outro = ""
            if tipo_defeito == "Outros":
                sub_outro = st.selectbox(f"Subcategoria {i}", sub_outros, key=f"sub_{i}")
            posicoes.append((i, regiao, tipo_defeito, sub_outro))
        submitted = st.form_submit_button("Salvar Inspeção")
        if submitted:
            inspecao_id = len(inspecoes_df) + 1
            inspecoes_df.loc[len(inspecoes_df)] = [inspecao_id, data, hora_inicio, hora_fim, numero_pa, molde, modelo, responsavel]
            for pos in posicoes:
                posicoes_df.loc[len(posicoes_df)] = [inspecao_id] + list(pos)
            save_data(inspecoes_df, posicoes_df, rechecks_df)
            st.success("Inspeção salva com sucesso!")

elif menu == "Recheck":
    st.header("Recheck de Inspeção")
    if inspecoes_df.empty:
        st.warning("Nenhuma inspeção registrada.")
    else:
        inspecao_ids = inspecoes_df["ID"].tolist()
        selected_id = st.selectbox("Selecione a Inspeção", inspecao_ids)
        defeitos = posicoes_df[(posicoes_df["Inspecao_ID"] == selected_id) & (posicoes_df["Tipo_Defeito"] != "")]
        if defeitos.empty:
            st.info("Nenhum defeito registrado para essa inspeção.")
        else:
            with st.form("form_recheck"):
                st.markdown("### Pontos com Defeito")
                for idx, row in defeitos.iterrows():
                    corrigido = st.selectbox(f"Posição {row['Posicao']} - {row['Tipo_Defeito']}", ["", "Sim", "Não"], key=f"corrigido_{idx}")
                    obs = st.text_input(f"Observações {row['Posicao']}", key=f"obs_{idx}")
                    responsavel = st.text_input(f"Responsável Recheck {row['Posicao']}", key=f"resp_{idx}")
                    if corrigido:
                        rechecks_df.loc[len(rechecks_df)] = [selected_id, row["Posicao"], corrigido, obs, responsavel]
                submitted = st.form_submit_button("Salvar Recheck")
                if submitted:
                    save_data(inspecoes_df, posicoes_df, rechecks_df)
                    st.success("Recheck salvo com sucesso!")

elif menu == "Histórico":
    st.header("Histórico de Inspeções")
    if inspecoes_df.empty:
        st.info("Nenhuma inspeção registrada.")
    else:
        st.dataframe(inspecoes_df)
        selected_id = st.selectbox("Ver detalhes da Inspeção", inspecoes_df["ID"])
        st.subheader("Posições Inspecionadas")
        st.dataframe(posicoes_df[posicoes_df["Inspecao_ID"] == selected_id])
        st.subheader("Rechecks")
        st.dataframe(rechecks_df[rechecks_df["Inspecao_ID"] == selected_id])
