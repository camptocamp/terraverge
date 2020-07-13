import os
import click

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
        app.config.from_mapping(
                PG_CONFIG=('host={host} '
                     'port={port} '
                     'dbname={dbname} '
                     'user={user} '
                     'password={password}').format(
                         host=os.getenv('PGHOST', 'localhost'),
                         port=os.getenv('PGPORT', '5432'),
                         dbname=os.getenv('PGDATABASE', 'terraverge'),
                         user=os.getenv('PGUSER', 'terraverge'),
                         password=os.getenv('PGPASSWORD', 'terraverge')
                     ),
                 )
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import plan
    app.register_blueprint(plan.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)

    return app
