import shutil
import smtplib
from email.message import EmailMessage
import secrets
import string
import uuid
from .models import Offer, Candidate, Application, Recruiter
from datetime import datetime, date
from flask import current_app
import os 
from datetime import date, datetime

def sendMail(receiver, subject, message):
    sender_email = "pfaproject77@gmail.com"
    password = "ubwleaqyfgpzkdwi"

    email = EmailMessage()
    email["From"] = sender_email
    email["To"] = receiver
    email["Subject"] = subject
    email.set_content(message)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    print("Login success")
    server.send_message(email)
    print("Email has been sent to", receiver)
    server.quit()



def generate_password(length):
    characters = string.ascii_letters + string.digits + "@*^%$#!"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def limit_string(text):
    words = text.split()
    limited_words = words[:10]
    limited_text = ' '.join(limited_words)
    return limited_text

def is_offer_in_array(offer, offers):
    for i in offers:
        if i.id == offer.id:
            return True 
    return False

def update_finished_offers(app, db):
    with app.app_context():
        offers = Offer.query.all()
        for offer in offers:
                if date.today() > offer.dateEnd:
                    offer.status = 'finished'
                    for application in offer.applications:
                        if application.status == 'Pending':
                            application.status = 'Refused'

        db.session.commit()



def insert_Candidates(app, db, upload_resume, upload_image):
    with app.app_context():
        with open('/Users/yassinebehilil/Desktop/flaskproj/makers/candidates.txt', 'r') as file:
            i = 1 
            for line in file:
                
                fields = line.strip().split(',')
                last_name = fields[0]
                first_name = fields[1]
                email = fields[2]
                password = fields[3]
                address = fields[4]
                phonenumber = fields[5]
                diploma = fields[6]
                speciality = fields[7]
                resume = fields[8]
                picture = fields[9]

                candidate = Candidate.query.filter_by(email=email).first()
                recruiter = Recruiter.query.filter_by(email=email).first()

                if candidate is None and recruiter is None:

                    res = os.path.basename(resume)
                    resumename = str(uuid.uuid4()) + os.path.splitext(res)[1]
                    shutil.copy(resume, upload_resume+"/"+resumename)

                    pic = os.path.basename(picture)
                    picturename = str(uuid.uuid4()) + os.path.splitext(pic)[1]
                    shutil.copy(picture, upload_image+"/"+picturename)

                    c = Candidate(first_name=first_name, last_name=last_name, address=address, phone=phonenumber, email=email, password=password, diploma=diploma,
                    speciality=speciality, resume=resumename, picture=picturename, status='active')
                    print(f"No {i}: "+first_name+" "+last_name+" has been added \n")
                    db.session.add(c)

                else:
                    pass
                    print("Candidate "+first_name+" "+last_name+" already exists \n")
                i = i + 1
        db.session.commit()


def insert_Recruiters(app, db, upload_image):
    with app.app_context():
        with open('/Users/yassinebehilil/Desktop/flaskproj/makers/recruiters.txt', 'r') as file:
            i = 1 
            for line in file:
                
                fields = line.strip().split(',')
                last_name = fields[0]
                first_name = fields[1]
                email = fields[2]
                password = fields[3]
                address = fields[4]
                phonenumber = fields[5]
                company = fields[6]
                picture = fields[7]

                candidate = Candidate.query.filter_by(email=email).first()
                recruiter = Recruiter.query.filter_by(email=email).first()

                if candidate is None and recruiter is None:

                    pic = os.path.basename(picture)
                    picturename = str(uuid.uuid4()) + os.path.splitext(pic)[1]
                    shutil.copy(picture, upload_image+"/"+picturename)

                    r = Recruiter(first_name=first_name, last_name=last_name, address=address, phone=phonenumber, email=email, password=password, company=company,
                    status='active', picture=picturename)
                   

                    print(f"No {i}: "+first_name+" "+last_name+" has been added \n")

                    db.session.add(r)

                else:
                    pass
                    print("Recruiter "+first_name+" "+last_name+" already exists \n")

                i = i + 1

        db.session.commit()


def insert_Offers(app, db):
    with app.app_context():
        with open('/Users/yassinebehilil/Desktop/flaskproj/makers/offers.txt', 'r') as file:
            i = 1
            for line in file:
                
                fields = line.strip().split(',')
                recruiter_id = fields[0]
                title = fields[1]
                description = fields[2]
                speciality = fields[3]
                position = fields[4]
                salary = float(fields[5])
                region = fields[6]
                category = fields[7]
                datecreation = datetime.strptime(fields[8], "%Y-%m-%d").date()
                dateend = datetime.strptime(fields[9], "%Y-%m-%d").date()
                
                offer = Offer.query.filter_by(title=title).first()

                if offer is None:

                    print(f"No {i} :  {title} have been added \n")

                    o = Offer(recruiter_id=recruiter_id, title=title, description=description, position=position, salary=salary, status='active', 
                    dateCreation=datecreation, dateEnd=dateend, speciality=speciality, region=region, category=category)

                    db.session.add(o)

                else:

                    print(f"{title} already exits \n")
                i = i + 1

        db.session.commit()

# this project project was made by the nvcao also called behilil yassine 
