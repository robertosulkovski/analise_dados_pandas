import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ⚙️ CONFIG
st.set_page_config(
    layout="wide",
    page_title="Dashboard Dolce Cacau",
    page_icon="🍫"
)

# -------------------------
# FUNÇÕES
# -------------------------
import os

@st.cache_data
def carregar_dados():
    BASE_DIR = os.path.dirname(__file__)
    caminho_dados = os.path.join(BASE_DIR, "data", "vendas.csv")

    df = pd.read_csv(caminho_dados)
    df['data'] = pd.to_datetime(df['data'])
    return df

def converter_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def formato_brl(x):
    return f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def preparar_dados_mes(df):
    df = df.copy()
    df['mes'] = df['data'].dt.to_period('M')
    return df

def calcular_kpis(df):
    faturamento = df['faturamento'].sum()
    lucro = df['lucro'].sum()
    margem = (lucro / faturamento) * 100 if faturamento != 0 else 0
    return faturamento, lucro, margem

def carregar_imagem_base64(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()

# -------------------------
# DADOS
# -------------------------
df = carregar_dados()

st.title("📋 Dashboard de Faturamento Ano 2024 - Empresa Dolce Cacau")

# 🎯 METAS ANUAIS

META_FATURAMENTO = 3_000_000
META_LUCRO = 1_439_000

# -------------------------
# SIDEBAR (LOGO + FILTROS)
# -------------------------
import os

BASE_DIR = os.path.dirname(__file__)
caminho_logo = os.path.join(BASE_DIR, "assets", "logo.png")

col1, col2, col3 = st.sidebar.columns([1,4,1])

with col2:
    st.image(caminho_logo, width=160)



st.sidebar.markdown(
    "<p style='text-align:center; font-size:18px; font-weight:600;'>Dolce Cacau</p>",
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.markdown("### 📅 Período")

periodo = st.sidebar.selectbox(
    "Período rápido",
    [
        "Personalizado",
        "Ano Inteiro",
        "1º Trimestre",
        "2º Trimestre",
        "3º Trimestre",
        "4º Trimestre"
    ]
)

ano = df['data'].dt.year.max()

if periodo == "Ano Inteiro":
    data_inicio = pd.Timestamp(f"{ano}-01-01")
    data_fim = pd.Timestamp(f"{ano}-12-31")

elif periodo == "1º Trimestre":
    data_inicio = pd.Timestamp(f"{ano}-01-01")
    data_fim = pd.Timestamp(f"{ano}-03-31")

elif periodo == "2º Trimestre":
    data_inicio = pd.Timestamp(f"{ano}-04-01")
    data_fim = pd.Timestamp(f"{ano}-06-30")

elif periodo == "3º Trimestre":
    data_inicio = pd.Timestamp(f"{ano}-07-01")
    data_fim = pd.Timestamp(f"{ano}-09-30")

elif periodo == "4º Trimestre":
    data_inicio = pd.Timestamp(f"{ano}-10-01")
    data_fim = pd.Timestamp(f"{ano}-12-31")

else:
    data_inicio = df['data'].min()
    data_fim = df['data'].max()

# 📅 CALENDÁRIO MANUAL

if periodo == "Personalizado":
    st.sidebar.markdown("📅 **Período personalizado**")

    data_inicio = st.sidebar.date_input("Data início", value=data_inicio)
    data_fim = st.sidebar.date_input("Data fim", value=data_fim)

###Selecione os Produtos

st.sidebar.markdown("### 📦 Produtos")

produtos = st.sidebar.multiselect(
    "Produto",
    df['produto'].unique(),
    placeholder="Selecione produtos"
)

st.sidebar.markdown("### 🏷️ Categoria")

categorias = st.sidebar.multiselect(
    "Categoria",
    df['categoria'].unique(),
    placeholder="Selecione categorias"
)

st.sidebar.markdown("### 🔍 Busca")

busca = st.sidebar.text_input("🔍 Buscar produto")

# -------------------------
# FILTRAGEM
# -------------------------
df_filtrado = df.copy()

df_filtrado = df_filtrado[
    (df_filtrado['data'] >= pd.to_datetime(data_inicio)) &
    (df_filtrado['data'] <= pd.to_datetime(data_fim))
]

if produtos:
    df_filtrado = df_filtrado[df_filtrado['produto'].isin(produtos)]

if categorias:
    df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias)]

if busca:
    df_filtrado = df_filtrado[
        df_filtrado['produto'].str.contains(busca, case=False, na=False)
    ]

# -------------------------
# PERFORMANCE CONSOLIDADA
# -------------------------
faturamento, lucro, margem = calcular_kpis(df_filtrado)
with st.expander("🎯 Performance Consolidada", expanded=True):

    col1, col2 = st.columns(2)

    # FATURAMENTO
    perc_fat = (faturamento / META_FATURAMENTO) * 100 if META_FATURAMENTO != 0 else 0

    col1.metric(
        "💰 Faturamento",
        formato_brl(faturamento),
        delta=f"{perc_fat:.2f}% da meta",
        delta_color="normal"
    )

    col1.caption(f"🎯 Meta: {formato_brl(META_FATURAMENTO)}")

    # LUCRO
    perc_lucro = (lucro / META_LUCRO) * 100 if META_LUCRO != 0 else 0

    col2.metric(
        "🧾 Lucro",
        formato_brl(lucro),
        delta=f"{perc_lucro:.2f}% da meta",
        delta_color="normal"
    )

    col2.caption(f"🎯 Meta: {formato_brl(META_LUCRO)}")

# -------------------------
# BASE PARA ANÁLISES
# -------------------------
df_comp = preparar_dados_mes(df_filtrado)

