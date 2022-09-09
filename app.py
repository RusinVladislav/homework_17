# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['RESTX_JSON'] = {'ensure_ascii': False}

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))

    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# создаем классы схемы
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# создаем соответствующие сериализаторы
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# создаем API и регистрируем соответствующие namespace
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


# регистрируем соответствующие классы CBV
@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie).all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Movie add", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()
            return movie_schema.dump(movie), 200
        except Exception:
            return "", 404

    def put(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        req_json = request.json

        movie.id = req_json.get('id')
        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "Move put", 204

    def patch(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        req_json = request.json

        if 'id' in req_json:
            movie.id = req_json.get('id')
        if 'title' in req_json:
            movie.title = req_json.get('title')
        if 'description' in req_json:
            movie.description = req_json.get('description')
        if 'trailer' in req_json:
            movie.trailer = req_json.get('trailer')
        if 'year' in req_json:
            movie.year = req_json.get('year')
        if 'rating' in req_json:
            movie.rating = req_json.get('rating')
        if 'genre_id' in req_json:
            movie.genre_id = req_json.get('genre_id')
        if 'director_id' in req_json:
            movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "Move patch", 204

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "Move delete", 204


@movie_ns.route('/director/<int:did>')
class MovieView(Resource):
    def get(self, did: int):
        try:
            movie = db.session.query(Movie).filter(Movie.director_id == did).all()
            return movies_schema.dump(movie), 200
        except Exception:
            return "", 404


@movie_ns.route('/genre/<int:gid>')
class MovieView(Resource):
    def get(self, gid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.genre_id == gid).all()
            return movies_schema.dump(movie), 200
        except Exception:
            return "", 404


@movie_ns.route('/director/<int:did>/genre/<int:gid>')
class MovieView(Resource):
    def get(self, did: int, gid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.director_id == did, Movie.genre_id == gid).all()
            return movies_schema.dump(movie), 200
        except Exception:
            return "", 404


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return jsonify(directors_schema.dump(all_directors)), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Director add", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        try:
            director = db.session.query(Director).filter(Director.id == uid).one()
            return jsonify(director_schema.dump(director)), 200
        except Exception:
            return "", 404

    def put(self, uid: int):
        director = db.session.query(Director).get(uid)
        req_json = request.json

        director.id = req_json.get('id')
        director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()

        return "Director put", 204

    def patch(self, uid: int):
        director = db.session.query(Director).get(uid)
        req_json = request.json

        if 'id' in req_json:
            director.id = req_json.get('id')
        if 'name' in req_json:
            director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()

        return "Director patch", 204

    def delete(self, uid: int):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "Director delete", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return jsonify(genres_schema.dump(all_genres)), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Genre add", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == uid).one()
            return jsonify(genre_schema.dump(genre)), 200
        except Exception:
            return "", 404

    def put(self, uid: int):
        genre = db.session.query(Genre).get(uid)
        req_json = request.json

        genre.id = req_json.get('id')
        genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return "Genre put", 204

    def patch(self, uid: int):
        genre = db.session.query(Genre).get(uid)
        req_json = request.json

        if 'id' in req_json:
            genre.id = req_json.get('id')
        if 'name' in req_json:
            genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return "Genre patch", 204

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "Genre delete", 204


if __name__ == '__main__':
    app.run(debug=True)
