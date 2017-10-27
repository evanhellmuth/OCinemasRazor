drop table if exists movies;
create table movies (
	id integer primary key autoincrement,
	title text not null,
	year integer,
	image_loc text,
	rating integer
);
