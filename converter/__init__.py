import errno, os
from converter import convert, download, generate_image, generate_sound
from flask import Flask
from flask_bootstrap import Bootstrap
from music21 import *
from subprocess import PIPE, Popen
import pathlib, stat

def setupAppAndCacheDirectories(app):
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    try:
        os.makedirs('musicxmlCache')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="lucien",
        UPLOAD_FOLDER = os.path.join(os.getcwd(),'musicxmlCache'),
        OUTPUT_FILE = os.path.join(os.getcwd(),'result.abc'),
        OUTPUT_IMG = os.path.join(os.getcwd(),'result.png'),
        ALLOWED_EXTENSIONS = {'musicxml'}
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    setupAppAndCacheDirectories(app)
    # apply the blueprints to the app

    app.register_blueprint(convert.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(generate_image.bp)
    app.register_blueprint(generate_sound.bp)

    app.add_url_rule("/", endpoint="index")
    os.environ['HOME'] = os.getcwd()
    bootstrap = Bootstrap(app)

    process1 = Popen(['which' ,'lilypond'], 
        stdout=PIPE, stderr = PIPE)
    stdout, stderr = process1.communicate()
    environment.set('lilypondPath', stdout.decode().replace('\n', ''))

    process2 = Popen(['which' ,'mscore-portable'], 
        stdout=PIPE, stderr = PIPE)
    stdout, stderr = process2.communicate()
    environment.set('musicxmlPath', stdout.decode().replace('\n', ''))
    environment.set('pdfPath', stdout.decode().replace('\n', ''))
    environment.set('midiPath', stdout.decode().replace('\n', ''))
    environment.set('vectorPath', stdout.decode().replace('\n', ''))
    environment.set('musescoreDirectPNGPath', stdout.decode().replace('\n', ''))
    
    return app