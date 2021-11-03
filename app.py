from flask import Flask, render_template, request, redirect, url_for
import json
import requests

app = Flask(__name__)

api_key = "f1dd7f2494de60ef4946ea81fd5ebaba"


@app.route("/view/movie/<id>")
def movie(id):
    tmdb_id = id
    imdb_req = requests.get(
        f"http://api.themoviedb.org/3/movie/{id}/external_ids?api_key={api_key}"
    ).json()
    imdb_id = imdb_req["imdb_id"]
    api = requests.get(
        f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}"
    )
    resp = api.json()
    title = resp["title"]
    movie_overview = resp["overview"]
    movie_runtime = f"{resp['runtime']} min."
    movie_rating = f"{resp['vote_average']}/10"
    movie_bg = f"https://image.tmdb.org/t/p/original/{resp['backdrop_path']}"
    date = resp["release_date"].split("-")
    rls_year = date[0]
    if rls_year == "":
        year = ""
    else:
        year = f"({rls_year})"
    tagline = resp["tagline"]
    return render_template(
        "movie.html",
        title=title,
        tmdb_id=tmdb_id,
        movie_overview=movie_overview,
        movie_runtime=movie_runtime,
        movie_rating=movie_rating,
        movie_bg=movie_bg,
        year=year,
        tagline=tagline,
        imdb_id=imdb_id,
    )


@app.route("/")
def index():
    return redirect("/browse")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/results")
def results():
    query = request.args.get("q")
    page = request.args.get("p")
    if query is None:
        return render_template("search.html")
    else:
        req = requests.get(
            f"http://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page={page}"
        )
        resp = req.json()
        if resp == json.loads('{"errors": ["query must be provided"]}'):
            msg = "You need to provide a query!"
            code = 403
            return render_template("error.html", msg=msg, code=code)
        results_length = len(resp["results"])
        if results_length == 0:
            msg = "Sorry, Not Found!"
            code = 404
            return render_template("error.html", msg=msg, code=code)
        else:
            poster_list = []
            titles = []
            tmdb_ids = []
            number = len(resp["results"])
            for poster_path in resp["results"]:
                path = poster_path["poster_path"]
                poster_list.append(poster_path["poster_path"])
            for title in resp["results"]:
                titles.append(title["title"])
            for tmdb_id in resp["results"]:
                tmdb_ids.append(tmdb_id["id"])
            return render_template(
                "results.html",
                posters=poster_list,
                titles=titles,
                tmdb_ids=tmdb_ids,
                number=number,
                query=query,
            )


@app.route("/browse")
def browse():
    poster_list = []
    titles = []
    movie_ids = []
    page = request.args.get("p")
    pop_movies = requests.get(
        f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}"
    )
    resp = pop_movies.json()
    for poster_path in resp["results"]:
        poster_list.append(poster_path["poster_path"])
    for title in resp["results"]:
        titles.append(title["title"])
    for movie_id in resp["results"]:
        movie_ids.append(movie_id["id"])
    return render_template(
        "index.html", posters=poster_list, titles=titles, movie_ids=movie_ids, page=page
    )


@app.route("/top")
def top():
    poster_list = []
    titles = []
    movie_ids = []
    page_check = request.args.get("p")
    if page_check is None:
        page = 1
    else:
        page = request.args.get("p")
    pop_movies = requests.get(
        f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}"
    )
    resp = pop_movies.json()
    for poster_path in resp["results"]:
        poster_list.append(poster_path["poster_path"])
    for title in resp["results"]:
        titles.append(title["title"])
    for movie_id in resp["results"]:
        movie_ids.append(movie_id["id"])
    return render_template(
        "top.html", posters=poster_list, titles=titles, movie_ids=movie_ids, page=page
    )


@app.route("/api/player")
def player():
    tmdb_id = request.args.get("id")
    if tmdb_id is None or not tmdb_id:
        return "ID Is A Required Parameter!"
    else:
        imdb_req = requests.get(
            f"http://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={api_key}"
        ).json()
        imdb_id = imdb_req["imdb_id"]
        return render_template("player.html", tmdb_id=tmdb_id, imdb_id=imdb_id)


@app.route("/search/tv")
def tv_search():
    return render_template("search_tv.html")


