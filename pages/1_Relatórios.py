import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

# CARREGA OS DADOS
@st.cache_data
def carrega_dados():
    data = pd.read_csv('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/dee3f7ca-4c97-4a73-abcf-9f7330ba06b6/download/ouvidoria-2019.csv', sep=';')
#    data = pd.read_csv('ouvidoria-2019.csv', sep=';')
    return data

atendimentos_completo = carrega_dados()

hoje = str(date.today())
atendimentos_completo['sigla_orgao_saida'] = atendimentos_completo['sigla_orgao_saida'].str.replace('Sem Tramit.','Pronto Atendimento')
atendimentos_completo['sigla_orgao_saida'] = atendimentos_completo['sigla_orgao_saida'].str.replace('Sem Tramit.','Pronto Atendimento')
atendimentos_completo.data_conclusao.fillna(hoje, inplace=True) 
atendimentos_completo[['data_conclusao','data_atendimento']] = atendimentos_completo[['data_conclusao','data_atendimento']].apply(pd.to_datetime)
atendimentos_completo['prazo_atendimento'] = (atendimentos_completo['data_conclusao'] - atendimentos_completo['data_atendimento']).dt.days
atendimentos_completo['atrasado'] = np.where(atendimentos_completo['prazo_atendimento'] > 30 , True, False)
atendimentos_completo['quantidade'] = 1

# TITULO DO APP
st.title("Relatório de Ouvidoria")

# CAMPOS DE FILTRO
ano = st.selectbox(
    'Selecione o ano',
    ('2019', '2020', '2021', '2022', '2023'), index=4)

relatorio = st.selectbox(
    'Selecione o relatório',
    ('primeiro trimestre', 'segundo trimestre', 'terceiro trimestre', 'quarto trimestre', 'ano'), index=1)

if relatorio == 'primeiro trimestre': 
    start_date = ano + '-01-01'
    end_date   = ano + '-03-31'
elif relatorio == 'segundo trimestre':
    start_date = ano + '-04-01'
    end_date   = ano + '-06-30'
elif relatorio == 'terceiro trimestre':
    start_date = ano + '-07-01'
    end_date   = ano + '-09-30'
elif relatorio == 'quarto trimestre':
    start_date = ano + '-10-01'
    end_date   = ano + '-12-31'
else:
    start_date = ano + '-01-01'
    end_date   = ano + '-12-31'


atendimentos = atendimentos_completo.query('data_atendimento >= @start_date and data_atendimento <= @end_date')

tamanho = len(atendimentos)

orgao = st.selectbox(
    'Selecione o órgão',
    ('TODOS', 'SICOS', 'SEPLAN', 'SIE'), index=0)

if orgao == 'SICOS':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SICOS"')
if orgao == 'SEPLAN':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SEPLAN"')
if orgao == 'SIE':
    atendimentos = atendimentos.query('sigla_orgao_primeiro_encaminhamento == "SIE"')    

ligacoes = st.number_input('Quantidade de ligações no período', min_value=1, value=999, step=1)




