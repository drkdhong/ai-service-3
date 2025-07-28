# apps/mypagex/forms.py 
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField  #구성요소
from wtforms.validators import DataRequired, Email, length, EqualTo, ValidationError #유효성
# form class
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    new_password = PasswordField('새 비밀번호', validators=[DataRequired(), length(min=1)])
    confirm_new_password = PasswordField('새 비밀번호 확인', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('비밀번호 변경')
