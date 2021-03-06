import os

from flask import Flask, request, json, render_template, make_response

import pandas as pd


def import_files():
    # Bases iniciais
    # file_path_movies = 'https://raw.githubusercontent.com/ce-cmiranda/apiflix/master/databases/IMDb%20movies.csv'
    # file_path_movies = 'databases/IMDb movies.csv'

    #O caminho na web é utilizado para deploy, na máquina para desenvolvimento
    file_path_movies = 'https://raw.githubusercontent.com/ce-cmiranda/apiflix/master/databases/movies_clean.csv'
    # file_path_movies = 'databases/movies_clean.csv'


    movies = pd.read_csv(file_path_movies, index_col='imdb_title_id', parse_dates=['Data de Publicação'],
                                  dtype={'Ano': 'str'})
    movies["percentual de lucro"] = movies["percentual de lucro"]*100

    return movies


def filter_by_string(string, df, column):
    #filtra qualquer coluna com um parâmetro contendo string
    df = df[df[column].notnull()]
    df = df[df[column].str.contains(string)]
    return df


def filter_by_date(min_date, max_date, df):
    #Aplica filtro com base na data de publicação do filme
    df = df[df['Data de Publicação'].notnull()]
    df = df[(df['Data de Publicação'] >= min_date) & (df['Data de Publicação'] <= max_date)]
    return df


def rank_by_param_movie_qtd(df, criteria):
    #Faz ranqueamento conforme quantidade de filmes por critério definido pelo usuário
    df = df[df[criteria].notnull()]
    df[criteria] = df[criteria].str.split(', ')
    df = df.explode(criteria)
    df = df[criteria].value_counts().sort_values(ascending=False)

    return df


def rank_param_by_criteria(df, param, criteria, qtd_votes=100000):
    #faz ranquemaneto utilizando um critério numérico e um parâmetro para ranqueamento
    #para evitar que filmes sem expressão fossem listados, colocamos um parâmetro de qtd de votos mínima
    #o valor padrão é 100 mil votos, a ideia era criar uma interface com formulário para o usuário alterar
    df = df[[param, criteria]][df['Quantidade de Votos'] >= qtd_votes]
    df = df[df[param].notnull()]

    df[param] = df[param].str.split(', ')
    df = df.explode(param)
    param_rank = df.groupby(param).mean()
    param_rank = param_rank.sort_values(criteria, ascending=False).reset_index().round(1)

    return param_rank


app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('/home.html')


@app.route('/rank/<criteria>/')
def home_rank(criteria):
    return render_template('/home_rank.html', criteria=criteria)


@app.route('/rank/qtd/<criteria>/')
@app.route('/rank/qtd/<criteria>/<int:page>')
def rank_page_qtd(criteria, page = 1):
    #a paginação está concluída, mas sem interface com o usuário
    #se trocar a página direto no navegador vai funcionar
    per_page = 10
    initial = (page-1)*per_page
    final = initial + per_page
    result = import_files()
    result = rank_by_param_movie_qtd(result, criteria)
    result = result[initial:final]
    max_value = result[0:1][0]
    title = "Ranking de Qtd por " + criteria
    result = result.to_dict()

    return render_template('/ranking_qtd.html', result=result, criteria=criteria, initial=initial, max_value=max_value, title=title)


@app.route('/rank/<criteria>/<param>/')
@app.route('/rank/<criteria>/<param>/<int:page>')
def rank_page_param(param, criteria, page=1):
    #a paginação está concluída, mas sem interface com o usuário
    #se trocar a página direto no navegador vai funcionar
    per_page = 10
    initial = (page-1)*per_page
    final = initial + per_page
    result = import_files()
    qtd_votes = 100000
    result = rank_param_by_criteria(result, param, criteria, qtd_votes)
    result = result.iloc[initial:final, :].to_dict(orient='index')
    firstsubkey = next(iter(result.values()))
    max_value = firstsubkey[criteria]

    return render_template('/ranking.html', result=result, firstsubkey=firstsubkey, initial=initial,
                           max_value=max_value)


@app.route('/filter/', methods=["GET", "POST"])
@app.route('/filter/<int:page>/', methods=["GET", "POST"])
def filter(page=1):
    # Aqui não foi implementada funcionalidade a tempo para manter o filtro e ao mesmo tempo
    # A paginação funcionar. Acredito que teria que usar parâmetros de filtro na url também
    # Mas teria que pesquisar

    per_page = 10
    initial = (page-1)*per_page
    final = initial + per_page
    result = import_files()
    if request.method == "POST":
        country_name = request.form["country"]
        title = request.form["title"]
        cast = request.form["cast"]
        genre = request.form["genre"]
        min_date = request.form["date_min"]
        max_date = request.form["date_max"]

        if country_name != "":
            result = filter_by_string(country_name, result, "País")
        if title != "":
            result = filter_by_string(title, result, "Título")
        if cast != "":
            result = filter_by_string(cast, result, "Atores")
        if genre != "":
            result = filter_by_string(genre, result, "Gênero")

        if min_date != "" and max_date != "":
            result = filter_by_date(min_date, max_date, result)

        result = result.iloc[initial:final, :].to_dict(orient='index')
        #num_results seria usado na implementação da paginação
        num_results = len(result)
        return render_template('/filter.html', result=result, num_results=num_results)

    result = result.iloc[initial:final, :].to_dict(orient='index')

    return render_template('/filter.html', result=result)


@app.route('/api/filter/', methods=["GET", "POST"])
def filter_api():
    #Não implementamos a tempo repostas de falha na pesquisa da API, então se é passado algum parâmetro que não existe
    # é retornado erro interno de servidor
    # Sobre o recebimento de valores pelas variáveis, acredito que tenha alguma forma mais fácil
    # Tentamos implementar com country_name = data["País"] or, mas não deu certo inicialmente, como o tempo era curto
    # implementamos de maneira menos elegante
    result = import_files()

    if request.method == "POST":
        data = json.loads(request.data)

        try:
            country_name = data["País"]
        except:
            country_name = ""
        try:
            title = data["Título"]
        except:
            title = ""
        try:
            cast = data["Atores"]
        except:
            cast = ""
        try:
            genre = data["Gênero"]
        except:
            genre = ""
        try:
            min_date = data["date_min"]
        except:
            min_date = ""
        try:
            max_date = data["date_max"]
        except:
            max_date = ""

        if country_name != "":
            result = filter_by_string(country_name, result, "País")
        if title != "":
            result = filter_by_string(title, result, "Título")
        if cast != "":
            result = filter_by_string(cast, result, "Atores")
        if genre != "":
            result = filter_by_string(genre, result, "Gênero")

        if min_date != "" and max_date != "":
            result = filter_by_date(min_date, max_date, result)

        # result = result.to_dict(orient='index')
        result = result.iloc[0:100, :].to_json(orient='index')
    else:
        result = filter_by_string("Germany", result, "País")
        result = filter_by_string("Drama", result, "Gênero")
        message = result.iloc[0:100, :].to_json(orient='index')
        result = """Opções de parâmetros:<br>"País", "Título", "Atores", "Gênero", "min_date", "max_date"
        <br><br>
        Exemplo:<br>
        {"País": "Germany", "Gênero": "Drama"}
        <br><br>
        Resultados esperados:
        <br><br>
        %s.""" % message
    return result


if __name__ == '__main__':
    #separados com comentário versão de deploy e versão de desenvolvimento
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
