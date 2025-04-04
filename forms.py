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
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "you@example.com"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)],
                             render_kw={"placeholder": "Enter your password"})
    submit = SubmitField('Login')
