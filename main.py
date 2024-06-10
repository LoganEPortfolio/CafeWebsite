from flask import Flask, jsonify,  abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from pprint import pprint
import pandas as pd
import numpy as np
import random
import os
from forms import RegisterUser, LoginUser, AddCafe
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


### Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'sqlite:///cafes_2.db')
db = SQLAlchemy(session_options={"autoflush": False})
db.init_app(app)



#### Cafe Table
class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    

    def to_dict(self):
        dictionary = {}

        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

#### Favorites Table
class Favorite(db.Model):
    __tablename__ = 'favorite'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"), primary_key=True)

#### USER TABLE 
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(250), nullable=False)
    favorites = relationship('Cafe', secondary=Favorite.__table__)
          
    
with app.app_context():
    db.create_all()

#### Load User
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#### Admin Only Function
def admin_only(f):
    @wraps(f)
    def wrapper_function(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            abort(403)
    return wrapper_function

#### Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


#### Main Route
@app.route("/")
def home():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    if current_user.is_authenticated:
        fav_cafes = db.session.query(Cafe).filter(Cafe.id == Favorite.cafe_id, current_user.id == Favorite.user_id).all()
    else:
        fav_cafes = []
    
    ### Sets heading text 
    heading_text = {
        "h1_container": "Free WiFi, great Coffee!",
        "p_container": "These cafes offer free Wi-Fi for any customer that order a coffee!"
    }
    return render_template("index.html", fav_cafes = fav_cafes, cafes=cafes, heading_text=heading_text, logged_in = current_user.is_authenticated)


#### About page Route
@app.route("/about")
def about():
    return render_template("about.html", logged_in = current_user.is_authenticated)


#### Favorites page Route
@app.route("/favorites", methods=["GET"])
@login_required
def favorites():
    heading_text = {
        "h1_container": f"{current_user.first_name}'s Favorite Cafes!",
        "p_container": "Below are your favorite cafes you've found!"
    }
    fav_cafes = db.session.query(Cafe).filter(Cafe.id == Favorite.cafe_id, current_user.id == Favorite.user_id).all()
    return render_template("favorites.html", cafes = fav_cafes, heading_text=heading_text, logged_in = current_user.is_authenticated, user=current_user)


### Add a Favorite for a User
@app.route('/favorite/<cafe_id>', methods=["GET", "POST"])
@login_required
def add_favorite(cafe_id):
    
    new_favorite = Favorite(
        user_id = current_user.id,
        cafe_id = cafe_id
    )
        
    exists = db.session.query(Favorite).filter(Favorite.cafe_id == cafe_id) is not None
    
    fav = db.session.query(Favorite).filter(Favorite.cafe_id == cafe_id, current_user.id == Favorite.user_id).scalar()
    
    if fav:
        
        print(exists)
        print(fav)
        db.session.delete(fav)
        db.session.commit()
    else:
        db.session.add(new_favorite)
        db.session.commit()
    return redirect(request.referrer)

### Search by location route
@app.route("/search", methods=["GET", "POST"])
def search():
    #located_cafes = db.session.query(Cafe).filter(Cafe.location == location)
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    
    location_list = np.unique([cafe.location for cafe in all_cafes])

    loc = request.form.get('location')
    print(loc)
    
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    
    heading_text = {
        "h1_container": "Search your favorite area!",
        "p_container": "Limited to these select areas."
    }
    
    return render_template("search.html", cafes = cafes, location_list = location_list, heading_text=heading_text, logged_in = current_user.is_authenticated)

#### Popular cafes,  Cafes that have sockets, toilet, and wifi
@app.route("/popular", methods=["GET"])
def popular():
    popular_cafes = db.session.query(Cafe).filter(Cafe.has_sockets == True, Cafe.has_toilet == True, Cafe.has_wifi == True).all()
    print(popular_cafes)
    heading_text = {
        "h1_container": "Popular Cafes",
        "p_container": "These cafes offer free Wi-Fi, have sockets for charging, and have a bathroom!"
    }
    return render_template("index.html", cafes=popular_cafes, heading_text=heading_text, logged_in = current_user.is_authenticated)

#### Cafe page route
@app.route("/cafe/<cafe_id>", methods=["GET"])
def get_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    
    if cafe.has_sockets:
        cafe.has_sockets = "Yes"
    else:
        cafe.has_sockets = "No"
        
    if cafe.has_toilet:
        cafe.has_toilet =  "Yes"
    else:
        cafe.has_toilet = "No"
        
    if cafe.has_wifi:
        cafe.has_wifi = "Yes"
    else: 
        cafe.has_wifi = "No"
    
    return render_template('cafe.html', cafe=cafe)

##### ADD CAFE, ADMIN ONLY
@app.route("/add", methods=["GET", "POST"])
@admin_only
def add_cafe():
    form = AddCafe()
    if form.validate_on_submit() and current_user.id == 1:
        form_data = {
            "name": request.form.get('name'),
            "map_url": request.form.get('map_url'),
            "img_url": request.form.get('img_url'),
            "location": request.form.get('location'),
            "seats": request.form.get('seats'),
            'has_toilet': request.form.get('has_toilet'),
            'has_sockets': request.form.get('has_sockets'),
            'has_wifi': request.form.get('has_wifi'),
            'can_take_calls': request.form.get('can_take_calls'),
            'coffee_price': request.form.get('coffee_price')
        }
        
        if form_data['has_toilet'] == 'y':
            form_data['has_toilet'] = 1
        else:
            form_data['has_toilet'] = 0
            
        if form_data['has_sockets'] == 'y':
            form_data['has_sockets'] = 1
        else:
            form_data['has_sockets'] = 0
            
        if form_data['has_wifi'] == 'y':
            form_data['has_wifi'] = 1
        else:
            form_data['has_wifi'] = 0
            
        if form_data['can_take_calls'] == 'y':
            form_data['can_take_calls'] = 1
        else:
            form_data['can_take_calls'] = 0
        
        pprint(form_data)
    
        with app.app_context():
            new_cafe = Cafe(
                name=form_data['name'],
                map_url=form_data['map_url'],
                img_url=form_data['img_url'],
                location=form_data['location'],
                seats=form_data['seats'],
                has_toilet=form_data['has_toilet'],
                has_sockets=form_data['has_sockets'],
                has_wifi=form_data['has_wifi'],
                can_take_calls=form_data['can_take_calls'],
                coffee_price='£'+form_data['coffee_price']
            )
            db.session.add(new_cafe)
            db.session.commit()        
    return render_template('add-cafe.html', form=form)

    


##### USER REGISTER/LOGIN
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterUser()
    if form.validate_on_submit():
        if db.session.execute(db.select(User).where(User.email == form.email.data)).scalar():
            flash("You've already signed up with that account. Please log in.")
            return redirect(url_for('login'))
        else:
            new_user = User(
                email = form.email.data,
                password = generate_password_hash(form.password.data, 'pbkdf2:sha256', 8),
                first_name = form.first_name.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(db.session.execute(db.select(User).where(User.email == form.email.data)).scalar())
            return redirect(url_for('home'))
    return render_template('register.html', form=form)
        
        
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginUser()
    if form.validate_on_submit():
        login_email = form.email.data
        login_pw = form.password.data
        user = db.session.execute(db.select(User).where(User.email == login_email)).scalar()
        
        if (user is None):
            flash("Email not found.")
        else:
            if (check_password_hash(user.password, login_pw) is False):
                flash("Incorrect Password.")
            else:
                login_user(user)
                return redirect(url_for('home'))
    return render_template('login.html', form=form)





if __name__ == '__main__':
    app.run(debug=True)
