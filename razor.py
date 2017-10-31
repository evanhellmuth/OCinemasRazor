import os
import sqlite3
from flask import Flask, g, url_for, render_template

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'razor.db')
))

def connect_db():
	""" Connect to specified database """
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	""" Opens a new database connection if there is
	none yet for the current application context """
	if not hasattr(g, 'movies_db'):
		g.movies_db = connect_db()
	return g.movies_db

@app.teardown_appcontext
def close_db(error):
	""" Closes the database again at the end of the request """
	if hasattr(g, 'movies_db'):
		g.movies_db.close()

def init_db():
	""" Initialize the database """
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	""" Initializes the database """
	init_db()
	print('Initialized database')

@app.route('/index')
@app.route('/')
def movies():
	db = get_db()
	cur = db.execute('select title, image_loc, year, rating from movies order by id desc')
	movies = cur.fetchall()
	return render_template('movies.html', movies=movies)

@app.route('/about')
def about():
	return render_template('about.html')
