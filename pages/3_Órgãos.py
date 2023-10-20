import streamlit as st
import pandas as pd
#import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

hoje = str(date.today())
ano = date.year

st.set_page_config(
    page_title="Indicadores do Órgão",
    layout="wide"
)

# CARREGA OS DADOS
@st.cache_data
def carrega_dados(arquivo):
    data = pd.read_json(arquivo)
#    data = pd.read_csv('ouvidoria-2019.csv', sep=';')
    return data

atendimentos = carrega_dados('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/5735a52c-a578-4529-ac0a-c8ca15da82ca/download/tb_atendimento.json')
encaminhamentos = carrega_dados('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/94575080-6d10-40e5-a160-938afaa73d2f/download/tb_encaminhamento.json')
cartas = carrega_dados('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/ea2d7235-b1b3-4d79-aacc-7f70bf4b4817/download/tb_carta.json')


def convert_df(df):
    return df.to_csv().encode('utf-8')

def verifica_transferido(row):
    if row['ch_atendimento'].startswith('E-SIC'):
        return 'Transferido para E-SIC'
    if row['ch_atendimento'].startswith('OGE'):
        return 'Recebido do E-SIC' 
    else:
        return 'Normal'

def buscar_encaminhamentos(df):
    return 


def buscar_cartas(encaminhamento):
    cartas_encaminhamento = cartas.query('id_encaminhamento == @encaminhamento and de_tipo == "C"')
    return cartas_encaminhamento

# TITULO DO APP
st.title("Indicadores por Órgão")

# CAMPOS DE FILTRO
ano = st.selectbox(
    'Selecione o ano',
    ('2019', '2020', '2021', '2022', '2023'), index=4)

intervalo = st.selectbox(
    'Selecione o intervalo',
    ('primeiro trimestre', 'segundo trimestre', 'terceiro trimestre', 'quarto trimestre', 'ano inteiro'), index=4)

if intervalo == 'primeiro trimestre': 
    start_date = ano + '-01-01'
    end_date   = ano + '-03-31'
elif intervalo == 'segundo trimestre':
    start_date = ano + '-04-01'
    end_date   = ano + '-06-30'
elif intervalo == 'terceiro trimestre':
    start_date = ano + '-07-01'
    end_date   = ano + '-09-30'
elif intervalo == 'quarto trimestre':
    start_date = ano + '-10-01'
    end_date   = ano + '-12-31'
else:
    start_date = ano + '-01-01'
    end_date   = ano + '-12-31'

atendimentos = atendimentos.query('dt_criacao >= @start_date and dt_criacao <= @end_date')


df = atendimentos.join(encaminhamentos.set_index('id_atendimento'), on='id_atendimento', lsuffix='_encam.')
df = df.join(cartas.set_index('id_encaminhamento'), on='id_encaminhamento', lsuffix='_cartas')
df_apenas_c = df.loc[df.de_tipo=='C']
orgaos = df['nm_orgao'].unique()
lista_ogaos = orgaos.tolist()
#st.dataframe(lista_orgaos)

orgao = st.selectbox(
    'Selecione o órgão',
    lista_ogaos, index=0)

if orgao == 'SICOS':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SICOS"')
if orgao == 'SEPLAN':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SEPLAN"')
if orgao == 'SIE':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SIE"')    

atendimentos['dt_criacao'] = pd.to_datetime(atendimentos['dt_criacao']).dt.date
atendimentos['transferido'] = atendimentos.apply(verifica_transferido, axis=1)

lista_encaminhamentos = encaminhamentos['id_encaminhamento']
#encaminhamentos['cartas'] = encaminhamentos.apply(lambda x: buscar_cartas(encaminhamentos['id_encaminhamento']))
#st.dataframe(encaminhamentos)

atendimentos_por_natureza = (atendimentos.groupby(['de_natureza','dt_criacao']).size()).reset_index(name='quantidade')
fig = px.area(atendimentos_por_natureza, x="dt_criacao", color="de_natureza",y="quantidade", title="Demandas por dia", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=1300,height=500)
st.write(fig)
fig = px.scatter(atendimentos_por_natureza, x="dt_criacao", y="quantidade", color="de_natureza", title="Demandas por dia",
                size="quantidade",hover_data=['de_natureza'], color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=1300,height=500)
st.write(fig)

