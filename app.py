# Simple flask app to return JSON of calendar API
from flask import Flask, jsonify
from cal import CalendarEvents

app = Flask(__name__)

@app.route('/')
def landing_page():
    return """Please format API requests as /day/month/year/, 
    with each being represented as a number. For example, 
    December 22, 2020 would be formatted as /22/12/2020/ """

@app.route('/<int:day>/<int:month>/<int:year>')
def get_events(day, month, year):
    events = CalendarEvents(day, month, year).get_event_dictionary()
    return jsonify(events)

if __name__ =='__main__':
    app.run(debug=True)