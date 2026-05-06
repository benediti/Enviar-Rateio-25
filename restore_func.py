import pandas as pd

df = pd.read_excel('projeto/FUNC.xlsx')
print(f'Antes: {len(df)} registros')

# Manter apenas os funcionários reais (matrícula >= 30)
df_original = df[df['matricula'] >= 30]

# Salvar
df_original.to_excel('projeto/FUNC.xlsx', index=False, engine='openpyxl')

# Verificar
df_check = pd.read_excel('projeto/FUNC.xlsx')
print(f'Depois: {len(df_check)} registros')
print(f'Matrículas: {df_check["matricula"].min()} a {df_check["matricula"].max()}')
