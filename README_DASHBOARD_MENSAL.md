# Dashboard Mensal - IPB Rio Preto

## 📋 Descrição

Dashboard interativo para visualização mensal de entradas (receitas) e saídas (despesas) da IPB Rio Preto. O sistema permite análise detalhada dos dados financeiros mensais com filtros avançados, gráficos e exportação de dados.

## 🚀 Como Executar

### 1. Certifique-se de ter as dependências instaladas:

```bash
pip3 install streamlit plotly openpyxl pandas
```

### 2. Execute o dashboard:

```bash
python3 -m streamlit run dashboard_mensal.py
```

Ou, se tiver o streamlit no PATH:

```bash
streamlit run dashboard_mensal.py
```

O dashboard abrirá automaticamente no seu navegador em `http://localhost:8501`

### 2b. Ou use o script auxiliar (mais fácil):

```bash
./run_dashboard_mensal.sh
```

## 📁 Estrutura de Arquivos

```
DashIPRioPreto/
├── dashboard_mensal.py          # Dashboard principal (mensal)
├── dashboard_despesas.py        # Dashboard anual existente
├── mensal/                      # Pasta com dados mensais
│   ├── dez-entradas.xlsx       # Entradas de dezembro
│   ├── dez-saidas.xlsx         # Saídas de dezembro
│   └── [outros meses]...       # Adicione mais meses aqui
```

## 📊 Funcionalidades

### Seção de ENTRADAS (Receitas)
- **KPIs Principais:**
  - Total de entradas do mês
  - Quantidade de lançamentos
  - Média por lançamento
  - Maior entrada

- **Gráficos:**
  - Pizza com distribuição por Centro de Custo
  - Evolução diária de entradas

- **Tabela Detalhada com Filtros:**
  - Filtro por Centro de Custo
  - Filtro por Especificação
  - Busca textual
  - Ordenação customizável
  - Limite de registros exibidos
  - Exportação para CSV

### Seção de SAÍDAS (Despesas)
- **KPIs Principais:**
  - Total de saídas do mês
  - Quantidade de lançamentos
  - Média por lançamento
  - Maior saída
  - Saldo do mês (Entradas - Saídas)
  - Percentual de despesas sobre receitas
  - Status (Superávit/Déficit)

- **Gráficos:**
  - Pizza com distribuição por Centro de Custo
  - Evolução diária de saídas
  - Comparativo Entradas x Saídas
  - Top 10 maiores despesas

- **Tabela Detalhada com Filtros:**
  - Filtro por Centro de Custo
  - Filtro por Especificação
  - Busca textual (busca em múltiplos campos)
  - Ordenação customizável
  - Limite de registros exibidos
  - Exportação para CSV

## 📅 Como Adicionar Novos Meses

Para adicionar dados de outros meses, siga este padrão de nomenclatura:

1. Crie os arquivos Excel na pasta `mensal/`:
   - `[mes]-entradas.xlsx` (ex: `jan-entradas.xlsx`, `fev-entradas.xlsx`)
   - `[mes]-saidas.xlsx` (ex: `jan-saidas.xlsx`, `fev-saidas.xlsx`)

2. Os arquivos devem conter as seguintes colunas principais:
   - **Data Lançamento** (obrigatório)
   - **Especificação** (obrigatório)
   - **Valor** (obrigatório)
   - **Centro de Custo** (opcional, mas recomendado)
   - **Observação** (opcional)
   - **Pessoa** (opcional)
   - **Conta** (opcional)
   - **Forma de Pagamento** (opcional)

3. O dashboard detectará automaticamente os novos meses disponíveis

## 🎨 Design e Interface

- Interface limpa e moderna
- Cores diferenciadas para entradas (verde) e saídas (vermelho)
- Seções claramente separadas
- Responsivo e otimizado para telas grandes
- Formatação em Real Brasileiro (R$)
- Datas no formato brasileiro (DD/MM/YYYY)

## 💡 Dicas de Uso

1. **Seleção de Mês:** Use o dropdown na barra lateral para escolher o mês desejado
2. **Filtros:** Combine múltiplos filtros para análises específicas
3. **Busca:** A busca funciona em múltiplos campos simultaneamente
4. **Exportação:** Use os botões de download para exportar:
   - Seleção atual (com filtros aplicados)
   - Todos os dados do mês
5. **Estatísticas:** Observe as métricas no rodapé das tabelas para resumo da seleção

## 📈 Comparativos Disponíveis

- **Entradas x Saídas:** Gráfico comparativo mostrando o saldo mensal
- **Evolução Diária:** Acompanhe a distribuição temporal dos lançamentos
- **Por Centro de Custo:** Visualize a distribuição de recursos por área
- **Top Despesas:** Identifique rapidamente os maiores gastos do mês

## 🔄 Atualizações

Para atualizar os dados:
1. Substitua os arquivos Excel na pasta `mensal/`
2. Recarregue a página do dashboard (F5)
3. O cache será automaticamente limpo e os novos dados carregados

---

**Desenvolvido com Streamlit** | IPB Rio Preto 2025
