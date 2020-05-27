from flask_sqlalchemy import SQLAlchemy
from enums import Genres

db = SQLAlchemy()

# ---------------------------------------------------------------------------- #
# Models.
# ---------------------------------------------------------------------------- #


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), default=[Genres.pop])
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(
        db.String(500), nullable=True, default='')
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    state = db.Column(db.String(120))
    website = db.Column(db.String(500))
    num_upcoming_shows = db.Column(db.Integer, default=0)
    num_past_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='venue')

    def __repr__(self):
        return f'< Venue name: {self.name} id: {self.id} city: {self.city} >'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), default=[Genres.pop])
    image_link = db.Column(db.String(500))
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True)
    state = db.Column(db.String(120))
    website = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='artist')

    def __repr__(self):
        return f'< Artist name: {self.name} id: {self.id} >'


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)
    artist_id = db.Column(db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'< Show id: {self.id} venue: {self.venue_id} artist: {self.artist_id} time: {self.start_time} >'
