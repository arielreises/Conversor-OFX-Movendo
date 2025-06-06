import streamlit as st
import pandas as pd
import re
from io import BytesIO
from openai import OpenAI

# 🚨 Config inicial do Streamlit
st.set_page_config(
    page_title="Conversor de OFX para XLSX",
    page_icon="https://pages.greatpages.com.br/www.movendo.com.br/1744681213/imagens/desktop/49713-f001ad13d8ae3e8304461f490af9f362.png",
    layout="centered"
)

# 🔐 Chave da OpenAI
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 🎨 Estilo visual da página
st.markdown("""
    <style>
        html, body {
            font-family: 'Open Sans', sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding-bottom: 60px;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 1em;
        }
        .header img {
            height: 50px;
        }
        .title {
            color: #5ebc67;
            font-weight: 800;
            font-size: 2.5em;
        }
        div.stDownloadButton > button {
            background-color: #ff932b;
            color: white;
            font-weight: bold;
            border-radius: 100px;
            padding: 0.75em 2em;
        }
        div.stDownloadButton > button:hover {
            background-color: #007a77;
        }
        footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #e6f2e8;
            color: #2d6a4f;
            text-align: center;
            padding: 10px 0;
            font-weight: 600;
            font-size: 0.95em;
        }
    </style>
""", unsafe_allow_html=True)

# 🟢 Header
st.markdown("""
    <div class="header">
        <img src="https://pages.greatpages.com.br/www.movendo.com.br/1744681213/imagens/desktop/49713-f001ad13d8ae3e8304461f490af9f362.png" alt="Logo Movendo" />
        <div class="title">Conversor de OFX para XLSX</div>
    </div>
""", unsafe_allow_html=True)

# 📥 Upload
uploaded_file = st.file_uploader("Envie o arquivo .OFX", type=["ofx"])

# # 💡 Função IA
# def classificar_ia(descricao):
#     prompt = f"""
# Você é um assistente financeiro. Seu trabalho é identificar o meio de pagamento utilizado com base na descrição da transação bancária abaixo.

# Retorne **somente o nome do meio de pagamento**, como: Pix Recebido, Pix QR Code, Cielo, Stone, Rede, Getnet, VR, Alelo, Sodexo (ou Pluxee), Ben Visa Vale, Transferência, Cartão Débito, Cartão Crédito, Dinheiro, etc.

# Descrição da transação: "{descricao}"

# Resposta:
# """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "Você é um analista financeiro especialista em identificar meios de pagamento."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2,
#             max_tokens=10
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         st.warning(f"Erro na IA para descrição: {descricao}\n\nMotivo:\n{e}")
#         return "Erro"

if uploaded_file:
    try:
        content = uploaded_file.read().decode("latin-1")
        raw_transactions = re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, re.DOTALL)
        data = []

        for t in raw_transactions:
            date = re.search(r"<DTPOSTED>(\d{8})", t)
            description = re.search(r"<MEMO>([^\r\n<]+)", t)
            amount = re.search(r"<TRNAMT>(-?\d+[.,]?\d*)", t)
            tipo = re.search(r"<TRNTYPE>([A-Z]+)", t)
            tid = re.search(r"<FITID>([^\r\n<]+)", t)

            parsed_date = pd.to_datetime(date.group(1), format='%Y%m%d').date() if date else ""
            data.append({
                "Data": parsed_date,
                "Descrição": description.group(1).strip() if description else "",
                "Valor": float(amount.group(1).replace(',', '.')) if amount else 0.0,
                "Tipo": tipo.group(1) if tipo else "",
                "ID": tid.group(1) if tid else ""
            })

        df = pd.DataFrame(data)

        # Mostrar prévia simples
        st.subheader("Prévia dos dados")
        st.dataframe(df)

        # Botão para baixar só os dados convertidos (sem classificação)
        file_name_simple = uploaded_file.name.replace(".ofx", "") + "_convertido_simples.xlsx"
        output_simple = BytesIO()
        with pd.ExcelWriter(output_simple, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name="Transações", index=False)
        output_simple.seek(0)

        st.download_button(
            label="Baixar arquivo convertido simples (.xlsx)",
            data=output_simple,
            file_name=file_name_simple,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    #     # Botão para iniciar a classificação com IA
    #     if st.button("Classificar com IA"):
    #         st.subheader("Classificando os meios de pagamento com IA...")

    #         cache_respostas = {}
    #         progress_bar = st.progress(0)
    #         status_text = st.empty()
    #         total = len(df)
    #         classificados = []

    #         for i, desc in enumerate(df["Descrição"]):
    #             if desc in cache_respostas:
    #                 resposta = cache_respostas[desc]
    #             else:
    #                 resposta = classificar_ia(desc) if desc.strip() else "Vazio"
    #                 cache_respostas[desc] = resposta

    #             classificados.append(resposta)
    #             progress_bar.progress((i + 1) / total)
    #             status_text.text(f"Classificando ({i + 1}/{total})...")

    #         df["Meio de Pagamento"] = classificados

    #         status_text.text("✅ Classificação concluída!")
    #         progress_bar.empty()

    #         resumo = df.groupby("Meio de Pagamento")["Valor"].sum().reset_index()
    #         resumo = resumo.sort_values("Valor", ascending=False)

    #         st.subheader("Dados classificados")
    #         st.dataframe(df)

    #         st.subheader("Resumo por Meio de Pagamento")
    #         st.dataframe(resumo)

    #         # Gerar arquivo XLSX com classificação
    #         file_name_classificado = uploaded_file.name.replace(".ofx", "") + "_convertido_classificado.xlsx"
    #         output_classificado = BytesIO()
    #         with pd.ExcelWriter(output_classificado, engine='xlsxwriter') as writer:
    #             df.to_excel(writer, sheet_name="Transações", index=False)
    #             resumo.to_excel(writer, sheet_name="Resumo IA", index=False)
    #         output_classificado.seek(0)

    #         st.download_button(
    #             label="Baixar arquivo convertido e classificado (.xlsx)",
    #             data=output_classificado,
    #             file_name=file_name_classificado,
    #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")


# 👣 Rodapé
st.markdown("""
    <footer style="
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #e6f2e8;
    color: #2d6a4f;
    text-align: center;
    padding: 12px;
    font-weight: 600;
    font-size: 0.95em;
    z-index: 999;
">
    Desenvolvido por Movendo 💚 <br>
    <a href="https://www.movendo.com.br" target="_blank" style="color: #2d6a4f; text-decoration: none;">www.movendo.com.br</a>
</footer>
""", unsafe_allow_html=True)
