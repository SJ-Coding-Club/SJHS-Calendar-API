# I think a cool use for this API could be an LCD screen that scrolls through daily information 
# For reference on using Google's Calendar API with Python: https://developers.google.com/calendar/quickstart/python

import datetime
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# I will setup class / init stuff later. This is just a proof of concept project so far.
# This essentially uses the Google Calendar API to access the official sjcadets.org Calendar
class CalendarEvents:
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, day, month, year):
        self.event_dictionary = self.__prettify_payload(self.__get_date_events(day,month,year))
    
    def get_event_dictionary(self):
        return self.event_dictionary

    def __get_date_events(self,day, month, year):
        """Simulates basic usage of the Google Calendar API and
        returns all events for a given day on the SJHS Calendar. The Google Calendar
        its accessing has all of the current data from the SJ Calendar uploaded.
        (Also, I need to add the times of each event here. So I might actually merge this
        and the prettify functions into one.)
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
        print(f'Getting events for {str(requested_date)[:10]}')
        events_result = service.events().list(calendarId='primary', timeMin=lower_bound, timeMax=upper_bound,
                                            maxResults=15, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No events found.')
        event_payload = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if int(start[8:10]) == day:
                event_payload.append(event['summary'])
        event_payload.append(requested_date) # last item will ALWAYS be date
        return event_payload
    
    def __number_to_dayname(self,num):
        """Converts raw number from datetime weekday() function into 
        its appropriate verbal representation.
        """
        return {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}[num]

    def __get_schedule_number(self, date_object):
        """Retrieves SJ schedule number for a given day from a hard-coded json file.
        I.e., day 1, day 2, 7A, etc. 
        I still need to fill that out, THEN make another json with the schedules for each of the 1-7 days
        """
        schedule_numbers = json.load(open('schedule_numbers.json'))
        day, month, year = str(date_object.day), str(date_object.month), str(date_object.year)
        return schedule_numbers[year][month][day]
        

    def __prettify_payload(self, event_payload):
        """ Neatens up the raw list of events into a formatted dictionary.
        Todo: Add more attributes to look for / classify. Some options could 
        be sports games / times, mass times, maybe look into club meeting times.
        """
        pretty_event_payload = {}

        events_to_remove = [] # Made this instead of indexing through list and subtracting 1 whenever an item is removed because i'm lazy
        for event in event_payload[0:-1]:
            if 'early dismissal' in event.lower():
                pretty_event_payload['early_dismissal'] = True
                events_to_remove.append(event)
            else:
                pretty_event_payload['early_dismissal'] = False
            
            if 'gold' in event.lower():
                pretty_event_payload['team_on_campus'] = 'gold'
                events_to_remove.append(event)
            elif 'maroon' in event.lower():
                pretty_event_payload['team_on_campus'] = 'maroon'
                events_to_remove.append(event)
        for event in events_to_remove:
            event_payload.remove(event)
        
        date_object = event_payload[-1] # access date stored at last index, as previously noted
        event_payload.remove(event_payload[-1])
        
        pretty_event_payload['weekday'] = self.__number_to_dayname(date_object.weekday())
        # pretty_event_payload['schedule_number'] = self.__get_schedule_number(date_object) NOT YET COMPLETED
 
        # Now add the rest of the events       
        pretty_event_payload['events'] = event_payload
        return pretty_event_payload

if __name__ == '__main__':
    day, month, year = [int(x) for x in input('Enter day month and year numbers, separated by spaces').split()]
    events = CalendarEvents(day=day,month=month,year=year).get_event_dictionary()
    print(events)
