import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


####################################################
# INICIALIZAÇÃO
#######################################################
# LAYOUT
with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

cores_cge = ['#A1C222', '#38a64c','#008265', '#005c64', '#171717', '#424242', '#d5d6d7', '#e42320', '#33EE33', '#33FF33']
verde_claro = ['#A1C222']
cinza_escuro = ['#424242']

hoje = str(date.today())

# CARREGA OS DADOS
def convert_df(df):
    return df.to_csv().encode('utf-8')

@st.cache_data
def carrega_dados():
    data = pd.read_csv('https://dados.sc.gov.br/dataset/3c9311c4-ad13-4730-bb6b-bb0f5fda2910/resource/dee3f7ca-4c97-4a73-abcf-9f7330ba06b6/download/ouvidoria-2019.csv', sep=';')
#    data = pd.read_csv('ouvidoria-2019.csv', sep=';')
    return data

atendimentos_completo = carrega_dados()


# LIMPAR ARQUIVO
atendimentos_completo['sigla_orgao_saida'] = atendimentos_completo['sigla_orgao_saida'].str.replace('Sem Tramit.','Pronto Atendimento')
atendimentos_completo.data_conclusao.fillna(hoje, inplace=True) 
atendimentos_completo[['data_conclusao','data_atendimento']] = atendimentos_completo[['data_conclusao','data_atendimento']].apply(pd.to_datetime)
atendimentos_completo['prazo_atendimento'] = (atendimentos_completo['data_conclusao'] - atendimentos_completo['data_atendimento']).dt.days
atendimentos_completo['atrasado'] = np.where(atendimentos_completo['prazo_atendimento'] > 30 , True, False)
atendimentos_completo['quantidade'] = 1

############################################################
# CABEÇALHOS 
###############################################################
# TITULO DO APP
st.header("FILTROS")
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
    periodicidade = "TRIMESTRAL"
    periodo = "1º trimestre de " + str(ano)
elif relatorio == 'segundo trimestre':
    start_date = ano + '-04-01'
    end_date   = ano + '-06-30'
    periodicidade = "TRIMESTRAL"
    periodo = "2º trimestre de " + str(ano)    
elif relatorio == 'terceiro trimestre':
    start_date = ano + '-07-01'
    end_date   = ano + '-09-30'
    periodicidade = "TRIMESTRAL"
    periodo = "3º trimestre de " + str(ano)    
elif relatorio == 'quarto trimestre':
    start_date = ano + '-10-01'
    end_date   = ano + '-12-31'
    periodicidade = "TRIMESTRAL"
    periodo = "4º trimestre de " + str(ano)    
else:
    start_date = ano + '-01-01'
    end_date   = ano + '-12-31'
    periodicidade = "ANUAL"
    periodo = str(ano)    

atendimentos_periodo = atendimentos_completo.query('data_atendimento >= @start_date and data_atendimento <= @end_date')

# FILTRO ÓRGÃO
#orgaos = pd.DataFrame(atendimentos['sigla_orgao_saida'].unique())
#orgaos = orgaos.sort_values(by=0)
#quantidade_orgaos = len(orgaos)
#todos = pd.DataFrame([['Todos']])
#orgaos = pd.concat([orgaos, todos], ignore_index=False)
#orgaos = orgaos.dropna(axis='rows')
#
#orgao = st.selectbox(
#    'Selecione o órgão',
#    orgaos, index=quantidade_orgaos-1)
#
#if orgao != "Todos":
#    atendimentos_periodo = atendimentos.query('sigla_orgao_primeiro_encaminhamento == @orgao')
orgao = 'Todos'

# INPUT LIGAÇÕES TELEFÔNICAS
ligacoes = st.number_input('Quantidade de ligações no período', min_value=1, value=999, step=1)

#FILTRO OPÇÕES
conta_transferidos = st.checkbox('Contabiliza Transferidos', value=True)
conta_pronto = st.checkbox('Contabiliza Pronto Atendimento', value=True)
junta_denuncias = st.checkbox('Consolida Denúncias (Disque 100)', value=True)

