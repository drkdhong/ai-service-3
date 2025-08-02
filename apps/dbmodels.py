# apps/dbmodels.py
import enum
import uuid
from flask import current_app
from apps import db  # apps에서 db를 import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 
#hash import
from datetime import datetime
from apps.config import Config
class User(db.Model, UserMixin):  # db.Model, UserMixin 상속하는 User 클래스 생성
    __tablename__= "users"  # 삭제시, 테이블 이름은 Model 이름 소문자 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String, index=True)
    email=db.Column(db.String, unique=True, index= True)
    password_hash=db.Column(db.String)
    is_admin=db.Column(db.Boolean,default=False)
    is_active=db.Column(db.Boolean, default=True)  # 활성화 여부
    usage_count = db.Column(db.Integer, default=0)
    # 특정 User에 대한 일일/월간 사용량 제한을 위한 필드 추가 가능 (예: daily_limit, monthly_limit)
    daily_limit = db.Column(db.Integer, default=1000)
    monthly_limit = db.Column(db.Integer, default=5000)
    created_at=db.Column(db.DateTime, default= datetime.now)
    updated_at=db.Column(db.DateTime, default= datetime.now, onupdate=datetime.now)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    #api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    #usage_logs = db.relationship('UsageLog', backref='user', lazy=True, cascade='all, delete-orphan')
    #iris_results = db.relationship('IRIS', backref='user', lazy=True, cascade='all, delete-orphan')
    # The 'password' property and its setter
    @property
    def password(self):
        """
        Prevent direct reading of the password.
        Attempting to read `user.password` will raise an AttributeError.
        """
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        """
        Hashes the plain-text password and stores it in password_hash.
        This allows you to do `user.password = "mysecretpassword"`.
        """
        self.password_hash = generate_password_hash(password)
    # Method to check password (you likely already have this or check_password)
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    # 비밀번호 체크
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Flask-Login required methods
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def __repr__(self):
        return f'<User {self.username}>'
    # 이메일 중복 체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    # flask-login에서 사용자 ID를 문자열로 반환하기 위한 함수
    # 이 함수는 Flask-Login이 사용자 객체를 로드할 때 사용됨
    def get_id(self):
        return str(self.id)
    # 현재 로그인하고 있는 사용자 정보 취득 함수 설정은 apps/__init__.py에서 정의함
class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    servicename = db.Column(db.String(100), unique=True, nullable=False)
    is_active=db.Column(db.Boolean, default=True)  # 활성화 여부
    is_auto=db.Column(db.Boolean, default=True)  # 자동승인 여부
    price = db.Column(db.Integer, default=0, nullable=False)  # 서비스 단가
    description = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(200), nullable=False)
    service_endpoint = db.Column(db.String(255), nullable=True)  # 서비스 엔드포인트 함수, 일단 True
    created_at=db.Column(db.DateTime, default= datetime.now)
    updated_at=db.Column(db.DateTime, default= datetime.now, onupdate=datetime.now)

    # 관계
    subscriptions = db.relationship('Subscription', backref='service', lazy=True, cascade="all, delete-orphan")
    #usage_logs = db.relationship('UsageLog', backref='service', lazy=True, cascade="all, delete-orphan")
    #prediction_results = db.relationship('PredictionResult', backref='service', lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Service(name='{self.servicename}')>" # servicename으로 변경
class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # aiservice.id -> services.id로 변경
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False) 
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, approved, rejected
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    approval_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'service_id', name='_user_service_uc'),)

    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, service_id={self.service_id}, status='{self.status}')>"
