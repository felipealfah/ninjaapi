import pandas as pd
from dash import get_df_bruto, transform_data

def get_crescimento_df():
    # Carregar e transformar dados brutos
    df_bruto = get_df_bruto()
    df_transf = transform_data(df_bruto)

    if df_transf.empty:
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

    # Filtrar produtos com tráfego mínimo de 5000 em cada um dos três períodos
    df_transf = df_transf[(df_transf['Trafego do mês'] >= 2000) & 
                          (df_transf['Trafego mês anterior'] >= 2000) & 
                          (df_transf['Trafego dois meses atrás'] >= 2000)]

    # Calcular crescimento percentual para os dois períodos
    df_transf['Crescimento Mes Anterior (%)'] = ((df_transf['Trafego mês anterior'] - df_transf['Trafego dois meses atrás']) / df_transf['Trafego dois meses atrás']) * 100
    df_transf['Crescimento Mes Atual (%)'] = ((df_transf['Trafego do mês'] - df_transf['Trafego mês anterior']) / df_transf['Trafego mês anterior']) * 100

    # Filtrar produtos que apresentaram crescimento superior a 15% no mês anterior em relação a dois meses atrás
    df_filtrado = df_transf[df_transf['Crescimento Mes Anterior (%)'] > 15]

    # Dentre esses produtos, filtrar novamente para aqueles que também cresceram mais de 15% no mês atual em relação ao mês anterior
    df_qualificados = df_filtrado[df_filtrado['Crescimento Mes Atual (%)'] > 15]

    # Obter os Top 5 produtos com maior crescimento no mês atual
    top_crescimento = df_qualificados.nlargest(5, 'Crescimento Mes Atual (%)')

    # Selecionar colunas relevantes para o DataFrame final `crescimento`
    crescimento = top_crescimento[[
        'Nome do produto', 'Plataforma', 'Trafego do mês', 
        'Trafego mês anterior', 'Crescimento Mes Atual (%)',
        'Trafego dois meses atrás', 'Crescimento Mes Anterior (%)'
    ]]

    # Renomear colunas para facilitar leitura e duplicar `Tráfego Mês Anterior` para comparação
    crescimento = crescimento.rename(columns={
        'Nome do produto': 'Produto',
        'Plataforma': 'Plataforma',
        'Trafego do mês': 'Tráfego Mês Atual',
        'Trafego mês anterior': 'Tráfego Mês Anterior',
        'Crescimento Mes Atual (%)': 'Relação MAxMAT (%)',
        'Trafego dois meses atrás': 'Tráfego Dois Meses Atrás',
        'Crescimento Mes Anterior (%)': 'Relação MATxDM (%)'
    })

    # Converter colunas de tráfego para `int`
    crescimento['Tráfego Mês Atual'] = crescimento['Tráfego Mês Atual'].astype(int)
    crescimento['Tráfego Mês Anterior'] = crescimento['Tráfego Mês Anterior'].astype(int)
    crescimento['Tráfego Dois Meses Atrás'] = crescimento['Tráfego Dois Meses Atrás'].astype(int)

    # Duplicar a coluna "Tráfego Mês Anterior" para comparação
    crescimento = crescimento.assign(**{
        'Tráfego Mês Anterior (MAT)': crescimento['Tráfego Mês Anterior']
    })

    # Reorganizar as colunas para mostrar "Tráfego Mês Anterior" em ambos os contextos de comparação
    crescimento = crescimento[[
        'Produto', 'Plataforma', 'Tráfego Mês Atual', 
        'Tráfego Mês Anterior', 'Relação MAxMAT (%)',
        'Tráfego Mês Anterior (MAT)', 'Tráfego Dois Meses Atrás', 
        'Relação MATxDM (%)'
    ]]

    return crescimento
