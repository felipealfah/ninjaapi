import pandas as pd
import requests
import json

# Obter dados da API
url = "http://api.fulled.com.br/clickbank"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    data_analise = data.get("ultima_atualizacao", None)  # Extrair a data da análise

    df = pd.DataFrame(data['dados'])

    # Selecionar as colunas necessárias para análise
    colunas_necessarias = [
        "nome_produto", "trafego_mes_atual", "trafego_mes_anterior", 
        "trafego_dois_meses_atras", "gravity_dia", "gravity_7d", 
        "gravity_15d", "gravity_30d", "gravity_45d", "gravity_60d", "gravity_90d"
    ]
    df = df[colunas_necessarias]

    # Função para calcular a variação percentual com verificações para evitar None e limitar a 100%
    def calcular_variacao_percentual(valor_anterior, valor_atual):
        if valor_anterior is None or valor_atual is None or valor_anterior == 0:
            return 0  # Retornamos 0 quando não é possível calcular a variação
        else:
            variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
            return max(min(variacao, 100), -100)  # Limitar a variação a um máximo de 100%

    # Função para calcular aumento e queda acumulada para tráfego e uma diminuição contínua para gravity
    def calcular_acumulado(row):
        # Cálculo do aumento acumulado de tráfego
        aumento_trafego = (
            calcular_variacao_percentual(row['trafego_dois_meses_atras'], row['trafego_mes_anterior']) +
            calcular_variacao_percentual(row['trafego_mes_anterior'], row['trafego_mes_atual'])
        )
        
        # Valores iniciais e finais de tráfego
        trafego_inicial = row['trafego_dois_meses_atras']
        trafego_final = row['trafego_mes_atual']
        
        # Cálculo da diminuição contínua para gravity (90d até gravity_dia)
        queda_gravity = 0
        gravity_periodos = ['gravity_90d', 'gravity_60d', 'gravity_45d', 'gravity_30d', 'gravity_15d', 'gravity_7d', 'gravity_dia']
        for i in range(len(gravity_periodos) - 1):
            queda_gravity += calcular_variacao_percentual(row[gravity_periodos[i]], row[gravity_periodos[i + 1]])

        # Valores iniciais e finais de gravity
        gravity_inicial = row['gravity_90d']
        gravity_final = row['gravity_dia']
        
        return aumento_trafego, trafego_inicial, trafego_final, queda_gravity, gravity_inicial, gravity_final

    # Calcular aumento acumulado para tráfego e diminuição contínua para gravity
    df[['aumento_trafego', 'trafego_inicial', 'trafego_final', 'queda_gravity', 'gravity_inicial', 'gravity_final']] = \
        df.apply(lambda x: pd.Series(calcular_acumulado(x)), axis=1)

    # Calcular variações simples de tráfego e gravity entre os últimos períodos
    df['variacao_trafego'] = df.apply(lambda x: calcular_variacao_percentual(x['trafego_mes_anterior'], x['trafego_mes_atual']), axis=1)
    df['variacao_gravity'] = df.apply(lambda x: calcular_variacao_percentual(x['gravity_90d'], x['gravity_dia']), axis=1)

    # Análise de Crescimento - Filtrar produtos com crescimento mínimo de 16%
    df_crescimento = df[(df['aumento_trafego'].notnull()) & (df['aumento_trafego'] >= 16) &
                        (df['variacao_gravity'].notnull()) & (df['variacao_gravity'] >= 16)]
    top_5_crescimento = df_crescimento.sort_values(by=['aumento_trafego', 'variacao_gravity'], ascending=False).head(5)

    # Relatório para produtos em crescimento
    relatorio_crescimento = {
        "top_produtos_crescimento": [
            {
                "nome_produto": row["nome_produto"],
                "crescimento_trafego": f"O produto {row['nome_produto']} teve um crescimento de tráfego de {row['aumento_trafego']:.2f}% passando de {row['trafego_inicial']} para {row['trafego_final']}.",
                "crescimento_gravity": f"Gravity teve um crescimento de {row['variacao_gravity']:.2f}% passando de {row['gravity_inicial']} para {row['gravity_final']}."
            }
            for _, row in top_5_crescimento.iterrows()
        ]
    }

    # Análise de Platô - Filtrar produtos com variação entre -15% e +15%
    df_plato = df[(df['variacao_trafego'].notnull()) & (df['variacao_gravity'].notnull()) &
                  (df['variacao_trafego'].abs() <= 15) & (df['variacao_gravity'].abs() <= 15)].copy()
    df_plato.loc[:, 'variacao_total'] = df_plato['variacao_trafego'].abs() + df_plato['variacao_gravity'].abs()
    top_5_plato = df_plato.sort_values(by='variacao_total').head(5)

    # Relatório para produtos em platô
    relatorio_plato = {
        "produtos_em_plato": [
            {
                "nome_produto": row["nome_produto"],
                "variacao_trafego": f"O produto {row['nome_produto']} teve uma variação de tráfego de {abs(row['variacao_trafego']):.2f}% de {'crescimento' if row['variacao_trafego'] >= 0 else 'queda'}, passando de {row['trafego_inicial']} para {row['trafego_final']}.",
                "variacao_gravity": f"Gravity teve uma variação de {abs(row['variacao_gravity']):.2f}% de {'crescimento' if row['variacao_gravity'] >= 0 else 'queda'}, passando de {row['gravity_inicial']} para {row['gravity_final']}."
            }
            for _, row in top_5_plato.iterrows()
        ]
    }

    # Análise de Produtos para Anúncios - Aumento de tráfego e queda contínua em gravity
    df_anunciar = df[(df['aumento_trafego'] > 15) & (df['queda_gravity'] < -15)]
    top_5_anunciar = df_anunciar.sort_values(by=['aumento_trafego', 'queda_gravity'], ascending=[False, True]).head(5)

    # Relatório para produtos para anúncio
    relatorio_anunciar = {
        "produtos_para_anunciar": [
            {
                "nome_produto": row["nome_produto"],
                "aumento_trafego": f"O produto {row['nome_produto']} teve um aumento de tráfego acumulado de {abs(row['aumento_trafego']):.2f}%, passando de {row['trafego_inicial']} para {row['trafego_final']}.",
                "queda_gravity": f"Gravity teve uma queda acumulada de {abs(row['queda_gravity']):.2f}%, passando de {row['gravity_inicial']} para {row['gravity_final']}."
            }
            for _, row in top_5_anunciar.iterrows()
        ]
    }

    # Análise de Queda - Filtrar produtos com queda acumulada maior que 15%
    df_queda = df[(df['aumento_trafego'].notnull()) & (df['aumento_trafego'] < -15) &
                  (df['queda_gravity'].notnull()) & (df['queda_gravity'] < -15)]
    top_5_queda = df_queda.sort_values(by=['aumento_trafego', 'queda_gravity']).head(5)

    # Relatório para produtos em queda
    relatorio_queda = {
        "top_produtos_queda": [
            {
                "nome_produto": row["nome_produto"],
                "queda_trafego": f"O produto {row['nome_produto']} teve uma queda de tráfego acumulada de {abs(row['aumento_trafego']):.2f}%, passando de {row['trafego_inicial']} para {row['trafego_final']}.",
                "queda_gravity": f"Gravity teve uma queda acumulada de {abs(row['queda_gravity']):.2f}%, passando de {row['gravity_inicial']} para {row['gravity_final']}."
            }
            for _, row in top_5_queda.iterrows()
        ]
    }

    # Combinar todos os relatórios em um único dicionário
    relatorio_final = {
        "data_analise": data_analise,
        "top_produtos_crescimento": relatorio_crescimento["top_produtos_crescimento"],
        "produtos_em_plato": relatorio_plato["produtos_em_plato"],
        "produtos_para_anunciar": relatorio_anunciar["produtos_para_anunciar"],
        "top_produtos_queda": relatorio_queda["top_produtos_queda"]
    }

    # Exibir o relatório final formatado
    print(json.dumps(relatorio_final, ensure_ascii=False, indent=4))
else:
    print("Erro ao acessar a API:", response.status_code)