# 1 - ATENDIMENTO DE OUVIDORIA
st.write(""" 
## 1 - ATENDIMENTO DE OUVIDORIA
O Atendimento de Ouvidoria se inicia a partir do contato realizado pelo usuário de produtos e serviços do governo estadual por meio de telefone, sistema informatizado de ouvidoria – Sistema OUV, carta, e-mail ou presencialmente.	
Após o registro da manifestação, a Ouvidoria-Geral procede à análise preliminar da manifestação. 

As manifestações são encaminhadas às ouvidorias setoriais ou seccionais diretamente envolvidas, as quais respondem à Ouvidoria-Geral do Estado, 
que analisa a resposta e envia a Decisão Administrativa Final ao usuário no prazo legalmente estabelecido, que atualmente é de até 30 dias.
""")
quantidade_atendimentos = len(atendimentos.index)
quantidade_pronto_atendimento = len(atendimentos[atendimentos["sigla_orgao_saida"]=="Pronto Atendimento"])
quantidade_transferidos = len(atendimentos[atendimentos["transferido"]=="Transferido"])
quantidade_telefonemas = len(atendimentos[atendimentos["forma_atendimento"]=="Telefone"])
quantidade_encaminhados = quantidade_atendimentos - quantidade_pronto_atendimento - quantidade_transferidos
quantidade_tratados = quantidade_atendimentos - quantidade_transferidos
atendimentos_tratados = atendimentos[(atendimentos["transferido"]!="Transferido") & (atendimentos["status"]=="Concluido")]
atendimentos_encaminhados = atendimentos[(atendimentos["transferido"]=="Normal") & (atendimentos["status"]!="Concluido")]
atendimentos_transferidos = atendimentos[atendimentos["transferido"]=="Transferido"]
quantidade_transferidos_2 = len(atendimentos_transferidos)
atendimentos_pronto = atendimentos[atendimentos["sigla_orgao_saida"]=="Pronto Atendimento"]
atendimentos_orgaos = atendimentos[atendimentos["sigla_orgao_saida"]!="Pronto Atendimento"]
quantidade_tratados_concluidos = len(atendimentos_tratados[atendimentos_tratados["status"]=="Concluido"])
quantidade_tratados_concluidos_prazo = len(atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido") & (atendimentos_tratados["atrasado"]==False)])
quantidade_tratados_concluidos_fora_prazo = len(atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido") & (atendimentos_tratados["atrasado"]==True)])
quantidade_tratados_encaminhados = len(atendimentos_encaminhados)
quantidade_tratados_encaminhados_prazo = len(atendimentos_encaminhados[atendimentos_encaminhados["atrasado"]==False])
quantidade_tratados_encaminhados_fora_prazo = len(atendimentos_encaminhados[atendimentos_encaminhados["atrasado"]==True])


# 2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO
st.write("""
## 2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO
""")
st.write("A Ouvidoria-Geral do Estado registrou " + str(quantidade_atendimentos) + 
         " manifestações no " + str(relatorio) + " de " + str(ano) + ", sendo que " + str(quantidade_encaminhados) + " foram encaminhadas aos órgãos e entidades do Poder Executivo Estadual em razão da pertinência da matéria; " + 
        str(quantidade_pronto_atendimento) + " são demandas de ouvidoria com pronto atendimento; " + str(quantidade_transferidos) + " manifestações transferidas ao sistema de informação ao cidadão (E-SIC); " +
        "e, " + str(ligacoes) + " ligações recebidas no 0800 sendo " + str(quantidade_telefonemas) + " convertidas manifestações de ouvidorias.")
st.write("Ressaltamos que cada órgão ou entidade da Administração Pública Estadual possui especificidades e características próprias, definidas pelos serviços prestados à população.")

atendimentos_tabela = atendimentos.groupby(['sigla_orgao_saida','natureza']).size().to_frame('quantidade')
atendimentos_tabela_pivot = pd.pivot_table(atendimentos_tabela, index='sigla_orgao_saida', values='quantidade', columns='natureza', aggfunc='sum' )
atendimentos_tabela_pivot.rename({'sigla_orgao_saida': 'Órgão'}, axis=1, inplace=True)
st.dataframe(atendimentos_tabela_pivot)

#atendimentos_trans_tabela = atendimentos_transferidos.groupby(['natureza']).size().to_frame('quantidade')
#atendimentos_trans_tabela_pivot = pd.pivot_table(atendimentos_trans_tabela, index='natureza', values='quantidade', columns='natureza', aggfunc='sum' )
#atendimentos_trans_tabela_pivot.rename({'sigla_orgao_saida': 'Órgão'}, axis=1, inplace=True)
#st.dataframe(atendimentos_trans_tabela_pivot)

# 3 - RESULTADOS DA OUVIDORIA NO PERÍODO
st.write(""" 
## 3 - RESULTADOS DA OUVIDORIA NO PERÍODO
O desempenho das atividades da Ouvidoria é medido por meio de indicadores, cujos resultados são acompanhados periodicamente.

Uma das principais competências das unidades de ouvidoria é fornecer aos órgãos e entidades informações sobre as necessidades dos cidadãos para que possa melhorar continuamente seus processos, produtos e serviços. Um adequado sistema de registro das demandas facilita o levantamento dessas informações, bem como, o acesso a outros dados do órgão ou da entidade.

""")

st.write("Visão Geral – Período: " + str(start_date) + " a " + str(end_date))

total = go.Figure(go.Indicator(
    mode = "number",
    value = quantidade_tratados,
    number = {"valueformat":"f"},
    title = {"text": "Atendimentos"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = "lightgray")
st.plotly_chart(total)
subtotal = go.Figure()
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = quantidade_tratados_concluidos,
    number = {"valueformat":"f"},
    title = {"text": "Respondidas"},
    delta = {'reference': 400, 'relative': True},
    domain = {'x': [0, 0.5], 'y': [0.7, 1]}))
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = quantidade_tratados_encaminhados,
    number = {"valueformat":"f"},
    title = {"text": "Em tratamento"},
    delta = {'reference': 400, 'relative': True},
    domain = {'x': [0.5, 1], 'y': [0.7, 1]}))
