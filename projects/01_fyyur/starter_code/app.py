#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import calendar
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,case
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Shows(db.Model):
    __tablename__ = 'Shows'
    id=db.Column(db.Integer,primary_key=True)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id', ondelete='CASCADE'),nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id', ondelete='CASCADE'),nullable=False)
    start_time = db.Column(db.DateTime,nullable=False)

    def __repr__(self):
      return f"<Show {self.id} >"

class AvailableTimes(db.Model):
    __tablename__="AvailableTimes"
    id=db.Column(db.Integer,primary_key=True)
    day_of_week = db.Column(db.Integer,nullable=False,default=0)
    start_time = db.Column(db.Time,nullable=False)
    end_time=db.Column(db.Time,nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id', ondelete='CASCADE'),nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    genres = db.Column(db.String(500),nullable=False)
    shows = db.relationship('Shows',cascade="all,delete",backref='shows', passive_deletes=True,lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
      return f'<Venue {self.id} : {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    shows_list = db.relationship('Shows',cascade="all,delete",backref='shows_list', passive_deletes=True,lazy=True)
    available_times = db.relationship('AvailableTimes',cascade="all,delete",backref='time_list', passive_deletes=True,lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
      return f'<Artist {self.id} : {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  #get most 10 recent artists and venues and show in main page
  recentVenues = Venue.query.with_entities(Venue.id,Venue.name).order_by(Venue.id.desc()).limit(10).all()  
  recentArtists = Artist.query.with_entities(Artist.id,Artist.name).order_by(Artist.id.desc()).limit(10).all()
  #equivalent sql query : select id,name from "Venue" order by id desc limit 10;
  # select id,name from "Shows" order by id desc limit 10;
  return render_template('pages/home.html',recentArtists=recentArtists,recentVenues=recentVenues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # select distinct city,state from venues to have categorized upon them
  cities_states = [(v.city,v.state) for v in db.session.query(Venue.city,Venue.state).distinct()]
  #equivalent sql query : select distinct city,state from "Venue";
  data = []
  #loop through city,state and retrieve venues in this city,state
  for city_state in cities_states:
    city = city_state[0]
    state = city_state[1]
    #query venues filtering venue.city=city and venue.state = state
    #also joining shows to count number of upcoming shows -> where show start time is larger than now
    venues = db.session.query(Venue.id,Venue.name,func.count(case([(Shows.start_time>func.now(),1)])).label('num_upcoming_shows'))\
      .outerjoin(Shows,Shows.venue_id==Venue.id)\
      .group_by(Venue.id)\
      .filter(Venue.city==city,Venue.state==state)\
      .all()
    #equivalent sql query : select "Venue".id,"Venue".name,COALESCE(count("Shows".id),0)  
    # ......................from "Venue" left join "Shows" on "Venue".id = "Shows".venue_id group by "Venue".id
    #.......................where "Venue".city=city and "Venue".state=state

    #create item with city,state, and venues in this city,state then append to response
    item={}
    item['city'] = city
    item['state']=state
    item['venues']=venues
    data.append(item)
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  response={}
  #query venues filtering name ilike search term, ilike for case insensitive
  venuesList = Venue.query.filter(Venue.name.ilike('%'+request.form.get('search_term')+'%'))
  #equivalent sql query : select "Venue".id,"Venue".name from "Venue" where LOWER(name) like LOWER('%search_term%')
  #get count and data from query
  response['count']=venuesList.count()
  response['data']=venuesList.all()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,    
  # }

  #get venue by id and add attributes to response data
  venue = Venue.query.get(venue_id)
  #equivalent sql query : select * from "Venue" where id=venue_id
  data={}
  data['id']=venue.id
  data['name']=venue.name
  data['genres']=venue.genres.split(",")
  data['address']=venue.address
  data['city']=venue.city
  data['state']=venue.state
  data['phone']=venue.phone
  data['website']=venue.website
  data['image_link']=venue.image_link
  data['facebook_link']=venue.facebook_link
  data['seeking_talent']=venue.seeking_talent
  data['seeking_description']=venue.seeking_description

  #query past show
  #query shows joining artists filtering the show start time is before now
  #creating labels for each column in query to match response format
  #equivalent sql query : select "Shows".start_time, "Artist".id,"Artist".name,"Artist".image_link as artist_image_link from "Shows" LEFT JOIN "Artist" on "Shows".artist_id = "Artist".id where "Shows".start_time<now()
  past_shows = db.session.query(func.to_char(Shows.start_time,"DD Mon YYYY HH:MM:SS").label('start_time'),Artist.id.label('artist_id'),Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'))\
    .outerjoin(Artist).filter(Shows.venue_id==venue_id,Shows.start_time<func.now())
  data['past_shows']=past_shows.all()
  data['past_shows_count']=past_shows.count()

  #query upcoming show
  #query shows joining artists filtering the show start time is after or equal now
  #creating labels for each column in query to match response format
  #equivalent sql query : select "Shows".start_time, "Artist".id,"Artist".name,"Artist".image_link as artist_image_link from "Shows" LEFT JOIN "Artist" on "Shows".artist_id = "Artist".id where "Shows".start_time>=now()
  upcoming_shows = db.session.query(func.to_char(Shows.start_time,"DD Mon YYYY HH:MM:SS").label('start_time'),Artist.id.label('artist_id'),Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'))\
    .outerjoin(Artist).filter(Shows.venue_id==venue_id,Shows.start_time>=func.now())
  data['upcoming_shows']=upcoming_shows.all()
  data['upcoming_shows_count']=upcoming_shows.count()

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  #prepare form from requested form
  form = VenueForm(request.form)
  #create a list of selected genres comma seperated, removing any extra quation, e.g selecting Heavy Metal will return "Heavy Metal"
  posted_genres = ','.join(form.genres.data).replace("\"","")
  #suppose succes is false
  success=False
  #create venue object from posted value
  venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      genres = posted_genres
    )
  #try add venue to database and commit
  #equivalent sql command : update "Venue" set name=name,city=city,..... where id=venue_id
  try:    
    db.session.add(venue)
    db.session.commit()
    #if commit succes is true
    success=True
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!','success')
  except:
    #if failed for any reason then rollback
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.','danger')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  #if success return to homepage else stay at new venue form
  if(success):
    return redirect(url_for('index'))
  else:
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  #equivalent sql : delete from "Venue" where id=venue_id
  success = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    success=True
  except:
    db.session.rollback()
  finally:
    db.session.close()

  #return json response with delete status
  return jsonify({'deleted':success,'venue_id':venue_id})
  


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

  #query artist id and name only, no need for all other columns
  data = Artist.query.with_entities(Artist.id,Artist.name).all()
  #equivalent sql : select id,name from "Artist"
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  success = False
  #equivalent sql : delete from "Artist" where id = artist_id
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    success=True
  except:
    db.session.rollback()
  finally:
    db.session.close()

  #return json response with delete status
  return jsonify({'deleted':success})
  
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  #query artists filtering name that like search_term case insensitive
  query = Artist.query.filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%'))
  #equivalent sql : select id,name from "Artist" where LOWER("Artist".name) like LOWER('%search_term%')
  response={
    "count": query.count(),
    "data": query.all()
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/placesearch', methods=['POST'])
def search_place_artists():
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals"
  #   }]
  # }

  #search for artist using city,state
  city_state = request.form.get('search_term').split(",")
  #check if search_term is in well format e.g "city, state"
  if(len(city_state)==2):
    city = city_state[0].strip()
    state = city_state[1].strip()
    #query artists filtering artist.city=city and artists.state = state
    #equivalent sql : select "Artist".id,"Artist".name from "Artist" where "Artist".city=city and "Artist".state = state
    query = Artist.query.filter(Artist.city==city,Artist.state==state)
    response={
      "count": query.count(),
      "data": query.all()
    }
  else:
    #if not in city,state format then flash an error and return empty string
    flash('\"'+request.form.get('search_term')+'\" is not a valid City,State','danger')
    response={
      "count": 0,
      "data": {}
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/placesearch', methods=['POST'])
def search_place_venues():
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals"
  #   }]
  # }

  #search venues by place, search term must like city,state
  city_state = request.form.get('search_term').split(",")
  #check if search_term is in well format e.g "city, state"
  if(len(city_state)==2):
    city = city_state[0].strip()
    state = city_state[1].strip()
    #query venues filtering by state and city in search term
    #equivalent sql : select "Venue".id,"Venue".name from "ArtVenueist" where "Venue".city=city and "Venue".state = state
    query = Venue.query.filter(Venue.city==city,Venue.state==state)
    response={
      "count": query.count(),
      "data": query.all()
    }
  else:
    #if not in city,state format then flash an error and return empty response
    flash('\"'+request.form.get('search_term')+'\" is not a valid City,State','danger')
    response={
      "count": 0,
      "data": {}
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }

  #get artist by id and add attributes to data
  #equivalent sql = select * from "Artist" where "Artist".id = artist_id
  artist = Artist.query.get(artist_id)
  data={}
  data['id']=artist.id
  data['name']=artist.name
  data['genres']=artist.genres.split(",")
  data['city']=artist.city
  data['state']=artist.state
  data['phone']=artist.phone
  data['seeking_venue']=artist.seeking_venue
  data['seeking_description']=artist.seeking_description
  data['image_link']=artist.image_link
  data['available_times']=artist.available_times

  #query artist's past shows by quering shows filtering start_time is before now
  #creating labels for columns to match response format
  #equivalent sql query : select "Shows".start_time, "Venue".id,"Venue".name,"Venue".image_link as venue_image_link from "Shows" LEFT JOIN "Venue" on "Shows".venue_id = "Venue".id where "Shows".start_time<now()
  past_shows = db.session.query(func.to_char(Shows.start_time,"DD Mon YYYY HH:MM:SS").label('start_time'),Venue.id.label('venue_id'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'))\
    .outerjoin(Venue).filter(Shows.artist_id==artist_id,Shows.start_time<func.now())
  data['past_shows']=past_shows.all()
  data['past_shows_count']=past_shows.count()

  #query artist's upcoming shows by quering shows filtering start_time is after now
  #creating labels for columns to match response format
  #equivalent sql query : select "Shows".start_time, "Venue".id,"Venue".name,"Venue".image_link as venue_image_link from "Shows" LEFT JOIN "Venue" on "Shows".venue_id = "Venue".id where "Shows".start_time>=now()
  upcoming_shows = db.session.query(func.to_char(Shows.start_time,"DD Mon YYYY HH:MM:SS").label('start_time'),Venue.id.label('venue_id'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'))\
    .outerjoin(Venue).filter(Shows.artist_id==artist_id,Shows.start_time>=func.now())
  data['upcoming_shows']=upcoming_shows.all()
  data['upcoming_shows_count']=upcoming_shows.count()

  days_names = calendar.day_name
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data,days_names=days_names)

@app.route('/artists/<int:artist_id>/timeedit', methods=['GET'])
def edit_artist_time(artist_id):
  form = TimeForm()
  artist = Artist.query.get(artist_id)
  days_names = calendar.day_name
  return render_template('forms/edit_artist_time.html', form=form, artist=artist,days_names=days_names)

@app.route('/artists/<int:artist_id>/timeedit', methods=['POST'])
def save_artist_time(artist_id):
  form = TimeForm()  
  artist = Artist.query.get(artist_id)
  day_of_week = request.form.get("day_of_week")
  start_time = request.form.get("start_time")
  end_time = request.form.get("end_time")
  if(end_time>=start_time):
    availableTime = AvailableTimes(artist_id=artist_id,
        start_time=start_time,
        end_time=end_time,
        day_of_week=day_of_week)
    try:
      # artist.availabel_times.append(availableTime)
      db.session.add(availableTime)
      db.session.commit()
      flash('Time added successfully','success')
    except:
      db.session.rollback()
      flash('Failed to add time','danger')
      form = TimeForm(request.form)
    finally:
      db.session.close()
  else:
    flash('end time must be after start time','danger')
  days_names = calendar.day_name
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist_time.html', form=form, artist=artist,days_names=days_names)

@app.route('/artisttime/<time_id>', methods=['DELETE'])
def delete_time(time_id):
  success = False
  try:
    t = AvailableTimes.query.get(time_id)
    db.session.delete(t)
    db.session.commit()
    success=True
  except:
    db.session.rollback()
  finally:
    db.session.close()

  #return json response with delete status
  return jsonify({'deleted':success})

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  #equivalent sql : select * from "Artist" where "Artist".id = artist_id
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  form.seeking_description.data=artist.seeking_description
  form.state.data = artist.state
  form.genres.data = artist.genres
  form.seeking_venue.data = "True" if artist.seeking_venue else "False"
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  #suppose success to be false by default until successfully commit
  success=False
  form = ArtistForm(request.form)  
  #get artist to be updated by id
  artist = Artist.query.get(artist_id)
  #create a list of selected genres comma seperated, remove quations from selected genres
  postedGenres = (",".join(form.genres.data)).replace("\"","")
  try:
    #try update artist info from posted form data
    #equivalent sql : update "Artist" set name=name , city=city ,.... where "Artist".id = artist_id
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.genres = postedGenres
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    #if committed then success is true
    success=True
    #flash success 
    flash('Updated Successfully','success')
  except:
    #if failed for any reason rollback and flash an error
    db.session.rollback()
    flash('Edit failed !!','danger')
    success=False
  finally:
    db.session.close()

  #if successfully updated then return to artist page else stay at edit page
  if(success):
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  #equivalent sql : select * from "Venue" where "Venue".id = venue_id
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.seeking_talent.data = "True" if venue.seeking_talent else "False"
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  #get venue to be updated by venue's id
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  #suppose success is false until successfully commit
  success=False
  #get a list of selected genres comma seperated, removing any quations in genre name
  postedGenres = (",".join(form.genres.data)).replace("\"","")
  try:
    #try update venue's info from posted form data
    #equivalent sql : update "Venue" set name=name,city=city, .... where "Venue".id=venue_id
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = postedGenres
    venue.image_link = form.image_link.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    #if successfully commit then success is true and flash a success
    success=True
    flash('Venues info updated','success')
  except:
    #if failed then rollback and flash an error
    db.session.rollback()
    success=False
    flash('Venues info could not be updated!')
  finally:
    db.session.close()
    #if success return to venue's page or else stay in edit page
  if(success):    
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  #prepare post from posted form,to read data, also in case of failure to keep input values
  form = ArtistForm(request.form)
  #suppose success is false until successfull commit
  success=False
  #create artist from posted form data
  artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = ','.join(form.genres.data).replace("\"",""), # create a list of selected genres comma seperated, removing qutations from genres names
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
  )
  #equivalent sql : insert into "Artist" (name,city,state,phone,genres,image_link,facebook_link,website,seeking_venue,seeking_description) values (name,city,state,phone,genres,image_link,facebook_link,website,seeking_venue,seeking_description)
  #try add new artist to db and commit
  try:
    db.session.add(artist)
    db.session.commit()
    #if successfully committed then success is true and flash a success
    flash('Artist ' + artist.name + ' was successfully listed!','success')
    success=True
  except:
    #if failed then rollback and flash an error
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.','danger')
  finally:
    db.session.close()

  #if successfully added return to homepage, else stay at create page
  if(success):
    return redirect(url_for('index'))
  else:
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  #get a list of all shows, querying Shows joining Venue and Artist to get their id and name
  #creating labels for each column to match response format
  showsList = db.session.query(func.to_char(Shows.start_time,"DD Mon YYYY HH:MM:SS").label('start_time'),Venue.id.label('venue_id'),Venue.name.label('venue_name'),Artist.id.label('artist_id'),Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'))\
    .outerjoin(Venue)\
    .outerjoin(Artist)\
    .all()
  #equivalent sql : SELECT "Artist".id,"Artist".name,"Venue".id,"Venue".name,"Shows".start_time 
  #.................FROM "Shows",
  #.................LEFT JOIN "Artist" on "Shows".artist_id = "Artist".id
  #.................LEFT JOIN "Venue" on "Shows".venue_id = "Venue".id
  
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=showsList)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  #suppose success is false untill success commit
  success=False
  #prepare form from posted form, to read data and keep inputs in case of failure
  postedForm = ShowForm(request.form)
  #check that venue id and artist id exists
  venue = Venue.query.get(postedForm.venue_id.data) # equivalent sql : select "Venue".id from "Venue" where "Venue".id=venue_id
  artist = Artist.query.get(postedForm.artist_id.data) # equivalent sql : select "Artist".id from "Artist" where "Artist".id=artist_id
  #if venues is none then id does not exist
  if(venue is None):
    flash('Venue id is not correct','danger')
    #if artist is none then id does not exist
  if(artist is None):
    flash('Artist id is not correct','danger')
  
  #must have both artist's id and venue's id correct to continue
  if(artist and venue):
    #create a show from posted data
    show = Shows(
      venue_id = postedForm.venue_id.data,
      artist_id = postedForm.artist_id.data,
      start_time = postedForm.start_time.data
    )
    #equivalent sql : insert into "Shows" (venue_id,artist_id,start_time) values (venue_id,artist_id,start_time)
    try:
      #try add show to db
      db.session.add(show)
      db.session.commit()
      #if successfully commited then flash success and success is true
      flash('Show was successfully listed!','success')
      success=True
    except:
      #if failed then rollback and flash an error
      db.session.rollback()
      flash('An error occurred. Show could not be listed.','danger')
    finally:
      db.session.close()

  #if success return to homepage, else stay in create page
  if(success):
    return redirect(url_for('index'))
  else:
    return render_template('forms/new_show.html', form=postedForm)
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