col1, col2, col3 = st.columns(3)
with col1:
    atendimentos_por_forma = (atendimentos.groupby(['de_forma']).size()).reset_index(name='quantidade')
    atendimentos_por_forma.reset_index(drop=False, inplace=True)
    atendimentos_por_forma_ordenado = atendimentos_por_forma.sort_values(by=['quantidade'],ascending=False)
    atendimentos_por_forma_top_10 = atendimentos_por_forma_ordenado.head(10)
    fig = px.pie(atendimentos_por_forma_top_10, names="de_forma", values="quantidade", title="Demandas por Canal", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, width=300,height=500)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-0.2,xanchor="right",x=1))
    st.write(fig)
with col2:
    atendimentos_transferidos = (atendimentos.groupby(['transferido']).size()).reset_index(name='quantidade')
    atendimentos_transferidos.reset_index(drop=False, inplace=True)
    atendimentos_transferidos_ordenado = atendimentos_transferidos.sort_values(by=['quantidade'],ascending=False)
    fig = px.pie(atendimentos_transferidos_ordenado, names="transferido", values="quantidade", title="Transferências", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, width=300,height=500)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-0.2,xanchor="right",x=1))
    st.write(fig)
with col3:
    atendimentos_por_programa = (atendimentos.groupby(['de_programa']).size()).reset_index(name='quantidade')
    atendimentos_por_programa.reset_index(drop=False, inplace=True)
    atendimentos_por_programa_ordenado = atendimentos_por_programa.sort_values(by=['quantidade'],ascending=False)
    fig = px.pie(atendimentos_por_programa_ordenado, names="de_programa", values="quantidade", title="Programas", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, width=300,height=500)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-0.2,xanchor="right",x=1))
    st.write(fig)

atendimentos_situacao = (atendimentos.groupby(['de_status_atendimento']).size()).reset_index(name='quantidade')
atendimentos_situacao.reset_index(drop=False, inplace=True)
atendimentos_situacao_ordenado = atendimentos_situacao.sort_values(by=['quantidade'],ascending=False)
fig = px.pie(atendimentos_situacao_ordenado, names="de_status_atendimento", values="quantidade", title="Situação do Atendimento", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=1000,height=500)
st.write(fig)

col1, col2 = st.columns(2)
with col1:
    atendimentos_por_natureza = (atendimentos.groupby(['de_natureza']).size()).reset_index(name='quantidade')
    atendimentos_por_natureza.reset_index(drop=False, inplace=True)
    atendimentos_por_natureza_ordenado = atendimentos_por_natureza.sort_values(by=['quantidade'],ascending=False)
    atendimentos_por_natureza_top_10 = atendimentos_por_natureza_ordenado.head(10)
    fig = px.pie(atendimentos_por_natureza_top_10, names="de_natureza", values="quantidade", title="Demandas por Natureza", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=500,height=700)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-1,xanchor="right",x=1))
    st.write(fig)
with col2:
    atendimentos_por_assunto = (atendimentos.groupby(['de_assunto']).size()).reset_index(name='quantidade')
    atendimentos_por_assunto.reset_index(drop=False, inplace=True)
    atendimentos_por_assunto_ordenado = atendimentos_por_assunto.sort_values(by=['quantidade'],ascending=False)
    atendimentos_por_assunto_top_10 = atendimentos_por_assunto_ordenado.head(10)
    fig = px.pie(atendimentos_por_assunto_top_10, names="de_assunto", values="quantidade", title="Demandas por Assunto", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=500,height=700)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-1,xanchor="right",x=1))
    st.write(fig)

atendimentos_natureza_assunto = atendimentos[['de_natureza', 'de_assunto', 'de_status_atendimento']]
atendimentos_natureza_assunto['quantidade'] = 1
atendimentos_natureza_assunto.de_assunto.fillna('Não Informado', inplace=True) 
fig = px.sunburst(atendimentos_natureza_assunto, title="Natureza e Assunto", path=['de_natureza', 'de_assunto'], values='quantidade', color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=1000,height=500)
st.write(fig)