percentual_tratados_prazo = (quantidade_tratados_concluidos_prazo * 100) / quantidade_tratados_concluidos
subtotal.add_trace(go.Indicator(
    mode = "number",
    title = {"text": "No prazo"},
    value = quantidade_tratados_concluidos_prazo,
    number = {"valueformat":".f"},
    domain = {'x': [0, 0.25], 'y': [0.2, 0.5]}))
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = percentual_tratados_prazo,
    number = {"valueformat":".2f", "suffix": "%"},
    domain = {'x': [0, 0.25], 'y': [0, 0.19]}))
percentual_tratados_fora_prazo = (quantidade_tratados_concluidos_fora_prazo * 100) / quantidade_tratados_concluidos
subtotal.add_trace(go.Indicator(
    mode = "number",
    title = {"text": "Fora prazo"},
    value = quantidade_tratados_concluidos_fora_prazo,
    number = {"valueformat":".f"},
    domain = {'x': [0.26, 0.5], 'y': [0.2, 0.5]}))
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = percentual_tratados_fora_prazo,
    number = {"valueformat":".2f", "suffix": "%"},
    domain = {'x': [0.26, 0.5], 'y': [0, 0.19]}))
percentual_encaminhados_prazo = (quantidade_tratados_encaminhados_prazo * 100) / quantidade_tratados_encaminhados
subtotal.add_trace(go.Indicator(
    mode = "number",
    title = {"text": "No prazo"},
    value = quantidade_tratados_encaminhados_prazo,
    number = {"valueformat":".f"},
    domain = {'x': [0.5, 0.75], 'y': [0.2, 0.5]}))
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = percentual_encaminhados_prazo,
    number = {"valueformat":".2f", "suffix": "%"},
    domain = {'x': [0.5, 0.75], 'y': [0, 0.19]}))
percentual_encaminhados_fora_prazo = (quantidade_tratados_encaminhados_fora_prazo * 100) / quantidade_tratados_encaminhados
subtotal.add_trace(go.Indicator(
    mode = "number",
    title = {"text": "Fora prazo"},
    value = quantidade_tratados_encaminhados_fora_prazo,
    number = {"valueformat":".f"},
    domain = {'x': [0.75, 1], 'y': [0.2, 0.5]}))
subtotal.add_trace(go.Indicator(
    mode = "number",
    value = percentual_encaminhados_fora_prazo,
    number = {"valueformat":".2f", "suffix": "%"},
    domain = {'x': [0.75, 1], 'y': [0, 0.19]}))
subtotal.update_layout(paper_bgcolor = "lightgray")
st.plotly_chart(subtotal)


atendimentos_tratados_concluidos = atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido")] 
prazo_medio = atendimentos_tratados_concluidos.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Geral)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = "lightgray")
st.plotly_chart(total)

prazo_medio_pronto = atendimentos_pronto.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio_pronto,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Pronto Atendimento)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = "lightgray")
st.plotly_chart(total)

prazo_medio_orgaos = atendimentos_orgaos.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio_orgaos,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Órgãos)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = "lightgray")
st.plotly_chart(total)

st.dataframe(atendimentos_encaminhados)


atendimentos_concluidos = atendimentos_tratados[atendimentos_tratados["status"]!="Concluidos"]
#atendimentos_concluidos['tempo_resposta'] = abs(datetime.datetime.strptime(str(atendimentos_concluidos['data_conclusao']), '%Y-%m-%d') - datetime.datetime.strptime(str(atendimentos_concluidos['data_atendimento']), '%Y-%m-%d')).days 
#st.dataframe(atendimentos_concluidos)

