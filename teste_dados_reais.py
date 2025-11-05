#!/usr/bin/env python3
"""
Teste com os dados reais fornecidos pelo usuário
"""

import pandas as pd
import io

# Dados fornecidos pelo usuário
dados_texto = """matricula	idsetor	valor
4794	427	560.25
1499	244	477.25
5150	284	456.5
5127	405	456.5
5257	294	311.25
4433	294	332
4734	294	477.25
3709	294	477.25
4820	294	477.25
236	294	166
4039	293	576.15
4902	293	576.15
3727	342	815
5130	64	477.25
5108	64	681.6
5265	64	269.75
5235	64	880.2
3908	211	477.25
3528	211	477.25
4739	105	477.25
4530	105	477.25
5084	217	477.25
4390	160	477.25
4262	379	477.25
5251	353	435.75
1221	352	560.25
5078	352	394.25
4509	352	83
5157	352	560.25
4838	352	560.25
5082	352	477.25
5242	352	560.25
4908	338	62.25
2063	439	477.25
4896	383	560.25
3874	413	62.25
4668	248	560.25
4683	406	560.25
5170	353	207.5
2916	64	145.25
5118	217	124.5"""

def teste_processamento():
    print("🧪 TESTE COM DADOS REAIS")
    print("=" * 50)
    
    # Simular leitura do Excel
    df = pd.read_csv(io.StringIO(dados_texto), sep='\t')
    
    print(f"📊 Dados originais: {len(df)} registros")
    print(f"📋 Colunas: {list(df.columns)}")
    
    # Normalizar colunas (como faz o sistema)
    df.columns = df.columns.str.lower().str.strip()
    print(f"📋 Colunas normalizadas: {list(df.columns)}")
    
    # Verificar colunas obrigatórias
    required_columns = ['matricula', 'idsetor', 'valor']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Colunas faltando: {missing_columns}")
        return
    
    print("✅ Todas as colunas obrigatórias encontradas!")
    
    # Limpeza de dados
    registros_originais = len(df)
    
    # Remove vazios
    df = df.dropna(how='all')
    df = df.dropna(subset=['matricula', 'idsetor', 'valor'])
    
    # Remove duplicatas
    df = df.drop_duplicates()
    
    # Converte tipos
    df['matricula'] = pd.to_numeric(df['matricula'], errors='coerce')
    df['idsetor'] = pd.to_numeric(df['idsetor'], errors='coerce')
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    
    # Remove inválidos
    df = df.dropna(subset=['matricula', 'idsetor', 'valor'])
    df = df[
        (df['matricula'] > 0) & 
        (df['idsetor'] > 0) & 
        (df['valor'] > 0)
    ]
    
    registros_limpos = len(df)
    
    print(f"🧹 Limpeza: {registros_originais - registros_limpos} registros removidos")
    print(f"📊 Registros finais: {registros_limpos}")
    
    # Estatísticas
    matriculas_unicas = df['matricula'].nunique()
    setores_unicos = df['idsetor'].nunique()
    valor_total = df['valor'].sum()
    
    print("\n📈 ESTATÍSTICAS FINAIS:")
    print(f"👥 Matrículas únicas: {matriculas_unicas}")
    print(f"🏢 Setores únicos: {setores_unicos}")
    print(f"💰 Valor total: R$ {valor_total:,.2f}")
    
    # Primeiros registros
    print("\n👁️ PRIMEIROS 5 REGISTROS:")
    print(df.head().to_string(index=False))
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("O sistema agora deve processar seus dados corretamente.")

if __name__ == "__main__":
    teste_processamento()