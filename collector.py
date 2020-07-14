import os
import psycopg2
import datetime
import json
import distutils.util
from flask import Flask, flash, request, redirect
from psycopg2.extensions import register_adapter

# Allow conversion from dict to jsonb with psycopg2
from psycopg2.extras import Json
register_adapter(dict, Json)

debug = distutils.util.strtobool(os.getenv('DEBUG', 'false'))
psk = os.getenv('PSK')
if psk is None:
    raise Exception('Please specify a PSK')

app = Flask(__name__)
app.secret_key = b'~\xea\x12T\xc2\x1c\t\\\x97\xfb\xbe\x0cD8\xfc\xd2BC\x90[A\xd9\x0f\xb6'

init_sql_file = 'init.sql'
connection_string = ('host={host} '
                     'port={port} '
                     'dbname={dbname} '
                     'user={user} '
                     'password={password}').format(
                         host=os.getenv('PGHOST', 'localhost'),
                         port=os.getenv('PGPORT', '5432'),
                         dbname=os.getenv('PGDATABASE', 'terraverge'),
                         user=os.getenv('PGUSER', 'terraverge'),
                         password=os.getenv('PGPASSWORD', 'terraverge')
                     )

# Create or update database
with psycopg2.connect(connection_string) as conn:
    with open(init_sql_file) as sql:
        with conn.cursor() as curs:
            curs.execute(sql.read())


def parse_date(str):
    return datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S%z")

def insert_plan(request):
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as curs:
            curs.execute("INSERT INTO plan (terraform_version, git_remote, git_commit, ci_url, source, generation_date, plan) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                         (request.values['terraform_version'],
                          request.values['git_remote'],
                          request.values['git_commit'],
                          request.values['ci_url'],
                          request.values['source'],
                          parse_date(request.values['generation_date']),
                          json.loads(request.files['plan'].read().decode('utf8'))))

@app.route('/plan', methods=['GET', 'POST'])
def submit_plan():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'plan' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['plan']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if request.values['psk'] != psk:
            raise Exception('Invalid psk !')
        if file:
            insert_plan(request)
            return 'ok'
    return '''
    <!doctype html>
    <title>Upload terraform plan</title>
    <h1>Upload new Plan</h1>
    <form method=post enctype=multipart/form-data>
      Terraform version: <input type=text name=terraform_version value="0.12.21"><br>
      Git remote URL: <input type=text name=git_remote value="git.c2c/infra/tf-test/"><br>
      Git commit:<input type=text name=git_commit value="aabc4578d"><br>
      CI URL :<input type=text name=git_commit value="http:gitlab/job/2332"><br>
      Source:<input type=text name=source value="local test"><br>
      Generation date: <input type=text name=generation_date value="2020-06-22T14:44:12+02:00"><br>
      Json Plan: <input type=file name=plan><br>
      PSK: <input type=text name=psk><br>
      <input type=submit value=Upload>
    </form>
    '''
if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0')
