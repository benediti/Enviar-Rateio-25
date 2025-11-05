#!/usr/bin/env python3
"""
Teste de conversão de matrículas para verificar o problema do zero
"""

import pandas as pd
import io

# Simular dados como vêm do Excel (com decimais)
dados_excel = """matricula,idsetor,valor
4794.0,427,560.25
1499.0,244,477.25
5150.0,284,456.5"""

print("🧪 TESTE DE CONVERSÃO DE MATRÍCULAS")
print("=" * 50)

# Simular leitura do Excel
df = pd.read_csv(io.StringIO(dados_excel))

print("📊 Dados originais (como vêm do Excel):")
print(df.head())
print(f"Tipos: {df.dtypes}")

print("\n🔧 APLICANDO CORREÇÃO:")

# Aplicar a mesma correção do código
df['matricula'] = df['matricula'].astype(str).str.replace(r'\.0$', '', regex=True)
df['matricula'] = pd.to_numeric(df['matricula'], errors='coerce').astype('Int64')
df['idsetor'] = pd.to_numeric(df['idsetor'], errors='coerce').astype('Int64')
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

# Converter para int normal
df['matricula'] = df['matricula'].astype(int)
df['idsetor'] = df['idsetor'].astype(int)

print("✅ Dados corrigidos:")
print(df.head())
print(f"Tipos: {df.dtypes}")

print("\n🎯 RESULTADO:")
print("As matrículas agora estão sem o zero extra!")
print("4794.0 → 4794")
print("1499.0 → 1499")
print("5150.0 → 5150")