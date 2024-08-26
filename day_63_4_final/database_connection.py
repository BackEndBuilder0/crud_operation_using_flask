from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6bsndiuas'
bootstrap = Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books_library.db"
db = SQLAlchemy()
db.init_app(app)


class BookLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(80), unique=True, nullable=False)
    author = db.Column(db.String(120), unique=True, nullable=False)
    rating = db.Column(db.String(10), nullable=False)


class BookForm(FlaskForm):
    book_name = StringField(name='Book Name', validators=[DataRequired('Book Name Is Required')])
    book_author = StringField(name='Author Name', validators=[DataRequired('Author Name Is Required')])
    rating = StringField(name='Rating', validators=[DataRequired('Rating Is Must')])
    add = SubmitField(name='Add Book')


class RatingForm(FlaskForm):
    rating = StringField(name='Rating', validators=[DataRequired('Rating Is Must')])
    update_rating = SubmitField(name='Update Rating')


with app.app_context():
    all_books = BookLibrary.query.all()


@app.route('/')
def home_page():
    return render_template('index.html', data=BookLibrary.query.all())


@app.route('/add', methods=['GET', 'POST'])
def add_page():
    form = BookForm()
    print(request.method)
    if request.method == 'POST':
        if form.validate_on_submit():
            with app.app_context():
                try:
                    db.create_all()
                    print(form.book_name.data, form.book_author.data, form.rating.data)
                    new_book = BookLibrary(book_name=form.book_name.data, author=form.book_author.data,
                                           rating=form.rating.data)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f'{e}', 'Error')
                    print(f'Exception {e}')
                finally:
                    db.session.close()
                    return render_template('index.html', data=BookLibrary.query.all())
        # return render_template('index.html', data=BookLibrary.query.all())
    return render_template('add.html', form=form)


@app.route('/edit/<int:rating>', methods=['GET', 'POST'])
def update_rating_point(rating):
    rating_form = RatingForm()
    if request.method == 'POST':
        new_rating = rating_form.rating.data
        curr_book = BookLibrary.query.session.get(BookLibrary, rating)
        curr_book.rating = new_rating
        db.session.commit()
        return render_template('index.html', data=BookLibrary.query.all())
    curr_book = BookLibrary.query.session.get(BookLibrary, rating)
    return render_template('update_rating.html', form=rating_form, curr_book=curr_book)


@app.route('/remove/<int:book_id>')
def delete_book(book_id):
    curr_book = BookLibrary.query.session.get(BookLibrary, book_id)
    BookLibrary.query.session.delete(curr_book)
    db.session.commit()
    return redirect(url_for('home_page',  data=BookLibrary.query.all()))


if __name__ == '__main__':
    app.run(debug=True)
