import streamlit as st
import pandas as pd
import tabula
import tempfile
import os

st.set_page_config(page_title="Gerador de Lista de Bloqueio DNS", page_icon="🚫")

st.title("🚫 Gerador de Lista de Bloqueio DNS")
st.write("Extraia automaticamente uma coluna de um PDF e gere o arquivo `.conf` no formato:")
st.code('local-zone: "domínio" always_refuse', language="bash")

uploaded_file = st.file_uploader("Envie o arquivo PDF", type=["pdf"])

# --- Etapa 1: Envio do PDF ---
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info("🔍 Lendo o PDF e identificando colunas disponíveis...")
    try:
        tabelas = tabula.read_pdf(tmp_path, pages="all", multiple_tables=True, guess=True)
    except Exception as e:
        st.error(f"❌ Erro ao ler o PDF: {e}")
        st.stop()

    # Coleta nomes de colunas únicos
    colunas = []
    for t in tabelas:
        df = pd.DataFrame(t)
        colunas.extend(list(df.columns))
    colunas_unicas = sorted(set([str(c).strip() for c in colunas if str(c).strip() != ""]))

    if not colunas_unicas:
        st.warning("⚠️ Nenhuma coluna identificada no PDF.")
        st.stop()

    st.success("✅ Colunas detectadas com sucesso!")
    coluna_selecionada = st.selectbox("Selecione a coluna que contém os domínios:", colunas_unicas)

    # --- Etapa 2: Geração do arquivo ---
    if st.button("Gerar arquivo .conf"):
        valores = []
        for t in tabelas:
            df = pd.DataFrame(t)
            for c in df.columns:
                if coluna_selecionada.lower() in str(c).lower():
                    vals = df[c].dropna().astype(str).str.strip()
                    valores.extend(vals)

        if not valores:
            st.warning(f"Nenhum valor encontrado na coluna '{coluna_selecionada}'.")
            st.stop()

        # Remove duplicados mantendo ordem
        valores_unicos = list(dict.fromkeys(valores))

        linhas = [f'local-zone: "{v}" always_refuse' for v in valores_unicos]
        conteudo = "\n".join(linhas)

        nome_saida = "lista_bloqueio.conf"
        with open(nome_saida, "w", encoding="utf-8") as f:
            f.write(conteudo)

        st.success(f"✅ Extração concluída! {len(valores_unicos)} domínios únicos encontrados.")
        st.download_button("📥 Baixar arquivo .conf", data=conteudo, file_name=nome_saida, mime="text/plain")