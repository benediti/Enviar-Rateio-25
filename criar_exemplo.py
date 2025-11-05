#!/usr/bin/env python3
"""
Criar arquivo Excel de exemplo com os dados fornecidos
"""

import pandas as pd
import os

# Dados fornecidos pelo usuário
dados = [
    [4794, 427, 560.25],
    [1499, 244, 477.25],
    [5150, 284, 456.5],
    [5127, 405, 456.5],
    [5257, 294, 311.25],
    [4433, 294, 332],
    [4734, 294, 477.25],
    [3709, 294, 477.25],
    [4820, 294, 477.25],
    [236, 294, 166],
    [4039, 293, 576.15],
    [4902, 293, 576.15],
    [3727, 342, 815],
    [5130, 64, 477.25],
    [5108, 64, 681.6],
    [5265, 64, 269.75],
    [5235, 64, 880.2],
    [3908, 211, 477.25],
    [3528, 211, 477.25],
    [4739, 105, 477.25],
    [4530, 105, 477.25],
    [5084, 217, 477.25],
    [4390, 160, 477.25],
    [4262, 379, 477.25],
    [5251, 353, 435.75],
    [1221, 352, 560.25],
    [5078, 352, 394.25],
    [4509, 352, 83],
    [5157, 352, 560.25],
    [4838, 352, 560.25],
    [5082, 352, 477.25],
    [5242, 352, 560.25],
    [4908, 338, 62.25],
    [2063, 439, 477.25],
    [4896, 383, 560.25],
    [3874, 413, 62.25],
    [4668, 248, 560.25],
    [4683, 406, 560.25],
    [5170, 353, 207.5],
    [2916, 64, 145.25],
    [5118, 217, 124.5]
]

# Criar DataFrame
df = pd.DataFrame(dados, columns=['matricula', 'idsetor', 'valor'])

# Salvar como Excel
arquivo_saida = "Exemplo_Dados_Beneficios.xlsx"
df.to_excel(arquivo_saida, index=False, engine='openpyxl')

print(f"✅ Arquivo criado: {arquivo_saida}")
print(f"📊 Registros: {len(df)}")
print(f"💰 Valor total: R$ {df['valor'].sum():,.2f}")
print("\n👁️ Primeiros 5 registros:")
print(df.head().to_string(index=False))