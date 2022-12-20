from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, URL
import requests
# from sqlalchemy import desc


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///My-Movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '4653gsafdg8465132h'
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False, unique=False)
    description = db.Column(db.String(1000), nullable=False, unique=True)
    rating = db.Column(db.Float, unique=False)
    ranking = db.Column(db.Integer, unique=False)
    review = db.Column(db.String(1000), unique=True)
    img_url = db.Column(db.String(500), unique=True, nullable=False)

# , nullable=False


# db.create_all()

# new_movie = Movie(title="Phone Booth", year=2002, description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negoatiation with the caller leads to a jaw-dropping climax.", rating=7.3, ranking=10, review="My favourite character was the caller.", img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#
# db.session.add(new_movie)
# db.session.commit()


# Create edit form
class EditForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g. 7.5')
    review = StringField('Your review')
    submit = SubmitField('Done')


# Create add form
class AddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), InputRequired()])
    # year = StringField("Year", validators=[DataRequired(), InputRequired()])
    # description = StringField("Description", validators=[DataRequired(), InputRequired()])
    # rating = StringField("Rating", validators=[DataRequired(), InputRequired()])
    # ranking = StringField("Ranking", validators=[DataRequired(), InputRequired()])
    # review = StringField("Review", validators=[DataRequired(), InputRequired()])
    # img_url = StringField("Img_Url", validators=[DataRequired(), InputRequired(), URL()])
    submit = SubmitField("Add Movie")


@app.route('/')
def home():
    all_movies = Movie.query.all()
    ordered = db.session.query(Movie).order_by(Movie.rating.asc())
    size = len(all_movies)
    return render_template('index.html', movies=ordered, length=size)


@app.route('/add', methods=["POST", "GET"])
def add():
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit():
            title = form.title.data
            # return render_template('select.html', movies=movies)
            return redirect(url_for('select', title=title))
    return render_template('add.html', form=form)


@app.route('/select', methods=["GET", "POST"])
def select():
    if request.method == "GET":
        API_KEY = '0365943eacf29ed6cf09778ecf431708'
        params = {"api_key": API_KEY,
                  "query": request.args.get('title'),
                  "language": 'en-US'}
        response = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
        response.raise_for_status()
        movies = response.json()['results']
        return render_template('select.html', movies=movies)
    else:
        return redirect(url_for('home'))


@app.route('/find')
def find():
    url = f"https://api.themoviedb.org/3/movie/{request.args.get('id')}"
    API_KEY = '0365943eacf29ed6cf09778ecf431708'
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()
    new_movie = Movie(title=result['original_title'], year=result['release_date'].split('-')[0],
                      description=result['overview'],
                      img_url=f"https://www.themoviedb.org/t/p/original{result['poster_path']}")
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', title=new_movie.title))


@app.route('/edit', methods=["POST", "GET"])
def edit():
    movie_to_edit = Movie.query.filter_by(title=request.args.get('title')).first()
    form = EditForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if len(form.rating.data) > 0:
                movie_to_edit.rating = form.rating.data
            if len(form.review.data) > 0:
                movie_to_edit.review = form.review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('edit.html', movie=movie_to_edit, form=form)


@app.route('/delete')
def delete():
    movie_title = request.args.get('title')
    movie_to_delete = Movie.query.filter_by(title=movie_title).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)