# Do not name this file calendar.py, as it will cause a conflict with a file in the googleapiclient.discovery library
# For reference: https://developers.google.com/calendar/quickstart/python

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# I will setup class / init stuff later. This is just a proof of concept project so far.
# This essentially uses the Google Calendar API to access the official sjcadets.org Calendar
class Calendar:
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self):
        pass

    def get_date_events(day, month, year):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the SJHS calendar.
        """
        
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        requested_date = datetime.datetime(year=year, month=month, day=day)
        lower_bound = requested_date.isoformat() + 'Z' # 'Z' indicates UTC time
        upper_bound = (requested_date + datetime.timedelta(days=1)).isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=lower_bound, timeMax=upper_bound,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if int(start[8:10]) == day:
                print(start, event['summary'])

if __name__ == '__main__':
    Calendar.get_date_events(22,12,2020)

# Todo:
# Format into JSON response that includes data such as isMaroonDay and events and games