# TOTALIZADORES
atendimentos_tratados = atendimentos_periodo[(atendimentos_periodo["transferido"]!="Transferido") & (atendimentos_periodo["status"]=="Concluido")]
#st.write("Tratados: " + str(len(atendimentos_tratados)))
atendimentos_encaminhados = atendimentos_periodo[(atendimentos_periodo["transferido"]=="Normal") & (atendimentos_periodo["status"]!="Concluido")]
#st.write("Em tratamento: " + str(len(atendimentos_encaminhados)))
atendimentos_transferidos = atendimentos_periodo[atendimentos_periodo["transferido"]=="Transferido"]
#st.write("Transferidos: " + str(len(atendimentos_transferidos)))
atendimentos_pronto = atendimentos_periodo[atendimentos_periodo["sigla_orgao_saida"]=="Pronto Atendimento"]
#st.write("Pronto Atendimento: " + str(len(atendimentos_pronto)))
atendimentos_orgaos = atendimentos_periodo[atendimentos_periodo["sigla_orgao_saida"]!="Pronto Atendimento"]
#st.write("Encaminhados: " + str(len(atendimentos_orgaos)))

if conta_transferidos:
    atendimentos_tratados = pd.concat([atendimentos_tratados, atendimentos_transferidos], ignore_index=False)
if conta_pronto:
    print("ok")
