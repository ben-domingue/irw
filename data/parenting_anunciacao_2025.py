import pandas as pd
import re

def process_parenting_data_final(file_path):
    df = pd.read_excel(file_path)

    df['id'] = range(1, len(df) + 1)
    df = df.drop(['Unnamed: 1'], axis=1)

    demo_map = {
        'Carimbo de data/hora': 'date',
        '1. Idade': 'cov_age',
        '2. Membro da família': 'cov_family_member',
        '3. Configuração familiar': 'cov_family_configuration',
        '4. Escolaridade': 'cov_education_level',
        '5. Em que estado você reside?': 'cov_state',
        '6. Em comparação com a sua cidade, em qual classe social você se encontra?': 'cov_social_class',
        '7. Quantos filhos você tem?': 'cov_children_count',
        'Nome completo e idade do(s) seu(s) filho(s)': 'cov_children_details',
        'Se você deseja escrever algum comentário (impressões, críticas, depoimentos, sugestões etc), utilize este espaço:': 'cov_comments'
    }
    
    df.rename(columns=demo_map, inplace=True)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = df['date'].apply(lambda x: x.timestamp() if pd.notnull(x) else None)

    cov_cols = list(demo_map.values())
    
    constructs = {
        'goals': [],
        'values': [],
        'affect': [],
        'rejection': [],
        'materialism': [],
        'material_rewards': []
    }
    
    item_cols = [c for c in df.columns if c != 'id' and c not in cov_cols]
    
    affect_keywords = [
        'fonte de encorajamento',
        'fonte de conforto',
        'elogio suas realizações',
        'coisas divertidas juntos'
    ]
    
    rejection_keywords = [
        'decepcionado',
        'ocupada',
        'evitar meu filho'
    ]
    
    mat_keywords = [
        'bens materiais', 'casas, carros', 'sinal de sucesso', 
        'bem sucedido', 'impressionam', 'vida simples', 'coisas que eu tenho', 
        'Comprar coisas', 'luxo', 'admiro pessoas'
    ]

    for col in item_cols:
        if re.search(r'\[\s*[A-ZÃÁÂÀÉÊÍÓÔÕÚÇ\s]+\.', col):
            constructs['values'].append(col)
            continue
            
        if 'Aprender' in col or 'Desenvolver' in col:
            constructs['goals'].append(col)
            continue
            
        if 'faz algo positivo' in col or 'tira boas notas' in col:
            continue
            
        if 'compra coisas para seu filho(a) só porque ele(a) quer' in col:
            constructs['material_rewards'].append(col)
            continue
            
        is_mat = False
        for k in mat_keywords:
            if k in col:
                constructs['materialism'].append(col)
                is_mat = True
                break
        if is_mat: continue
        
        for k in affect_keywords:
            if k in col:
                constructs['affect'].append(col)
                break
                
        for k in rejection_keywords:
            if k in col:
                constructs['rejection'].append(col)
                break

    output_files = []
    
    for name, cols in constructs.items():
        if not cols:
            continue
            
        valid_cols = [c for c in cols if c in df.columns]
        existing_covs = [c for c in cov_cols if c in df.columns]
        
        melted = df.melt(id_vars=['id'] + existing_covs, 
                         value_vars=valid_cols, 
                         var_name='item', value_name='resp')
        
        melted.dropna(subset=['resp'], inplace=True)

        cols_order = ['id', 'item', 'resp'] + existing_covs
        final_df = melted[cols_order]
        final_df.sort_values(by=['id', 'item'], inplace=True)
        
        filename = f"parenting_anunciacao_2025_{name}.csv"
        final_df.to_csv(filename, index=False)
        output_files.append(filename)
        print(f"Saved: {filename}")
        
    return output_files

if __name__ == "__main__":
    filename = "O exercício da parentalidade em diferentes configurações familiares_ trajetórias de socialização de valores e atitudes materialistas (respostas).xlsx"
    process_parenting_data_final(filename)