from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from feed.tables import ArXivUpdate,db
from datetime import datetime

        
def db_testing():
    db=current_app.extensions['sqlalchemy'].db
 
    print(ArXivUpdate.query.limit(2).all())
 
    return
