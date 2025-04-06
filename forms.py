from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "you@example.com"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)],
                             render_kw={"placeholder": "Enter your password"})

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"placeholder": "Your username"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "you@example.com"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)],
                             render_kw={"placeholder": "Enter your password"})
    submit = SubmitField('Register')


class AddVisitorForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()],
                             render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[DataRequired()],
                            render_kw={"placeholder": "Last Name"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "you@example.com"})
    pesel = StringField('Pesel', validators=[DataRequired()],
                        render_kw={"placeholder": "Pesel"})
    submit = SubmitField('Register')
