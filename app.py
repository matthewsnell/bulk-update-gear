import time

from flask import Flask, render_template, request, redirect, session, flash, url_for
import requests
from Forms import updateSettings
import os
import config
import werkzeug
from datetime import datetime, timedelta
from celery import Celery
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE']: 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)
app.static_folder = 'static'
EPOCH = datetime.utcfromtimestamp(0)
app.config['CELERY_BROKER_URL'] = config.CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = config.CELERY_RESULT_BACKEND

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)


def convert_to_epoch(dt):
    return (dt - EPOCH).total_seconds()


@app.errorhandler(werkzeug.exceptions.NotFound)
def page_not_found(e):
    return 'not found'


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_server_error(e):
    flash('Oops, something went wrong. Are you sure you granted the correct permissions?', 'danger')
    return redirect('/')

@celery.task
def update_gear(gear, before_date, after_date, headers):
    if gear[0] == 'b':
        activity_type = 'Ride'
    elif gear[0] == 'g':
        activity_type = 'Run'
    else:
        activity_type = None
    page_activities = ['Not empty']
    page_number = 1
    all_activities = []
    request_count = 2
    while page_activities:
        params = {
            'before': before_date,
            'after': after_date,
            'page': page_number,
            'per_page': 100
        }
        r = requests.get("https://www.strava.com/api/v3/athlete/activities", params=params,
                         headers=headers)
        if is_valid_request(r) != True:
            break
        page_activities = r.json()
        all_activities += page_activities
        request_count += 1
        page_number += 1

    for activity in all_activities:
        if activity["type"] == activity_type and activity['gear_id'] != gear:
            data = {
                'gear_id': gear
            }
            update_request = requests.put(url=f"https://www.strava.com/api/v3/activities/{activity.get('id')}",
                                          data=data, headers=headers)
            request_count += 1
            if is_valid_request(update_request) != True:
                break
            elif request_count > 505:
                break

def is_valid_request(r):
    if r.status_code == 200 or r.status_code == 201:
        return True
    elif 400 < r.status_code < 405:
        return 'Oops, looks like something went wrong. Are you sure you granted the correct permissions?'
    elif r.status_code == 429:
        return "Oops, we've hit our request limit from Strava. Try again in 15 minutes."
    elif r.status_code == 500:
        return "Oops, looks like Strava's having issues there end. Try again later."
    else:
        return "Oops, looks like something went wrong."


@app.route('/')
def home():
    print("session data at home: ", session)
    return render_template('home.html', return_url=config.url, url=config.url, client_id=config.client_id)


@app.route('/exchange_token')
def token_aquired():
    print("session data after strava redirect: ", session)
    print("checking token")
    if request.args.get('error') is not None:
        return redirect('/')

    r = requests.post(url="https://www.strava.com/oauth/token", params={'client_id': config.client_id,
                                                                    'client_secret': config.client_secret,
                                                                    'code': request.args.get('code'),
                                                                    'grant_type': 'authorization_code'})
    print("send request for access token")
    if is_valid_request(r) != True:
        flash(is_valid_request(r), 'danger')
        return redirect('/')
    print("success")
    session['headers'] = {"Authorization": f"Bearer { r.json()['access_token']}"}
    session.modified = True
    return redirect('/addGear')


@app.route('/addGear', methods=['GET', 'POST'])
def add_gear():
    print("sesion data at add gear: ", session)
    if session.get('headers') is None:
        flash('Something went wrong. Try again. If this persists, please get in touch.', 'danger')
        print("no access token redirecting")
        return redirect('/')
    r = requests.get("https://www.strava.com/api/v3/athlete", headers=session.get('headers'))
    if is_valid_request(r) != True:
        flash(is_valid_request(r), 'danger')
        print("invalid request")
        return redirect('/')
    bikes = r.json()["bikes"]
    shoes = r.json()["shoes"]
    form = updateSettings(request.form)
    form.gearselect.choices = [(item['id'], item['name']) for item in (bikes + shoes)]

    if request.method == 'POST':
        if form.validate_on_submit():
            before_date = form.before_date.data
            if before_date is not None:
                before_date = convert_to_epoch(datetime.strptime(before_date.isoformat(), "%Y-%m-%d"))
            after_date = form.after_date.data
            if after_date is not None:
                after_date = convert_to_epoch(datetime.strptime(after_date.isoformat(), "%Y-%m-%d"))
            gear = form.gearselect.data
            update_gear.delay(gear, before_date, after_date, session.get('headers'))
            return redirect('result')
        else:
            flash(form.errormessage, 'danger')
            return render_template('add_gear.html', form=form)

    return render_template('add_gear.html', form=form)



@app.route('/result')
def results():
    return render_template('results.html')


if __name__ == '__main__':
    app.run()
