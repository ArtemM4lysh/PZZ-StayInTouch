from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange


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
    name = StringField('Name', validators=[DataRequired()],
                             render_kw={"placeholder": "Name"})
    phone_number = StringField('Phone Number', validators=[DataRequired()],
                               render_kw={"placeholder": "Phone Number"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "you@example.com"})
    pesel = StringField('Pesel', validators=[DataRequired()],
                        render_kw={"placeholder": "Pesel"})
    check_in_date = DateField('Check-in Date', validators=[DataRequired()], render_kw={"placeholder": "Check-in Date"})
    check_out_date = DateField('Check-out Date', render_kw={"placeholder": "Check-out Date"})
    hotel_id = IntegerField('Hotel ID', validators=[DataRequired(), NumberRange(min=1)],
                           render_kw={"placeholder": "Hotel ID"})
    room_type = SelectField('Room Type', validators=[DataRequired()],
                           choices=[('VIP', 'VIP'), ('BUSINESS', 'Business'), ('BUDGET', 'Budget')])
    submit = SubmitField('Add Visitor')