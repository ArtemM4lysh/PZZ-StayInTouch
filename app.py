import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

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
            pesel = hashed_pesel,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data
        )

        db.session.add(new_visitor)
        db.session.commit()
    return render_template("dashboard.html", form=form, visitors=visitors)


@app.route('/add_visitor_ajax', methods=['POST'])
@login_required
def add_visitor_ajax():
    form = AddVisitorForm()

    if form.validate_on_submit():
        try:
            hashed_pesel = generate_password_hash(form.pesel.data)
            new_visitor = Visitor(
                name=form.name.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                pesel=hashed_pesel,
                check_in_date=form.check_in_date.data,
                check_out_date=form.check_out_date.data
            )

            db.session.add(new_visitor)
            db.session.commit()

            # Return success response with visitor data
            return jsonify({
                'success': True,
                'visitor': {
                    'name': new_visitor.name,
                    'email': new_visitor.email,
                    'phone_number': new_visitor.phone_number,
                    'check_in_date': new_visitor.check_in_date.strftime(
                        '%Y-%m-%d') if new_visitor.check_in_date else 'N/A',
                    'check_out_date': new_visitor.check_out_date.strftime(
                        '%Y-%m-%d') if new_visitor.check_out_date else 'N/A'
                }
            })
        except Exception:
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': {'general': ['An error occurred while saving the visitor.']}
            }), 500
    else:
        # Return validation errors
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400


if __name__ == '__main__':
    app.run(debug=True)