else:
    atendimentos_tratados.drop(atendimentos_tratados[atendimentos_tratados["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)
if junta_denuncias:
    atendimentos_tratados['natureza'] = atendimentos_completo['natureza'].str.replace('Denúncia (Disque 100)','Denúncia')

quantidade_pronto_atendimento = len(atendimentos_pronto)
quantidade_transferidos = len(atendimentos_transferidos)
quantidade_telefonemas = len(atendimentos_periodo[atendimentos_periodo["forma_atendimento"]=="Telefone"])
quantidade_encaminhados = len(atendimentos_orgaos) - quantidade_transferidos
quantidade_tratados = len(atendimentos_tratados)
quantidade_atendimentos = len(atendimentos_tratados) + len(atendimentos_encaminhados)
quantidade_tratados_concluidos = len(atendimentos_tratados[atendimentos_tratados["status"]=="Concluido"])
quantidade_tratados_concluidos_prazo = len(atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido") & (atendimentos_tratados["atrasado"]==False)])
quantidade_tratados_concluidos_fora_prazo = len(atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido") & (atendimentos_tratados["atrasado"]==True)])
quantidade_tratados_encaminhados = len(atendimentos_encaminhados)
quantidade_tratados_encaminhados_prazo = len(atendimentos_encaminhados[atendimentos_encaminhados["atrasado"]==False])
quantidade_tratados_encaminhados_fora_prazo = len(atendimentos_encaminhados[atendimentos_encaminhados["atrasado"]==True])

###############################################################
# 0 - TÍTULO DO RELATÓRIO
###############################################################
texto_título = "RELATÓRIO " + periodicidade + " DE GESTÃO DE OUVIDORIA"
st.header(texto_título)
st.subheader(periodo)
st.subheader("Florianópolis, " + hoje)

###############################################################
# 1 - ATENDIMENTO DE OUVIDORIA
###############################################################
st.header("1 - ATENDIMENTO DE OUVIDORIA")
st.write("""  
O Atendimento de Ouvidoria se inicia a partir do contato realizado pelo usuário de produtos e serviços do governo estadual por meio de telefone, sistema informatizado de ouvidoria – Sistema OUV, carta, e-mail ou presencialmente.	
Após o registro da manifestação, a Ouvidoria-Geral procede à análise preliminar da manifestação. 

As manifestações são encaminhadas às ouvidorias setoriais ou seccionais diretamente envolvidas, as quais respondem à Ouvidoria-Geral do Estado, 
que analisa a resposta e envia a Decisão Administrativa Final ao usuário no prazo legalmente estabelecido, que atualmente é de até 30 dias.
""")


#####################################################################
# 2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO
st.header("2 - MANIFESTAÇÕES POR ÓRGÃO OU ENTIDADE DO PODER EXECUTIVO")
st.write("A Ouvidoria-Geral do Estado registrou " + str(quantidade_atendimentos) + 
         " manifestações no " + periodo + ", sendo que " + str(quantidade_encaminhados) + " foram encaminhadas aos órgãos e entidades do Poder Executivo Estadual em razão da pertinência da matéria; " + 
        str(quantidade_pronto_atendimento) + " são demandas de ouvidoria com pronto atendimento; " + str(quantidade_transferidos) + " manifestações transferidas ao sistema de informação ao cidadão (E-SIC).")
st.write("Por meio do atendimento telefônico (0800), foram recebidas " + str(ligacoes) + " ligações recebidas no 0800 sendo " + str(quantidade_telefonemas) + " convertidas manifestações de ouvidorias.")
st.write("Ressaltamos que cada órgão ou entidade da Administração Pública Estadual possui especificidades e características próprias, definidas pelos serviços prestados à população.")
atendimentos_totais = pd.concat([atendimentos_tratados, atendimentos_encaminhados], ignore_index=False)
atendimentos_tabela = atendimentos_totais.groupby(['sigla_orgao_saida','natureza']).size().to_frame('quantidade')
atendimentos_tabela_pivot = pd.pivot_table(atendimentos_tabela, index='sigla_orgao_saida', values='quantidade', columns='natureza', aggfunc='sum' )
atendimentos_tabela_pivot.rename({'sigla_orgao_saida': 'Órgão'}, axis=1, inplace=True)

if conta_transferidos:
    transferidos = pd.DataFrame([["Transferidos", 0, 0, 0, 0, quantidade_transferidos, 0]])
    transferidos.columns = ["sigla_orgao", "Denúncia", "Denúncia (Disque 100)", "Elogio", "Reclamação", "Solicitação", "Sugestão"]
    transferidos = transferidos.set_index("sigla_orgao")
    atendimentos_tabela_pivot = pd.concat([atendimentos_tabela_pivot, transferidos], ignore_index=False)

if "Denúncia" in atendimentos_tabela_pivot.columns:
    denuncias = atendimentos_tabela_pivot["Denúncia"].sum()
else:
    denuncias = 0
if "Denúncia (Disque 100)" in atendimentos_tabela_pivot.columns:
    disque100 = atendimentos_tabela_pivot["Denúncia (Disque 100)"].sum()
else:
    disque100 = 0
if "Elogio" in atendimentos_tabela_pivot.columns:
    elogios = atendimentos_tabela_pivot["Elogio"].sum()
else:
    elogios =0
if "Reclamação" in atendimentos_tabela_pivot.columns:
    reclamacoes = atendimentos_tabela_pivot["Reclamação"].sum()
else:
    reclamacoes = 0
if "Solicitação" in atendimentos_tabela_pivot.columns:
    solicitacoes = atendimentos_tabela_pivot["Solicitação"].sum()
else:
    solicitacoes = 0
if "Sugestão" in atendimentos_tabela_pivot.columns:
    sugestoes = atendimentos_tabela_pivot["Sugestão"].sum()
else:
    sugestoes = 0
if "Solicitação Documentos/Informações/Lei de Acesso à Informação" in atendimentos_tabela_pivot.columns:
    lais = atendimentos_tabela_pivot["Solicitação Documentos/Informações/Lei de Acesso à Informação"].sum()
    totalizador = pd.DataFrame([["Total", denuncias, disque100, elogios, reclamacoes, solicitacoes, lais, sugestoes]])
    totalizador.columns = ["sigla_orgao", "Denúncia", "Denúncia (Disque 100)", "Elogio", "Reclamação", "Solicitação", "Solicitação Documentos/Informações/Lei de Acesso à Informação", "Sugestão"]
else:
    totalizador = pd.DataFrame([["Total", denuncias, disque100, elogios, reclamacoes, solicitacoes, sugestoes]])
    totalizador.columns = ["sigla_orgao", "Denúncia", "Denúncia (Disque 100)", "Elogio", "Reclamação", "Solicitação", "Sugestão"]
totalizador = totalizador.set_index("sigla_orgao")

if orgao == 'Todos':
    atendimentos_tabela_pivot = pd.concat([atendimentos_tabela_pivot, totalizador], ignore_index=False)
    atendimentos_tabela_pivot = atendimentos_tabela_pivot.fillna(0)
    if "Solicitação Documentos/Informações/Lei de Acesso à Informação" in atendimentos_tabela_pivot.columns:
        atendimentos_tabela_pivot["Total"] = atendimentos_tabela_pivot["Denúncia"] + atendimentos_tabela_pivot["Denúncia (Disque 100)"] + atendimentos_tabela_pivot["Elogio"] + atendimentos_tabela_pivot["Reclamação"] + atendimentos_tabela_pivot["Solicitação"] + atendimentos_tabela_pivot["Solicitação Documentos/Informações/Lei de Acesso à Informação"] + atendimentos_tabela_pivot["Sugestão"]
    else:
        atendimentos_tabela_pivot["Total"] = atendimentos_tabela_pivot["Denúncia"] + atendimentos_tabela_pivot["Denúncia (Disque 100)"] + atendimentos_tabela_pivot["Elogio"] + atendimentos_tabela_pivot["Reclamação"] + atendimentos_tabela_pivot["Solicitação"] + atendimentos_tabela_pivot["Sugestão"]
    # TABELA 1 - Tabela 1 - Manifestações recebidas por Tipo, segundo os órgãos e entidades do Poder Executivo
    st.write("TABELA 1 - Tabela 1 - Manifestações recebidas por Tipo, segundo os órgãos e entidades do Poder Executivo")
    st.dataframe(atendimentos_tabela_pivot)
    st.caption("Fonte: Sistema OUV. " + hoje)


##################################################################
# 3 - RESULTADOS DA OUVIDORIA NO PERÍODO
st.header("3 - RESULTADOS DA OUVIDORIA NO PERÍODO")
st.write(""" 
O desempenho das atividades da Ouvidoria é medido por meio de indicadores, cujos resultados são acompanhados periodicamente.

Uma das principais competências das unidades de ouvidoria é fornecer aos órgãos e entidades informações sobre as necessidades dos cidadãos para que possa melhorar continuamente seus processos, produtos e serviços. Um adequado sistema de registro das demandas facilita o levantamento dessas informações, bem como, o acesso a outros dados do órgão ou da entidade.
""")

st.write("Visão Geral – Período: " + str(start_date) + " a " + str(end_date))

total = go.Figure(go.Indicator(
    mode = "number",
    value = quantidade_atendimentos,
    number = {"valueformat":"f"},
    title = {"text": "Total de Manifestações"},
    #textfont = {'family': "Roboto", 'size': 50, 'color': "#fff"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = '#A1C222', font_family="Roboto", font=dict(family="Roboto", size=100, color="white"))
st.plotly_chart(total)
st.write("O indicador representa o tempo médio de encaminhamento de respostas ao usuário, a partir do recebimento da manifestação.")
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
subtotal.update_layout(paper_bgcolor = '#424242', font_family="Roboto", font=dict(family="Roboto", size=100, color="white"))
st.plotly_chart(subtotal)

st.write("3.1 TEMPO MÉDIO DE RESPOSTA DA OUVIDORIA-GERAL (EM DIAS)")
atendimentos_tratados_concluidos = atendimentos_tratados[(atendimentos_tratados["status"]=="Concluido")] 
prazo_medio = atendimentos_tratados_concluidos.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Geral)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = '#A1C222', font_family="Roboto", font=dict(family="Roboto", size=100, color="white"))
st.plotly_chart(total)

prazo_medio_pronto = atendimentos_pronto.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio_pronto,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Pronto Atendimento)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = '#424242', font_family="Roboto", font=dict(family="Roboto", size=100, color="white"))
st.plotly_chart(total)

prazo_medio_orgaos = atendimentos_orgaos.loc[:, 'prazo_atendimento'].mean()
total = go.Figure(go.Indicator(
    mode = "number",
    value = prazo_medio_orgaos,
    number = {"valueformat":".1f", "suffix":" dias"},
    title = {"text": "Tempo Médio Resposta (Órgãos)"},
    domain = {'x': [0, 1], 'y': [0.25, 0.75]}))
total.update_layout(paper_bgcolor = '#A1C222', font_family="Roboto", font=dict(family="Roboto", size=100, color="white"))
st.plotly_chart(total)
st.write("O tempo médio de resposta da Ouvidoria-Geral ao usuário foi de " + str(round(prazo_medio,2)) + " dias, incluindo as manifestações com o tratamento de pronto atendimento e as transferidas ao E-SIC.")
st.write("Se considerarmos apenas as manifestações que foram encaminhadas aos órgãos e entidades do poder executivo estadual para tratamento, o tempo médio de resposta passa para " + str(round(prazo_medio_orgaos,2)) + " dias.")

atendimentos_concluidos = atendimentos_tratados[atendimentos_tratados["status"]!="Concluidos"]

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


#####################################################################################
# 4 - RESULTADOS DO PERÍODO
#####################################################################################
st.header("4 - RESULTADOS DO PERÍODO")
st.subheader("4.1 TIPOS DE MANIFESTAÇÕES")

if junta_denuncias:
    st.write("A maior parte das manifestações (" + str(percentual_solicitacoes) + "%) atendidas pela Ouvidoria pertence ao tipo Solicitação. O tipo Reclamação, alcança percentual bem menor (" + str(percentual_reclamacoes) + "%), Denúncias (" + str(percentual_denuncias) + "%), Elogios (" + str(percentual_elogios) + "%) e Sugestões (" + str(percentual_sugestoes) + "%).")
else:
    quantidade_disque100 = int(ate_primeiro_por_natureza.query("natureza == 'Denúncia (Disque 100)'").values[0])
    percentual_disque100 = round((quantidade_disque100 * 100) / quantidade_atendimentos_tratados, 2)
    st.write("A maior parte das manifestações (" + str(percentual_solicitacoes) + "%) atendidas pela Ouvidoria pertence ao tipo Solicitação. O tipo Reclamação, alcança percentual bem menor (" + str(percentual_reclamacoes) + "%), Denúncias (" + str(percentual_denuncias) + "%), Denúncias - Disque 100 (" + str(percentual_disque100) + "%), Elogios (" + str(percentual_elogios) + "%) e Sugestões (" + str(percentual_sugestoes) + "%).")
pizza = px.pie(atendimentos_tratados, values='quantidade', names='natureza', title='Gráfico 1 - Tipologia das Manifestações', color_discrete_sequence=cores_cge)
pizza.update_layout(font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(pizza)
st.write("Fonte: Sistema OUV. " + hoje)

st.write(""" 
### 4.2 - ASSUNTOS MAIS DEMANDADOS
""")
atendimentos_solicitacoes = atendimentos_tratados[atendimentos_tratados["natureza"]=="Solicitação"]

ate_primeiro_por_assunto = atendimentos_tratados.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
data_top = ate_primeiro_por_assunto_ordenado.head(10)
data_top.reset_index(drop=True, inplace=True)

st.write("Apresentamos o ranking dos 10 assuntos mais demandados no " + periodo + ":")
fig=px.histogram(data_top, x='quantidade',y='assunto', orientation='h', title=" Gráfico 2 - Assuntos mais demandados", color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
#st.write(fig)
if st.checkbox('Mostrar Todos os Assuntos'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)



st.write(""" ### 4.3 - ANÁLISE DAS MANIFESTAÇÕES – SOLICITAÇÕES""")

atendimentos_solicitacoes = atendimentos_tratados[atendimentos_tratados["natureza"]=="Solicitação"]

ate_primeiro_por_assunto = atendimentos_solicitacoes.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_orgao = atendimentos_solicitacoes.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_orgao.reset_index(inplace=True)

ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
#ate_primeiro_por_orgao.drop(ate_primeiro_por_orgao[ate_primeiro_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)

ate_primeiro_por_orgao_ordenado = ate_primeiro_por_orgao.sort_values(by=['quantidade'],ascending=False)
orgaos_top = ate_primeiro_por_orgao_ordenado.head(10)
orgaos_top.reset_index(drop=False, inplace=True)


ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
assuntos_top = ate_primeiro_por_assunto_ordenado.head(10)
assuntos_top.reset_index(drop=True, inplace=True)

st.write("Solicitação: requerimento de adoção de providência por parte da Administração Pública Estadual. ")
st.write("No período, foram recepcionadas " + str(quantidade_solicitacoes) + " solicitações de providências, incluindo 98 Pedidos de Acesso à Informação que não apresentaram os requisitos legais para efetuar a transferência ao E-SIC.")

fig=px.histogram(orgaos_top, x='quantidade',y='sigla_orgao_saida', orientation='h', title="Gráfico 3 - Manifestações do tipo Solicitação, por órgão ou entidade (10 mais demandados)", color='quantidade', color_discrete_sequence=cinza_escuro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Órgãos das Solicitações'):
    st.dataframe(ate_primeiro_por_orgao_ordenado)


st.write("Apresentamos o ranking dos 10 assuntos mais demandados no " + periodo + " para as solicitações:")
fig=px.histogram(assuntos_top, x='quantidade',y='assunto', orientation='h', title="Gráfico 4 - Os 10 principais assuntos das Solicitações", color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Assuntos das Solicitações'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)

st.write("""
### 4.4 - ANÁLISE DAS MANIFESTAÇÕES – RECLAMAÇÕES """)

atendimentos_solicitacoes = atendimentos_tratados[atendimentos_tratados["natureza"]=="Reclamação"]

ate_primeiro_por_assunto = atendimentos_solicitacoes.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_orgao = atendimentos_solicitacoes.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_orgao.reset_index(inplace=True)

ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
#ate_primeiro_por_orgao.drop(ate_primeiro_por_orgao[ate_primeiro_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)

ate_primeiro_por_orgao_ordenado = ate_primeiro_por_orgao.sort_values(by=['quantidade'],ascending=False)
orgaos_top = ate_primeiro_por_orgao_ordenado.head(10)
orgaos_top.reset_index(drop=False, inplace=True)


ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
assuntos_top = ate_primeiro_por_assunto_ordenado.head(10)
assuntos_top.reset_index(drop=True, inplace=True)

st.write("Reclamação: demonstração de insatisfação relativa ao serviço ou à política pública")
st.write("No período, foram recepcionadas " + str(quantidade_reclamacoes) + " reclamações de providências, que são consideradas como demonstração de insatisfação")

fig=px.histogram(orgaos_top, x='quantidade',y='sigla_orgao_saida', orientation='h', title="Gráfico 5 - Manifestações do tipo Reclamação, por órgão ou entidade (10 mais demandados)", color='quantidade', color_discrete_sequence=cinza_escuro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Órgãos das Reclamações'):
    st.dataframe(ate_primeiro_por_orgao_ordenado)

st.write("Apresentamos o ranking dos 10 assuntos mais demandados nesse trimestre de 2023 para as reclamações:")
fig=px.histogram(data_top, x='quantidade',y='assunto', orientation='h', title="Gráfico 6 - Os 10 principais assuntos das Reclamações",color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Assuntos das Reclamações'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)

st.write("""### 4.5 - ANÁLISE DAS MANIFESTAÇÕES – DENÚNCIAS""")

atendimentos_denuncias = atendimentos_tratados[atendimentos_tratados["natureza"]=="Denúncia"]

ate_primeiro_por_assunto = atendimentos_denuncias.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_orgao = atendimentos_denuncias.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_orgao.reset_index(inplace=True)

ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
#ate_primeiro_por_orgao.drop(ate_primeiro_por_orgao[ate_primeiro_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)

ate_primeiro_por_orgao_ordenado = ate_primeiro_por_orgao.sort_values(by=['quantidade'],ascending=False)
orgaos_top = ate_primeiro_por_orgao_ordenado.head(10)
orgaos_top.reset_index(drop=False, inplace=True)

ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
assuntos_top = ate_primeiro_por_assunto_ordenado.head(10)
assuntos_top.reset_index(drop=True, inplace=True)

st.write("Denúncias: comunicação de prática de irregularidades ou ato ilícito cuja solução dependa da atuação dos órgãos apuratórios competentes.")
st.write("No período, foram recepcionadas " + str(quantidade_denuncias) + " reclamações de providências, que são consideradas como demonstração de insatisfação")

fig=px.histogram(orgaos_top, x='quantidade',y='sigla_orgao_saida', orientation='h', title="Gráfico 7 - Manifestações do tipo Denúncia, por órgão ou entidade (10 mais demandados)", color='quantidade', color_discrete_sequence=cinza_escuro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Órgãos das Denúncias'):
    st.dataframe(ate_primeiro_por_orgao_ordenado)

st.write("Apresentamos o ranking dos 10 assuntos mais demandados nesse trimestre de 2023 para as denúncias:")
fig=px.histogram(assuntos_top, x='quantidade',y='assunto', orientation='h', title="Gráfico 8 - Os 10 principais assuntos das Denúncias",color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Assuntos das Denúncias'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)

st.write("""### 4.6 - ANÁLISE DAS MANIFESTAÇÕES – ELOGIOS""")
atendimentos_elogios = atendimentos_tratados[atendimentos_tratados["natureza"]=="Elogio"]

ate_primeiro_por_assunto = atendimentos_elogios.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_orgao = atendimentos_elogios.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_orgao.reset_index(inplace=True)

ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
ate_primeiro_por_orgao.drop(ate_primeiro_por_orgao[ate_primeiro_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)


ate_primeiro_por_orgao_ordenado = ate_primeiro_por_orgao.sort_values(by=['quantidade'],ascending=False)
orgaos_top = ate_primeiro_por_orgao_ordenado.head(10)
orgaos_top.reset_index(drop=False, inplace=True)

ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
assuntos_top = ate_primeiro_por_assunto_ordenado.head(10)
assuntos_top.reset_index(drop=True, inplace=True)

st.write("Elogios: comunicação de prática de irregularidades ou ato ilícito cuja solução dependa da atuação dos órgãos apuratórios competentes.")
st.write("No período, foram recepcionadas " + str(quantidade_elogios) + " reclamações de providências, que são consideradas como demonstração de insatisfação")

fig=px.histogram(orgaos_top, x='quantidade',y='sigla_orgao_saida', orientation='h', title="Gráfico 9 - Manifestações do tipo Elogio, por órgão ou entidade (10 mais demandados)", color='quantidade', color_discrete_sequence=cinza_escuro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Órgãos dos Elogios'):
    st.dataframe(ate_primeiro_por_orgao_ordenado)


st.write("Apresentamos o ranking dos 10 assuntos mais demandados nesse trimestre de 2023 para os elogios:")
fig=px.histogram(assuntos_top, x='quantidade',y='assunto', orientation='h', title="Gráfico 10 - Os 10 principais assuntos dos Elogios", color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Assuntos dos Elogios'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)

         
st.write("""### 4.7 - ANÁLISE DAS MANIFESTAÇÕES – SUGESTÕES""")
atendimentos_sugestoes = atendimentos_tratados[atendimentos_tratados["natureza"]=="Sugestão"]

ate_primeiro_por_assunto = atendimentos_sugestoes.groupby(['assunto']).size().to_frame('quantidade')
ate_primeiro_por_orgao = atendimentos_sugestoes.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
ate_primeiro_por_assunto.reset_index(inplace=True)
ate_primeiro_por_orgao.reset_index(inplace=True)

ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Manifestação Incompleta (Falta Dados)"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Devolução Para Proteção aos Dados do Usuário"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não Foi Possível Compreender"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Atendimento em Duplicidade"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência municipal"].index, inplace=True)
#ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Lei de Acesso à Informação"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Não é de Competência da OGE"].index, inplace=True)
ate_primeiro_por_assunto.drop(ate_primeiro_por_assunto[ate_primeiro_por_assunto["assunto"] == "Competência da União/Federal"].index, inplace=True)
#ate_primeiro_por_orgao.drop(ate_primeiro_por_orgao[ate_primeiro_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)

ate_primeiro_por_orgao_ordenado = ate_primeiro_por_orgao.sort_values(by=['quantidade'],ascending=False)
orgaos_top = ate_primeiro_por_orgao_ordenado.head(10)
orgaos_top.reset_index(drop=False, inplace=True)

ate_primeiro_por_assunto_ordenado = ate_primeiro_por_assunto.sort_values(by=['quantidade'],ascending=False)
assuntos_top = ate_primeiro_por_assunto_ordenado.head(10)
assuntos_top.reset_index(drop=True, inplace=True)

st.write("Sugestões: comunicação de prática de irregularidades ou ato ilícito cuja solução dependa da atuação dos órgãos apuratórios competentes.")
st.write("No período, foram recepcionadas " + str(quantidade_sugestoes) + " reclamações de providências, que são consideradas como demonstração de insatisfação")

fig=px.histogram(orgaos_top, x='quantidade',y='sigla_orgao_saida', orientation='h', title="Gráfico 9 - Manifestações do tipo Elogio, por órgão ou entidade (10 mais demandados)", color='quantidade', color_discrete_sequence=cinza_escuro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Órgãos das Sugestões'):
    st.dataframe(ate_primeiro_por_orgao_ordenado)

st.write("Apresentamos o ranking dos 10 assuntos mais demandados nesse trimestre de 2023 para as sugestões:")
fig=px.histogram(assuntos_top, x='quantidade',y='assunto', orientation='h', title="Gráfico 12 - Os 10 principais assuntos das Sugestões", color='quantidade', color_discrete_sequence=verde_claro)       
fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(fig)
if st.checkbox('Mostrar Todos os Assuntos das Sugestões'):
    st.dataframe(ate_primeiro_por_assunto_ordenado)



###############################################################################
# 5 - PERFIL DOS SOLICITANTES
st.write(""" ## 5 - PERFIL DOS SOLICITANTES""")
st.write("De acordo com os dados apresentados na tabela 2, que demonstra o perfil do manifestante, pode-se inferir que o demandante é, em sua maioria pessoa física do sexo feminino.")

pizza = px.pie(atendimentos_tratados, values='quantidade', names='forma_atendimento', title='Gráfico 13 - Forma de Atendimento', color_discrete_sequence=cores_cge)
pizza.update_layout(font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(pizza)

pizza = px.pie(atendimentos_tratados, values='quantidade', names='tipo_identificacao', title='Gráfico 14 - Tipo de Identificação', color_discrete_sequence=cores_cge)
pizza.update_layout(font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(pizza)

pizza = px.pie(atendimentos_tratados, values='quantidade', names='tipo_pessoa', title='Gráfico 15 - Tipo do Solicitante', color_discrete_sequence=cores_cge)
pizza.update_layout(font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(pizza)

pizza = px.pie(atendimentos_tratados, values='quantidade', names='sexo', title='Gráfico 16 - Sexo dos Solicitante', color_discrete_sequence=cores_cge)
pizza.update_layout(font_family="Roboto", titlefont_family="Roboto")
st.plotly_chart(pizza)

##############################################################################################3
# 6 - OS 5 ÓRGÃOS COM MAIORES MANIFESTAÇÕES DE OUVIDORIA POR TIPOLOGIA E ASSUNTO
st.write(""" ## 6 - OS 5 ÓRGÃOS COM MAIORES MANIFESTAÇÕES DE OUVIDORIA POR TIPOLOGIA E ASSUNTO""")

ate_por_orgao = atendimentos_tratados.groupby(['sigla_orgao_saida']).size().to_frame('quantidade')
#st.dataframe(ate_por_orgao)
ate_por_orgao.reset_index(inplace=True)
ate_por_orgao.drop(ate_por_orgao[ate_por_orgao["sigla_orgao_saida"] == "Pronto Atendimento"].index, inplace=True)
ate_por_orgao_ordenado = ate_por_orgao.sort_values(by=['quantidade'],ascending=False)
ate_por_orgao_top = ate_por_orgao_ordenado.head(5)
ate_por_orgao_top.reset_index(drop=True, inplace=True)
lista_orgaos = ate_por_orgao_top["sigla_orgao_saida"].values.tolist()
#st.dataframe(lista_orgaos)         
tab1, tab2, tab3, tab4, tab5 = st.tabs(lista_orgaos)

def montar_tabela_orgao(orgao, natureza):
    reclamacoes_orgao = atendimentos_tratados.loc[(atendimentos_tratados["natureza"]==natureza) & (atendimentos_tratados["sigla_orgao_saida"]==orgao)]
    #st.dataframe(reclamacoes_orgao)
    reclamacoes_orgao_quantidade = reclamacoes_orgao.groupby(['assunto']).size().to_frame('quantidade')
    reclamacoes_orgao_quantidade_ordenado = reclamacoes_orgao_quantidade.sort_values(by=['quantidade'],ascending=False)
    reclamacoes_top = reclamacoes_orgao_quantidade_ordenado.head(5)
    return reclamacoes_top



with tab1:
    orgao_analise = lista_orgaos[0]
    st.write("Reclamação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Reclamação")
    st.dataframe(dados_tabela)
    st.write("Denúncia")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia")
    st.dataframe(dados_tabela)
    st.write("Solicitação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Solicitação")
    st.dataframe(dados_tabela)
    st.write("Sugestão")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Sugestão")
    st.dataframe(dados_tabela)    
    st.write("Elogio")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Elogio")
    st.dataframe(dados_tabela)    

with tab2:
    orgao_analise = lista_orgaos[1]
    st.write("Reclamação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Reclamação")
    st.dataframe(dados_tabela)
    st.write("Denúncia")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia")
    st.dataframe(dados_tabela)
    st.write("Solicitação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Solicitação")
    st.dataframe(dados_tabela)
    st.write("Sugestão")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Sugestão")
    st.dataframe(dados_tabela)    
    st.write("Elogio")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Elogio")
    st.dataframe(dados_tabela)    
with tab3:
    orgao_analise = lista_orgaos[2]
    st.write("Reclamação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Reclamação")
    st.dataframe(dados_tabela)
    st.write("Denúncia")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia")
    st.dataframe(dados_tabela)
    st.write("Solicitação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Solicitação")
    st.dataframe(dados_tabela)
    st.write("Sugestão")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Sugestão")
    st.dataframe(dados_tabela)    
    st.write("Elogio")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Elogio")
    st.dataframe(dados_tabela)    

with tab4:
    orgao_analise = lista_orgaos[3]
    st.write("Reclamação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Reclamação")
    st.dataframe(dados_tabela)
    st.write("Denúncia")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia")
    st.dataframe(dados_tabela)
    st.write("Solicitação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Solicitação")
    st.dataframe(dados_tabela)
    st.write("Sugestão")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Sugestão")
    st.dataframe(dados_tabela)    
    st.write("Elogio")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Elogio")
    st.dataframe(dados_tabela)    

with tab5:
    orgao_analise = lista_orgaos[4]
    st.write("Reclamação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Reclamação")
    st.dataframe(dados_tabela)
    st.write("Denúncia")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia")
    st.dataframe(dados_tabela)
    st.write("Denúncia (Disque 100)")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Denúncia (Disque 100)")    
    st.dataframe(dados_tabela)
    st.write("Solicitação")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Solicitação")
    st.dataframe(dados_tabela)
    st.write("Sugestão")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Sugestão")
    st.dataframe(dados_tabela)    
    st.write("Elogio")
    dados_tabela = montar_tabela_orgao(orgao_analise, "Elogio")
    st.dataframe(dados_tabela)    

# DADOS ABERTOS
st.write(""" ## 7 - DADOS BRUTOS""")
st.write("Os dados abertos podem ser encontrados também no Portal de Dados Abertos do Estado de Santa Catarina.")
#http://dados.sc.gov.br/dataset/8f14904e-91c9-482e-9b3b-862aad886b52/resource/d9f2d5d2-14da-42a2-93ba-e63a57d6f7a9/download/pda.png
if st.checkbox('Mostrar Dados Abertos'):
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
    
