import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from terraverge.db import get_db

bp = Blueprint('plan', __name__, url_prefix='/plan')

@bp.route('/overview', methods=['GET'])
def overview():
    db = get_db()
    error = None
    
    if error is not None:
        flash(error)

    entries = ""

    return render_template('plan/overview.html')
