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



class ProfileForm(FlaskForm):
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	supplier_id = StringField('Supplier ID', validators=[DataRequired()])
	submit = SubmitField('Save Changes')


# ------------------------------------ ADMIN ------------------------------------
# ---------------------------------------------------------------------------------


class SupplierAdmin(FlaskForm):
	# Form to edit an existing supplier
	image = FileField()
	display_name = StringField('Display Name', validators=[
		DataRequired(message='Enter an tile to be displayed for this supplier.'),
		])
	umbrella_id = StringField('Umbrella ID')
	submit = SubmitField('Save and Upload')


class CreateUmbrellaSupplier(FlaskForm):
	# Form to create an umbrella supplier
    supplier_name = StringField('Supplier Name', validators=[DataRequired()])
    submit = SubmitField('Create Account')