drop table if exists movies;
create table movies (
	id integer primary key autoincrement,
	title text not null,
	year integer,
	rating integer,
	image_loc text,
	image_url text
);

drop table if exists directors;
create table directors (
	id integer primary key autoincrement,
	name text not null,
	movie_id integer
);

drop table if exists writers;
create table writers (
	id integer primary key autoincrement,
	name text not null,
	movie_id integer
);

drop table if exists actors;
create table actors (
	id integer primary key autoincrement,
	name text not null,
	movie_id integer
);
