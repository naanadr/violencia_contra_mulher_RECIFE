from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import re
import six
%matplotlib inline

# %% markdown
# #### Helper para salvar planilha
# %%
def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#4a86e8', row_colors=['#f1f1f2', 'w'],
                     edge_color='w', bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array(
                [col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox,
                         colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
    return ax, fig


# %% markdown
# ## Analisando os dados
# %%

# TODO:
# ter uma noção da porcentação de processos de violência / processos totais

local_raiz = 'database/'
local_anos = list(Path(local_raiz).glob('*'))

processos_anos = []
andamentos_anos = []
assuntos_anos = []

for local in local_anos:
    processos_anos.append(list(Path(local).glob('*_comarca_recife.csv'))[0])
    andamentos_anos.append(list(Path(local).glob('*_andamentos.csv'))[0])
    assuntos_anos.append(list(Path(local).glob('*_assuntos.csv'))[0])

df_processos = [pd.read_csv(str(processo)) for processo in processos_anos]
df_andamentos = [pd.read_csv(str(andamento)) for andamento in andamentos_anos]
df_assuntos = [pd.read_csv(str(assunto)) for assunto in assuntos_anos]

df_processos_totais = pd.concat(df_processos)
df_andamentos_totais = pd.concat(df_andamentos)
df_assuntos_totais = pd.concat(df_assuntos)


# %% markdown
# ### Classe CNJ
# %%
classe_cnj = df_processos_totais['Classe CNJ']
classe_cnj.unique()

title = "Frequência das Classes CNJ"
fig = plt.figure()
classe_cnj.value_counts().plot.barh(title=title, edgecolor='black',
                                    colors='y')
fig.savefig('figures/{}'.format(title), dpi=100, bbox_inches='tight')


ax, fig = render_mpl_table(df_assuntos_totais.iloc[:, 1:].head(n=7),
                           header_columns=0, col_width=5)
fig.savefig('figures/assuntos_totais_pt1', dpi=100, bbox_inches='tight')
ax, fig = render_mpl_table(df_processos_totais.iloc[:, 3:].head(n=7),
                           header_columns=0, col_width=3.5)
fig.savefig('figures/processos_totais_pt2', dpi=100, bbox_inches='tight')

# %% markdown
# ### Assunto
# %%
assuntos = df_assuntos_totais['Assunto']
assuntos.unique()
assuntos_valor = assuntos.value_counts()
assuntos_filtrado_index = assuntos_valor.iloc[assuntos_valor.values > 9].index
assuntos_filtrado_values = assuntos_valor.iloc[
                                            assuntos_valor.values > 9].values

assuntos_filtrado = pd.DataFrame({
    'Assunto': assuntos_filtrado_index,
    'Frequência': assuntos_filtrado_values
})


ax, fig = render_mpl_table(assuntos_filtrado,
                           header_columns=0, col_width=7.5)
fig.savefig('figures/assuntos_filtrados', dpi=100, bbox_inches='tight')

title = "Assuntos CNJ com mais de 10 aparições"
fig = plt.figure()
assuntos_filtrado.plot.barh(title=title, edgecolor='black', colors='y')
fig.savefig('figures/{}'.format(title), dpi=100, bbox_inches='tight')


# %% markdown
# ### Uma passada pelos anos
# %%
anos_lista = []
assuntos_lista = []

for processo in df_assuntos_totais['Numero'].unique():
    df_assun = df_assuntos_totais[(df_assuntos_totais['Numero'] == processo)]
    assuntos = df_assun['Assunto'].values
    processo_corrigido = str(processo).zfill(20)
    ano = re.match('\d{9}(\d{4})', processo_corrigido).group(1)

    for assunto in assuntos:
        assuntos_lista.append(assunto)
        anos_lista.append(ano)

df_assuntos_ano = pd.DataFrame({
    'Ano': anos_lista,
    'Assunto': assuntos_lista
})

for ano in df_assuntos_ano['Ano'].unique():
    assuntos_values = df_assuntos_ano[(
                      df_assuntos_ano['Ano'] == ano)]['Assunto'].value_counts()
    assuntos_filtrados = assuntos_values.loc[assuntos_values.values > 9]
    title = "Principais Assuntos CNJ do Ano {}".format(ano)
    fig = plt.figure()
    assuntos_filtrado.plot.barh(title=title, edgecolor='black', color='y')
    fig.savefig('figures/{}'.format(title), dpi=100, bbox_inches='tight')

# %% markdown
# ### Andamento
# %%
numeros_aux = []
data_inicio_aux = []
data_fim_aux = []
duracao_aux = []

for numero in df_andamentos_totais['numero'].unique():
    lista = list(df_andamentos_totais[(
                 df_andamentos_totais['numero'] == int(numero))]['data'])
    lista = [datetime.strptime(lista[i], "%d/%m/%Y %H:%M:%S") for i in range(len(lista))]

    if max(lista).year != 2019:
        duracao = abs(lista[0] - lista[-1]).days

        numeros_aux.append(numero)
        data_inicio_aux.append(min(lista))
        data_fim_aux.append(max(lista))
        duracao_aux.append(duracao)

duracao_andamentos = pd.DataFrame({
    'Numero': numeros_aux,
    'Data Inicio': data_inicio_aux,
    'Data Fim': data_fim_aux,
    'Duracao (em dias)': duracao_aux
})

dura_total = duracao_andamentos.sort_values(by='Duracao (em dias)')
title =
duracao_andamentos['Duracao (em dias)'].plot.hist(bins=30, edgecolor='black')
