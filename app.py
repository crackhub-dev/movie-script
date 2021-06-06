from flask import Flask, render_template, request, redirect, url_for
import json
import requests

app = Flask(__name__)

api_key = 'YOUR_API_KEY_HERE'


@app.route('/view/movie/<id>')
def movie(id):
    base_url = "https://image.tmdb.org/t/p/original/"
    link = "https://www.2embed.ru/embed/tmdb/movie?id=" + id
    tmdb_id = id
    imdb_req = requests.get(
        f'http://api.themoviedb.org/3/movie/{id}/external_ids?api_key={api_key}').json()
    imdb_id = imdb_req['imdb_id']
    api = requests.get(
        f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}')
    resp = api.json()
    title = resp['title']
    movieDesc = resp['overview']
    date = resp['release_date'].split('-')
    rls_year = date[0]
    if rls_year == "":
        year = ''
    else:
        year = f'({rls_year})'
    tagline = resp['tagline']
    return render_template('movie.html', link=link, title=title, tmdb_id=tmdb_id, movieDesc=movieDesc, year=year,
                           tagline=tagline, imdb_id=imdb_id)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/results')
def results():
    query = request.args.get('q')
    page = request.args.get('p')
    if query is None:
        return render_template('search.html')
    else:
        req = requests.get(
            f'http://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page={page}')
        resp = req.json()
        if resp == json.loads('{"errors": ["query must be provided"]}'):
            msg = 'You need to provide a query!'
            code = 403
            return render_template('error.html', msg=msg, code=code)
        results_length = len(resp['results'])
        if results_length == 0:
            msg = 'Sorry, Not Found!'
            code = 404
            return render_template('error.html', msg=msg, code=code)
        else:
            poster_list = []
            titles = []
            tmdb_ids = []
            number = len(resp['results'])
            for poster_path in resp['results']:
                path = poster_path['poster_path']
                poster_list.append(poster_path['poster_path'])
            for title in resp['results']:
                titles.append(title['title'])
            for tmdb_id in resp['results']:
                tmdb_ids.append(tmdb_id['id'])
            return render_template('results.html', posters=poster_list, titles=titles, tmdb_ids=tmdb_ids, number=number,
                                   query=query)


@app.route('/browse')
def browse():
    poster_list = []
    titles = []
    movie_ids = []
    page = request.args.get('p')
    pop_movies = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}')
    resp = pop_movies.json()
    for poster_path in resp['results']:
        poster_list.append(poster_path['poster_path'])
    for title in resp['results']:
        titles.append(title['title'])
    for movie_id in resp['results']:
        movie_ids.append(movie_id['id'])
    return render_template('index.html', posters=poster_list, titles=titles, movie_ids=movie_ids, page=page)


@app.route("/top")
def top():
    poster_list = []
    titles = []
    movie_ids = []
    page_check = request.args.get('p')
    if page_check is None:
        page = 1
    else:
        page = request.args.get('p')
    pop_movies = requests.get(
        f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}')
    resp = pop_movies.json()
    for poster_path in resp['results']:
        poster_list.append(poster_path['poster_path'])
    for title in resp['results']:
        titles.append(title['title'])
    for movie_id in resp['results']:
        movie_ids.append(movie_id['id'])
    return render_template('top.html', posters=poster_list, titles=titles, movie_ids=movie_ids, page=page)


@app.route('/api/player')
def player():
    tmdb_id = request.args.get('id')
    if tmdb_id is None or not tmdb_id:
        return 'ID Is A Required Parameter!'
    else:
        imdb_req = requests.get(
            f'http://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={api_key}').json()
        imdb_id = imdb_req['imdb_id']
        return render_template('player.html', tmdb_id=tmdb_id, imdb_id=imdb_id)


@app.route('/api')
def api():
    return render_template('api.html')


if __name__ == "__main__":
    app.run()
