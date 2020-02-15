from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
# from flask_mail import Mail
import os
# , file=sys.stderr



app = Flask(__name__)

from website_end import route
from website_end import models

