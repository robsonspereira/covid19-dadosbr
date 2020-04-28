import streamlit as st
import pandas as pd
import base64
import random
import datetime
import plotly.express as px
import plotly.graph_objects as go
import base64

def sortear_cor():
    color_list=['#4682B4','#90EE90','#BC8F8F','#DDA0DD','#FFB6C1','#FF6347','#F0E68C','#FF6347','#483D8B']
    color_select =random.choice(color_list) 
    return color_select

def plot_bar(df, list_var):
    df=df
    x_values = df['estado']
    data_bar = []


    for i in list_var:
             cor_bar = sortear_cor()
             data_bar.append(go.Bar(name=i, x=x_values, y=df[i],orientation='v',
             text = df[i],
              textposition='outside'
             ))

    
    fig = go.Figure(data=data_bar
                )
  

    fig.update_layout(barmode='group',
                      showlegend = True,
                       plot_bgcolor='AliceBlue',
                       autosize=False,
                       margin=dict(
                       autoexpand=True,
                       l=100,
                       r=20,
                       t=110))
    return fig


def plot_scatter(df, list_var,list_estado,x):
    df=df[df[list_var[0]]>0]
    df.sort_values(x, inplace= True)
    
    data_scatter = []

    for j in list_estado:
        df_scatter= df[df['estado']==j]
        x_values = df_scatter[x]
        for i in list_var:
                cor_bar = sortear_cor()
                data_scatter.append(go.Scatter(name=(j+' - '+i), x=x_values, y=df_scatter[i]))
    
    fig = go.Figure(data_scatter)
    fig.update_layout(
        xaxis=dict(
        showline=True,
        showgrid=True,
        gridcolor = 'lightgray',
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
        ),
        yaxis=dict(
        showgrid=True,
        gridcolor = 'lightgray',
        zeroline=True,
        showline=False,
        showticklabels=True,
        ),
        autosize=True,
        margin=dict(
        autoexpand=True,
        l=100,
        r=20,
        t=110,
        ),
        showlegend=True,
        legend_title_text='Legenda',
        plot_bgcolor='AliceBlue'
        )   

    return fig

def tratar_df(df):
        df.query('regiao in ["Norte","Nordeste","Sudeste","Sul","Centro-Oeste"]', inplace = True)
        while True:
            try:
                df['data']= pd.to_datetime(df['data'], format='%d/%m/%Y')
                break
            except ValueError:
                df['data']= pd.to_datetime(df['data'], format='%Y-%m-%d')
        df['casosNovos']= df['casosNovos'].astype(float)
        df['casosAcumulados']= df['casosAcumulados'].astype(float)
        df['obitosNovos']= df['obitosNovos'].astype(float)
        df['obitosAcumulados']= df['obitosAcumulados'].astype(float)
        df['letalidade'] = (df['obitosAcumulados']/df['casosAcumulados']).astype(float)
        df.sort_values(by = ['estado'], inplace = True)
        
def var_MilhaoPop(df):
        df['obitoMilhaoPop'] = (df['obitosAcumulados']/(df['PopCenso2012']/1000000)).astype(float)
        df['casosMilhaoPop'] = (df['casosAcumulados']/(df['PopCenso2012']/1000000)).astype(float)
        df['duration'] = (pd.to_datetime(df['data']) - pd.to_datetime(df['data_100'])).dt.days.astype(float)

