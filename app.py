import os

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required
from flask_migrate import Migrate
from sqlalchemy.util import methods_equivalent
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv


from extensions import db
from forms import LoginForm, RegisterForm, AddVisitorForm
from models import User, Visitor

load_dotenv("./flask.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if a user with the given email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            return redirect(url_for("register"))  # Redirect back to the registration page

        # Proceed with user creation
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = AddVisitorForm()
    visitors = Visitor.query.all()
    if form.validate_on_submit():
        hashed_pesel = generate_password_hash(form.pesel.data)
        new_visitor = Visitor(
            name = form.name.data,
            phone_number = form.phone_number.data,
            email = form.email.data,
            pesel = hashed_pesel
        )

        db.session.add(new_visitor)
        db.session.commit()
    return render_template("dashboard.html", form=form, visitors=visitors)


if __name__ == '__main__':
    app.run(debug=True)