from flask import Flask
import os

application = Flask(__name__)

application.config['UPLOAD_FOLDER'] = '/Users/richikghosh/Documents/GitHub/Audio to speech/uploads'
import os
os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)
# Set the upload folder configuration
#app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
from app import routes
