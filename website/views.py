import os
import uuid
from flask import Blueprint, render_template, redirect, request, flash , url_for, send_from_directory
from flask_login import  login_required, current_user
from .models import Candidate, Recruiter, Offer, Application
from sqlalchemy.sql import func 
from . import db 
from .extras import is_float, sendMail, limit_string, is_offer_in_array
from PIL import Image
from datetime import datetime, date
import re 


views = Blueprint('views', __name__ )

upload_resume = views.root_path + '/static/resume'
upload_image = views.root_path + '/static/images'

@views.route('/serve-resume/<filename>')
def serve_resume(filename):
    return send_from_directory(upload_resume, filename)

@views.route('/serve-picture/<filename>')
def serve_picture(filename):
    return send_from_directory(upload_image, filename)

@views.route('/', methods=['GET', 'POST'])
def home():

    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')
    elif isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    ofs = Offer.query.filter_by(status='active').all()
    regions = Offer.query.with_entities(Offer.region.distinct()).all()
    companies = Recruiter.query.with_entities(Recruiter.company.distinct()).all()

    if request.method == 'POST':
        position = request.form.get('position')
        category = request.form.get('category')
        company = request.form.get('company')
        region = request.form.get('region')

        if (position == '' or position is None ) and category == 'Select your Category' and company == 'Select your Company' and region == 'Select your Region':
            return render_template('index.html', offers=ofs[:8] , regions=regions, companies=companies, position=None, category=None, region=None, company=None)

        ps = []
        cats = []
        comps = []
        regs = []

        if position != '' and not None:
            positions = Offer.query.filter(Offer.position.like('%'+position+'%')).all()
            
            for pos in positions:
                if is_offer_in_array(pos, ofs):
                    ps.append(pos)

        if category != 'Select your Category':
            categories = Offer.query.filter(Offer.category.like('%'+category+'%')).all()
            
            for c in categories:
                if is_offer_in_array(c, ofs):
                    cats.append(c)
        
        if company != 'Select your Company':
            for c in ofs:
                print("\n\n\n"+str(c.recruiter)+"\t"+str(c.id)+"\n\n\n")
                if c.recruiter.company == company:
                    comps.append(c)
        
        if region != 'Select your Region':
            ions = Offer.query.filter(Offer.region.like('%'+region+'%')).all()
            
            for r in ions:
                if is_offer_in_array(r, ofs):
                    regs.append(r)

        ars = [ ps, cats, comps, regs]
        bigs = max(len(array) for array in ars)
        biggest = max(ars, key=lambda array: len(array), default=[])

        
        all_offers = []

        for i in biggest:
            valid = True 
            if position != '' and not None:
                if is_offer_in_array(i, ps) == False:
                    valid = False

            if category != 'Select your Category':
                if not is_offer_in_array(i, cats):
                    valid = False

            if company != 'Select your Company':
                if not is_offer_in_array(i, comps):
                    valid = False 
            
            if region != 'Select your Region':
                if not is_offer_in_array(i, regs):
                    valid = False

            if valid:
                all_offers.append(i)
        
        return render_template('index.html', offers=all_offers , regions=regions, companies=companies, position=position, category=category, region=region, company=company)


    return render_template('index.html', offers=ofs[:8] , regions=regions, companies=companies, position=None, category=None, region=None, company=None)

@views.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        message = request.form.get('message')

        sendMail("yassinebehilil@gmail.com","Mail from Jobless visitor", "Here is the message from "+full_name+" that has the email : "+email+" and sent this message : \n"+message)
        flash('Your message have been succesfully sent. You will soon get a response', category='success')
        return redirect('/contact')

    return render_template('contact.html')

@views.route('/home')
def homes():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')
    elif isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')
    else:
        return redirect('/')
    

@views.route('/home-candidate')
@login_required
def home_candidate():
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    apps = current_user.applications

    as_data = []

    for a in apps:
        
        if a.status == 'Pending':
            asa = {
                "offer": a.offer,
                "candidate": a.candidate,
                "appliers": len(a.offer.applications),
                "recruiter": a.offer.recruiter,
                "status": a.status,
                "dateApply": a.dateApply
            }
            as_data.append(asa)

    return render_template('home_candidate.html', user=current_user, apps=as_data)


