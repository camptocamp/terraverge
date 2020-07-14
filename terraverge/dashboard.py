import functools
import psycopg2.extras
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from terraverge.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/last-plans', methods=['GET'])
def overview():
    db = get_db()
    error = None
    
    if error is not None:
        flash(error)

    with db.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            'SELECT * FROM plan ORDER BY generation_date DESC LIMIT 50'
            )
        entries = cursor.fetchall()

        data = []
        for entry in entries:
            convergence_success = True
            if len(entry['plan']['resource_changes']) > 0:
                convergence_success = False

            data.append({
                "generation_date": entry['generation_date'],
                "terraform_version": entry['terraform_version'],
                "git_remote": entry['git_remote'],
                "git_commit": entry['git_commit'],
                "ci_url": entry['ci_url'],
                "source": entry['source'],
                "convergence_success": convergence_success,
            })

    return render_template('dashboard/overview.html', data=data)