@app.route("/results/tv")
def tv_results():
    query = request.args.get("q")
    page = request.args.get("p")
    if query is None:
        return render_template("search.html")
    else:
        req = requests.get(
            f"http://api.themoviedb.org/3/search/tv?api_key={api_key}&query={query}&page={page}"
        )
        resp = req.json()
        if resp == json.loads('{"errors": ["query must be provided"]}'):
            msg = "You need to provide a query!"
            code = 403
            return render_template("error.html", msg=msg, code=code)
        results_length = len(resp["results"])
        if results_length == 0:
            msg = "Sorry, Not Found!"
            code = 404
            return render_template("error.html", msg=msg, code=code)
        else:
            poster_list = []
            titles = []
            tmdb_ids = []
            number = len(resp["results"])
            for poster_path in resp["results"]:
                poster_list.append(poster_path["poster_path"])
            for title in resp["results"]:
                titles.append(title["name"])
            for tmdb_id in resp["results"]:
                tmdb_ids.append(tmdb_id["id"])
            return render_template(
                "results_tv.html",
                posters=poster_list,
                titles=titles,
                tmdb_ids=tmdb_ids,
                number=number,
                query=query,
            )


@app.route("/view/tv/<id>")
def tv(id):
    tmdb_id = id
    imdb_req = requests.get(
        f"http://api.themoviedb.org/3/tv/{id}/external_ids?api_key={api_key}"
    ).json()
    imdb_id = imdb_req["imdb_id"]
    api = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}")
    resp = api.json()
    title = resp["name"]
    tv_overview = resp["overview"]
    tv_runtime = f"{resp['episode_run_time'][0]} min."
    tv_rating = f"{resp['vote_average']}/10"
    tv_bg = f"https://image.tmdb.org/t/p/original/{resp['backdrop_path']}"
    date = resp["first_air_date"].split("-")
    rls_year = date[0]
    seasons = resp["seasons"]
    if rls_year == "":
        year = ""
    else:
        year = f"({rls_year})"

    return render_template(
        "tv.html",
        title=title,
        tmdb_id=tmdb_id,
        tv_overview=tv_overview,
        tv_runtime=tv_runtime,
        tv_rating=tv_rating,
        tv_bg=tv_bg,
        year=year,
        imdb_id=imdb_id,
        seasons=seasons,
    )


@app.route("/view/tv/<id>/<s>/<e>")
def s_tv(id, s, e):
    try:
        resp = requests.get(
            f"https://api.themoviedb.org/3/tv/{id}/season/{s}/episode/{e}?api_key={api_key}"
        ).json()
        overview = resp["overview"]
        title = resp["name"]
        air_date = resp["air_date"].split("-")
        year = air_date[0]
        rating = round(float(resp["vote_average"]), 1)
        tv_resp = requests.get(
            f"https://api.themoviedb.org/3/tv/{id}?api_key={api_key}"
        ).json()
        seasons_array = []
        seasondicts = tv_resp["seasons"]
        for season in seasondicts:
            seasons_array.append(season["episode_count"])

        if len(seasondicts) == 1:
            current_season = int(s) - 1
        else:
            current_season = int(s) - 1

        ep_count = seasons_array[current_season] + 1
        next_season = current_season + 1
        return render_template(
            "view_tv.html",
            id=id,
            s=s,
            e=e,
            overview=overview,
            title=title,
            year=year,
            rating=rating,
            seasons_array=seasons_array,
            current_season=current_season,
            ep_count=ep_count,
            next_season=next_season,
        )
    except KeyError:
        return render_template("error.html", msg="Sorry, Not Found!", code=404), 404


@app.route("/browse/tv")
def browse_tv():
    poster_list = []
    titles = []
    tv_ids = []
    page = request.args.get("p")
    pop_movies = requests.get(
        f"https://api.themoviedb.org/3/tv/popular?api_key={api_key}&page={page}"
    )
    resp = pop_movies.json()
    for poster_path in resp["results"]:
        poster_list.append(poster_path["poster_path"])
    for title in resp["results"]:
        titles.append(title["name"])
    for tv_id in resp["results"]:
        tv_ids.append(tv_id["id"])
    return render_template(
        "tv_browse.html",
        posters=poster_list,
        titles=titles,
        movie_ids=tv_ids,
        page=page,
    )


@app.route("/top/tv")
def top_tv():
    poster_list = []
    titles = []
    movie_ids = []
    page_check = request.args.get("p")
    if page_check is None:
        page = 1
    else:
        page = request.args.get("p")
    pop_movies = requests.get(
        f"https://api.themoviedb.org/3/tv/top_rated?api_key={api_key}&page={page}"
    )
    resp = pop_movies.json()
    for poster_path in resp["results"]:
        poster_list.append(poster_path["poster_path"])
    for title in resp["results"]:
        titles.append(title["name"])
    for movie_id in resp["results"]:
        movie_ids.append(movie_id["id"])
    return render_template(
        "top_tv.html",
        posters=poster_list,
        titles=titles,
        movie_ids=movie_ids,
        page=page,
    )


@app.route("/api")
def api():
    return render_template("api.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