# faturamento por mês
faturamento_mes = df_comp.groupby('mes')['faturamento'].sum().sort_index()

# resumo mensal (faturamento + lucro)
resumo_mes = (
    df_comp.groupby('mes')[['faturamento', 'lucro']]
    .sum()
    .sort_index()
)

# cálculo de variação
variacao = 0

if len(faturamento_mes) >= 2:
    fat_atual = faturamento_mes.iloc[-1]
    fat_anterior = faturamento_mes.iloc[-2]

    variacao = (
        (fat_atual - fat_anterior) / fat_anterior * 100
        if fat_anterior != 0 else 0
    )


# -------------------------
# INSIGHTS
# -------------------------
if not df_filtrado.empty:

    top_produto = (
        df_filtrado.groupby('produto')['faturamento']
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )

    if not top_produto.empty:
        nome = top_produto.index[0]
        valor = top_produto.iloc[0]

        st.info(
            f"📌 O produto **{nome}** foi o maior responsável pelo faturamento, gerando {formato_brl(valor)} no período."
        )

# alerta de queda
if len(faturamento_mes) >= 2 and variacao < 0:
    st.warning(f"⚠ O faturamento caiu {variacao:.2f}% em relação ao mês anterior.")

st.divider()

# -------------------------
# GRÁFICO LINHA
# -------------------------
df_plot = df_comp.copy()

evolucao = df_plot.groupby('mes')['faturamento'].sum().reset_index()

evolucao = evolucao.sort_values('mes')
evolucao['mes'] = evolucao['mes'].astype(str)

fig = px.line(
    evolucao,
    x='mes',
    y='faturamento',
    markers=True
)

fig.update_traces(marker_color="#3E2723")

with st.expander("📈 Gráfico Evolução do Faturamento", expanded=False):

    st.markdown(
        "<p style='font-size:16px; font-weight:bold;'>📊 Como o faturamento evoluiu ao longo dos meses</p>",
        unsafe_allow_html=True
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# GRÁFICO BARRAS
# -------------------------
faturamento_mes_df = faturamento_mes.reset_index()
faturamento_mes_df = faturamento_mes_df.sort_values('mes')
faturamento_mes_df['mes'] = faturamento_mes_df['mes'].astype(str)

fig_bar = px.bar(
    faturamento_mes_df,
    x='mes',
    y='faturamento',
    title="📊 Resumo mensal"
)

fig_bar.update_traces(marker_color="#1f77b4")
fig_bar.update_layout(template="plotly_white")
fig_bar.update_yaxes(tickprefix="R$ ")

with st.expander("📊 Gráfico Faturamento por mês", expanded=False):
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------
# TABELA DETALHADA
# -------------------------
if not df_filtrado.empty:

    df_exibir = df_filtrado.copy()
    df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y')

    colunas_dinheiro = ['preco','custo','faturamento','custo_total','lucro']

    for col in colunas_dinheiro:
        df_exibir[col] = df_exibir[col].apply(formato_brl)

    with st.expander("📊 Tabela Controle de Faturamento", expanded=False):

            expander = st.expander("🔎 Ajustar filtros da tabela", expanded=False)


            filtro_produto = st.multiselect(
                "Produto",
                df_exibir['produto'].unique()
            )

        df_tabela = df_exibir.copy()

        if filtro_produto:
            df_tabela = df_tabela[df_tabela['produto'].isin(filtro_produto)]

        st.dataframe(df_tabela, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado para esse filtro")

#
# -------------------------
# RESUMO MENSAL
# -------------------------
tabela_mes = resumo_mes.reset_index()
tabela_mes.columns = ['Mês', 'Faturamento', 'Lucro']

meses_pt = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# 📊 Margem (ANTES da formatação)
tabela_mes['Margem (%)'] = (
    (tabela_mes['Lucro'] / tabela_mes['Faturamento']) * 100
).round(2)

# 🗓️ Nome do mês
tabela_mes['Mês'] = tabela_mes['Mês'].dt.month.map(meses_pt)

# 💰 Formatação (DEPOIS)
tabela_mes['Faturamento'] = tabela_mes['Faturamento'].apply(formato_brl)
tabela_mes['Lucro'] = tabela_mes['Lucro'].apply(formato_brl)
tabela_mes['Margem (%)'] = tabela_mes['Margem (%)'].apply(lambda x: f"{x:.2f}%")

with st.expander("📊 Tabela Resumo Mensal", expanded=False):
    st.dataframe(tabela_mes, use_container_width=True)
#
# 
# 
# -------------------------
# MARGEM POR CATEGORIA
# -------------------------
df_categoria = df_filtrado.copy()

resumo_categoria = (
    df_categoria.groupby('categoria')[['faturamento', 'lucro']]
    .sum()
    .reset_index()
)

# calcular margem
resumo_categoria['margem'] = (
    (resumo_categoria['lucro'] / resumo_categoria['faturamento']) * 100
).round(2)

# gráfico
fig_cat = px.bar(
    resumo_categoria,
    x='categoria',
    y='margem',
    title="📊 Margem Bruta por categoria (%)",
    text='margem'
)

fig_cat.update_traces(
    marker_color="#2563eb",
    texttemplate='%{text:.2f}%',
    textposition='outside'
)

fig_cat.update_layout(
    template="plotly_white",
    yaxis_title="Margem (%)",
    xaxis_title="Categoria"
)

# mostrar
with st.expander("📊 Gráfico Margem Bruta por categoria", expanded=False):
    st.plotly_chart(fig_cat, use_container_width=True)
#     

# -------------------------
# DOWNLOAD
# -------------------------
csv = converter_csv(df_filtrado)

st.download_button(
    label="📥 Baixar dados filtrados",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv'
)