#atendimentos_por_tipo_pessoa = (atendimentos.groupby(['de_sexo_solicitante']).size()).reset_index(name='quantidade')
#atendimentos_por_tipo_pessoa.reset_index(drop=False, inplace=True)
#aatendimentos_por_tipo_pessoa_ordenado = atendimentos_por_tipo_pessoa.sort_values(by=['quantidade'],ascending=False)
#fig = px.pie(aatendimentos_por_tipo_pessoa_ordenado, names="de_sexo_solicitante", values="quantidade", title="Demandas por Sexo", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
#fig.update_layout(title_x=0.2, xaxis_rangeslider_visible=True, width=1000,height=500)
#st.write(fig)

atendimentos_por_identificacao = (atendimentos.groupby(['de_tp_identificacao']).size()).reset_index(name='quantidade')
atendimentos_por_identificacao.reset_index(drop=False, inplace=True)
atendimentos_por_identificacao_ordenado = atendimentos_por_identificacao.sort_values(by=['quantidade'],ascending=False)
fig = px.pie(atendimentos_por_identificacao_ordenado, names="de_tp_identificacao", values="quantidade", title="Demandas por Tipo de Identificacação", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=1000,height=500)
st.write(fig)

col1, col2 = st.columns(2)
with col1:
    atendimentos_por_pessoa = (atendimentos.groupby(['tipo_pessoa']).size()).reset_index(name='quantidade')
    atendimentos_por_pessoa.reset_index(drop=False, inplace=True)
    atendimentos_por_pessoa_ordenado = atendimentos_por_pessoa.sort_values(by=['quantidade'],ascending=False)
    fig = px.pie(atendimentos_por_pessoa_ordenado, names="tipo_pessoa", values="quantidade", title="Demandas por Tipo de Pessoa", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=500,height=500)
    st.write(fig)
with col2:
    atendimentos_por_sexo = (atendimentos.groupby(['de_sexo_solicitante']).size()).reset_index(name='quantidade')
    atendimentos_por_sexo.reset_index(drop=False, inplace=True)
    atendimentos_por_sexo_ordenado = atendimentos_por_sexo.sort_values(by=['quantidade'],ascending=False)
    atendimentos_por_sexo_ordenado['de_sexo_solicitante'] = atendimentos_por_sexo_ordenado['de_sexo_solicitante'].replace('M', 'Maculino')
    atendimentos_por_sexo_ordenado['de_sexo_solicitante'] = atendimentos_por_sexo_ordenado['de_sexo_solicitante'].replace('F', 'Feminino')
    atendimentos_por_sexo_ordenado['de_sexo_solicitante'] = atendimentos_por_sexo_ordenado['de_sexo_solicitante'].replace('N', 'Não Informado')
    fig = px.pie(atendimentos_por_sexo_ordenado, names="de_sexo_solicitante", values="quantidade", title="Demandas por Sexo", color_discrete_sequence=['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'])
    fig.update_layout(title_x=0.15, xaxis_rangeslider_visible=True, width=500,height=500)
    st.write(fig)


def verifica_orgao_saida(row):
    if row['ch_atendimento'].startswith('E-SIC'):
        return 'Transferido para E-SIC'
    if row['ch_atendimento'].startswith('OGE'):
        return 'Recebido do E-SIC' 
    else:
        return 'Normal'

#atendimentos_lista = atendimentos[['id_atendimento', 'de_natureza', 'de_assunto', 'de_status_atendimento']]
#atendimentos_com_encaminhamentos = pd.merge(atendimentos_lista, encaminhamentos, on='id_atendimento')
#st.dataframe(atendimentos_com_encaminhamentos)

#encaminhamentos_arvore = encaminhamentos['nm_orgao_origem', 'nm_orgao']
#st.dataframe(encaminhamentos_arvore)

if st.checkbox('Dados Abertos'):
    st.subheader('Atendimentos de Ouvidoria')
    #st.dataframe(atendimentos)
    atendimentos_csv = convert_df(atendimentos)
    st.download_button(
        label="Download dos dados em CSV",
        data=atendimentos_csv,
        file_name='manifestacoes_ouvidoria.csv',
        mime='text/csv'
    )
    st.subheader('Encaminhamentos de Ouvidoria')
    #st.dataframe(encaminhamentos)
    encaminhamentos_csv = convert_df(encaminhamentos)
    st.download_button(
        label="Download dos encaminhamentos em CSV",
        data=atendimentos_csv,
        file_name='encaminhamentos_ouvidoria.csv',
        mime='text/csv'
    )

