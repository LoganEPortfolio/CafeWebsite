from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, URL, Email, EqualTo, InputRequired


class RegisterUser(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired('This is required.')])
    email = StringField('Email', validators=[DataRequired('This is required.'), Email('Must be an email address.')])
    password = PasswordField('Password', validators=[InputRequired(), DataRequired('This is required.'), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), DataRequired('This is required.'), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Submit')
    
class LoginUser(FlaskForm):
    email = StringField('Email', validators=[DataRequired('This is required.'), Email('Must be an email address.')])
    password = PasswordField('Password', validators=[DataRequired('This is required')])
    submit = SubmitField("Submit")
    
    
class AddCafe(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired('This field is required.')])
    map_url = StringField('Map URL', validators=[DataRequired('This field is required'), URL('Must be a URL.')])
    img_url = StringField('Image URL', validators=[DataRequired('This field is required.'), URL('Must be a URL.')])
    location = StringField('Location', validators=[DataRequired('This field is required.')])
    seats = StringField('Number of Seats', validators=[DataRequired('This field is required.')])
    has_toilet = BooleanField('Has Toilet', false_values={False, 'false', '', None})
    has_sockets = BooleanField('Has Sockets', false_values={False, 'false', '', None})
    has_wifi = BooleanField('Has WIFI', false_values={False, 'false', '', None})
    can_take_calls = BooleanField('Can Take Calls', false_values={False, 'false', '', None})
    coffee_price = StringField('Coffee Price', validators=[DataRequired('This field is required.')])
    submit = SubmitField("Submit")