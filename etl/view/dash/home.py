import streamlit as st
import pandas as pd
from dash import get_df_bruto, transform_data, filter_data
from analise import get_crescimento_df, get_plato_df, get_queda_df  # Importa as funções de análise

# Configuração da página principal
st.set_page_config(page_title="Ninja Click", initial_sidebar_state="collapsed", layout="wide")

# Exemplo de credenciais
USERNAME = "rich"
PASSWORD = "password123"

def login(username, password):
    return username == USERNAME and password == PASSWORD

# Inicializar o estado de autenticação e de página na sessão
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "home"

# Função para colorir as colunas de crescimento
def color_growth(val):
    try:
        val = float(val)
    except ValueError:
        return ''
    if val > 16:
        color = '#68967e'
    elif -15 <= val <= 15:
        color = '#96933d'
    else:
        color = 'red'
    return f'background-color: {color}'

# Verificar estado de autenticação
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Dashboard de Login")
        st.subheader("Faça login para acessar o dashboard")
        username_input = st.text_input("Usuário")
        password_input = st.text_input("Senha", type="password")
        login_button = st.button("Login")
        if login_button:
            if login(username_input, password_input):
                st.session_state.authenticated = True
                st.success("Login bem-sucedido!")
                st.session_state.page = "home"
else:
    st.sidebar.success("Bem-vindo! Use o menu lateral para navegar.")

    if st.session_state.page == "home":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("Bem-vindo ao Ninja Click!")
            st.write("Escolha uma opção abaixo para continuar.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Dashboard de Produtos", type="primary"):
                    st.session_state.page = "dashboard"
            with col2:
                if st.button("Relatório", type="primary"):
                    st.session_state.page = "relatorio"

    elif st.session_state.page == "dashboard":
        st.title("Dashboard Produtos")
        df_bruto = get_df_bruto()
        if not df_bruto.empty:
            df_transf = transform_data(df_bruto)
            col_filtros, _, _ = st.columns([1, 1, 2])
            with col_filtros:
                plataformas = df_transf['Plataforma'].unique()
                paises = pd.concat([df_transf['Pais 1'], df_transf['Pais 2'], df_transf['Pais 3'],
                                    df_transf['Pais 4'], df_transf['Pais 5']]).unique()
                plataforma_selecionada = st.selectbox("Filtrar por Plataforma", options=[""] + list(plataformas))
                aplicar_filtro_fundo_funil = st.checkbox("Mostrar apenas produtos com Fundo de Funil (True)")
                aplicar_filtro_pais = st.checkbox("Filtrar por País específico")
                pais_selecionado = st.selectbox("Escolha o País", options=[""] + list(paises)) if aplicar_filtro_pais else None
            df_filtrado = filter_data(df_transf, plataforma=plataforma_selecionada if plataforma_selecionada else None, pais=pais_selecionado if aplicar_filtro_pais and pais_selecionado else None)
            if aplicar_filtro_fundo_funil:
                df_filtrado = df_filtrado[df_filtrado['Fundo de Funil'] == True]
            if df_filtrado.empty:
                st.warning("Nenhum produto corresponde aos critérios selecionados.")
            else:
                st.write("### Dados Filtrados")
                st.dataframe(df_filtrado)
        else:
            st.warning("Nenhum dado disponível para exibir no momento.")
        if st.button("Voltar para Home"):
            st.session_state.page = "home"

    elif st.session_state.page == "relatorio":
        # Análise de Crescimento
        st.title("Relatório - Análise de Produtos")
        st.write("### Análise de Crescimento de Produtos")
        st.write("Produtos com mais de 2000 de tráfego e Crescimento acima de 15%")
        crescimento_df = get_crescimento_df()
        if not crescimento_df.empty:
            crescimento_df['Relação MAxMAT (%)'] = crescimento_df['Relação MAxMAT (%)'].round(2)
            crescimento_df['Relação MATxDM (%)'] = crescimento_df['Relação MATxDM (%)'].round(2)
            styled_df_crescimento = crescimento_df.style.format({
                'Relação MAxMAT (%)': '{:.2f}%',
                'Relação MATxDM (%)': '{:.2f}%'
            }).applymap(color_growth, subset=['Relação MAxMAT (%)', 'Relação MATxDM (%)'])
            
            st.dataframe(styled_df_crescimento)
            st.write("MA - Tráfego Mês Atual | MAT - Táfego Mês Anterior | DM - Tráfego Dois Mestes Atrás")
        else:
            st.warning("Nenhum dado disponível para análise de crescimento.")
        
        # Análise de Platô
        st.write("### Análise de Produtos em Platô")
        st.write("Produtos em Platô (Variação de tráfego entre -15% e +15%)")
        plato_df = get_plato_df()
        if not plato_df.empty:
            plato_df['Variação MAxMAT (%)'] = plato_df['Variação MAxMAT (%)'].round(2)
            plato_df['Variação MATxDM (%)'] = plato_df['Variação MATxDM (%)'].round(2)
            styled_df_plato = plato_df.style.format({
                'Variação MAxMAT (%)': '{:.2f}%',
                'Variação MATxDM (%)': '{:.2f}%'
            }).applymap(color_growth, subset=['Variação MAxMAT (%)', 'Variação MATxDM (%)'])
            
            st.dataframe(styled_df_plato)
            st.write("MA - Tráfego Mês Atual | MAT - Táfego Mês Anterior | DM - Tráfego Dois Mestes Atrás")
        else:
            st.warning("Nenhum dado disponível para análise de platô.")  

        # Análise de queda
        st.write("### Análise de Queda de Produtos")
        st.write("Produtos com mais de 2000 de tráfego e Queda acima de 15%")
        queda_df = get_queda_df()
        if not crescimento_df.empty:
            queda_df['Relação MAxMAT (%)'] = queda_df['Relação MAxMAT (%)'].round(2)
            queda_df['Relação MATxDM (%)'] = queda_df['Relação MATxDM (%)'].round(2)
            styled_df_queda = queda_df.style.format({
                'Relação MAxMAT (%)': '{:.2f}%',
                'Relação MATxDM (%)': '{:.2f}%'
            }).applymap(color_growth, subset=['Relação MAxMAT (%)', 'Relação MATxDM (%)'])
            
            st.dataframe(styled_df_queda)
            st.write("MA - Tráfego Mês Atual | MAT - Táfego Mês Anterior | DM - Tráfego Dois Mestes Atrás")
        else:
            st.warning("Nenhum dado disponível para análise de crescimento.")

        if st.button("Voltar para Home"):
            st.session_state.page = "home"   

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.page = "home"
