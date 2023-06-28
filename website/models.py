import uuid
from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func 

class Candidate(db.Model, UserMixin):
    __tablename__ = 'candidate'
    id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    diploma = db.Column(db.String(255))
    speciality = db.Column(db.String(255))
    resume = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    status = db.Column(db.String(255))
    applications = db.relationship('Application', backref='candidate', lazy=True)

    def __init__(self, first_name, last_name, address, phone, email, password, diploma, speciality, resume, picture, status):
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password 
        self.diploma = diploma
        self.speciality = speciality
        self.resume = resume
        self.picture = picture
        self.status = status 

class Recruiter(db.Model, UserMixin):
    __tablename__ = 'recruiter'
    id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    company = db.Column(db.String(255))
    status = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    offers = db.relationship('Offer', backref='recruiter', lazy=True)

    def __init__(self, first_name, last_name, address, phone, email, password, company, status, picture):
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.company = company 
        self.status = status 
        self.picture = picture

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.String(255), primary_key=True)
    recruiter_id = db.Column(db.String(255), db.ForeignKey('recruiter.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.String(10000))
    position = db.Column(db.String(255))
    salary = db.Column(db.Float)
    status = db.Column(db.String(255))
    dateCreation = db.Column(db.Date)
    dateEnd = db.Column(db.Date)
    speciality = db.Column(db.String(255))
    region = db.Column(db.String(255))
    category = db.Column(db.String(255))
    applications = db.relationship('Application', backref='offer', lazy=True)

    def __init__(self, recruiter_id, title, description, position, salary, status, dateCreation, dateEnd, speciality, region, category):
        self.id = str(uuid.uuid4())
        self.recruiter_id = recruiter_id
        self.title = title
        self.description = description
        self.position = position
        self.salary = salary
        self.status = status 
        self.dateCreation = dateCreation
        self.dateEnd = dateEnd
        self.speciality = speciality
        self.region = region
        self.category = category


class Application(db.Model):
    __tablename__ = 'application'
    candidate_id = db.Column(db.String(255), db.ForeignKey('candidate.id'), primary_key=True)
    offer_id = db.Column(db.String(255), db.ForeignKey('offer.id'), primary_key=True )
    status = db.Column(db.String(255))
    dateApply = db.Column(db.Date)



