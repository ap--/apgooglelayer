# -*- coding: utf-8 -*-

def listcalendars(service, http=None):
    page_token=None
    ret = {}
    while True:
        clist = service.calendarList().list(pageToken=page_token, fields='items(id,summary)').execute(http=http)
        if clist['items']:
            for clist_entry in clist['items']:
                ret[clist_entry['summary']] = clist_entry['id']
        page_token = clist.get('nextPageToken')
        if not page_token:
            break
    return ret


class GoogleCalendar(object):

    def __init__(self, service, name=None):
        self.service = service
        self.calendarName = name
        if name is not None:
            self.calendarId = self.getcalendarid()
        else:
            self.calendarId = None

    def _findcalendarid(self, name=None):
        if name is not None:
            pass
        elif self.calendarName is not None:
            name = self.calendarName
        else:
            raise ValueError('provide name, or set calendarName')
        
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
    
    def listcalendars(self, http=None, key=None):
        page_token=None
        ret = {}
        while True:
            clist = self.service.calendarList().list(pageToken=page_token).execute(http=http)
            if clist['items']:
                for clist_entry in clist['items']:
                    if key == 'id':
                        ret[clist_entry['id']] = clist_entry['summary']
                    else:
                        ret[clist_entry['summary']] = clist_entry['id']
            page_token = clist.get('nextPageToken')
            if not page_token:
                break
        return ret
        


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


    def iterevents(self, **x):
        http = x.pop('http', None)
        if self.calendarId is None:
            raise ValueError('please set calendarId')
        page_token = None
        while True:
            events = self.service.events().list(calendarId=self.calendarId,
                                    pageToken=page_token, **x).execute(http=http)
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
        if self.calendarId is None:
            raise ValueError('please set calendarId')
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
        if self.calendarId is None:
            raise ValueError('please set calendarId')
        self.service.events().insert(calendarId=self.calendarId,
                                     body=event).execute()

    def deleteevent(self, eventid):
        if self.calendarId is None:
            raise ValueError('please set calendarId')
        self.service.events().delete(calendarId=self.calendarId,
                                    eventId=eventid).execute()

    
    def get_events_from_calendar(self, calendarId, http):
        old = self.calendarId
        self.calendarId = calendarId
        EVENTS={}
        for ev in self.iterevents(http=http,
                fields="items(id,start,recurrence,location,summary,description)"):
            _id = ev.pop('id')
            EVENTS[_id] = ev
        self.calendarId = old
        return EVENTS