def main ():
    st.sidebar.markdown('Opção Desejada')
    selecao_secao = st.sidebar.radio('Seleciona a seção desejada', ('Resumo','Visualizar Base','Gráficos'))

    #Importandado dados Default
    df = pd.read_csv('arquivo_geral.csv',sep = ';', encoding = 'latin')
    pop = pd.read_csv('popCenso2012.csv',sep = ';',encoding = 'latin')
   

    #Definindo Layout topo
    st.image("https://covid.saude.gov.br/assets/imgs/logo-app.png",  width= 500)
   
    #Seleção da seção
    
    #Sessão para import de dados
    st.write('Para atualizar os dados acesse a página https://covid.saude.gov.br/ ,faça o download do "Arquivo.Csv" e faça o Upload na sessão abaixo.')
    file = st.file_uploader('Faça o upload do arquivo csv', type = 'csv', encoding = 'latin')
    if file is not None:
        df=pd.read_csv(file, sep = ';')
        
    #tratando dataset
    tratar_df(df) #função para tratar variaveis
    df_caso_100 = df[['estado','casosAcumulados','data']][df['casosAcumulados']>=100]
    df_caso_100 =df_caso_100.groupby(['estado']).agg({'data':'min'})
    df_caso_100.columns = ['data_100'] 
    df_caso_100.head(30)
    df = df.merge(df_caso_100, left_on = 'estado', right_on = 'estado', how ='left')
    df = df.merge(pop,left_on = 'estado', right_on = 'UF', how = 'left') #Join com base de Censo
    df.update(df['data_100'].fillna(datetime.date.today()))
    var_MilhaoPop(df) #Criar variaiveis de população
    max_data_import = max(df['data'])

    
    #Seletor de Data de Última Data
    st.sidebar.markdown('Filtros para Gráficos')
    filter_date = st.sidebar.date_input('Selecione data fim da visualização', max(df['data']))
    max_date = max(df['data'])
    if filter_date <= max_date:
        max_date = filter_date
    else:
        st.sidebar.error('Data selecionada é maior do que a última disponível.')
   
    df = df[df['data']<= str(max_date)]
    st.sidebar.markdown('Dados atualizados até: {}'.format(format(max_data_import,'%d/%m/%Y')))
    
    #Seletor de Estado
    filter_estado = st.sidebar.multiselect('Selecione os Estados',  df['Unidade da Federação'].unique())
    if filter_estado == []:
        pass
    else:
       df = df[df['Unidade da Federação'].isin(filter_estado)]

    #Seletor de Variaveis
    aux = pd.DataFrame({'colunas' : df.columns, 'tipos' : df.dtypes})
    lista = list(aux['colunas'].loc[(aux['tipos'] == 'float')])
    df[lista]=df[lista].apply(lambda x:round(x,2))
    
    #filter bar
    filter_var = st.sidebar.multiselect('Selecione a Variavel Gráfico de Barras', lista)
    if filter_var == []:
        filter_var = lista
    else:
       pass
    
    #filter scattter
    filter_var_sc = st.sidebar.multiselect('Selecione a Variavel Gráfico de Linhas', lista)
    if filter_var_sc == []:
        filter_var_sc = lista
    else:
       pass

       #Criando data set 'hoje'
    df_hoje = df[df['data']==max(df['data'])]

    if selecao_secao == 'Resumo':
        st.title('Resumo')
        st.subheader('Descrição da ferramenta:')
        st.write('A ferramenta auxilia na visualização de dados do COVID-19 no Brasil, ela foi desenvolvida para interagir com os dados disponibilizados pelo Ministério da Saúde.')
        st.write('A ferramenta é totalmente interativa, portanto para gerar os dados você deve interagir com os filtros da barra lateral esquerda.')
        st.write('Para atualizar os dados acesse a página https://covid.saude.gov.br/ ,faça o download do "Arquivo.Csv" e faça o Upload no ínicio da página.')
        st.subheader('Descrição dos dados:')
        st.markdown('<b>data:</b> Data do reporte, não significa que a morte ou o caso aconteceu neste dia, mas sim a data que o estado reportou ao ministério.',unsafe_allow_html=True)
        st.markdown('<b>casosNovos: </b> Casos reportados na data.' ,unsafe_allow_html=True)
        st.markdown('<b>casosAcumulados: </b> Casos somados até a data.' ,unsafe_allow_html=True)
        st.markdown('<b>obitosNovos: </b> Óbitos reportados na data.' ,unsafe_allow_html=True)
        st.markdown('<b>obitosAcumulados: </b> Óbitos somados até a data.' ,unsafe_allow_html=True)
        st.markdown('<b>letalidade: </b> Letalidade é a relação entre óbitos e casos acumulados (óbitos/casos).' ,unsafe_allow_html=True)
        st.markdown('<b>PopCenso2012: </b> População do estado segundo censo realizado em 2012.' ,unsafe_allow_html=True)
        st.markdown('<b>obitoMilhaoPop: </b> Óbitos por milhão de habitantes, esse indicador é importante pois dá dimensão da proporção da doença em cada região.' ,unsafe_allow_html=True)
        st.markdown('<b>casosMilhaoPop: </b> Casos por milhão de habitantes.' ,unsafe_allow_html=True)
        st.markdown('<b>data_100: </b> Este parametro, traz o dia que a doença está, a partir do reporte do caso 100, como a pandâmenia está em tempos diferentes para cada região, esta variável põe as regiões na mesma linha do tempo.' ,unsafe_allow_html=True)
        
    if selecao_secao == 'Visualizar Base':
        #Mostrando Data Set
        st.subheader('Dados completos')
        st.dataframe(df)
        st.subheader('Dados do dia')
        st.dataframe(df_hoje)

    if selecao_secao == 'Gráficos':
        #Grafico de barras
        st.title('Gráficos')
        st.subheader(('Gráfico - Resumo de Dados -'+format(format(max_date,'%d/%m/%Y'))))
        st.plotly_chart(plot_bar(df_hoje,filter_var)) #Chamando função para plotar gráfico plot_bar
        st.subheader(('Gráfico - Evolução na Linha do Tempo'))
        st.plotly_chart(plot_scatter(df,filter_var_sc, df['estado'].unique(),'data')) #Chamando função para plotar gráfico plot_bar
        df = df[df['duration']>=0]
        st.subheader(('Gráfico - Evolução à partir do Caso 100'))
        st.plotly_chart(plot_scatter(df,filter_var_sc, df['estado'].unique(),'duration'))
    
    st.sidebar.markdown('Autor : Robson Pereira')
    st.sidebar.markdown('Linkedin: https://www.linkedin.com/in/robson-pereira90/')
    st.sidebar.markdown('Código: https://github.com/robsonspereira')

if __name__ == '__main__':
    main()

