import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="BRB Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

col = st.columns((4.5, 2), gap='medium')
select_idh_estado = "" 
select_idh_rm = "" 
select_idh_municipio = ""

# Função para criar gráficos de donut
def make_donut(input_response, input_text, input_color, is_percentage=True, is_integer=False):
    # Definição das cores com base no valor
    if input_response >= 0.8:
        chart_color = ['#27AE60', '#2C3E50']  # Verde   
    elif input_response >= 0.66:
        chart_color = ['#F1C40F', '#2C3E50']  # Amarelo
    else:
        chart_color = ['#E74C3C', '#2C3E50']  # Vermelho
    
    if is_percentage:
        input_response = input_response * 100  # Converte para porcentagem

    # Formatação do valor (inteiro ou com 3 casas decimais)
    formatted_value = f"{input_response:.0f}" if is_integer else f"{input_response:.3f}"

    # Se for o gráfico de "Posição IDHM", adicione o símbolo de grau
    if input_text == 'Posição IDHM':
        formatted_value = f"{formatted_value}°"
        input_response = 100
        chart_color = ['#3498DB', '#2C3E50']

    # Se a entrada for para "Região Metropolitana", use um nome específico
    if 'Região Metropolitana' in input_text:
        input_text = 'Região Metropolitana'

    # Se a entrada for para "Municípios", use um nome específico
    if 'Municípios' in input_text:
        input_text = 'Municípios'

    # Preparando os dados para o gráfico
    if input_text == 'Posição IDHM':
        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [1 - input_response / 100, input_response / 100]
        })

    else:
        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [1 - input_response, input_response]
        })
    
    # Background do gráfico
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [1, 0]
    })
    
    # Gráfico de donut
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    # Texto centralizado no gráfico
    text = plot.mark_text(align='center', color="#fff", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(
        text=alt.value(f'{formatted_value}' if not is_percentage else f'{formatted_value} %')
    )
    
    # Background adicional para o gráfico
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    return plot_bg + plot + text

# Definição de página IDH
def idh_page(df, filtro):
    with col[0]:
        if select_idh_estado == "" and select_idh_rm == "" and select_idh_municipio == "":
            st.markdown('#### IDH por ' + filtro)
            st.dataframe(df, 
                        column_order=("Territorialidade", "Posição IDHM", "IDHM", "IDHM Renda", "IDHM Educação", "IDHM Longevidade"),
                        hide_index=True,
                        width=None,
                        column_config={
                            "Territorialidade": st.column_config.TextColumn(filtro),
                            "Posição IDHM": st.column_config.TextColumn("Posição IDHM"),
                            "IDHM": st.column_config.ProgressColumn("IDHM", format="%.3f", min_value=0, max_value=1),
                            "IDHM Renda": st.column_config.ProgressColumn("IDHM Renda", format="%.3f", min_value=0, max_value=1),
                            "IDHM Educação": st.column_config.ProgressColumn("IDHM Educação", format="%.3f", min_value=0, max_value=1),
                            "IDHM Longevidade": st.column_config.ProgressColumn("IDHM Longevidade", format="%.3f", min_value=0, max_value=1)
                            }
                        )
            
        else:
            st.markdown('## ' + select_idh_estado + " " + select_idh_municipio + " " + select_idh_rm)
            
            # Obtenha os valores do IDHM e outras métricas
            if select_idh_estado != "":
                selected_row = df[df['Territorialidade'] == select_idh_estado]  # Ajuste conforme o filtro
            elif select_idh_rm != "":
                selected_row = df[df['Territorialidade'] == select_idh_rm]
            elif select_idh_municipio != "":
                selected_row = df[df['Territorialidade'] == select_idh_municipio]
            idhm_value = selected_row['IDHM'].values[0] if not selected_row.empty else 0  # Evita erro se não encontrar
            idhm_renda = selected_row['IDHM Renda'].values[0] if not selected_row.empty else 0
            idhm_educacao = selected_row['IDHM Educação'].values[0] if not selected_row.empty else 0
            idhm_longevidade = selected_row['IDHM Longevidade'].values[0] if not selected_row.empty else 0
            pos_idhm = selected_row['Posição IDHM'].values[0] if not selected_row.empty else 0

            # Organize the layout with columns for side-by-side display
            col1, col2, col3 = st.columns(3)

            # Exibe o gráfico de Posição IDHM (com número inteiro)
            with col1:
                st.markdown("**Ranking IDHM**")
                donut_chart_pos = make_donut(pos_idhm, 'Posição IDHM', 'green', is_percentage=False, is_integer=True)
                st.altair_chart(donut_chart_pos, use_container_width=True)
                
            # Exibe o gráfico de IDHM (valor real)
            with col2:
                st.markdown("**IDHM**")
                donut_chart_idhm = make_donut(idhm_value, 'IDHM', 'green', is_percentage=False, is_integer=False)
                st.altair_chart(donut_chart_idhm, use_container_width=True)

            # Exibe os gráficos de IDHM Renda, Educação e Longevidade (valores reais)
            with col3:
                st.markdown("**IDHM Renda**")
                donut_chart_renda = make_donut(idhm_renda, 'IDHM Renda', 'green', is_percentage=False, is_integer=False)
                st.altair_chart(donut_chart_renda, use_container_width=True)

            # Segunda linha de gráficos
            col4, col5 = st.columns(2)

            with col4:
                st.markdown("**IDHM Educação**")
                donut_chart_educacao = make_donut(idhm_educacao, 'IDHM Educação', 'green', is_percentage=False, is_integer=False)
                st.altair_chart(donut_chart_educacao, use_container_width=True)

            with col5:
                st.markdown("**IDHM Longevidade**")
                donut_chart_longevidade = make_donut(idhm_longevidade, 'IDHM Longevidade', 'green', is_percentage=False, is_integer=False)
                st.altair_chart(donut_chart_longevidade, use_container_width=True)

# Função ajustada para exibir as métricas com base no filtro
def pof_page(local):
    with col[1]:
        st.markdown('### Pesquisa de Orçamento Familiar')
        st.markdown('#### ' + local)

        # Garantir que as colunas de alimentos sejam numéricas
        df_pof_alimento.iloc[:, 1:] = df_pof_alimento.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
        # Encontrar a linha onde "Territorialidade" corresponde ao local selecionado
        row = df_pof_alimento[df_pof_alimento['Territorialidade'] == local].iloc[0]
        # Calcular o total da quantidade de alimentos por família
        total_food_amount = row.iloc[1:].sum()
        st.metric(label="Quantidade de Alimento Total Médio por Família", value=f"{total_food_amount:.2f} Kg/Ano")

        # Garantir que a coluna "Total" do df_pof_familias seja numérica
        df_pof_familias['Total'] = pd.to_numeric(df_pof_familias['Total'], errors='coerce')
        # Encontrar a linha onde "Territorialidade" corresponde ao local selecionado no df_pof_familias
        row_familias = df_pof_familias[df_pof_familias['Territorialidade'] == local].iloc[0]
        # Obter o valor do total médio de famílias
        total_familias = row_familias['Total']
        # Formatar com separador de milhares
        formatted_familias = f"{total_familias:,.0f}".replace(",", ".")  # Usa pontos como separador de milhares
        st.metric(label="Quantidade Média Famílias", value=f"{formatted_familias} famílias")

        # Encontrar a linha onde "Territorialidade" corresponde ao local selecionado no df_pof_despesa
        row_despesa = df_pof_despesa[df_pof_despesa['Territorialidade'] == local].iloc[0]
        total_despesa = row_despesa['Total']
        st.metric(label="Despesas Média por Família", value=f"{total_despesa} /Mês")

        # Encontrar a linha onde "Territorialidade" corresponde ao local selecionado no df_pof_rendimento
        row_rendimento = df_pof_rendimento[df_pof_rendimento['Territorialidade'] == local].iloc[0]
        total_rendimento = row_rendimento['Total']
        st.metric(label="Rendimento Médio por Família", value=f"{total_rendimento} /Mês")
                    
# Puxando dados
# IDH
df_idh_estados_2010 = pd.read_csv("DashBoard/streamlit/dados/IDH/IDH_Estados_2010.csv")
df_idh_estados_2021 = pd.read_csv("DashBoard/streamlit/dados/IDH/IDH_Estados_2021.csv")
df_idh_municipios = pd.read_csv("DashBoard/streamlit/dados/IDH/IDH_Municipios.csv")
df_idh_rm_2010 = pd.read_csv("DashBoard/streamlit/dados/IDH/IDH_RM_2010.csv")
df_idh_rm_2021 = pd.read_csv("DashBoard/streamlit/dados/IDH/IDH_RM_2021.csv")

# POF
df_pof_alimento = pd.read_csv("DashBoard/streamlit/dados/POF/POF_Alimento_filtrado.csv")
df_pof_familias = pd.read_csv("DashBoard/streamlit/dados/POF/POF_Num_Familia_Classes_filtrado.csv")
df_pof_despesa = pd.read_csv("DashBoard/streamlit/dados/POF/POF_Despesa_Classe_filtrado.csv")  
df_pof_rendimento = pd.read_csv("DashBoard/streamlit/dados/POF/POF_Rendimento_Classe_filtrado.csv") 

# Configurações Sidebar
with st.sidebar:
    # Definindo Titulo
    st.image("DashBoard/streamlit/imagens/brb.png", width=500)

    # Selecionar modulo
    select_modulo = st.selectbox('Selecione um Módulo:', ["Geográfico", "Social"])

    # Geográfico
    if select_modulo == "Geográfico":
        # IDH
        # Selecionar ano
        select_idh_ano = st.selectbox('Selecione um Ano:', ["2021", "2010"])

        # Checkbox de estado, municipio e região
        if select_idh_ano == "2021":
            options_idh_check = ["Nenhum", "Estado", "Região Metropolitana"]
        else:
            options_idh_check = ["Nenhum", "Estado", "Município", "Região Metropolitana"]

        idh_check = st.radio(
            "Selecione um Filtro:",
            options_idh_check
        )      

        # Se 2021
        if select_idh_ano == "2021":

            # Estado
            if idh_check == "Estado":
                select_idh_estado = st.selectbox('Selecione Estado:', [""] + sorted(df_idh_estados_2021['Territorialidade'].unique().tolist()))

            # Região Metropolitana
            if idh_check == "Região Metropolitana":
                select_idh_rm = st.selectbox('Selecione Região Metropolitana:', [""] + sorted(df_idh_rm_2021['Territorialidade'].unique().tolist()))

        elif select_idh_ano == "2010":
            # Estado
            if idh_check == "Estado":
                select_idh_estado = st.selectbox('Selecione Estado:', [""] + sorted(df_idh_estados_2010['Territorialidade'].unique().tolist()))

            # Município
            if idh_check == "Município":
                select_idh_municipio = st.selectbox('Selecione Município:', [""] + sorted(df_idh_municipios['Territorialidade'].unique().tolist()))

            # Região Metropolitana
            if idh_check == "Região Metropolitana":
                select_idh_rm = st.selectbox('Selecione Região Metropolitana:', [""] + sorted(df_idh_rm_2010['Territorialidade'].unique().tolist()))

    elif select_modulo == "Social":
        tipo_opcoes = ["Publica", "Privada"]
        select_tipo = st.selectbox('Selecione Tipo:', tipo_opcoes)

# Código para exibir a função idh_page na página principal
if select_modulo == "Geográfico":
    if select_idh_ano == "2021":
        if idh_check == "Estado" and select_idh_estado != "":
            idh_page(df_idh_estados_2021[df_idh_estados_2021['Territorialidade'] == select_idh_estado], "Estado")
            pof_page(select_idh_estado)
        elif idh_check == "Estado":
            idh_page(df_idh_estados_2021, "Estado")
            pof_page("Brasil")
        elif idh_check == "Região Metropolitana" and select_idh_rm != "":
            idh_page(df_idh_rm_2021[df_idh_rm_2021['Territorialidade'] == select_idh_rm], "Região Metropolitana")
        elif idh_check == "Região Metropolitana":
            idh_page(df_idh_rm_2021, "Região Metropolitana")
            pof_page("Brasil")

    elif select_idh_ano == "2010":
        if idh_check == "Estado" and select_idh_estado != "":
            idh_page(df_idh_estados_2010[df_idh_estados_2010['Territorialidade'] == select_idh_estado], "Estado")
            pof_page(select_idh_estado)
        elif idh_check == "Estado":
            idh_page(df_idh_estados_2010, "Estado")
            pof_page("Brasil")
        elif idh_check == "Município" and select_idh_municipio != "":
            idh_page(df_idh_municipios[df_idh_municipios['Territorialidade'] == select_idh_municipio], "Município")
        elif idh_check == "Município":
            idh_page(df_idh_municipios, "Município")
            pof_page("Brasil")
        elif idh_check == "Região Metropolitana" and select_idh_rm != "":
            idh_page(df_idh_rm_2010[df_idh_rm_2010['Territorialidade'] == select_idh_rm], "Região Metropolitana")
        elif idh_check == "Região Metropolitana":
            idh_page(df_idh_rm_2010, "Região Metropolitana")
            pof_page("Brasil")
