from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Enter an email'),
        ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddUser(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[
        DataRequired(message='Enter an email'),
        ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')


class SupplierAdmin(FlaskForm):
    image = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')