import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from terraverge.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
def overview():
    db = get_db()
    error = None
    
    if error is not None:
        flash(error)

    entries = ""

    return render_template('dashboard/overview.html')
