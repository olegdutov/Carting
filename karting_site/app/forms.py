from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Имя пользователя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email уже зарегистрирован.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

from flask_wtf import FlaskForm
from wtforms import SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, ValidationError

class ReservationForm(FlaskForm):
    kart_id = SelectField('Выберите карт', coerce=int, validators=[DataRequired()])
    start_time = DateTimeField('Время начала (ГГГГ-ММ-ДД ЧЧ:ММ)', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('Время окончания (ГГГГ-ММ-ДД ЧЧ:ММ)', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    submit = SubmitField('Забронировать')

    def validate_end_time(self, end_time):
        if self.start_time.data >= end_time.data:
            raise ValidationError('Время окончания должно быть позже времени начала.')


