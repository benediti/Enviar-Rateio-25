import pandas as pd
import uuid

# Ler FUNC.xlsx
df = pd.read_excel('projeto/FUNC.xlsx')
print(f"FUNC.xlsx antes: {len(df)} registros")
print(f"Matrículas atuais: {df['matricula'].min()} a {df['matricula'].max()}\n")

# Criar novos registros para matrículas 0-101
novos_registros = []
for i in range(102):  # 0 a 101
    if i not in df['matricula'].values:  # Só adiciona se não existir
        novos_registros.append({
            'matricula': i,
            'nome': f'FUNCIONÁRIO {i:03d}',
            'Coluna2': str(uuid.uuid4())
        })

print(f"Novos registros a adicionar: {len(novos_registros)}\n")

if novos_registros:
    df_novos = pd.DataFrame(novos_registros)
    df = pd.concat([df, df_novos], ignore_index=True)
    
    # Ordenar por matrícula
    df = df.sort_values('matricula').reset_index(drop=True)
    
    # Salvar com openpyxl para manter compatibilidade
    df.to_excel('projeto/FUNC.xlsx', index=False, engine='openpyxl')
    print(f"✅ FUNC.xlsx atualizado: {len(df)} registros")
    print(f"Matrículas agora: {df['matricula'].min()} a {df['matricula'].max()}")
    print(f"\nNovos registros adicionados: {len(novos_registros)}")
else:
    print("Nenhum novo registro necessário")
