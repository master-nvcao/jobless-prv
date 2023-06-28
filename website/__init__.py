from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime, date

db = SQLAlchemy()
DB_NAME= "pfa_v1.db"

def create_app():
    app =  Flask(__name__)
    app.config['SECRET_KEY'] = 'this_is_my_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    



    db.init_app(app)


    from .views import views
    from .auth import auth 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, urlprefix='/')

    from .models import Candidate, Recruiter, Offer, Application 

    with app.app_context():
        db.create_all()


    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        candidate = Candidate.query.get(id)
        if candidate:
            return candidate
        else:
            return Recruiter.query.get(id)

    from .extras import update_finished_offers, insert_Candidates, insert_Recruiters, insert_Offers

    update_finished_offers(app=app, db=db)

    r = auth.root_path + '/static/resume'
    p = auth.root_path + '/static/images'
    
    #insert_Candidates(app=app, db=db, upload_image=p, upload_resume=r)
    #insert_Recruiters(app=app, db=db, upload_image=p)
    #insert_Offers(app=app, db=db)
    # this project project was made by the nvcao also called behilil yassine 

    

    return app



