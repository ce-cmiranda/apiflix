from flask import Flask, render_template, request

import pandas as pd
import numpy as np
from datetime import datetime
from flask import jsonify
from werkzeug.utils import redirect


def import_files():
    file_path_movies = 'databases/iMDb movies.csv'
    file_path_names = 'databases/IMDb names.csv'
    file_path_ratings = 'databases/IMDb ratings.csv'

    movies = pd.read_csv(file_path_movies, index_col='imdb_title_id', parse_dates=['date_published'])
    # names = pd.read_csv(file_path_names, index_col='imdb_name_id', parse_dates=True)
    # ratings = pd.read_csv(file_path_ratings, index_col='imdb_title_id', parse_dates=True)

    return movies


def filter_by_country(country, df):
    df = df[df['country'].notnull()]
    df = df[df['country'].str.contains(country)]
    return df

def filter_by_date(min_date, max_date, df):
    df = df[df['date_published'].notnull()]
    df = df[(df['date_published']>=min_date) & (df['date_published']<=max_date)]
    return df

# cl_genre = movies.loc[:, ['title', 'genre', 'avg_vote', 'votes']]
# cl_genre['genre'] = cl_genre['genre'].str.split(',')
# cl_genre = cl_genre.explode('genre')
# # Tratando os espaços em branco:
# cl_genre['genre'] = cl_genre['genre'].str.lstrip()
# genre_rank = cl_genre.groupby('genre').mean().avg_vote
# genre_rank.sort_values(axis = 0 ,ascending = False)
#New comment

app = Flask(__name__)


# @app.route('/')
# def index():
#      movies = import_files()
#      # movies = movies.head(5)
#      # movies = movies.to_dict(orient='index')
#      # movies = list(movies.values())
#      # return movies[0]
#
#      result = filter_by_country('Germany', movies).iloc[0:10,:].to_dict(orient='index')
#      return result

@app.route('/')
def filter_page():
    return render_template('/home.html')


@app.route('/filter/country/', methods=["GET", "POST"])
def filter_by_country_page():
    movies = import_files()
    if request.method == "POST":
        country_name = request.form["country"]
        min_date = request.form["date_min"]
        max_date = request.form["date_max"]

        result = filter_by_country(country_name, movies)

        if min_date != "" and max_date != "":
            result = filter_by_date(min_date, max_date, result)

        result = result.iloc[0:10, :].to_dict(orient='index')
        num_results = len(result)
        return render_template('/filter_country.html', result=result, num_results=num_results)

    result = movies.iloc[0:10, :].to_dict(orient='index')

    return render_template('/filter_country.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
