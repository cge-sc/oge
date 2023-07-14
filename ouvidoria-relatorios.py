import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#from st_aggrid import AgGrid, GridOptionsBuilder
#import plotly.figure_factory as ff

# CARREGA OS DADOS
@st.cache_data
def carrega_dados():
    data = pd.read_csv('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/dee3f7ca-4c97-4a73-abcf-9f7330ba06b6/download/ouvidoria-2019.csv', sep=';')
    return data

atendimentos_completo = carrega_dados()

atendimentos_completo['sigla_orgao_saida'] = atendimentos_completo['sigla_orgao_saida'].str.replace('Sem Tramit.','Pronto Atendimento')

# TITULO DO APP
st.title("Relatório de Ouvidoria")

# CAMPOS DE FILTRO
ano = st.selectbox(
    'Selecione o ano?',
    ('2019', '2020', '2021', '2022', '2023'), index=4)


relatorio = st.selectbox(
    'Selecione o relatório?',
    ('primeiro trimestre', 'segundo trimestre', 'terceiro trimestre', 'quarto trimestre', 'ano'), index=1)

if relatorio == 'primeiro trimestre': 
    start_date = ano + '-01-01'
    end_date   = ano + '-03-31'
elif relatorio == 'segundo trimestre':
    start_date = ano + '-04-01'
    end_date   = ano + '-06-30'
elif relatorio == 'terceiro trimestre':
    start_date = ano + '-07-01'
    end_date   = ano + '-09-31'
elif relatorio == 'quarto trimestre':
    start_date = ano + '-10-01'
    end_date   = ano + '-12-31'
else:
    start_date = ano + '-01-01'
    end_date   = ano + '-12-31'

atendimentos = atendimentos_completo.query('data_atendimento >= @start_date and data_atendimento <= @end_date')

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
atendimentos_tratados = atendimentos[atendimentos["transferido"]!="Transferido"]
quantidade_tratados_concluidos = len(atendimentos_tratados[atendimentos_tratados["status"]=="Concluido"])
quantidade_tratados_encaminhados = len(atendimentos_tratados[atendimentos_tratados["status"]=="Encaminhado"])

# 2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO
st.write("""
## 2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO
""")
st.write("A Ouvidoria-Geral do Estado registrou " + str(quantidade_atendimentos) + 
         " manifestações no " + str(relatorio) + " de " + str(ano) + ", sendo que " + str(quantidade_encaminhados) + " foram encaminhadas aos órgãos e entidades do Poder Executivo Estadual em razão da pertinência da matéria; " + 
        str(quantidade_pronto_atendimento) + " são demandas de ouvidoria com pronto atendimento; " + str(quantidade_transferidos) + " manifestações transferidas ao sistema de informação ao cidadão (E-SIC); " +
        "e, " + str(999) + " ligações recebidas no 0800 sendo " + str(quantidade_telefonemas) + " convertidas manifestações de ouvidorias.")
st.write("Ressaltamos que cada órgão ou entidade da Administração Pública Estadual possui especificidades e características próprias, definidas pelos serviços prestados à população.")

atendimentos_tabela = atendimentos.groupby(['sigla_orgao_saida','natureza']).size().to_frame('quantidade')
atendimentos_tabela_pivot = pd.pivot_table(atendimentos_tabela, index='sigla_orgao_saida', values='quantidade', columns='natureza', aggfunc='sum' )
atendimentos_tabela_pivot.rename({'sigla_orgao_saida': 'Órgão'}, axis=1, inplace=True)
st.dataframe(atendimentos_tabela_pivot)


# 3 - RESULTADOS DA OUVIDORIA NO PERÍODO
st.write(""" 
## 3 - RESULTADOS DA OUVIDORIA NO PERÍODO
O desempenho das atividades da Ouvidoria é medido por meio de indicadores, cujos resultados são acompanhados periodicamente.

Uma das principais competências das unidades de ouvidoria é fornecer aos órgãos e entidades informações sobre as necessidades dos cidadãos para que possa melhorar continuamente seus processos, produtos e serviços. Um adequado sistema de registro das demandas facilita o levantamento dessas informações, bem como, o acesso a outros dados do órgão ou da entidade.

""")

st.write("Visão Geral – Período: " + str(start_date) + " a " + str(end_date))

fig = go.Figure(go.Indicator(
    mode = "number",
    value = quantidade_tratados,
    number = {"valueformat":"f"},
    title = {"text": "Atendimentos"},
    domain = {'x': [0, 1], 'y': [0, 1]}))