@views.route('/home-recruiter')
@login_required
def home_recruiter():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    ofs = Offer.query.filter_by(recruiter_id=current_user.id, status='active').all()

    
    of_data = []
    x = 1
    for offer in ofs:
        
        of = { 
            "id" : offer.id,
            "recruiter_id": offer.recruiter_id,
            "title": offer.title,
            "description": offer.description,
            "position": offer.position,
            "salary": offer.salary,
            "status": offer.status,
            "dateCreation": offer.dateCreation,
            "dateEnd": offer.dateEnd,
            "speciality": offer.speciality,
            "region": offer.region,
            "category":offer.category,
            "applications": [],
            "length": 0,
            "x": x,
        }

        for application in offer.applications:
            if application.candidate.status == 'active' and application.status != 'Canceled':
                ap ={
                    "id" : application.candidate.id,
                    "first_name": application.candidate.first_name,
                    "last_name": application.candidate.last_name,
                    "address": application.candidate.address,
                    "phone": application.candidate.phone,
                    "email": application.candidate.email,
                    "password": application.candidate.password,
                    "diploma": application.candidate.diploma,
                    "speciality": application.candidate.speciality,
                    "resume": application.candidate.resume,
                    "picture": application.candidate.picture,
                    "status": application.status,
                    "dateApply": application.dateApply
                }
                of["applications"].append(ap)
                x = x + 1

        of["length"] = len(of["applications"])  
        of["x"] = str(x)
        print("\n\n\n"+of["x"]+"\n\n\n")      
        of_data.append(of)
        x = x + 2
        
        

    
    return render_template('home_recruiter.html', user=current_user, offers=of_data)

@views.route('/profile-candidate', methods=['GET', 'POST'])
@login_required
def profile_candidate():
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')
    
    if request.method == 'POST':
        id = request.form.get('id')
        candidate = Candidate.query.filter_by(id=id).first()

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

        candidate.first_name = first_name
        candidate.last_name = last_name 
        candidate.address = address 
        candidate.phone = phone 
        candidate.email = email 
        candidate.password = password 
        candidate.diploma = diploma 
        candidate.speciality = speciality

        if resume:
            resumename = str(uuid.uuid4()) + os.path.splitext(resume.filename)[1]
            resume.save(os.path.join(upload_resume, resumename))
            candidate.resume = resumename

        if picture:
            picturename = str(uuid.uuid4()) + os.path.splitext(picture.filename)[1]

            image = Image.open(picture)
            resized_image = image.resize( (200, 200) )

            resized_image.save(os.path.join(upload_image, picturename))
            #picture.save(os.path.join(upload_image, picturename))
            candidate.picture = picturename

        db.session.commit()

        return redirect('/profile-candidate')


    return render_template("profile_candidate.html", user=current_user)


@views.route('/deactivate-candidate', methods=['GET', 'POST'])
@login_required
def deactivate_candidate():
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    if request.method == 'POST':
        id = request.form.get('id')
        candidate = Candidate.query.filter_by(id=id).first()

        for application in candidate.applications:
            application.status = 'Canceled'

        candidate.status = 'not active'
        db.session.commit()

        return redirect('/login')

    return redirect('/login')


@views.route('/profile-recruiter', methods=['GET', 'POST'])
@login_required
def profile_recruiter():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    if request.method == 'POST':
        id = request.form.get('id')
        recruiter = Recruiter.query.filter_by(id=id).first()

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        company = request.form.get('company')
        email = request.form.get('email')
        password = request.form.get('password')

        picture = request.files['picture']  

        recruiter.first_name = first_name
        recruiter.last_name = last_name 
        recruiter.address = address 
        recruiter.phone = phone 
        recruiter.email = email 
        recruiter.password = password 
        recruiter.company = company 

        if picture:
            picturename = str(uuid.uuid4()) + os.path.splitext(picture.filename)[1]

            image = Image.open(picture)
            resized_image = image.resize( (200, 200) )

            resized_image.save(os.path.join(upload_image, picturename))

            #picture.save(os.path.join(upload_image, picturename))
            recruiter.picture = picturename
        
        db.session.commit()
        
        return redirect('/profile-recruiter')




    return render_template("profile_recruiter.html", user=current_user)


@views.route('/deactivate-recruiter', methods=['GET', 'POST'])
@login_required
def deactivate_recruiter():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    if request.method == 'POST':
        id = request.form.get('id')
        recruiter = Recruiter.query.filter_by(id=id).first()

        recruiter.status = 'not active'

        for offer in recruiter.offers:
            offer.status='canceled'

        db.session.commit()

        return redirect('/login')

    return redirect('/login')


