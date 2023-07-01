import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Candidate, Recruiter
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .extras import sendMail,generate_password
from PIL import Image 


auth = Blueprint('auth', __name__ )

upload_resume = auth.root_path + '/static/resume'
upload_image = auth.root_path + '/static/images'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        candidate = Candidate.query.filter_by(email=email).first()
        recruiter = Recruiter.query.filter_by(email=email).first()

        

        if candidate:
            if candidate.password == password:
                if candidate.status == 'active':
                    flash('Welcome Back '+candidate.first_name+" "+candidate.last_name, category='success')
                    login_user(candidate, remember=False)
                    return redirect(url_for('views.home_candidate'))
                else:
                    flash('Your account have been already deleted',category='error')
            else:
                flash('Incorrect password. Try again', category='error')
        
        elif recruiter:
            if recruiter.password == password:
                if recruiter.status == 'active':
                    flash('Welcome Back '+recruiter.first_name+" "+recruiter.last_name, category='success')
                    login_user(recruiter, remember=False)
                    
                    return redirect(url_for('views.home_recruiter'))
                else:
                    flash('Your account have been already deleted',category='error')
            else:
                flash('Incorrect password. Try again', category='error')
        else:
            flash('User doesn\'t exist ', category='error')


    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@auth.route('/register')
def register():

    if current_user.is_authenticated:
        return redirect('/home')
    
    return render_template('register.html')

@auth.route('/candidate-register', methods=['GET', 'POST'])
def candidate_register():
    if request.method == 'POST':
        first_name = request.form.get('first_name').lower()
        last_name = request.form.get('last_name').lower()
        address = request.form.get('address').lower()
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        diploma = request.form.get('diploma').lower()
        speciality = request.form.get('speciality').lower()

        resume = request.files['resume']
        picture = request.files['picture']

        picturename = "default_profile.png"

        candidate = Candidate.query.filter_by(email=email).first()
        recruiter = Recruiter.query.filter_by(email=email).first()

        if candidate:
            if candidate.status == 'not active':
                flash('User have been activated', category='success')
                candidate.status = 'active'
                db.session.commit()
                return redirect('/login')
            else:
                flash('User already exists. try login in ', category='error')
                return redirect('/login')
        elif recruiter:
            if recruiter.status == 'not active':
                flash('User have been activated', category='success')
                recruiter.status = 'active'
                db.session.commit()
                return redirect('/login')
            else:
                flash('User already exists. Try login in', category='error')
                return redirect('/login')

        elif not phone.isnumeric():
            flash('you should enter a valid phone number ', category='error')
        elif not resume:
            flash('you should enter a valid resume', category='error')
        else:
            resumename = str(uuid.uuid4()) + os.path.splitext(resume.filename)[1]
            resume.save(os.path.join(upload_resume, resumename))

            if picture:
                picturename = str(uuid.uuid4()) + os.path.splitext(picture.filename)[1]

                image = Image.open(picture)
                resized_image = image.resize( (200, 200) )
                resized_image.save(os.path.join(upload_image, picturename))
                #picture.save(os.path.join(upload_image, picturename))

            candidate = Candidate(first_name=first_name, last_name=last_name, address=address, phone=phone, email=email, password=password, diploma=diploma, speciality=speciality, resume=resumename,picture=picturename, status='active')

            db.session.add(candidate)
            db.session.commit()

            flash('Account successfully created', category='success')
            login_user(candidate, remember=False)

            return redirect(url_for('views.home_candidate'))

    
    return redirect('/register')

@auth.route('/recruiter-register', methods=['GET', 'POST'])
def recruiter_register():

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        company = request.form.get('company')
        email = request.form.get('email')
        password = request.form.get('password')

        picture = request.files['picture']        

        candidate = Candidate.query.filter_by(email=email).first()
        recruiter = Recruiter.query.filter_by(email=email).first()

        

        picturename = "default_profile.png"

        if candidate:
            if candidate.status == 'not active':
                flash('User have been activated', category='success')
                candidate.status = 'active'
                db.session.commit()
                return redirect('/login')
            else:
                flash('User already exists. try login in ', category='error')
                return redirect('/login')
        elif recruiter:
            if recruiter.status == 'not active':
                flash('User have been activated', category='success')
                recruiter.status = 'active'
                db.session.commit()
                return redirect('/login')
            else:
                flash('User already exists. Try login in', category='error')
                return redirect('/login')

        elif not phone.isnumeric():
            flash('you should enter a valid phone number ', category='error')

        else:

            if picture:
                picturename = str(uuid.uuid4()) + os.path.splitext(picture.filename)[1]
                
                image = Image.open(picture)
                resized_image = image.resize( (200, 200) )
                resized_image.save(os.path.join(upload_image, picturename))

                #picture.save(os.path.join(upload_image, picturename))

            recruiter = Recruiter(first_name=first_name, last_name=last_name, address=address, phone=phone, email=email, password=password, company=company, picture=picturename, status='active')
            db.session.add(recruiter)
            db.session.commit()

            flash('Account successfully created', category='success')
            login_user(recruiter, remember=False)
            return redirect(url_for('views.home_recruiter'))



    return redirect('/register')

# this project project was made by the nvcao also called behilil yassine 


@auth.route('/forgotpassword',  methods=['GET', 'POST'])
def forgotpassword():

    if current_user.is_authenticated:
        return redirect('/home')
        
    if request.method == 'POST':
        email = request.form.get('email')
        candidate = Candidate.query.filter_by(email=email).first()
        recruiter = Recruiter.query.filter_by(email=email).first()
        password = generate_password(12)
        

        if candidate:
            if candidate.status == 'active':
                candidate.password = password
                sendMail(candidate.email,'Reset your password','You new password is : '+password)
                flash('A new password have been sent to your email', category='success')
                db.session.commit()
                return redirect('/login')
            else:
                flash('Your account have been already deactivated',category='error')
                return redirect('/register')

        elif recruiter:
            if recruiter.status == 'active':
                recruiter.password = password
                sendMail(recruiter.email,'Reset your password','You new password is : '+password)
                flash('A new password have been sent to your email', category='success')
                db.session.commit()
                return redirect('/login')
            else:
                flash('Your account have been already deactivated',category='error')
                return redirect('/register')

        else:
            flash('Email does not exist. Create a new account', category='error')


    return render_template('forgot_password.html')


