from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import Email, DataRequired, Length, EqualTo, Regexp


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired("Email is required"), Email("Wrong email format")])
    password = PasswordField("Password", validators=[DataRequired("Password is required")])
    submit = SubmitField("Submit")


class RegistrationForm(FlaskForm):
    surname = StringField("Surname", validators=[DataRequired("Surname is required"), Regexp("^\S*$", message="Invalid surname")])
    name = StringField("Name", validators=[DataRequired("Name is required"), Regexp("^\S*$", message="Invalid name")])
    email = StringField("Email", validators=[DataRequired("Email is required"), Email("Wrong email format")])
    password = PasswordField("Password", validators=[DataRequired("Password is required")])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired("Password is required"), EqualTo("password", message="Passwords do not match")])
    phone_number = StringField("Phone number", validators=[DataRequired("Phone number is required"), 
                    Regexp("^\+?[1-9][0-9]{4,14}$", message="Wrong phone number format")])
    submit = SubmitField("Submit")