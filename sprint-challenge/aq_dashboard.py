from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)
api = openaq.OpenAQ()

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


@APP.route('/')
def root():
    """Base view."""
#    status, body=api.measurements(city='Los Angeles', parameter='pm25')
#    result=[]
#    for x in range(len(body['results'])):
#        check_value=body['results'][x]['value']
#        if check_value >=10:
#            tuple=(body['results'][x]['date']['utc'],body['results'][x]['value'])
#            result.append(tuple)
    """From DB instead of API"""
    result = Record.query.filter(Record.value >= 10).all()
    return render_template('home.html', title='Risky', result=result)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return 'Time {} --- Value {}'.format(self.datetime, self.value)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    result = []
    for x in range(len(body['results'])):
        result.append(body['results'][x]['date']['utc'])
        add_record = Record(
                           id=x, datetime=body['results'][x]['date']['utc'],
                           value=body['results'][x]['value'])
        DB.session.add(add_record)
    DB.session.commit()
    return 'Data refreshed!'
