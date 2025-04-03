from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required
from extensions import db
from forms import LoginForm
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:123234345@localhost/my_flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


@app.route('/dashboard')
@login_required
def dashboard():
    return "Welcome to your dashboard!"


if __name__ == '__main__':
    app.run(debug=True)
