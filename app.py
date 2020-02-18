from flask import Flask, render_template, request, jsonify, redirect, session
from classes import Strava, Toggls
import ast
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/')
def index():
    session['stravaurl'] = Strava().url
    return render_template("index.html", strava=session['stravaurl'])

@app.route('/authorization')
def returned():
    session['code'] = request.args['code']
    session['stravacode'] = Strava().get_access_token(session['code'])
    return render_template("returned.html")

@app.route('/table',  methods = ['POST'])
def table():
    session['days'] = request.form["days"]
    activities = Strava().get_activities(days = int(session['days']), code = session['stravacode'])
    session['key'] = request.form["key"]
    session['workspaces'] = []
    session['projects'] = {}
    session['workspaces1'] = Toggls(session['key']).get_Workspaces()
    session['workspaces'] = []
    for workspace in session['workspaces1']:
        session['workspaces'].append(workspace['name'])
        Plist = []
        try:
            for project in Toggls(session['key']).getprojectsinworkspace(workspace['id']):
                Plist.append(project['name'])
        except:
            pass
        session['projects'][workspace['name']] = Plist
    session['all_workouts'] = []
    for workout in activities:
        session['start_date'] = workout.start_date.strftime("%m/%d/%Y, %H:%M:%S")
        session['moving_time'] = str(workout.moving_time)
        worko = [workout.name, session['start_date'], session['moving_time']]
        session['all_workouts'].append(worko)
    session['all_workouts'].reverse()
    session['all_workspaces'] = list(session['projects'].keys())
    try:
        session['all_projects'] = session['projects'][list(session['projects'].keys())[0]]
    except:
        session['all_projects'] = ''
    return render_template("togglauth.html", all_workouts = session['all_workouts'], all_workspaces=session['all_workspaces'],
                           all_projects=session['all_projects'])

@app.route('/_update_dropdown')
def update_dropdown():

    # the value of the first dropdown (selected by the user)
    session['selected_workspace'] = request.args.get('selected_workspace', type=str)
    # get values for the second dropdown
    session['updated_projects'] = session['projects'][session['selected_workspace']]

    # create the value sin the dropdown as a html string
    session['html_string_selected'] = ''
    for entry in session['updated_projects']:
        session['html_string_selected'] += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=session['html_string_selected'])

@app.route('/process_entry')
def process_entry():
    session['selected_workspace'] = request.args.get('selected_workspace', type=str)
    session['selected_project'] = request.args.get('selected_project', type=str)
    session['selected_workout'] = request.args.get('selected_workout', type=str)
    session['id'] = int(Toggls(session['key']).get_workspace(session['selected_workspace'])['id'])
    session['projects'] = Toggls(session['key']).getprojectsinworkspace(session['id'])
    for project in session['projects']:
        if project['name'] == session['selected_project']:
            print(Toggls(session['key']).make_time_entry(pid=project['id'], workout=ast.literal_eval(session['selected_workout'])))
    return redirect("success")

@app.route('/success')
def success():
    return render_template("success.html")

if __name__ == '__main__':
    app.run(debug=True)