def get_plato_df():
    # Carregar e transformar dados brutos
    df_bruto = get_df_bruto()
    df_transf = transform_data(df_bruto)

    if df_transf.empty:
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

    # Filtrar produtos com tráfego mínimo de 2000 em cada um dos três períodos
    df_transf = df_transf[(df_transf['Trafego do mês'] >= 2000) & 
                          (df_transf['Trafego mês anterior'] >= 2000) & 
                          (df_transf['Trafego dois meses atrás'] >= 2000)]

    # Calcular variação percentual entre períodos
    df_transf['Variação MATxDM (%)'] = ((df_transf['Trafego mês anterior'] - df_transf['Trafego dois meses atrás']) / df_transf['Trafego dois meses atrás']) * 100
    df_transf['Variação MAxMAT (%)'] = ((df_transf['Trafego do mês'] - df_transf['Trafego mês anterior']) / df_transf['Trafego mês anterior']) * 100

    # Filtrar produtos em platô (variação entre -15% e +15% em ambos os períodos)
    df_plato = df_transf[(df_transf['Variação MATxDM (%)'].between(-15, 15)) & 
                         (df_transf['Variação MAxMAT (%)'].between(-15, 15))]

    # Obter o Top 5 produtos em platô com a maior variação absoluta, limitada a ±15%
    top_plato = df_plato.reindex(df_plato['Variação MAxMAT (%)'].abs().sort_values(ascending=False).index).head(5)

    # Selecionar e renomear colunas para o DataFrame final
    plato = top_plato[[
        'Nome do produto', 'Plataforma', 'Trafego do mês',
        'Trafego mês anterior', 'Variação MAxMAT (%)', 
        'Trafego dois meses atrás', 'Variação MATxDM (%)'
    ]]
    
    # Renomear colunas para facilitar leitura e adicionar a coluna duplicada
    plato = plato.rename(columns={
        'Nome do produto': 'Produto',
        'Plataforma': 'Plataforma',
        'Trafego do mês': 'Tráfego Mês Atual',
        'Trafego mês anterior': 'Tráfego Mês Anterior',
        'Variação MAxMAT (%)': 'Variação MAxMAT (%)',
        'Trafego dois meses atrás': 'Tráfego Dois Meses Atrás',
        'Variação MATxDM (%)': 'Variação MATxDM (%)'
    })

    # Converter colunas de tráfego para `int`
    plato['Tráfego Mês Atual'] = plato['Tráfego Mês Atual'].astype(int)
    plato['Tráfego Mês Anterior'] = plato['Tráfego Mês Anterior'].astype(int)
    plato['Tráfego Dois Meses Atrás'] = plato['Tráfego Dois Meses Atrás'].astype(int)

    # Adicionar a coluna duplicada de forma direta
    plato['Tráfego Mês Anterior (MAT)'] = plato['Tráfego Mês Anterior']

    # Reorganizar colunas para exibição
    plato = plato[[
        'Produto', 'Plataforma', 'Tráfego Mês Atual',
        'Tráfego Mês Anterior', 'Variação MAxMAT (%)', 
        'Tráfego Mês Anterior (MAT)', 'Tráfego Dois Meses Atrás', 'Variação MATxDM (%)'
    ]]
    
    return plato

import pandas as pd
from dash import get_df_bruto, transform_data

def get_queda_df():
    # Carregar e transformar dados brutos
    df_bruto = get_df_bruto()
    df_transf = transform_data(df_bruto)

    if df_transf.empty:
        return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

    # Filtrar produtos com tráfego mínimo de 2000 em cada um dos três períodos
    df_transf = df_transf[(df_transf['Trafego do mês'] >= 2000) & 
                          (df_transf['Trafego mês anterior'] >= 2000) & 
                          (df_transf['Trafego dois meses atrás'] >= 2000)]

    # Calcular queda percentual para os dois períodos
    df_transf['Queda Mes Anterior (%)'] = ((df_transf['Trafego mês anterior'] - df_transf['Trafego dois meses atrás']) / df_transf['Trafego dois meses atrás']) * 100
    df_transf['Queda Mes Atual (%)'] = ((df_transf['Trafego do mês'] - df_transf['Trafego mês anterior']) / df_transf['Trafego mês anterior']) * 100

    # Filtrar produtos que apresentaram queda superior a 15% no mês anterior em relação a dois meses atrás
    df_filtrado = df_transf[df_transf['Queda Mes Anterior (%)'] < -15]

    # Dentre esses produtos, filtrar novamente para aqueles que também caíram mais de 15% no mês atual em relação ao mês anterior
    df_qualificados = df_filtrado[df_filtrado['Queda Mes Atual (%)'] < -15]

    # Obter os Top 5 produtos com maior queda no mês atual
    top_queda = df_qualificados.nsmallest(5, 'Queda Mes Atual (%)')

    # Selecionar colunas relevantes para o DataFrame final `queda`
    queda = top_queda[[
        'Nome do produto', 'Plataforma', 'Trafego do mês', 
        'Trafego mês anterior', 'Queda Mes Atual (%)',
        'Trafego dois meses atrás', 'Queda Mes Anterior (%)'
    ]]

    # Renomear colunas para facilitar leitura e duplicar `Tráfego Mês Anterior` para comparação
    queda = queda.rename(columns={
        'Nome do produto': 'Produto',
        'Plataforma': 'Plataforma',
        'Trafego do mês': 'Tráfego Mês Atual',
        'Trafego mês anterior': 'Tráfego Mês Anterior',
        'Queda Mes Atual (%)': 'Relação MAxMAT (%)',
        'Trafego dois meses atrás': 'Tráfego Dois Meses Atrás',
        'Queda Mes Anterior (%)': 'Relação MATxDM (%)'
    })

    # Converter colunas de tráfego para `int`
    queda['Tráfego Mês Atual'] = queda['Tráfego Mês Atual'].astype(int)
    queda['Tráfego Mês Anterior'] = queda['Tráfego Mês Anterior'].astype(int)
    queda['Tráfego Dois Meses Atrás'] = queda['Tráfego Dois Meses Atrás'].astype(int)

    # Duplicar a coluna "Tráfego Mês Anterior" para comparação
    queda = queda.assign(**{
        'Tráfego Mês Anterior (MAT)': queda['Tráfego Mês Anterior']
    })

    # Reorganizar as colunas para mostrar "Tráfego Mês Anterior" em ambos os contextos de comparação
    queda = queda[[
        'Produto', 'Plataforma', 'Tráfego Mês Atual', 
        'Tráfego Mês Anterior', 'Relação MAxMAT (%)',
        'Tráfego Mês Anterior (MAT)', 'Tráfego Dois Meses Atrás', 
        'Relação MATxDM (%)'
    ]]

    return queda
