import os

from flask import Flask, request, json, render_template

import pandas as pd
import numpy as np
from datetime import datetime
from flask import jsonify
from werkzeug.utils import redirect


def import_files():
    file_path_movies = 'https://raw.githubusercontent.com/ce-cmiranda/apiflix/master/databases/IMDb%20movies.csv'
    # file_path_movies = 'databases/IMDb movies.csv'
    # file_path_names = 'databases/IMDb names.csv'
    # file_path_ratings = 'databases/IMDb ratings.csv'

    movies = pd.read_csv(file_path_movies, index_col='imdb_title_id', parse_dates=['date_published'])
    # names = pd.read_csv(file_path_names, index_col='imdb_name_id', parse_dates=True)
    # ratings = pd.read_csv(file_path_ratings, index_col='imdb_title_id', parse_dates=True)

    return movies


def filter_by_country(country, df, column):
    df = df[df[column].notnull()]
    df = df[df[column].str.contains(country)]
    return df


def filter_by_date(min_date, max_date, df):
    df = df[df['date_published'].notnull()]
    df = df[(df['date_published']>=min_date) & (df['date_published']<=max_date)]
    return df


def rank_by_criteria(df, criteria):
    rank = df[['title', criteria]].sort_values(by=criteria, ascending = False)
    return rank

# cl_genre = movies.loc[:, ['title', 'genre', 'avg_vote', 'votes']]
# cl_genre['genre'] = cl_genre['genre'].str.split(',')
# cl_genre = cl_genre.explode('genre')
# # Tratando os espaços em branco:
# cl_genre['genre'] = cl_genre['genre'].str.lstrip()
# genre_rank = cl_genre.groupby('genre').mean().avg_vote
# genre_rank.sort_values(axis = 0 ,ascending = False)
#New comment

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('/home.html')


@app.route('/rank/<criteria>')
def rank_page(criteria):
    number = 10
    result = import_files()
    result = rank_by_criteria(result, criteria)
    result = result.iloc[0:number, :].to_json(orient='index')
    result = json.loads(result)
    firstsubkey = next(iter(result.values()))
    position = [i+1 for i in range(number)]
    print(position)
    return render_template('/ranking.html', result=result, firstsubkey=firstsubkey, position = position)
    # return result["tt10914342"]


@app.route('/filter/country/', methods=["GET", "POST"])
def filter_by_country_page():
    result = import_files()
    if request.method == "POST":
        country_name = request.form["country"]
        title = request.form["title"]
        cast = request.form["cast"]
        genre = request.form["genre"]
        min_date = request.form["date_min"]
        max_date = request.form["date_max"]

        if country_name != "":
            result = filter_by_country(country_name, result, "country")
        if title != "":
            result = filter_by_country(title, result, "title")
        if cast != "":
            result = filter_by_country(cast, result, "actors")
        if genre!="":
            result = filter_by_country(genre, result, "genre")

        if min_date != "" and max_date != "":
            result = filter_by_date(min_date, max_date, result)

        result = result.iloc[0:10, :].to_dict(orient='index')
        num_results = len(result)
        return render_template('/filter_country.html', result=result, num_results=num_results)

    result = result.iloc[0:10, :].to_dict(orient='index')
    # result = result.iloc[0:10, :].to_dict(orient='index')


    return render_template('/filter_country.html', result=result)

@app.route('/api/filter/', methods=["GET", "POST"])
def filter_api():
    result = import_files()

    # result = result.to_dict(orient='index')
    result = result.iloc[0:100, :].to_json(orient='index')

    return result


if __name__ == '__main__':
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)