fig.update_layout(paper_bgcolor = "lightgray")

st.plotly_chart(fig)

st.write( quantidade_tratados_concluidos)
st.write( quantidade_tratados_encaminhados)
atendimentos_concluidos = atendimentos_tratados[atendimentos_tratados["status"]!="Concluidos"]
atendimentos_concluidos['tempo_resposta'] = abs(datetime.datetime.strptime(str(atendimentos_concluidos['data_conclusao']), '%Y-%m-%d') - datetime.datetime.strptime(str(atendimentos_concluidos['data_atendimento']), '%Y-%m-%d')).days 
st.dataframe(atendimentos_concluidos)

ate_primeiro_por_natureza = atendimentos.groupby(['natureza']).size().to_frame('quantidade')
st.dataframe(ate_primeiro_por_natureza)
quantidade_solicitacoes = int(ate_primeiro_por_natureza.query("natureza == 'Solicitação'").values[0])
quantidade_reclamacoes = int(ate_primeiro_por_natureza.query("natureza == 'Reclamação'").values[0])
quantidade_denuncias = int(ate_primeiro_por_natureza.query("natureza == 'Denúncia'").values[0])
quantidade_elogios = int(ate_primeiro_por_natureza.query("natureza == 'Elogio'").values[0])
quantidade_sugestoes = int(ate_primeiro_por_natureza.query("natureza == 'Sugestão'").values[0])
percentual_solicitacoes = round((quantidade_solicitacoes * 100) / quantidade_atendimentos, 2) 
percentual_reclamacoes = round((quantidade_reclamacoes * 100) / quantidade_atendimentos, 2)
percentual_denuncias = round((quantidade_denuncias * 100) / quantidade_atendimentos, 2)
percentual_elogios = round((quantidade_elogios * 100) / quantidade_atendimentos, 2) 
percentual_sugestoes = round((quantidade_sugestoes * 100) / quantidade_atendimentos, 2) 


# 4 - RESULTADOS DO PERÍODO
st.write(""" 
## 4 - RESULTADOS DO PERÍODO


### 4.1 TIPOS DE MANIFESTAÇÕES
""")
st.write("A maior parte das manifestações (" + str(percentual_solicitacoes) + "%) atendidas pela Ouvidoria pertence ao tipo Solicitação. O tipo Reclamação, alcança percentual bem menor (" + str(percentual_reclamacoes) + "%), Denúncias (" + str(percentual_denuncias) + "%), Elogios (" + str(percentual_elogios) + "%) e Sugestões (" + str(percentual_sugestoes) + "%).")
#quantidade_solicitações = ate_primeiro_por_natureza
st.bar_chart(ate_primeiro_por_natureza)
#st.plotly_chart(fig, use_container_width=False, sharing="streamlit", theme="streamlit", **kwargs)


ate_primeiro_por_assunto = atendimentos.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
st.dataframe(ate_primeiro_por_assunto_ordenado)
data_top = ate_primeiro_por_assunto_ordenado.head()
st.write(data_top)
#ate_primeiro_por_assunto_ordenado_limpo = ate_primeiro_por_assunto_ordenado.drop(ate_primeiro_por_assunto_ordenado[ate_primeiro_por_assunto_ordenado.assunto == 'Manifestação Incompleta (Falta Dados)'].index)
#indexDelete = ate_primeiro_por_assunto_ordenado[ (ate_primeiro_por_assunto_ordenado['assunto'] == 'Manifestação Incompleta (Falta Dados)') & (ate_primeiro_por_assunto_ordenado['assunto'] == 'Manifestação Incompleta (Falta Dados)') ].index
#ate_primeiro_por_assunto_ordenado.drop(indexDelete , inplace=True)
#ate_primeiro_por_assunto_ordenado_limpo = ate_primeiro_por_assunto_ordenado.loc[ate_primeiro_por_assunto_ordenado["assunto"] == "Manifestação Incompleta (Falta Dados)"]
st.dataframe(ate_primeiro_por_assunto_ordenado)

st.write(""" 
### 4.2 - ASSUNTOS MAIS DEMANDADOS
""")
st.bar_chart(ate_primeiro_por_assunto)
st.write("""
### 4.3 - ANÁLISE DAS MANIFESTAÇÕES – SOLICITAÇÕES


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
