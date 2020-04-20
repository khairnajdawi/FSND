from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField,TextAreaField,TimeField
from wtforms.validators import DataRequired, AnyOf, URL
from enum import Enum

class Genres(Enum):
    Alternative= 'Alternative'
    Blues= 'Blues'
    Classical= 'Classical'
    Country= 'Country'
    Electronic= 'Electronic'
    Folk= 'Folk'
    Funk= 'Funk'
    Hip_Hop= 'Hip-Hop'
    Heavy_Metal= 'Heavy Metal'
    Instrumental= 'Instrumental'
    Jazz= 'Jazz'
    Musical_Theatre= 'Musical Theatre'
    Pop= 'Pop'
    Punk= 'Punk'
    RNB= 'R&B'
    Reggae= 'Reggae'
    Rock_n_Roll= 'Rock n Roll'
    Soul= 'Soul'
    Other= 'Other'

class StatesEnum(Enum):
    AL= 'AL'
    AK= 'AK'
    AZ= 'AZ'
    AR= 'AR'
    CA= 'CA'
    CO= 'CO'
    CT= 'CT'
    DE= 'DE'
    DC= 'DC'
    FL= 'FL'
    GA= 'GA'
    HI= 'HI'
    ID= 'ID'
    IL= 'IL'
    IN= 'IN'
    IA= 'IA'
    KS= 'KS'
    KY= 'KY'
    LA= 'LA'
    ME= 'ME'
    MT= 'MT'
    NE= 'NE'
    NV= 'NV'
    NH= 'NH'
    NJ= 'NJ'
    NM= 'NM'
    NY= 'NY'
    NC= 'NC'
    ND= 'ND'
    OH= 'OH'
    OK= 'OK'
    OR= 'OR'
    MD= 'MD'
    MA= 'MA'
    MI= 'MI'
    MN= 'MN'
    MS= 'MS'
    MO= 'MO'
    PA= 'PA'
    RI= 'RI'
    SC= 'SC'
    SD= 'SD'
    TN= 'TN'
    TX= 'TX'
    UT= 'UT'
    VT= 'VT'
    VA= 'VA'
    WA= 'WA'
    WV= 'WV'
    WI= 'WI'
    WY= 'WY'
class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            (name, member.value) for name,member in StatesEnum.__members__.items()
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[(member.value, member.value) for name,member in Genres.__members__.items()]
        # choices=[
        #     ('Alternative', 'Alternative'),
        #     ('Blues', 'Blues'),
        #     ('Classical', 'Classical'),
        #     ('Country', 'Country'),
        #     ('Electronic', 'Electronic'),
        #     ('Folk', 'Folk'),
        #     ('Funk', 'Funk'),
        #     ('Hip-Hop', 'Hip-Hop'),
        #     ('Heavy Metal', 'Heavy Metal'),
        #     ('Instrumental', 'Instrumental'),
        #     ('Jazz', 'Jazz'),
        #     ('Musical Theatre', 'Musical Theatre'),
        #     ('Pop', 'Pop'),
        #     ('Punk', 'Punk'),
        #     ('R&B', 'R&B'),
        #     ('Reggae', 'Reggae'),
        #     ('Rock n Roll', 'Rock n Roll'),
        #     ('Soul', 'Soul'),
        #     ('Other', 'Other'),
        # ]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_talent = SelectField(
            'seeking_talent', validators=[DataRequired()],
            choices=[('True','Yes'),('False','No')]
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )
class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            (name, member.value) for name,member in StatesEnum.__members__.items()
        ]
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[(member.value, member.value) for name,member in Genres.__members__.items()]
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_venue = SelectField(
            'seeking_venue', validators=[DataRequired()],
            choices=[('True','Yes'),('False','No')]
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM


class TimeForm(Form):
    day_of_week = SelectField(
        'day_of_week',
        validators=[DataRequired()],
        choices=[('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')]
    )
    end_time = TimeField(
        'end_time',
        validators=[DataRequired()]
    )
    start_time = TimeField(
        'start_time',
        validators=[DataRequired()]
    )
