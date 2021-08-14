from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Enter A Username', 
                validators=[DataRequired(), Length(min=5, max=25)], 
                render_kw={'placeholder': "Username"})
    
    password = StringField('Enter A Password', 
                validators=[DataRequired(), Length(min=8, max=50)],
                render_kw={'placeholder': 'Password'})
    
    email = StringField('Enter an Email Address (Optional)', validators=[Optional()],
                        render_kw={'placeholder': 'Email Address'})