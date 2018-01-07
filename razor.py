import os
import sqlite3
from flask import Flask, g, url_for, render_template, request, \
		flash, redirect, session, abort

import scraper

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'razor.db'),
	SECRET_KEY='super secret key',
	USERNAME='admin',
	PASSWORD='12345'
))

def connect_db():
	""" Connect to specified database """
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	""" Opens a new database connection if there is
	none yet for the current application context """
	if not hasattr(g, 'razor_db'):
		g.razor_db = connect_db()
	return g.razor_db

@app.teardown_appcontext
def close_db(error):
	""" Closes the database again at the end of the request """
	if hasattr(g, 'razor_db'):
		g.razor_db.close()

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
	cur = db.execute('select id, title, year, image_loc, rating from movies order by id desc')
	movies = cur.fetchall()
	cur = db.execute('select * from directors')
	directors = cur.fetchall()
	cur = db.execute('select * from writers')
	writers = cur.fetchall()
	cur = db.execute('select * from actors')
	actors = cur.fetchall()
	return render_template('movies.html',
			movies=movies,
			directors=directors,
			writers=writers,
			actors=actors)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/login', methods=['POST'])
def login():
	error = None
	if request.form['username'] != app.config['USERNAME']:
		error = 'Invalid username'
	elif request.form['password'] != app.config['PASSWORD']:
		error = 'Invalid password'
	else:
		session['logged_in'] = True
		flash('You were logged in')
		return redirect(url_for('admin'))
	return render_template('admin_login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	#flash('You were logged out')
	return redirect(url_for('movies'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if not session.get('logged_in'):
		return render_template('admin_login.html')
	movie_info = None
	if request.method == 'POST':
		movie_info = scraper.movie_info_from_url(request.form['imdb_url'])
		if not movie_info:
			flash('Bad url')
	return render_template('admin.html', movie_info=movie_info)

@app.route('/add_movie', methods=['POST'])
def add_movie():
	""" add a movie to the database, starting by downloading the poster """
	if not session.get('logged_in'):
		abort(401)
	poster_filename=''
	if request.form['poster_url']:
		poster_filename = '_'.join(request.form['title'].lower().split())
		poster_filename = poster_filename + '_' + request.form['year'] + '.jpg'
		scraper.download_image(request.form['poster_url'], 'static/movie_posters/'+poster_filename)

	db = get_db()
	# add basic movie info to database
	cur = db.execute('insert into movies (title, year, image_loc, image_url, rating) values (?, ?, ?, ?, ?)',
			[request.form['title'],
			request.form['year'],
			poster_filename,
			request.form['poster_url'],
			request.form['rating']])
	movie_id = cur.lastrowid # gives id of the movie

	# add directors, writers, actors to database
	for director in request.form.getlist('director'):
		db.execute('insert into directors (name, movie_id) values (?, ?)',
				[director,
				movie_id])
	for writer in request.form.getlist('writer'):
		db.execute('insert into writers (name, movie_id) values (?, ?)',
				[writer,
				movie_id])
	for actor in request.form.getlist('actor'):
		db.execute('insert into actors (name, movie_id) values (?, ?)',
				[actor,
				movie_id])
	db.commit()
	flash('Added ' + request.form['title'] + ' to database')
	return redirect(url_for('admin'))

@app.route('/database')
def view_database():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	cur = db.execute('select * from movies')
	movies = cur.fetchall()
	return render_template('view_database.html', movies=movies)
