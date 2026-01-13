import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent
MENSAL_DIR = BASE_DIR / "mensal"

# Configuração da página
st.set_page_config(
    page_title="Dashboard Mensal - IPB",
    page_icon="📅",
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
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background: linear-gradient(90deg, #f0f0f0 0%, #ffffff 100%);
        border-left: 5px solid #3498db;
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
    .entrada-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .saida-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Função para formatar valores em Real
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para carregar dados de entradas
@st.cache_data
def carregar_entradas(mes):
    arquivo = MENSAL_DIR / f"{mes}-entradas.xlsx"
    if arquivo.exists():
        df = pd.read_excel(arquivo)
        # Converter data para datetime se necessário
        if 'Data Lançamento' in df.columns:
            df['Data Lançamento'] = pd.to_datetime(df['Data Lançamento'])
        return df
    return pd.DataFrame()

# Função para carregar dados de saídas
@st.cache_data
def carregar_saidas(mes):
    arquivo = MENSAL_DIR / f"{mes}-saidas.xlsx"
    if arquivo.exists():
        df = pd.read_excel(arquivo)
        # Converter data para datetime se necessário
        if 'Data Lançamento' in df.columns:
            df['Data Lançamento'] = pd.to_datetime(df['Data Lançamento'])
        return df
    return pd.DataFrame()

# Header
st.markdown('<h1 class="main-header">📅 Dashboard Mensal - IPB 2025</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Seleção de Mês
st.sidebar.header("📆 Seleção de Período")

# Listar meses disponíveis
meses_disponiveis = []
if MENSAL_DIR.exists():
    for arquivo in MENSAL_DIR.glob("*-entradas.xlsx"):
        mes = arquivo.stem.replace("-entradas", "")
        meses_disponiveis.append(mes)

if not meses_disponiveis:
    st.error("⚠️ Nenhum arquivo mensal encontrado na pasta 'mensal/'")
    st.stop()

# Mapear nomes de meses
meses_pt = {
    'jan': 'Janeiro', 'fev': 'Fevereiro', 'mar': 'Março', 'abr': 'Abril',
    'mai': 'Maio', 'jun': 'Junho', 'jul': 'Julho', 'ago': 'Agosto',
    'set': 'Setembro', 'out': 'Outubro', 'nov': 'Novembro', 'dez': 'Dezembro'
}

mes_opcoes = {meses_pt.get(m, m.upper()): m for m in sorted(meses_disponiveis)}
mes_selecionado_label = st.sidebar.selectbox(
    "Mês",
    options=list(mes_opcoes.keys()),
    index=len(mes_opcoes) - 1  # Seleciona o último mês por padrão
)
mes_selecionado = mes_opcoes[mes_selecionado_label]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Visualizando dados de **{mes_selecionado_label}/2025**")

# Carregar dados
df_entradas = carregar_entradas(mes_selecionado)
df_saidas = carregar_saidas(mes_selecionado)

# ============================================================================
# SEÇÃO 1: ENTRADAS (RECEITAS)
# ============================================================================

st.markdown('<div class="section-header">💰 ENTRADAS / RECEITAS</div>', unsafe_allow_html=True)

if df_entradas.empty:
    st.warning(f"⚠️ Nenhum dado de entrada encontrado para {mes_selecionado_label}")
else:
    # KPIs de Entradas
    col1, col2, col3, col4 = st.columns(4)

    total_entradas = df_entradas['Valor'].sum()
    qtd_entradas = len(df_entradas)
    media_entrada = df_entradas['Valor'].mean()
    maior_entrada = df_entradas['Valor'].max()

    with col1:
        st.metric(
            label="💵 Total de Entradas",
            value=formatar_real(total_entradas)
        )

    with col2:
        st.metric(
            label="📝 Quantidade de Lançamentos",
            value=f"{qtd_entradas:,}".replace(",", ".")
        )

    with col3:
        st.metric(
            label="📈 Média por Lançamento",
            value=formatar_real(media_entrada)
        )

    with col4:
        st.metric(
            label="🔝 Maior Entrada",
            value=formatar_real(maior_entrada)
        )

    st.markdown("---")

    # Gráficos de Entradas
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📊 Entradas por Centro de Custo")

        if 'Centro de Custo' in df_entradas.columns:
            entradas_por_centro = df_entradas.groupby('Centro de Custo')['Valor'].sum().reset_index()
            entradas_por_centro = entradas_por_centro.sort_values('Valor', ascending=False)

            fig_entrada_centro = px.pie(
                entradas_por_centro,
                values='Valor',
                names='Centro de Custo',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_entrada_centro.update_layout(height=400)
            fig_entrada_centro.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
            )
            st.plotly_chart(fig_entrada_centro, use_container_width=True)

    with col_g2:
        st.subheader("📅 Evolução Diária de Entradas")

        if 'Data Lançamento' in df_entradas.columns:
            entradas_por_dia = df_entradas.groupby(df_entradas['Data Lançamento'].dt.date)['Valor'].sum().reset_index()
            entradas_por_dia.columns = ['Data', 'Valor']

            fig_entrada_dia = px.bar(
                entradas_por_dia,
                x='Data',
                y='Valor',
                color='Valor',
                color_continuous_scale='Greens',
                labels={'Valor': 'Valor (R$)', 'Data': 'Data'}
            )
            fig_entrada_dia.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                height=400
            )
            fig_entrada_dia.update_traces(
                hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig_entrada_dia, use_container_width=True)

    st.markdown("---")

    # Tabela Detalhada de Entradas
    st.subheader("📋 Detalhamento das Entradas")

    # Filtros para Entradas
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        if 'Centro de Custo' in df_entradas.columns:
            centros_entrada = ['Todos'] + sorted(df_entradas['Centro de Custo'].dropna().unique().tolist())
            centro_filtro_entrada = st.selectbox(
                "Centro de Custo (Entradas)",
                options=centros_entrada,
                index=0,
                key="centro_entrada"
            )

    with col_f2:
        if 'Especificação' in df_entradas.columns:
            specs_entrada = ['Todas'] + sorted(df_entradas['Especificação'].dropna().unique().tolist())
            spec_filtro_entrada = st.selectbox(
                "Especificação (Entradas)",
                options=specs_entrada,
                index=0,
                key="spec_entrada"
            )

    with col_f3:
        ordenar_entrada = st.selectbox(
            "Ordenar por",
            options=['Data', 'Valor (Maior)', 'Valor (Menor)', 'Centro de Custo'],
            index=0,
            key="ordenar_entrada"
        )

    # Busca e limite
    col_f4, col_f5 = st.columns(2)

    with col_f4:
        busca_entrada = st.text_input("🔍 Buscar nas Entradas:", "", key="busca_entrada")

    with col_f5:
        limite_entrada = st.selectbox(
            "Exibir registros",
            options=['Todos', '25', '50', '100', '200'],
            index=0,
            key="limite_entrada"
        )

    # Aplicar filtros
    df_entradas_filtrado = df_entradas.copy()

    if 'Centro de Custo' in df_entradas.columns and centro_filtro_entrada != 'Todos':
        df_entradas_filtrado = df_entradas_filtrado[df_entradas_filtrado['Centro de Custo'] == centro_filtro_entrada]

    if 'Especificação' in df_entradas.columns and spec_filtro_entrada != 'Todas':
        df_entradas_filtrado = df_entradas_filtrado[df_entradas_filtrado['Especificação'] == spec_filtro_entrada]

    if busca_entrada:
        mask = pd.Series([False] * len(df_entradas_filtrado))
        for col in ['Especificação', 'Observação', 'Centro de Custo', 'Pessoa']:
            if col in df_entradas_filtrado.columns:
                mask = mask | df_entradas_filtrado[col].astype(str).str.contains(busca_entrada, case=False, na=False)
        df_entradas_filtrado = df_entradas_filtrado[mask]

    # Ordenar
    if ordenar_entrada == 'Valor (Maior)':
        df_entradas_filtrado = df_entradas_filtrado.sort_values('Valor', ascending=False)
    elif ordenar_entrada == 'Valor (Menor)':
        df_entradas_filtrado = df_entradas_filtrado.sort_values('Valor', ascending=True)
    elif ordenar_entrada == 'Centro de Custo' and 'Centro de Custo' in df_entradas_filtrado.columns:
        df_entradas_filtrado = df_entradas_filtrado.sort_values('Centro de Custo')
    else:
        if 'Data Lançamento' in df_entradas_filtrado.columns:
            df_entradas_filtrado = df_entradas_filtrado.sort_values('Data Lançamento')

    # Aplicar limite
    if limite_entrada != 'Todos':
        df_entradas_filtrado = df_entradas_filtrado.head(int(limite_entrada))

    # Preparar colunas para exibição
    colunas_exibir_entrada = []
    for col in ['Data Lançamento', 'Especificação', 'Centro de Custo', 'Valor', 'Observação', 'Pessoa', 'Conta', 'Forma de Pagamento']:
        if col in df_entradas_filtrado.columns:
            colunas_exibir_entrada.append(col)

    df_entrada_display = df_entradas_filtrado[colunas_exibir_entrada].copy()

    # Formatar valor e data
    if 'Valor' in df_entrada_display.columns:
        df_entrada_display['Valor'] = df_entrada_display['Valor'].apply(formatar_real)
    if 'Data Lançamento' in df_entrada_display.columns:
        df_entrada_display['Data Lançamento'] = df_entrada_display['Data Lançamento'].dt.strftime('%d/%m/%Y')

    st.caption(f"Exibindo {len(df_entradas_filtrado)} de {len(df_entradas)} registros")

    st.dataframe(
        df_entrada_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Estatísticas da seleção
    if len(df_entradas_filtrado) > 0:
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("Total da Seleção", formatar_real(df_entradas_filtrado['Valor'].sum()))
        with col_stat2:
            st.metric("Média da Seleção", formatar_real(df_entradas_filtrado['Valor'].mean()))
        with col_stat3:
            st.metric("Maior Valor", formatar_real(df_entradas_filtrado['Valor'].max()))
        with col_stat4:
            st.metric("Menor Valor", formatar_real(df_entradas_filtrado['Valor'].min()))

    # Download
    col_down1, col_down2 = st.columns(2)
    with col_down1:
        st.download_button(
            label="📥 Baixar seleção atual (CSV)",
            data=df_entradas_filtrado.to_csv(index=False).encode('utf-8'),
            file_name=f"entradas_{mes_selecionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_entrada_selecao"
        )
    with col_down2:
        st.download_button(
            label="📥 Baixar todas entradas (CSV)",
            data=df_entradas.to_csv(index=False).encode('utf-8'),
            file_name=f"entradas_{mes_selecionado}_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_entrada_todas"
        )

st.markdown("---")
st.markdown("---")

# ============================================================================
# SEÇÃO 2: SAÍDAS (DESPESAS)
# ============================================================================

st.markdown('<div class="section-header">💸 SAÍDAS / DESPESAS</div>', unsafe_allow_html=True)

if df_saidas.empty:
    st.warning(f"⚠️ Nenhum dado de saída encontrado para {mes_selecionado_label}")
else:
    # KPIs de Saídas
    col1, col2, col3, col4 = st.columns(4)

    total_saidas = df_saidas['Valor'].sum()
    qtd_saidas = len(df_saidas)
    media_saida = df_saidas['Valor'].mean()
    maior_saida = df_saidas['Valor'].max()

    with col1:
        st.metric(
            label="💸 Total de Saídas",
            value=formatar_real(total_saidas)
        )

    with col2:
        st.metric(
            label="📝 Quantidade de Lançamentos",
            value=f"{qtd_saidas:,}".replace(",", ".")
        )

    with col3:
        st.metric(
            label="📈 Média por Lançamento",
            value=formatar_real(media_saida)
        )

    with col4:
        st.metric(
            label="🔝 Maior Saída",
            value=formatar_real(maior_saida)
        )

    # KPI de Saldo
    if not df_entradas.empty:
        st.markdown("---")
        col_saldo1, col_saldo2, col_saldo3 = st.columns(3)

        saldo = total_entradas - total_saidas
        percentual_gasto = (total_saidas / total_entradas * 100) if total_entradas > 0 else 0

        with col_saldo1:
            st.metric(
                label="📊 Saldo do Mês",
                value=formatar_real(saldo),
                delta=f"{saldo/total_entradas*100:.1f}% das entradas" if total_entradas > 0 else "N/A"
            )

        with col_saldo2:
            st.metric(
                label="📉 % Despesas/Receitas",
                value=f"{percentual_gasto:.1f}%"
            )

        with col_saldo3:
            status = "✅ Superávit" if saldo >= 0 else "⚠️ Déficit"
            st.metric(
                label="Status",
                value=status
            )

    st.markdown("---")

    # Gráficos de Saídas
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📊 Saídas por Centro de Custo")

        if 'Centro de Custo' in df_saidas.columns:
            saidas_por_centro = df_saidas.groupby('Centro de Custo')['Valor'].sum().reset_index()
            saidas_por_centro = saidas_por_centro.sort_values('Valor', ascending=False)

            fig_saida_centro = px.pie(
                saidas_por_centro,
                values='Valor',
                names='Centro de Custo',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig_saida_centro.update_layout(height=400)
            fig_saida_centro.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
            )
            st.plotly_chart(fig_saida_centro, use_container_width=True)

    with col_g2:
        st.subheader("📅 Evolução Diária de Saídas")

        if 'Data Lançamento' in df_saidas.columns:
            saidas_por_dia = df_saidas.groupby(df_saidas['Data Lançamento'].dt.date)['Valor'].sum().reset_index()
            saidas_por_dia.columns = ['Data', 'Valor']

            fig_saida_dia = px.bar(
                saidas_por_dia,
                x='Data',
                y='Valor',
                color='Valor',
                color_continuous_scale='Reds',
                labels={'Valor': 'Valor (R$)', 'Data': 'Data'}
            )
            fig_saida_dia.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                height=400
            )
            fig_saida_dia.update_traces(
                hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig_saida_dia, use_container_width=True)

    st.markdown("---")

    # Gráfico Comparativo
    if not df_entradas.empty:
        st.subheader("📊 Comparativo Entradas x Saídas")

        fig_comparativo = go.Figure()

        fig_comparativo.add_trace(go.Bar(
            name='Entradas',
            x=['Total'],
            y=[total_entradas],
            marker_color='#2ecc71',
            text=[formatar_real(total_entradas)],
            textposition='auto',
            hovertemplate="<b>Entradas</b><br>R$ %{y:,.2f}<extra></extra>"
        ))

        fig_comparativo.add_trace(go.Bar(
            name='Saídas',
            x=['Total'],
            y=[total_saidas],
            marker_color='#e74c3c',
            text=[formatar_real(total_saidas)],
            textposition='auto',
            hovertemplate="<b>Saídas</b><br>R$ %{y:,.2f}<extra></extra>"
        ))

        fig_comparativo.add_trace(go.Scatter(
            name='Saldo',
            x=['Total'],
            y=[saldo],
            mode='markers+text',
            marker=dict(color='#3498db', size=20),
            text=[formatar_real(saldo)],
            textposition='top center',
            hovertemplate="<b>Saldo</b><br>R$ %{y:,.2f}<extra></extra>"
        ))

        fig_comparativo.update_layout(
            barmode='group',
            height=400,
            yaxis_title="Valor (R$)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)

        st.markdown("---")

    # Top 10 Maiores Despesas
    st.subheader("🔝 Top 10 Maiores Despesas")

    if 'Especificação' in df_saidas.columns:
        top_saidas = df_saidas.nlargest(10, 'Valor')[['Especificação', 'Valor', 'Centro de Custo', 'Data Lançamento']].copy()
        top_saidas['Especificação_Curta'] = top_saidas['Especificação'].apply(
            lambda x: x[:50] + '...' if len(str(x)) > 50 else x
        )

        fig_top_saidas = px.bar(
            top_saidas,
            x='Valor',
            y='Especificação_Curta',
            orientation='h',
            color='Valor',
            color_continuous_scale='Reds',
            labels={'Valor': 'Valor (R$)', 'Especificação_Curta': 'Especificação'}
        )
        fig_top_saidas.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig_top_saidas.update_traces(
            hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>"
        )
        st.plotly_chart(fig_top_saidas, use_container_width=True)

    st.markdown("---")

    # Tabela Detalhada de Saídas
    st.subheader("📋 Detalhamento das Saídas")

    # Filtros para Saídas
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        if 'Centro de Custo' in df_saidas.columns:
            centros_saida = ['Todos'] + sorted(df_saidas['Centro de Custo'].dropna().unique().tolist())
            centro_filtro_saida = st.selectbox(
                "Centro de Custo (Saídas)",
                options=centros_saida,
                index=0,
                key="centro_saida"
            )

    with col_f2:
        if 'Especificação' in df_saidas.columns:
            specs_saida = ['Todas'] + sorted(df_saidas['Especificação'].dropna().unique().tolist())
            spec_filtro_saida = st.selectbox(
                "Especificação (Saídas)",
                options=specs_saida,
                index=0,
                key="spec_saida"
            )

    with col_f3:
        ordenar_saida = st.selectbox(
            "Ordenar por",
            options=['Data', 'Valor (Maior)', 'Valor (Menor)', 'Centro de Custo'],
            index=0,
            key="ordenar_saida"
        )

    # Busca e limite
    col_f4, col_f5 = st.columns(2)

    with col_f4:
        busca_saida = st.text_input("🔍 Buscar nas Saídas:", "", key="busca_saida")

    with col_f5:
        limite_saida = st.selectbox(
            "Exibir registros",
            options=['Todos', '25', '50', '100', '200'],
            index=0,
            key="limite_saida"
        )

    # Aplicar filtros
    df_saidas_filtrado = df_saidas.copy()

    if 'Centro de Custo' in df_saidas.columns and centro_filtro_saida != 'Todos':
        df_saidas_filtrado = df_saidas_filtrado[df_saidas_filtrado['Centro de Custo'] == centro_filtro_saida]

    if 'Especificação' in df_saidas.columns and spec_filtro_saida != 'Todas':
        df_saidas_filtrado = df_saidas_filtrado[df_saidas_filtrado['Especificação'] == spec_filtro_saida]

    if busca_saida:
        mask = pd.Series([False] * len(df_saidas_filtrado))
        for col in ['Especificação', 'Observação', 'Centro de Custo', 'Fornecedor', 'Histórico']:
            if col in df_saidas_filtrado.columns:
                mask = mask | df_saidas_filtrado[col].astype(str).str.contains(busca_saida, case=False, na=False)
        df_saidas_filtrado = df_saidas_filtrado[mask]

    # Ordenar
    if ordenar_saida == 'Valor (Maior)':
        df_saidas_filtrado = df_saidas_filtrado.sort_values('Valor', ascending=False)
    elif ordenar_saida == 'Valor (Menor)':
        df_saidas_filtrado = df_saidas_filtrado.sort_values('Valor', ascending=True)
    elif ordenar_saida == 'Centro de Custo' and 'Centro de Custo' in df_saidas_filtrado.columns:
        df_saidas_filtrado = df_saidas_filtrado.sort_values('Centro de Custo')
    else:
        if 'Data Lançamento' in df_saidas_filtrado.columns:
            df_saidas_filtrado = df_saidas_filtrado.sort_values('Data Lançamento')

    # Aplicar limite
    if limite_saida != 'Todos':
        df_saidas_filtrado = df_saidas_filtrado.head(int(limite_saida))

    # Preparar colunas para exibição
    colunas_exibir_saida = []
    for col in ['Data Lançamento', 'Especificação', 'Centro de Custo', 'Valor', 'Observação', 'Histórico', 'Fornecedor', 'Conta', 'Forma de Pagamento']:
        if col in df_saidas_filtrado.columns:
            colunas_exibir_saida.append(col)

    df_saida_display = df_saidas_filtrado[colunas_exibir_saida].copy()

    # Formatar valor e data
    if 'Valor' in df_saida_display.columns:
        df_saida_display['Valor'] = df_saida_display['Valor'].apply(formatar_real)
    if 'Data Lançamento' in df_saida_display.columns:
        df_saida_display['Data Lançamento'] = df_saida_display['Data Lançamento'].dt.strftime('%d/%m/%Y')

    st.caption(f"Exibindo {len(df_saidas_filtrado)} de {len(df_saidas)} registros")

    st.dataframe(
        df_saida_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Estatísticas da seleção
    if len(df_saidas_filtrado) > 0:
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("Total da Seleção", formatar_real(df_saidas_filtrado['Valor'].sum()))
        with col_stat2:
            st.metric("Média da Seleção", formatar_real(df_saidas_filtrado['Valor'].mean()))
        with col_stat3:
            st.metric("Maior Valor", formatar_real(df_saidas_filtrado['Valor'].max()))
        with col_stat4:
            st.metric("Menor Valor", formatar_real(df_saidas_filtrado['Valor'].min()))

    # Download
    col_down1, col_down2 = st.columns(2)
    with col_down1:
        st.download_button(
            label="📥 Baixar seleção atual (CSV)",
            data=df_saidas_filtrado.to_csv(index=False).encode('utf-8'),
            file_name=f"saidas_{mes_selecionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_saida_selecao"
        )
    with col_down2:
        st.download_button(
            label="📥 Baixar todas saídas (CSV)",
            data=df_saidas.to_csv(index=False).encode('utf-8'),
            file_name=f"saidas_{mes_selecionado}_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_saida_todas"
        )

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Dashboard Mensal IPB - {mes_selecionado_label}/2025 | Desenvolvido com Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
