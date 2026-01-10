import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "despesas-anual.xlsx"
RECEITAS_FILE = BASE_DIR / "receitas-anual.xlsx"

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro - IPB",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Função para formatar valores em Real
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel(DATA_FILE)

    # Criar coluna de mês numérico para ordenação
    df['Mes_Num'] = df['Mês Ano Ref.'].apply(lambda x: int(x.split('/')[0]) if pd.notna(x) else 0)
    df['Ano'] = df['Mês Ano Ref.'].apply(lambda x: int(x.split('/')[1]) if pd.notna(x) else 0)

    # Criar nome do mês
    meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
             5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
             9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    df['Nome_Mes'] = df['Mes_Num'].map(meses)

    return df

# Função para carregar dados de receitas
@st.cache_data
def carregar_receitas():
    df_receitas = pd.read_excel(RECEITAS_FILE)

    # Meses para transformação
    meses_colunas = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                     'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    meses_num = {m: i+1 for i, m in enumerate(meses_colunas)}

    # Filtrar apenas linhas com dados relevantes (excluir totais e linhas vazias)
    df_receitas = df_receitas.dropna(subset=['A) DIZIMAVEIS IGREJA'])
    df_receitas = df_receitas[~df_receitas['A) DIZIMAVEIS IGREJA'].str.contains('Total|total', na=False)]

    # Transformar de wide para long format
    registros = []
    for _, row in df_receitas.iterrows():
        categoria = row['A) DIZIMAVEIS IGREJA']
        for mes in meses_colunas:
            if mes in row.index and pd.notna(row[mes]) and row[mes] != 0:
                registros.append({
                    'Categoria': categoria,
                    'Nome_Mes': mes.capitalize(),
                    'Mes_Num': meses_num[mes],
                    'Valor': float(row[mes]) if isinstance(row[mes], (int, float)) else 0
                })

    df_long = pd.DataFrame(registros)
    return df_long

# Carregar dados
df = carregar_dados()
df_receitas = carregar_receitas()

