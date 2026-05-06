import pandas as pd

df_func = pd.read_excel('projeto/FUNC.xlsx')

print('=== FUNC.xlsx - Estrutura ===')
print(f'Total de funcionários: {len(df_func)}')
print(f'Matrículas: {df_func["matricula"].min()} a {df_func["matricula"].max()}')
print(f'\nTodas as matrículas e nomes:')
print(df_func[['matricula', 'nome']].sort_values('matricula').to_string())