@views.route('/add-offer', methods=['GET', 'POST'])
@login_required
def add_offer():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    if request.method == 'POST':
        title = request.form.get('title').lower()
        description = request.form.get('description').lower()
        speciality = request.form.get('speciality').lower()
        position = request.form.get('position').lower()
        salary = request.form.get('salary')
        dateend = datetime.strptime(request.form.get('dateend'), "%Y-%m-%d").date()
        category = request.form.get('category')
        region = request.form.get('region').lower()
        

        if not is_float(salary):
            flash('The salary must be a numeric value', category='error')
            return redirect('/add-offer')
        elif dateend < date.today():
            flash('You can\'t choose a date in the past ', category='error')
            return redirect('/add-offer')
        else:
            salary = float(salary)
            offer = Offer(recruiter_id=current_user.id,title=title, description=description, speciality=speciality, position=position, salary=salary,status='active',dateCreation=func.date(), dateEnd=dateend, region=region, category=category)

            db.session.add(offer)
            db.session.commit()
            flash('Offer have been successfully added', category='success')
            return redirect('/home')

    return render_template('add_offer.html', user=current_user)


 
@views.route('/offer-profile/<offer_id>')
@login_required
def offer_profile(offer_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    offer = Offer.query.filter_by(id=offer_id).first()

    return render_template('offer_profile.html', user=current_user, offer=offer)

@views.route('/candidate-profile/<candidate_id>', methods=['GET', 'POST'])
@login_required
def candidate_profile(candidate_id):

    if isinstance(current_user, Candidate):
            return redirect('/home-candidate')

    candidate = Candidate.query.filter_by(id=candidate_id).first()
    
    if request.method == 'POST':
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        message = request.form.get('message')

        sendMail(receiver,'This is a mail from '+str(sender)+' a recruiter in jobless','here is the message sent : '+str(message))
        flash('Message sent successfully. You might get a response on your mail. Look forward to it', category='success')


    return render_template('candidate_profile.html', user=current_user, candidate=candidate)



@views.route('/offers-history', methods=['GET','POST'])
@login_required
def offers_history():

    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    if request.method == 'POST':
        id = request.form.get('id')
        title = request.form.get('title').lower()
        description = request.form.get('description').lower()
        speciality = request.form.get('speciality').lower()
        position = request.form.get('position').lower()
        salary = request.form.get('salary')
        dateend = datetime.strptime(request.form.get('dateend'), "%Y-%m-%d").date()
        region = request.form.get('region').lower()
        category = request.form.get('category')

        if not is_float(salary):
            flash('The salary must be a numeric value', category='error')
            return redirect('/home-recruiter')
        if dateend < date.today():
            flash('The date should be in the future not the past ')
            return redirect('/home-recruiter')
        else:
            salary = float(salary)

            offer = Offer.query.filter_by(id=id).first()

            offer.title = title
            offer.description = description 
            offer.speciality = speciality
            offer.position = position 
            offer.salary = salary
            offer.dateend = dateend 
            offer.region = region 
            offer.category = category 

            db.session.commit()

            flash('Updated Successfully', category='success')
            return redirect('/home-recruiter')



    ofs = Offer.query.filter_by(recruiter_id=current_user.id).all()
    of_data = []

    for offer in ofs:
        if offer.status != 'active':
            of = { 
                "id" : offer.id,
                "recruiter_id": offer.recruiter_id,
                "title": offer.title,
                "description": offer.description,
                "position": offer.position,
                "salary": offer.salary,
                "status": offer.status,
                "dateCreation": offer.dateCreation,
                "dateEnd": offer.dateEnd,
                "speciality": offer.speciality,
                "region": offer.region,
                "category":offer.category,
                "applications": [],
                "length": 0
            }

            for application in offer.applications:
                if application.candidate.status == 'active' and application.status != 'Canceled':
                    ap ={
                        "id" : application.candidate.id,
                        "first_name": application.candidate.first_name,
                        "last_name": application.candidate.last_name,
                        "address": application.candidate.address,
                        "phone": application.candidate.phone,
                        "email": application.candidate.email,
                        "password": application.candidate.password,
                        "diploma": application.candidate.diploma,
                        "speciality": application.candidate.speciality,
                        "resume": application.candidate.resume,
                        "picture": application.candidate.picture,
                        "status": application.status,
                        "dateApply": application.dateApply
                    }
                    of["applications"].append(ap)
            of["length"] = len(of["applications"])        
            of_data.append(of)


    return render_template('offers_history.html', user=current_user, offers=of_data)




@views.route('/cancel-offer/<offer_id>')
@login_required
def cancel_offer(offer_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')
    
    offer = Offer.query.filter_by(id=offer_id).first()
    offer.status = 'canceled'

    for application in offer.applications:
        if application.status == 'Pending':
            application.status = 'Refused'

    db.session.commit()

    return redirect('/offers-history')

@views.route('/finish-offer/<offer_id>')
@login_required
def finish_offer(offer_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    offer = Offer.query.filter_by(id=offer_id).first()
    apps = []
    for application in offer.applications:
        if application.status == 'Accepted':
            apps.append(application)

    if len(apps) == 0:
        
        flash('You have to at least accept one candidate in order to finish an offer. You can cancel the offer if you won\'t accept any candidates ',category='error')
        return redirect('/offer-profile/'+offer_id)
    
    offer.status = 'finished'
    for application in offer.applications:
        if application.status == 'Pending':
            application.status = 'Refused'

    db.session.commit()

    return redirect('/offer-profile/'+offer_id)


@views.route('/accept-refuse-offers')
@login_required
def accept_refuse_offers():
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')
    
    ofs = Offer.query.filter_by(recruiter_id=current_user.id, status='active').all()
    of_data = []

    for offer in ofs:
        of = { 
            "id" : offer.id,
            "recruiter_id": offer.recruiter_id,
            "title": offer.title,
            "description": limit_string(offer.description),
            "position": offer.position,
            "salary": offer.salary,
            "status": offer.status,
            "dateCreation": offer.dateCreation,
            "dateEnd": offer.dateEnd,
            "speciality": offer.speciality,
            "region": offer.region,
            "category":offer.category,
            "days_left": (offer.dateEnd - offer.dateCreation).days - 1,
            "applications": [],
            "length": 0
            
        }
        for application in offer.applications:
            if application.candidate.status == 'active':
                ap ={
                    "id" : application.candidate.id,
                    "first_name": application.candidate.first_name,
                    "last_name": application.candidate.last_name,
                    "address": application.candidate.address,
                    "phone": application.candidate.phone,
                    "email": application.candidate.email,
                    "password": application.candidate.password,
                    "diploma": application.candidate.diploma,
                    "speciality": application.candidate.speciality,
                    "resume": application.candidate.resume,
                    "picture": application.candidate.picture,
                    "status": application.status,
                    "dateApply": application.dateApply
                }
                of["applications"].append(ap)
        of["length"] = len(of["applications"])        
        of_data.append(of)

    return render_template('ar_offers.html', user=current_user, offers=of_data)


@views.route('/ar-offer-profile/<offer_id>')
@login_required
def ar_offer_profile(offer_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')
    offer = Offer.query.filter_by(id=offer_id, recruiter_id=current_user.id).first()



    return render_template('ar_offer_profile.html', user=current_user, offer=offer )


@views.route('/accept-candidate/<offer_id>/<candidate_id>')
@login_required
def accept_candidate(offer_id, candidate_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    offer = Offer.query.filter_by(id=offer_id, recruiter_id=current_user.id).first()

    for application in offer.applications:
        if application.candidate_id == candidate_id:
            application.status = 'Accepted'
            sendMail(application.candidate.email,"You have been approved for the offer "+application.offer.title, "You can check for more details on the website ")

    db.session.commit()

    return redirect('/ar-offer-profile/'+offer_id)


@views.route('/refuse-candidate/<offer_id>/<candidate_id>')
@login_required
def refuse_candidate(offer_id, candidate_id):
    if isinstance(current_user, Candidate):
        return redirect('/home-candidate')

    offer = Offer.query.filter_by(id=offer_id, recruiter_id=current_user.id).first()

    for application in offer.applications:
        if application.candidate_id == candidate_id:
            application.status = 'Refused'
            sendMail(application.candidate.email,"You have been refused for the offer "+application.offer.title, "You can check for more details on the website ")

            
    db.session.commit()

    return redirect('/ar-offer-profile/'+offer_id)

@views.route('/applications-history')
@login_required
def application_history():
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    apps = current_user.applications

    as_data = []

    for a in apps:
        
        if a.status != 'Pending':
            asa = {
                "offer": a.offer,
                "candidate": a.candidate,
                "appliers": len(a.offer.applications),
                "recruiter": a.offer.recruiter,
                "status": a.status,
                "dateApply": a.dateApply
            }
            as_data.append(asa)
        
    
    return render_template("applications_history.html", user=current_user, apps=as_data)

@views.route('/candidate-offer-profile/<offer_id>', methods=['GET', 'POST'])
@login_required
def candidate_offer_profile(offer_id):
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    checker=True   
    ap = Application.query.filter_by(offer_id=offer_id, candidate_id=current_user.id).first()

    if ap is None:
        ap ={
            "offer": Offer.query.filter_by(id=offer_id).first(),
            "candidate": current_user
        }
        checker = False   

    if request.method == 'POST':
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        message = request.form.get('message')

        sendMail(receiver,'This is a mail from '+str(sender)+' a candidate in jobless','here is the message sent : '+str(message))
        flash('Message sent successfully. You might get a response on your mail. Look forward to it', category='success')

    return render_template("candidate_offer_profile.html", user=current_user, application=ap, checker=checker)

@views.route('/cancel-application/<offer_id>')
@login_required
def cancel_application(offer_id):
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    application = Application.query.filter_by(offer_id=offer_id, candidate_id=current_user.id).first()

    application.status = 'Canceled'

    db.session.commit()

    return redirect('/home-candidate')


@views.route('/browse-offers', methods=['GET', 'POST'])
@login_required
def browse_offers():
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    offers = Offer.query.filter_by(status='active').all()
    regions = Offer.query.with_entities(Offer.region.distinct()).all()
    companies = Recruiter.query.with_entities(Recruiter.company.distinct()).all()

    ofs = []

    for offer in offers:
        application = Application.query.filter_by(offer_id= offer.id, candidate_id = current_user.id).first()
        if application is None:
            ofs.append(offer)

    if request.method == 'POST':
        position = request.form.get('position')
        category = request.form.get('category')
        company = request.form.get('company')
        region = request.form.get('region')

        print("\n\n Position : "+position+" Category : "+category+" Company : "+company+" Region : "+region+"\n\n")

        if (position == '' or position is None ) and category == 'Select your Category' and company == 'Select your Company' and region == 'Select your Region':
            return render_template('browse_offers.html', user=current_user, offers=ofs[:8] , regions=regions, companies=companies, position=None, category=None, region=None, company=None)

        ps = []
        cats = []
        comps = []
        regs = []
        if position != '' and not None:
            positions = Offer.query.filter(Offer.position.like('%'+position+'%')).all()
            
            for pos in positions:
                if is_offer_in_array(pos, ofs):
                    print("\n\n\n valid pos : "+str(pos)+"\n\n\n")
                    ps.append(pos)

        if category != 'Select your Category':
            categories = Offer.query.filter(Offer.category.like('%'+category+'%')).all()
            
            for c in categories:
                if is_offer_in_array(c, ofs):
                    cats.append(c)
        
        if company != 'Select your Company':
            
            for c in ofs:
                if c.recruiter.company == company:
                    comps.append(c)
        
        if region != 'Select your Region':
            ions = Offer.query.filter(Offer.region.like('%'+region+'%')).all()
            
            for r in ions:
                if is_offer_in_array(r, ofs):
                    regs.append(r)

        ars = [ ps, cats, comps, regs]
        bigs = max(len(array) for array in ars)
        biggest = max(ars, key=lambda array: len(array), default=[])

        
        all_offers = []

        for i in biggest:
            valid = True 
            if position != '' and not None:
                if is_offer_in_array(i, ps) == False:
                    valid = False

            if category != 'Select your Category':
                if not is_offer_in_array(i, cats):
                    valid = False

            if company != 'Select your Company':
                if not is_offer_in_array(i, comps):
                    valid = False 
            
            if region != 'Select your Region':
                if not is_offer_in_array(i, regs):
                    valid = False

            if valid:
                all_offers.append(i)
        
        return render_template('browse_offers.html', user=current_user, offers=all_offers , regions=regions, companies=companies, position=position, category=category, region=region, company=company)


    return render_template('browse_offers.html', user=current_user, offers=ofs[:8] , regions=regions, companies=companies, position=None, category=None, region=None, company=None)


@views.route('/apply-offer/<offer_id>')
@login_required
def apply_offer(offer_id):
    if isinstance(current_user, Recruiter):
        return redirect('/home-recruiter')

    application = Application(candidate_id=current_user.id, offer_id=offer_id, status='Pending', dateApply=func.date() )

    db.session.add(application)
    db.session.commit()

    flash('Your Application have been sent successfully. You can see your pending applications here ', category='success')

    return redirect('/home-candidate')


@views.route('/visitor-offer-profile/<offer_id>')
def visitor_offer_profile(offer_id):

    offer = Offer.query.filter_by(id=offer_id).first()

    return render_template('visitor_offer_profile.html', offer=offer)


