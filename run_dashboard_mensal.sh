#!/bin/bash

# Script para executar o Dashboard Mensal IPB
# Uso: ./run_dashboard_mensal.sh

echo "================================================"
echo "    Dashboard Mensal IPB Rio Preto 2025"
echo "================================================"
echo ""
echo "Iniciando o dashboard..."
echo ""

# Executar o streamlit
python3 -m streamlit run dashboard_mensal.py

# Se der erro, tentar com streamlit direto
if [ $? -ne 0 ]; then
    echo ""
    echo "Tentando iniciar com 'streamlit' direto..."
    streamlit run dashboard_mensal.py
fi
