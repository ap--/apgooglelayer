# -*- coding: utf-8 -*-

class GoogleCalendar(object):

    def __init__(self, service, name):
        self.service = service
        self.calendarName = name
        self.calendarId = self.getcalendarid()

    def _findcalendarid(self):
        page_token=None
        while True:
            clist = self.service.calendarList().list(pageToken=page_token).execute()
            if clist['items']:
                for clist_entry in clist['items']:
                    if clist_entry['summary'] == self.calendarName:
                        return clist_entry['id']
            page_token = clist.get('nextPageToken')
            if not page_token:
                return None


    def _addcalendar(self, summary, description, timezone):
        cl = { 'summary'     : summary,
               'description' : description,
               'timeZone'    : timezone,
               'reminders'   : {'useDefault' : False},
               'defaultReminders' : []}
        ret = self.service.calendars().insert(body=cl).execute()
        return ret['id']


    def getcalendarid(self):
        _id = self._findcalendarid()
        if _id is None:
            raise Exception('Please add calendar with name %s' % self.calendarName)
            _id = self._addcalendar()
        return _id


    def iterevents(self):
        page_token = None
        while True:
            events = self.service.events().list(calendarId=self.calendarId,
                                                pageToken=page_token).execute()
            try:
                events['items']
            except KeyError:
                return
            if events['items']:
                for event in events['items']:
                    yield event
            page_token = events.get('nextPageToken')
            if not page_token:
                return


    def addevent(self, date, summary, description, location, duration):
        start = date
        end = start + duration
        start = start.isoformat('T')
        end = end.isoformat('T')
        event = {
            'summary': summary,
            'start': { 'dateTime': start,
                       'timeZone': self.FCTIMEZONE },
            'end': { 'date': end,
                     'timeZone': self.FCTIMEZONE },
            'description' : description,
            'location' : location,
                }
        
        self.service.events().insert(calendarId=self.calendarId,
                                     body=event).execute()

    def addrawevent(self, event):
        self.service.events().insert(calendarId=self.calendarId,
                                     body=event).execute()





