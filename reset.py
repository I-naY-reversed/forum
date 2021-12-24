try:import os;os.remove('login.db')
except:pass
from main import db
db.create_all()