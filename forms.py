from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional


class RegistrationForm(FlaskForm):
    """The form used to register a new user."""
    username = StringField('Enter A Username', 
                validators=[DataRequired(), Length(min=5, max=25)], 
                render_kw={'placeholder': "Username"})
    
    password = PasswordField('Enter A Password', 
                validators=[DataRequired(), Length(min=8, max=50)],
                render_kw={'placeholder': 'Password'})
    
    email = StringField('Enter an Email Address', validators=[DataRequired()],
                        render_kw={'placeholder': 'Email Address'})


class LoginForm(FlaskForm):
    """The form used to login an existing user."""
    username = StringField('Enter A Username', 
                validators=[DataRequired(), Length(min=5, max=25)], 
                render_kw={'placeholder': "Username"})
    
    password = PasswordField('Enter A Password', 
                validators=[DataRequired(), Length(min=8, max=50)],
                render_kw={'placeholder': 'Password'})


class RouteSearchForm(FlaskForm):
    """The form used to search for routes."""
    street_address = StringField('Enter a Street Address (Optional)',
                        validators=[Optional()],
                        render_kw={'placeholder': 'Ex: 425 W Lake St.'})
    
    city = StringField('Enter Your City',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Ex: Boston'})
    
    state = StringField('Enter Your State/Country',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Ex: Massachusetts'})


class ResetPasswordForm(FlaskForm):
    """The form used to reset a user's password."""
    temp_password = PasswordField('Enter the temporary password.',
                                    validators=[DataRequired()],
                                    render_kw={'placeholder': "Temporary Password"})
    
    new_password = PasswordField('Enter your new password',
                                    validators=[DataRequired()],
                                    render_kw={'placeholder': 'Enter your new password.'})


class GetEmailForm(FlaskForm):
    """The form used to get an email address to see if there is
    a match with a user. This is then used to send an email to reset
    the user's password."""

    email = StringField('Enter your email address',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Email address'})