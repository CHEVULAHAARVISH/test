from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db' 
db = SQLAlchemy(app)
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_of_release = db.Column(db.Integer)
    user_ratings = db.Column(db.Float)
    genres = db.relationship('Genre', secondary='movie_genre', backref='movies')
    actors = db.relationship('Actor', secondary='movie_actor', backref='movies')
    technicians = db.relationship('Technician', secondary='movie_technician', backref='movies')
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year_of_release': self.year_of_release,
            'user_ratings': self.user_ratings,
            'genres': [genre.name for genre in self.genres],
            'actors': [actor.name for actor in self.actors],
            'technicians': [technician.name for technician in self.technicians]
        }

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

movie_genre = db.Table('movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)
class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(),nullable=False)

movie_actor = db.Table('movie_actor',
    db.Column('movie_id', db.Integer, db.ForeignKey("movie.id")),
    db.Column('actor_id', db.Integer, db.ForeignKey("actor.id"))
)
class Technician(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(),nullable=False)

movie_technician = db.Table('movie_technician',
    db.Column('movie_id', db.Integer, db.ForeignKey("movie.id")),
    db.Column('technician_id', db.Integer, db.ForeignKey("technician.id")))
@app.route('/',methods=['Get'])
def hello_world():
    return "hi prends"

# API to get all movies
@app.route('/movies', methods=['GET'])
def get_all_movies():
    movies = Movie.query.all()
    movie_list = [movie.to_dict() for movie in movies]
    return jsonify({'movies': movie_list})

#api to
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    if movie:
        return jsonify(movie.to_dict())
    return jsonify({'error': 'Movie not found'}), 404


@app.route('/movies', methods=['POST'])
def create_movie():
    data = request.get_json()

    # Retrieve genre, actor, and technician data from the JSON
    genres_data = data.get('genres', [])
    actors_data = data.get('actors', [])
    technicians_data = data.get('technicians', [])

    # Create Movie instance
    new_movie = Movie(
        name=data['name'],
        year_of_release=data['year_of_release'],
        user_ratings=data['user_ratings']
    )
    
    existing_movie = Movie.query.filter_by(name=new_movie.name, year_of_release=new_movie.year_of_release).first()
    if existing_movie:
        return jsonify({'error': 'Movie already exists'}), 400

    # Create Genre instances and assign them to the movie
    genres = [Genre(name=genre) for genre in genres_data]
    new_movie.genres.extend(genres)
    
    # Create Actor instances and assign them to the movie
    actors = [Actor(name=actor) for actor in actors_data]
    new_movie.actors.extend(actors)
    
    # Create Technician instances and assign them to the movie
    technicians = [Technician(name=technician) for technician in technicians_data]
    new_movie.technicians.extend(technicians)
    
    db.session.add(new_movie)
    db.session.commit()
    
    return jsonify({'message': 'Movie created successfully'}), 201


@app.route('/movies/<string:movie_name>', methods=['PATCH'])
def update_movie(movie_name):
    movie = Movie.query.filter_by(name=movie_name).first()
    
    if movie:
        data = request.get_json()
        movie.name = data.get('name', movie.name)
        movie.year_of_release = data.get('year_of_release', movie.year_of_release)
        movie.user_ratings = data.get('user_ratings', movie.user_ratings)
        
        genres_data = data.get('genres', [])
        genres = [Genre(name=genre) for genre in genres_data]
        movie.genres = genres
        
        actors_data = data.get('actors', [])
        actors = [Actor(name=actor) for actor in actors_data]
        movie.actors = actors
        
        technicians_data = data.get('technicians', [])
        technicians = [Technician(name=technician) for technician in technicians_data]
        movie.technicians = technicians
        
        db.session.commit()
        
        return jsonify({'message': 'Movie updated successfully'})
    
    return jsonify({'error': 'Movie not found'}), 404


@app.route('/movie', methods=['GET'])
def get_all_moviesbycondi():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    actor = request.args.get('actor')
    genre = request.args.get('genre')
    user_rating = request.args.get('user_rating')
    
    query = Movie.query
    
    if genre:
        query = query.filter(Movie.genres.any(name=genre))
    if actor:
        query = query.filter(Movie.actors.any(name=actor))
    if user_rating:
        query = query.filter(Movie.user_ratings == float(user_rating))
    
    movies = query.paginate(page=page, per_page=per_page)
    movie_list = [movie.to_dict() for movie in movies.items]
    
    return jsonify({
        'movies': movie_list,
        'total_pages': movies.pages,
        'current_page': movies.page,
        'total_movies_matching are': movies.total
    })



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

