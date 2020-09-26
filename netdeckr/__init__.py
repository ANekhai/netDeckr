import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'netdeckr.sqlite')
    )

    if test_config is None:
        # load instance config, if it exists, when not testing app
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load passed in test config
        app.config.from_mapping(test_config)

    # look for instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Import modules
    from . import db
    db.init_app(app)

    from . import catalog
    app.register_blueprint(catalog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
