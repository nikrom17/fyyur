# ---------------------------------------------------------------------------- #
# Imports
# ---------------------------------------------------------------------------- #

from enum import Enum
import json
import dateutil.parser
import babel
from config import SQLALCHEMY_DATABASE_URI
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate  # import to run flask db <command>
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from defaultData import artists_default_data, venues_default_data

# ---------------------------------------------------------------------------- #
# App Config.
# ---------------------------------------------------------------------------- #

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

# ---------------------------------------------------------------------------- #
# Enums
# ---------------------------------------------------------------------------- #


class Genres(Enum):
    alternative = 'Alternative',
    blues = 'Blues',
    classical = 'Classical',
    country = 'Country',
    electronic = 'Electronic',
    folk = 'Folk',
    funk = 'Funk',
    hip_hop = 'Hip-Hop',
    heavy_metal = 'Heavy Metal',
    instrumental = 'Instrumental',
    jazz = 'Jazz',
    musical_theatre = 'Musical Theatre',
    pop = 'Pop',
    punk = 'Punk',
    r_n_b = 'R&B',
    reggae = 'Reggae',
    rock_n_roll = 'Rock n Roll',
    soul = 'Soul',
    other = 'Other',

# ---------------------------------------------------------------------------- #
# Models.
# ---------------------------------------------------------------------------- #


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), default=[Genres.pop])
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean)
    state = db.Column(db.String(120))
    website = db.Column(db.String(500))
    num_upcoming_shows = db.Column(db.Integer)
    num_past_shows = db.Column(db.Integer)
    shows = db.relationship('Show', backref='venues')

    def __repr__(self):
        return f'< Venue {self.name} {self.id} {self.city} >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), default=[Genres.pop])
    image_link = db.Column(db.String(500))
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean)
    state = db.Column(db.String(120))
    website = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show', backref='artists')

    def __repr__(self):
        return f'< Artist {self.name} {self.id} >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist = db.Column(db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


db.create_all()

# ---------------------------------------------------------------------------- #
# Load default data.
# ---------------------------------------------------------------------------- #


def addVenueData():
    venues = Venue.query.all()
    # only load data if db is empty
    if (not len(venues)):
        for defaultVenue in venues_default_data:
            venue = Venue()
            venue.address = defaultVenue['address']
            venue.city = defaultVenue['city']
            venue.facebook_link = defaultVenue['facebook_link']
            venue.genres = defaultVenue['genres']
            venue.image_link = defaultVenue['image_link']
            venue.name = defaultVenue['name']
            venue.phone = defaultVenue['phone']
            venue.seeking_description = defaultVenue['seeking_description']
            venue.seeking_talent = defaultVenue['seeking_talent']
            venue.state = defaultVenue['state']
            venue.website = defaultVenue['website']
            db.session.add(venue)
        db.session.commit()


def addArtistData():
    artists = Artist.query.all()
    # only load data if db is empty
    if (not len(artists)):
        for defaultArtist in artists_default_data:
            artist = Artist()
            artist.city = defaultArtist['city']
            artist.facebook_link = defaultArtist['facebook_link']
            artist.genres = defaultArtist['genres']
            artist.image_link = defaultArtist['image_link']
            artist.name = defaultArtist['name']
            artist.phone = defaultArtist['phone']
            artist.seeking_description = defaultArtist['seeking_description']
            artist.seeking_venue = defaultArtist['seeking_venue']
            artist.state = defaultArtist['state']
            artist.website = defaultArtist['website']
            db.session.add(artist)
        db.session.commit()

# ---------------------------------------------------------------------------- #
# Filters.
# ---------------------------------------------------------------------------- #


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ---------------------------------------------------------------------------- #
# Controllers.
# ---------------------------------------------------------------------------- #


@app.route('/')
def index():
    addVenueData()
    addArtistData()
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    locations = db.session.query(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    venues = []
    for location in locations:
        (city, state) = location
        city_venues = Venue.query.filter(
            Venue.city == city).filter(Venue.state == state).all()
        venues.append({'city': city, 'state': state, 'venues': city_venues})

    return render_template('pages/venues.html', areas=venues)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    search_value = request.form.get('search_term', '')
    search_term = "%{}%".format(search_value)
    venues = Venue.query.filter(func.lower(
        Venue.name).like(func.lower(search_term))).all()
    data = []
    for venue in venues:
        data.append({'id': venue.id, 'name': venue.name,
                     'num_upcoming_shows': 1})  # TODO pull this data
    response = {"count": len(venues), "data": data}

    return render_template('pages/search_venues.html', results=response, search_term=search_value)


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    data = Venue.query.get(venue_id)
    if data:
        return render_template('pages/show_venue.html', venue=data)
    else:
        return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        submission = request.form
        venue.address = submission['address']
        venue.city = submission['city']
        venue.facebook_link = submission['facebook_link']
        venue.genres = submission.getlist('genres')
        venue.image_link = submission['image_link']
        venue.name = submission['name']
        venue.phone = submission['phone']
        venue.seeking_description = submission['seeking_description']
        venue.seeking_talent = True if submission['seeking_talent'] == 'y' else False
        venue.state = submission['state']
        venue.website = submission['website']
        db.session.add(venue)
        db.session.commit()
        print('end of try')
    except():
        print('except')
        error = True
        db.session.rollback()
    finally:
        print('finally')
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        print('error')
        # TODO this is not failing gracefully
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    search_value = request.form.get('search_term', '')
    search_term = "%{}%".format(search_value)
    artists = Artist.query.filter(func.lower(
        Artist.name).like(func.lower(search_term))).all()

    data = []
    for artist in artists:
        data.append({'id': artist.id, 'name': artist.name})
    response = {"count": len(artists), "data": data}

    return render_template('pages/search_artists.html', results=response, search_term=search_value)


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    data = Artist.query.get(artist_id)
    if data:
        return render_template('pages/show_artist.html', artist=data)
    else:
        return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    print(artist.genres)
    form.genres.data = artist.genres
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    # called upon submitting the new artist listing form
    error = False
    try:
        artist = Artist.query.get(artist_id)
        submission = request.form
        artist.city = submission['city']
        artist.facebook_link = submission['facebook_link']
        artist.genres = submission.getlist('genres')
        artist.name = submission['name']
        artist.phone = submission['phone']
        artist.state = submission['state']
        db.session.add(artist)
        db.session.commit()
    except(error):
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        submission = request.form
        venue.address = submission['address']
        venue.city = submission['city']
        venue.facebook_link = submission['facebook_link']
        venue.genres = submission.getlist('genres')
        venue.name = submission['name']
        venue.phone = submission['phone']
        venue.state = submission['state']
        db.session.add(venue)
        db.session.commit()
    except():
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        print('error')
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    try:
        artist = Artist()
        submission = request.form
        artist.city = submission['city']
        artist.facebook_link = submission['facebook_link']
        artist.genres = submission.getlist('genres')
        artist.image_link = submission['image_link']
        artist.name = submission['name']
        artist.phone = submission['phone']
        artist.seeking_description = submission['seeking_description']
        artist.seeking_venue = True if submission['seeking_venue'] == 'y' else False
        artist.state = submission['state']
        artist.website = submission['website']
        db.session.add(artist)
        db.session.commit()
    except(error):
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ---------------------------------------------------------------------------- #
# Launch.
# ---------------------------------------------------------------------------- #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
