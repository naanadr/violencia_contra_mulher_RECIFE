from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import re
import six


# Helper para salvar graficos
def render_table(data, col_width=3.0, row_height=0.625, font_size=14,
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


# Helper para ajudar no plot de graficos
def autolabel(rects, xpos='center', ax=None):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset[xpos]*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha[xpos], va='bottom')


def paths_datasets():
    local_raiz = 'database/'

    return list(Path(local_raiz).glob('*'))


def read_datasets(locais_anos):
    processos_anos = []
    andamentos_anos = []
    assuntos_anos = []

    for local in locais_anos:
        processos_anos.append(list(Path(local).glob('*_recife.csv'))[0])
        andamentos_anos.append(list(Path(local).glob('*_andamentos.csv'))[0])
        assuntos_anos.append(list(Path(local).glob('*_assuntos.csv'))[0])

    df_processos = [pd.read_csv(str(processo)) for processo in processos_anos]
    df_andamentos = [pd.read_csv(str(andamento)) for andamento in andamentos_anos]
    df_assuntos = [pd.read_csv(str(assunto)) for assunto in assuntos_anos]

    return (pd.concat(df_processos), pd.concat(df_andamentos),
            pd.concat(df_assuntos))


def save_grafico(grafico, title):
    fig = plt.figure()
    grafico.plot.barh(title=title, edgecolor='black', color='y')
    fig.savefig('figures/{}'.format(title), dpi=100, bbox_inches='tight')


def save_tabela(dados, title, col_width):
    fig = plt.figure()
    ax, fig = render_table(dados, header_columns=0, col_width=col_width)
    fig.savefig('figures/'.format(title), dpi=100, bbox_inches='tight')


def classe_cnj_analise(df_processos_totais):
    classe_cnj = df_processos_totais['Classe CNJ']

    save_grafico(classe_cnj.value_counts(), title='Frequência das Classes CNJ')

    save_tabela(dados=df_assuntos_totais.iloc[:, 1:].head(n=7),
                title='assuntos_totais_pt1', col_width=5)
    save_tabela(dados=df_processos_totais.iloc[:, 3:].head(n=7),
                title='processos_totais_pt2', col_width=3.5)


def assunto_analise(df_assuntos_totais):
    assuntos = df_assuntos_totais['Assunto']

    assuntos_valor = assuntos.value_counts()
    assuntos_filtrado_index = assuntos_valor.iloc[
                              assuntos_valor.values > 9].index
    assuntos_filtrado_values = assuntos_valor.iloc[
                               assuntos_valor.values > 9].values

    assuntos_filtrado = pd.DataFrame({
        'Assunto': assuntos_filtrado_index,
        'Frequência': assuntos_filtrado_values
    })

    save_tabela(dados=assuntos_filtrado, title='assuntos_filtrados',
                col_width=7.5)

    save_grafico(grafico=assuntos_filtrado,
                 title='Assuntos CNJ com mais de 10 aparições')


# TODO: Realizar uma analise com esses dados
def duracao_andamentos(numeros_aux, data_inicio_aux, data_fim_aux,
                       duracao_aux):
    duracao_andamentos = pd.DataFrame({
        'Numero': numeros_aux,
        'Data Inicio': data_inicio_aux,
        'Data Fim': data_fim_aux,
        'Duracao (em dias)': duracao_aux
    })


def andamentos_analise(df_andamentos_totais):
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

    duracao_andamentos(numeros_aux, data_inicio_aux, data_fim_aux, duracao_aux)


def relacao_anos_processos():
    anos_frequencia = pd.DataFrame({
        'Ano': [2014, 2015, 2016, 2017, 2018],
        'Proc_ano': [18466, 17366, 11605, 12519, 15075],
        'Proc_vcm': [407, 972, 1111, 2169, 3786]
    })

    ind = np.arange(len(anos_frequencia['Proc_vcm']))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, anos_frequencia['Proc_ano'], width,
                    label='Proc')
    rects2 = ax.bar(ind + width/2, anos_frequencia['Proc_vcm'], width,
                    label='VCM')

    ax.set_ylabel('Num Processos'); ax.set_xticks(ind)
    ax.set_xticklabels(anos_frequencia['Ano']); ax.legend()
    autolabel(rects1, "center", ax); autolabel(rects2, "center", ax)

    fig.set_size_inches(7.5, 6.5, forward=True)
    fig.savefig('figures/processos_anos', dpi=100, bbox_inches='tight')
    plt.show()


def anos_assuntos(anos, assuntos):
    df_assuntos_ano = pd.DataFrame({
        'Ano': anos,
        'Assunto': assuntos
    })

    for ano in df_assuntos_ano['Ano'].unique():
        assuntos_values = df_assuntos_ano[
                          (df_assuntos_ano['Ano'] == ano)]['Assunto'].value_counts()
        assuntos_filtrados = assuntos_values.loc[assuntos_values.values > 9]

        save_grafico(grafico=assuntos_filtrados,
                     title='Principais Assuntos CNJ do Ano {}'.format(ano))


def anos_frequencia(df_assuntos_totais):
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

    anos_assuntos(anos_lista, assuntos_lista)


if __name__ == '__main__':
    locais_anos = paths_datasets()
    df_processos_totais, df_andamentos_totais, df_assuntos_totais = read_datasets(locais_anos)

    classe_cnj_analise(df_processos_totais)
    assunto_analise(df_assuntos_totais)
    andamentos_analise(df_andamentos_totais)
    anos_frequencia(df_assuntos_totais)

    relacao_anos_processos()