# Header
st.markdown('<h1 class="main-header">⛪ Dashboard Financeiro - IPB 2025</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de Centro de Custo
centros_custo = ['Todos'] + sorted(df['Centro de Custo'].dropna().unique().tolist())
centro_selecionado = st.sidebar.multiselect(
    "Incluir Centro de Custo",
    options=centros_custo[1:],
    default=[]
)

# Filtro para Excluir Centro de Custo
centro_excluido = st.sidebar.multiselect(
    "Excluir Centro de Custo",
    options=centros_custo[1:],
    default=[]
)

# Filtro de Mês
meses_disponiveis = sorted(df['Mês Ano Ref.'].unique().tolist(),
                           key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
meses_selecionados = st.sidebar.multiselect(
    "Mês/Ano",
    options=meses_disponiveis,
    default=[]
)

# Filtro de valor mínimo/máximo
valor_min, valor_max = st.sidebar.slider(
    "Faixa de Valor (R$)",
    min_value=0.0,
    max_value=float(df['Valor'].max()),
    value=(0.0, float(df['Valor'].max())),
    format="R$ %.2f"
)

# Aplicar filtros
df_filtrado = df.copy()

if centro_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Centro de Custo'].isin(centro_selecionado)]

if centro_excluido:
    df_filtrado = df_filtrado[~df_filtrado['Centro de Custo'].isin(centro_excluido)]

if meses_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Mês Ano Ref.'].isin(meses_selecionados)]

df_filtrado = df_filtrado[(df_filtrado['Valor'] >= valor_min) & (df_filtrado['Valor'] <= valor_max)]

# Filtrar receitas pelos meses selecionados (se houver)
# Se centro de custo estiver selecionado, não mostrar receitas (receitas não têm centro de custo)
if centro_selecionado or centro_excluido:
    df_receitas_filtrado = pd.DataFrame(columns=df_receitas.columns)
    mostrar_receitas = False
else:
    df_receitas_filtrado = df_receitas.copy()
    mostrar_receitas = True
    if meses_selecionados:
        meses_num_selecionados = [int(m.split('/')[0]) for m in meses_selecionados]
        df_receitas_filtrado = df_receitas_filtrado[df_receitas_filtrado['Mes_Num'].isin(meses_num_selecionados)]

# KPIs principais - Despesas
st.subheader("📊 Indicadores de Despesas")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_gasto = df_filtrado['Valor'].sum()
    st.metric(
        label="💸 Total Despesas",
        value=formatar_real(total_gasto)
    )

with col2:
    total_lancamentos = len(df_filtrado)
    st.metric(
        label="📝 Lançamentos",
        value=f"{total_lancamentos:,}".replace(",", ".")
    )

with col3:
    media_lancamento = df_filtrado['Valor'].mean() if len(df_filtrado) > 0 else 0
    st.metric(
        label="📈 Média/Lançamento",
        value=formatar_real(media_lancamento)
    )

with col4:
    maior_despesa = df_filtrado['Valor'].max() if len(df_filtrado) > 0 else 0
    st.metric(
        label="🔝 Maior Despesa",
        value=formatar_real(maior_despesa)
    )

# KPIs de Receitas e Saldo (apenas se não houver filtro de centro de custo)
if mostrar_receitas:
    st.subheader("💰 Indicadores de Receitas e Saldo")
    col1, col2, col3, col4 = st.columns(4)

    total_receitas = df_receitas_filtrado['Valor'].sum()
    saldo = total_receitas - total_gasto

    with col1:
        st.metric(
            label="💵 Total Receitas",
            value=formatar_real(total_receitas)
        )

    with col2:
        delta_color = "normal" if saldo >= 0 else "inverse"
        st.metric(
            label="📊 Saldo",
            value=formatar_real(saldo),
            delta=f"{(saldo/total_receitas*100):.1f}% das receitas" if total_receitas > 0 else "N/A"
        )

    with col3:
        percentual_gasto = (total_gasto / total_receitas * 100) if total_receitas > 0 else 0
        st.metric(
            label="📉 % Despesas/Receitas",
            value=f"{percentual_gasto:.1f}%"
        )

    with col4:
        categorias_receita = df_receitas_filtrado['Categoria'].nunique()
        st.metric(
            label="🏷️ Categorias Receita",
            value=categorias_receita
        )
else:
    st.info("📌 Dados de receitas ocultados - filtro de Centro de Custo ativo. Receitas não possuem centro de custo.")

st.markdown("---")

# Gráfico Comparativo Receitas x Despesas (apenas se não houver filtro de centro de custo)
if mostrar_receitas:
    st.subheader("📊 Comparativo Receitas x Despesas por Mês")

    # Preparar dados de despesas por mês
    despesas_mes = df_filtrado.groupby(['Mes_Num', 'Nome_Mes'])['Valor'].sum().reset_index()
    despesas_mes.columns = ['Mes_Num', 'Nome_Mes', 'Despesas']

    # Preparar dados de receitas por mês
    receitas_mes = df_receitas_filtrado.groupby(['Mes_Num', 'Nome_Mes'])['Valor'].sum().reset_index()
    receitas_mes.columns = ['Mes_Num', 'Nome_Mes', 'Receitas']

    # Merge dos dados
    comparativo = pd.merge(receitas_mes, despesas_mes, on=['Mes_Num', 'Nome_Mes'], how='outer').fillna(0)
    comparativo = comparativo.sort_values('Mes_Num')
    comparativo['Saldo'] = comparativo['Receitas'] - comparativo['Despesas']

    # Gráfico de barras agrupadas
    fig_comparativo = go.Figure()

    fig_comparativo.add_trace(go.Bar(
        name='Receitas',
        x=comparativo['Nome_Mes'],
        y=comparativo['Receitas'],
        marker_color='#2ecc71',
        hovertemplate="<b>%{x}</b><br>Receitas: R$ %{y:,.2f}<extra></extra>"
    ))

    fig_comparativo.add_trace(go.Bar(
        name='Despesas',
        x=comparativo['Nome_Mes'],
        y=comparativo['Despesas'],
        marker_color='#e74c3c',
        hovertemplate="<b>%{x}</b><br>Despesas: R$ %{y:,.2f}<extra></extra>"
    ))

    # Linha de saldo
    fig_comparativo.add_trace(go.Scatter(
        name='Saldo',
        x=comparativo['Nome_Mes'],
        y=comparativo['Saldo'],
        mode='lines+markers',
        marker=dict(color='#3498db', size=10),
        line=dict(color='#3498db', width=3),
        hovertemplate="<b>%{x}</b><br>Saldo: R$ %{y:,.2f}<extra></extra>"
    ))

    fig_comparativo.update_layout(
        barmode='group',
        height=450,
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Valor (R$)"
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

    st.markdown("---")

# Gráficos - Linha 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Evolução Mensal das Despesas")

    # Agrupar por mês
    evolucao_mensal = df_filtrado.groupby(['Mes_Num', 'Nome_Mes'])['Valor'].sum().reset_index()
    evolucao_mensal = evolucao_mensal.sort_values('Mes_Num')

    fig_evolucao = px.bar(
        evolucao_mensal,
        x='Nome_Mes',
        y='Valor',
        color='Valor',
        color_continuous_scale='Blues',
        labels={'Valor': 'Valor (R$)', 'Nome_Mes': 'Mês'}
    )
    fig_evolucao.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        height=400
    )
    fig_evolucao.update_traces(
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)

with col2:
    st.subheader("🏷️ Distribuição por Centro de Custo")

    # Agrupar por centro de custo
    por_centro = df_filtrado.groupby('Centro de Custo')['Valor'].sum().reset_index()
    por_centro = por_centro.sort_values('Valor', ascending=False)

    fig_centro = px.pie(
        por_centro,
        values='Valor',
        names='Centro de Custo',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_centro.update_layout(height=400)
    fig_centro.update_traces(
        textposition='inside',
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
    )
    st.plotly_chart(fig_centro, use_container_width=True)

st.markdown("---")

# Gráficos - Linha 2
if mostrar_receitas:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💵 Distribuição de Receitas por Categoria")

        # Agrupar receitas por categoria
        receitas_por_categoria = df_receitas_filtrado.groupby('Categoria')['Valor'].sum().reset_index()
        receitas_por_categoria = receitas_por_categoria.sort_values('Valor', ascending=False)
        receitas_por_categoria['Categoria_Curta'] = receitas_por_categoria['Categoria'].apply(
            lambda x: x[:30] + '...' if len(str(x)) > 30 else x
        )

        fig_receitas_cat = px.pie(
            receitas_por_categoria,
            values='Valor',
            names='Categoria_Curta',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_receitas_cat.update_layout(height=400)
        fig_receitas_cat.update_traces(
            textposition='inside',
            textinfo='percent',
            hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig_receitas_cat, use_container_width=True)

    with col2:
        st.subheader("🔝 Top 10 Maiores Despesas por Especificação")

        top_especificacoes = df_filtrado.groupby('Especificação')['Valor'].sum().reset_index()
        top_especificacoes = top_especificacoes.sort_values('Valor', ascending=False).head(10)
        top_especificacoes['Especificação_Curta'] = top_especificacoes['Especificação'].apply(
            lambda x: x[:40] + '...' if len(x) > 40 else x
        )

        fig_top = px.bar(
            top_especificacoes,
            x='Valor',
            y='Especificação_Curta',
            orientation='h',
            color='Valor',
            color_continuous_scale='Reds',
            labels={'Valor': 'Valor (R$)', 'Especificação_Curta': 'Especificação'}
        )
        fig_top.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig_top.update_traces(
            hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>"
        )
        st.plotly_chart(fig_top, use_container_width=True)
else:
    # Mostrar apenas o gráfico de despesas em largura total
    st.subheader("🔝 Top 10 Maiores Despesas por Especificação")

    top_especificacoes = df_filtrado.groupby('Especificação')['Valor'].sum().reset_index()
    top_especificacoes = top_especificacoes.sort_values('Valor', ascending=False).head(10)
    top_especificacoes['Especificação_Curta'] = top_especificacoes['Especificação'].apply(
        lambda x: x[:40] + '...' if len(x) > 40 else x
    )

    fig_top = px.bar(
        top_especificacoes,
        x='Valor',
        y='Especificação_Curta',
        orientation='h',
        color='Valor',
        color_continuous_scale='Reds',
        labels={'Valor': 'Valor (R$)', 'Especificação_Curta': 'Especificação'}
    )
    fig_top.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    fig_top.update_traces(
        hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# Tabela detalhada por Centro de Custo
st.subheader("📋 Resumo por Centro de Custo")

resumo_centro = df_filtrado.groupby('Centro de Custo').agg({
    'Valor': ['sum', 'mean', 'count', 'max']
}).reset_index()
resumo_centro.columns = ['Centro de Custo', 'Total', 'Média', 'Qtd. Lançamentos', 'Maior Valor']
resumo_centro = resumo_centro.sort_values('Total', ascending=False)
resumo_centro['% do Total'] = (resumo_centro['Total'] / resumo_centro['Total'].sum() * 100).round(2)

# Formatar valores para exibição
resumo_display = resumo_centro.copy()
resumo_display['Total'] = resumo_display['Total'].apply(formatar_real)
resumo_display['Média'] = resumo_display['Média'].apply(formatar_real)
resumo_display['Maior Valor'] = resumo_display['Maior Valor'].apply(formatar_real)
resumo_display['% do Total'] = resumo_display['% do Total'].apply(lambda x: f"{x:.2f}%")

st.dataframe(
    resumo_display,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Seção de Receitas Detalhadas (apenas se não houver filtro de centro de custo)
if mostrar_receitas:
    st.subheader("💰 Análise Detalhada de Receitas")

    # Gráficos de receitas lado a lado
    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.markdown("**📈 Evolução Mensal das Receitas**")

        # Agrupar receitas por mês
        evolucao_receitas = df_receitas_filtrado.groupby(['Mes_Num', 'Nome_Mes'])['Valor'].sum().reset_index()
        evolucao_receitas = evolucao_receitas.sort_values('Mes_Num')

        fig_evolucao_rec = px.bar(
            evolucao_receitas,
            x='Nome_Mes',
            y='Valor',
            color='Valor',
            color_continuous_scale='Greens',
            labels={'Valor': 'Valor (R$)', 'Nome_Mes': 'Mês'}
        )
        fig_evolucao_rec.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickangle=-45,
            height=350
        )
        fig_evolucao_rec.update_traces(
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>"
        )
        st.plotly_chart(fig_evolucao_rec, use_container_width=True)

    with col_rec2:
        st.markdown("**🏆 Top Categorias de Receita**")

        # Top categorias de receita
        top_receitas = df_receitas_filtrado.groupby('Categoria')['Valor'].sum().reset_index()
        top_receitas = top_receitas.sort_values('Valor', ascending=True).tail(10)
        top_receitas['Categoria_Curta'] = top_receitas['Categoria'].apply(
            lambda x: x[:35] + '...' if len(str(x)) > 35 else x
        )

        fig_top_rec = px.bar(
            top_receitas,
            x='Valor',
            y='Categoria_Curta',
            orientation='h',
            color='Valor',
            color_continuous_scale='Greens',
            labels={'Valor': 'Valor (R$)', 'Categoria_Curta': 'Categoria'}
        )
        fig_top_rec.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=350
        )
        fig_top_rec.update_traces(
            hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>"
        )
        st.plotly_chart(fig_top_rec, use_container_width=True)

    # Tabela de Resumo de Receitas por Categoria
    st.markdown("**📋 Resumo de Receitas por Categoria**")

    resumo_receitas = df_receitas_filtrado.groupby('Categoria').agg({
        'Valor': ['sum', 'mean', 'count']
    }).reset_index()
    resumo_receitas.columns = ['Categoria', 'Total', 'Média Mensal', 'Meses com Registro']
    resumo_receitas = resumo_receitas.sort_values('Total', ascending=False)
    resumo_receitas['% do Total'] = (resumo_receitas['Total'] / resumo_receitas['Total'].sum() * 100).round(2)

    # Formatar valores
    resumo_receitas_display = resumo_receitas.copy()
    resumo_receitas_display['Total'] = resumo_receitas_display['Total'].apply(formatar_real)
    resumo_receitas_display['Média Mensal'] = resumo_receitas_display['Média Mensal'].apply(formatar_real)
    resumo_receitas_display['% do Total'] = resumo_receitas_display['% do Total'].apply(lambda x: f"{x:.2f}%")

    st.dataframe(
        resumo_receitas_display,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

# Gráfico de evolução por Centro de Custo (Treemap)
st.subheader("🗂️ Mapa de Despesas por Centro de Custo e Especificação")

treemap_data = df_filtrado.groupby(['Centro de Custo', 'Especificação'])['Valor'].sum().reset_index()
treemap_data = treemap_data[treemap_data['Valor'] > 0]

fig_treemap = px.treemap(
    treemap_data,
    path=['Centro de Custo', 'Especificação'],
    values='Valor',
    color='Valor',
    color_continuous_scale='RdYlBu_r'
)
fig_treemap.update_layout(height=600)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>"
)
st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")

# Tabela de dados detalhada
st.subheader("📑 Dados Detalhados")

# Filtros específicos para a tabela detalhada
st.markdown("**Filtros da Tabela:**")
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    # Filtro de Especificação
    especificacoes = ['Todas'] + sorted(df_filtrado['Especificação'].dropna().unique().tolist())
    especificacao_tabela = st.selectbox(
        "Especificação",
        options=especificacoes,
        index=0
    )

with col_filtro2:
    # Filtro de Centro de Custo para tabela
    centros_tabela = ['Todos'] + sorted(df_filtrado['Centro de Custo'].dropna().unique().tolist())
    centro_tabela = st.selectbox(
        "Centro de Custo (Tabela)",
        options=centros_tabela,
        index=0
    )

with col_filtro3:
    # Ordenação
    ordenar_por = st.selectbox(
        "Ordenar por",
        options=['Mês Ano Ref.', 'Valor (Maior)', 'Valor (Menor)', 'Centro de Custo', 'Especificação'],
        index=0
    )

# Segunda linha de filtros
col_filtro4, col_filtro5 = st.columns(2)

with col_filtro4:
    # Opção de busca
    busca = st.text_input("🔍 Buscar (Especificação, Observação ou Centro de Custo):", "")

with col_filtro5:
    # Limite de registros
    limite_registros = st.selectbox(
        "Exibir registros",
        options=['Todos', '50', '100', '200', '500'],
        index=0
    )

# Preparar dados para exibição
colunas_exibir = ['Mês Ano Ref.', 'Especificação', 'Centro de Custo', 'Valor', 'Observação']
df_exibir = df_filtrado[colunas_exibir].copy()

# Aplicar filtro de especificação
if especificacao_tabela != 'Todas':
    df_exibir = df_exibir[df_exibir['Especificação'] == especificacao_tabela]

# Aplicar filtro de centro de custo da tabela
if centro_tabela != 'Todos':
    df_exibir = df_exibir[df_exibir['Centro de Custo'] == centro_tabela]

# Aplicar busca
if busca:
    mask = (
        df_exibir['Especificação'].str.contains(busca, case=False, na=False) |
        df_exibir['Observação'].str.contains(busca, case=False, na=False) |
        df_exibir['Centro de Custo'].str.contains(busca, case=False, na=False)
    )
    df_exibir = df_exibir[mask]

# Aplicar ordenação
if ordenar_por == 'Valor (Maior)':
    df_exibir = df_exibir.sort_values('Valor', ascending=False)
elif ordenar_por == 'Valor (Menor)':
    df_exibir = df_exibir.sort_values('Valor', ascending=True)
elif ordenar_por == 'Centro de Custo':
    df_exibir = df_exibir.sort_values(['Centro de Custo', 'Mês Ano Ref.'])
elif ordenar_por == 'Especificação':
    df_exibir = df_exibir.sort_values(['Especificação', 'Mês Ano Ref.'])
else:
    df_exibir = df_exibir.sort_values(['Mês Ano Ref.', 'Centro de Custo'])

# Aplicar limite de registros
if limite_registros != 'Todos':
    df_exibir = df_exibir.head(int(limite_registros))

# Mostrar contagem de registros
st.caption(f"Exibindo {len(df_exibir)} de {len(df_filtrado)} registros filtrados")

# Formatar valores para exibição
df_exibir_formatado = df_exibir.copy()
df_exibir_formatado['Valor'] = df_exibir_formatado['Valor'].apply(formatar_real)

st.dataframe(
    df_exibir_formatado,
    use_container_width=True,
    hide_index=True,
    height=400
)

# Estatísticas rápidas da seleção atual
if len(df_exibir) > 0:
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Total da Seleção", formatar_real(df_exibir['Valor'].sum()))
    with col_stat2:
        st.metric("Média da Seleção", formatar_real(df_exibir['Valor'].mean()))
    with col_stat3:
        st.metric("Maior Valor", formatar_real(df_exibir['Valor'].max()))
    with col_stat4:
        st.metric("Menor Valor", formatar_real(df_exibir['Valor'].min()))

# Botões de download
col_down1, col_down2 = st.columns(2)
with col_down1:
    st.download_button(
        label="📥 Baixar seleção atual (CSV)",
        data=df_exibir.to_csv(index=False).encode('utf-8'),
        file_name=f"despesas_selecao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
with col_down2:
    st.download_button(
        label="📥 Baixar todos filtrados (CSV)",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name=f"despesas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Dashboard Financeiro IPB 2025 | Desenvolvido com Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