ate_primeiro_por_natureza = atendimentos_tratados.groupby(['natureza']).size().to_frame('quantidade')
quantidade_atendimentos_tratados = len(atendimentos_tratados)
quantidade_solicitacoes = int(ate_primeiro_por_natureza.query("natureza == 'Solicitação'").values[0])
quantidade_reclamacoes = int(ate_primeiro_por_natureza.query("natureza == 'Reclamação'").values[0])
quantidade_denuncias = int(ate_primeiro_por_natureza.query("natureza == 'Denúncia'").values[0])
quantidade_elogios = int(ate_primeiro_por_natureza.query("natureza == 'Elogio'").values[0])
quantidade_sugestoes = int(ate_primeiro_por_natureza.query("natureza == 'Sugestão'").values[0])
percentual_solicitacoes = round((quantidade_solicitacoes * 100) / quantidade_atendimentos_tratados, 2) 
percentual_reclamacoes = round((quantidade_reclamacoes * 100) / quantidade_atendimentos_tratados, 2)
percentual_denuncias = round((quantidade_denuncias * 100) / quantidade_atendimentos_tratados, 2)
percentual_elogios = round((quantidade_elogios * 100) / quantidade_atendimentos_tratados, 2) 
percentual_sugestoes = round((quantidade_sugestoes * 100) / quantidade_atendimentos_tratados, 2) 


# 4 - RESULTADOS DO PERÍODO
st.write(""" 
## 4 - RESULTADOS DO PERÍODO
### 4.1 TIPOS DE MANIFESTAÇÕES
""")
st.write("A maior parte das manifestações (" + str(percentual_solicitacoes) + "%) atendidas pela Ouvidoria pertence ao tipo Solicitação. O tipo Reclamação, alcança percentual bem menor (" + str(percentual_reclamacoes) + "%), Denúncias (" + str(percentual_denuncias) + "%), Elogios (" + str(percentual_elogios) + "%) e Sugestões (" + str(percentual_sugestoes) + "%).")

pizza = px.pie(atendimentos_tratados, values='quantidade', names='natureza', title='Tipologia das Manifestações', color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(pizza)

#fig.show()


st.write(""" 
### 4.2 - ASSUNTOS MAIS DEMANDADOS
""")
ate_primeiro_por_assunto = atendimentos_tratados.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
data_top = ate_primeiro_por_assunto_ordenado.head(10)
data_top.reset_index(drop=False, inplace=True)

#st.write(fig)

st.write("""
### 4.3 - ANÁLISE DAS MANIFESTAÇÕES – SOLICITAÇÕES
Apresentamos o ranking dos 10 assuntos mais demandados no período.
""")
st.dataframe(data_top)  
st.write(data_top.columns)
fig=px.bar(data_top, x='quantidade',y='assunto', orientation='h', color='quantidade', color_discrete_sequence=px.colors.sequential.RdBu)       
st.write(fig)

st.write("""
### 4.4 - ANÁLISE DAS MANIFESTAÇÕES – RECLAMAÇÕES


### 4.5 - ANÁLISE DAS MANIFESTAÇÕES – DENÚNCIAS


### 4.6 - ANÁLISE DAS MANIFESTAÇÕES – ELOGIOS


### 4.7 - ANÁLISE DAS MANIFESTAÇÕES – SUGESTÕES

""")

# 5 - PERFIL DOS SOLICITANTES
st.write(""" 
## 5 - PERFIL DOS SOLICITANTES
De acordo com os dados apresentados na tabela 2, que demonstra o perfil do manifestante, pode-se inferir que o demandante é, em sua maioria pessoa física do sexo feminino.
""")

# 6 - OS 5 ÓRGÃOS COM MAIORES MANIFESTAÇÕES DE OUVIDORIA POR TIPOLOGIA E ASSUNTO
st.write(""" 
## 6 - OS 5 ÓRGÃOS COM MAIORES MANIFESTAÇÕES DE OUVIDORIA POR TIPOLOGIA E ASSUNTO
""")
         

if st.checkbox('Dados Abertos'):
    st.subheader('Manifestações de Ouvidoria')
    st.dataframe(atendimentos)
    atendimentos_csv = convert_df(atendimentos)
    st.download_button(
        label="Download dos dados em CSV",
        data=atendimentos_csv,
        file_name='manifestacoes_ouvidoria.csv',
        mime='text/csv'
    )


    demandas_em_tratamento = convert_df(atendimentos_encaminhados)
    st.download_button(
        label="Download dados em CSV",
        data=demandas_em_tratamento,
        file_name='demandas_em_tratamento.csv',
        mime='text/csv',
    )
    
