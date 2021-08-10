"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/users')
def user_list():

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def new_user():

    if request.method == 'POST':

        user = User(email=request.form['email'], password=request.form['password'],
                    age=request.form['age'], zipcode=request.form['zipcode'])

        db.session.add(user)
        db.session.commit()

        flash('User registered')
        return redirect('/')

    else:

        return render_template('register_form.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=f'{email}').first()

        if password == user.password:
            session['logged_in'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('Incorrect password')
            return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash('Logged out')

    return redirect('/')


@app.route('/users/<int:user_id>')
def user_page(user_id):

    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)
    return render_template('user_details.html', user=user, user_ratings=user_ratings)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
