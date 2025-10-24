import streamlit as st
import re

st.set_page_config(page_title="Limpeza de Duplicados .conf", page_icon="🧹")

st.title("🧹 Limpeza de Duplicados em Arquivos .conf")
st.write("Envie um arquivo `.conf` (ex: gerado pelo app anterior) e remova domínios duplicados.")

uploaded_file = st.file_uploader("Envie o arquivo .conf", type=["conf", "txt"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")

    # Extrai os domínios do formato local-zone: "dominio" always_refuse
    domains = re.findall(r'local-zone:\s*"([^"]+)"', content)
    total = len(domains)
    unique_domains = list(dict.fromkeys(domains))
    duplicates = total - len(unique_domains)

    st.info(f"📦 Total de linhas: {total}")
    st.warning(f"🔁 Duplicadas removidas: {duplicates}")
    st.success(f"✅ Restaram {len(unique_domains)} entradas únicas.")

    # Gera novo conteúdo limpo
    clean_lines = [f'local-zone: "{d}" always_refuse' for d in unique_domains]
    clean_text = "\n".join(clean_lines)

    st.download_button(
        "📥 Baixar arquivo limpo (.conf)",
        data=clean_text,
        file_name="lista_bloqueio_sem_duplicados.conf",
        mime="text/plain"
    )
