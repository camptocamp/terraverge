import json
import os
from flask import Flask, flash, request, redirect, url_for
from sqlalchemy import create_engine, Table, Column, DDL, event, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)

pghost = os.getenv('PGHOST', 'localhost')
pgport = os.getenv('PGPORT', '5432')
pgdatabase = os.getenv('PGDATABASE', 'terraverge')
pguser = os.getenv('PGUSER', 'terraverge')
pgpassword = os.getenv('PGPASSWORD', 'terraverge')

engine = create_engine('postgresql://%s:%s@%s:%s/%s' %
                       (pguser, pgpassword, pghost, pgport, pgdatabase))

Base = declarative_base()


class Plan(Base):
     __tablename__ = 'plan'

     id = Column(Integer, primary_key=True)
     workspace_url = Column(String)
     plan = Column(JSON)
     update_count = Column(Integer)
     noop_count = Column(Integer)

     def __repr__(self):
        return "<Plan(url='%s', updates='%s', noop='%s')>" % (
            self.workspace_url, self.update_count, self.noop_count)

     def computeChanges(self):
         updates = []
         reads = []
         for change in self.plan['resource_changes']:
             action = change['change']['actions'][0]
             if action == 'no-op':
                 continue
             elif action == 'read' :
                 reads.append(change['change'])
             elif action == 'update':
                 updates.append(PlanUpdate(change['change']))
                 print(change)
             else:
                 raise Exception('Unknow action : %s' % action)
         return 'ok'


class PlanUpdate:

    def __init__(self, change):
        self.change = change
        self.before = change['before']
        self.after = change['after']

    def diff(self):
        diffs = {}
        for key in union(self.before.keys(), self.after.keys()):
            before = self.before[key]
            after = self.after[key]
            diffs[key] = diff(before, after)



# update_task_state = DDL('''\
# CREATE TRIGGER update_task_state UPDATE OF state ON obs
#   BEGIN
#     UPDATE task SET state = 2 WHERE (obs_id = old.id) and (new.state = 2);
#   END;''')
# event.listen(Plan.__table__, 'after_create', update_task_state)


from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()
# mytable = Table(
#     'mytable', metadata,
#     Column('id', Integer, primary_key=True),
#     Column('data', String(50))
# )
#
# trigger = DDL(
#     "CREATE TRIGGER dt_ins BEFORE INSERT ON mytable "
#     "FOR EACH ROW BEGIN SET NEW.data='ins'; END"
# )
#
# event.listen(
#     mytable,
#     'after_create',
#     trigger.execute_if(dialect='postgresql')
# )

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
        if file:
            plan = Plan(plan=json.loads(file.read()))
            s.add(plan)
            s.commit()
            return 'ok'
    return '''
    <!doctype html>
    <title>Upload terraform plan</title>
    <h1>Upload new Plan</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=plan>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/diff')
def diff_plan():
    plans = s.query(Plan).all()
    output  ='''
    <!doctype html>
    <title>Upload terraform plan</title>
    <h1>Diff</h1>'''
    for plan in plans:
      json = plan.plan
      print(plan.computeChanges())


    output += ''''''
    return output
