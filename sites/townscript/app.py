import os
import sys
import subprocess

sys.path.append('/media/hp/New Volume/Users/hp/personal/main_events/sites/townscript/temp')
import json
import random
import requests
from pprint import pprint
from datetime import datetime

# IMG_LOCATION = '/media/hp/New Volume/Users/hp/personal/main_events/sites/townscript/temp'
IMG_LOCATION = '/var/www/html'


class Townscript():

    def __init__(self, TOWNSCRIPT_INFO):
        self.TOWNSCRIPT_INFO = TOWNSCRIPT_INFO
        self.session = requests.Session()
        self.current_url = 'https://www.townscript.com/signin'
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.61 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.current_url,
            'Connection': 'stay-alive'
        }
        self.user_details = {}
        self.event_creation_error = {}
        self.success_events = []
        self.event_published = False
        self.event_url = None
        self.field_types = {
            'text': 'TEXT',
            'paragraph': 'PARAGRAPH_TEXT',
            'dropdown': 'LIST',
            'number': 'TEXT',
            'date': 'CALENDAR'
        }

    # login
    def login(self):
        login_referral = 'https://www.townscript.com/signin'
        credentials = self.TOWNSCRIPT_INFO['credentials']
        # preparing body
        data = {'emailId': credentials['email'], 'password': credentials['password']}
        login_res = self.session.post("https://www.townscript.com/api/user/loginwithtownscript", data=data)
        # eval response

        login_res = json.loads(login_res.text)
        # login_res = eval(login_res.text)
        if login_res['result'] == 'Success':
            self.session.headers['Authorization'] = login_res['data']
            self.user_details = login_res['userDetails']
        else:
            raise Exception(login_res['data'])

    def date_formatter(self, date, time):
        try:
            import dateparser
            date = dateparser.parse(date).strftime('%Y-%m-%d')
            return dateparser.parse('{} {}'.format(date, time)).strftime("%Y-%m-%dT%H:%M:%S.000+0530")
        except:
            try:
                return datetime.strptime('{} {}'.format(date, time), '%Y-%m-%d %H:%M %p').strftime(
                    "%Y-%m-%dT%H:%M:%S.000+0530")
            except:
                return datetime.strptime('{} {}'.format(date, time), '%Y-%m-%d %H:%M:%S %p').strftime(
                    "%Y-%m-%dT%H:%M:%S.000+0530")

    # create-event
    def create_event(self):

        events = self.TOWNSCRIPT_INFO['events']
        # import ipdb; ipdb.set_trace()
        for event in events:
            request_data = {
                "isRecurrent": False,  # repeating event
                "live": False,
                "draft": True,
                "stepNumber": 2,
                "eventCreatorId": self.user_details['userId'],
                "startTime": self.date_formatter(event['start date'], event['start time']),
                "endTime": self.date_formatter(event['end date'], event['end time']),
                "name": event['event name'],
                "isPublic": True,  # public or private event
                "organizerName": self.user_details['user'],
                "eventTimeZone": None,
                "shortName": '{}-{}'.format(event['event name'][:20].replace(" ", "-").lower(),
                                            random.randint(1, 99999999))
            }

            # step1 - name and event daterange
            data = {
                "dewa_json_data": json.dumps(request_data),
                "eventtype": "0",
                "rrulePattern": "None",
                "timeSlots": "[]"
            }
            self.session.headers['Referer'] = 'https://www.townscript.com/dashboard/events'
            event_res = self.session.post('https://www.townscript.com/api/eventdata/add', data=data)
            event_res = json.loads(event_res.text)
            if event_res['result'] != 'Success':
                self.event_creation_error[event['event name']] = event_res[
                    'message'] if 'message' in event_res else 'Error'
                continue

            # step2 - venue
            request_data['stepNumber'] = 3
            request_data['id'] = event_res['Id']
            # TODO:: ONLINE EVENT HANDLING
            request_data['onlineEvent'] = False
            request_data["venueLocation"] = event['address 1']
            request_data["addressLine1"] = event['address 2']
            request_data["addressLine2"] = ''
            request_data["city"] = event['city']
            request_data["country"] = event['country']
            request_data["venueState"] = event['state']
            request_data["pinCode"] = event['pincode']
            request_data["latitude"] = event['latitude'] if 'latitude' in event and event['latitude'] else 72.0
            request_data["longitude"] = event['longitude'] if 'longitude' in event and event['longitude'] else 80.0
            request_data["isVenueTBD"] = False
            request_data["onlineEventLink"] = None
            request_data["description"] = event['description']

            update_data = {
                'dewa_json_data': json.dumps(request_data),
                'eventtype': '0'
            }

            event_up_res = self.session.post("https://www.townscript.com/api/eventdata/update", data=update_data)
            event_up_res = json.loads(event_up_res.text)
            # event_up_res = eval(event_up_res.text)
            if event_up_res['result'] != 'Success':
                self.event_creation_error[event['event name']] = event_up_res[
                    'message'] if 'message' in event_up_res else 'Error'
                continue

            # step3 - Event Tags
            tags = self.session.get(
                "https://www.townscript.com/api/eventdata/generatetopicsandeventtype?id={}".format(event_res['Id']))
            eventtypes = self.session.get("https://www.townscript.com/api/eventdata/loadallkeywordsandeventtypes")
            event_type_id = None
            # import ipdb; ipdb.set_trace()
            if eventtypes.status_code == 200:
                eventtypes_all_data = json.loads(eventtypes.text)
                eventtypes_data = eventtypes_all_data['data']
                eventtypes_eventtypes = json.loads(json.loads(eventtypes_data)['eventtypes'])[0]
                event_type_id = [eventtypes_eventtypes['id']]

            data = {"dewa_json_data": json.dumps(
                {"keywords": json.loads(json.loads(tags.json()['data'])['keywords']), "eventid": event_res['Id'],
                 "eventTypeId": event_type_id[0] if event_type_id else
                 json.loads(json.loads(tags.json()['data'])['eventtype'])['id'], 'isUpdate': False})}
            event_type = self.session.post("https://www.townscript.com/api/eventdata/addorupdatetopicsandeventtype",
                                           data=data)
            draftstatus = self.session.post("https://www.townscript.com/api/eventdata/updatedraftstatus",
                                            data={"id": event_res['Id'], "draft": True, "stepNumber": 5})

            # step4 - Upload photos
            # check path
            event['banner'] = event['banner'].strip()
            banner_path = '{}/{}'.format(IMG_LOCATION, event['banner'].strip())
            if not os.path.exists(banner_path):
                banner_path = '{}'.format(event['banner'])
                if not os.path.exists(banner_path):
                    self.event_creation_error[event['event name']] = '{} Does not exists'.format(banner_path)
                    continue

            banner_res = self.session.post('https://www.townscript.com/api/eventdata/upload-event-image',
                                           files={'file': open(banner_path, 'rb')},
                                           data={'eventId': event_res['Id'], 'imageType': 'cover'})

            if banner_res.status_code != 200:
                self.event_creation_error[event['event name']] = event_up_res[
                    'message'] if 'message' in event_up_res else 'Error while uploading Image'
                continue

            if event['profile image']:
                event['profile image'] = event['profile image'].strip()
                profile_path = '{}{}'.format(IMG_LOCATION, event['profile image'].strip())
                if not os.path.exists(profile_path):
                    profile_path = '{}'.format(event['profile image'])
                    if not os.path.exists(profile_path):
                        self.event_creation_error[event['event name']] = '{} Does not exists'.format(profile_path)
                        continue

                try:
                    profile_res = self.session.post('https://www.townscript.com/api/eventdata/upload-event-image',
                                                    files={'file': open(profile_path, 'rb')},
                                                    data={'eventId': event_res['Id'], 'imageType': 'card'})
                    profile_res = json.loads(profile_res.text)
                    # profile_res = eval(profile_res.text)
                    if profile_res['result'] != "Success":
                        self.event_creation_error[event['event name']] = event_up_res[
                            'message'] if 'message' in event_up_res else 'Error while uploading Image'
                        continue
                except:
                    pass

            draftstatus = self.session.post("https://www.townscript.com/api/eventdata/updatedraftstatus",
                                            data={"id": event_res['Id'], "draft": True, "stepNumber": 6})

            # Tickets
            tickets = self.TOWNSCRIPT_INFO['tickets']
            # print(type(self.TOWNSCRIPT_INFO), self.TOWNSCRIPT_INFO)
            # print(type(event), event)
            for ticket in tickets:
                if 'ticket name' in ticket:
                    ticket_data = {"dewa_json_data": json.dumps({
                        "eventId": event_res['Id'],
                        "userId": self.user_details['userId'],
                        "ticketName": ticket['ticket name'],
                        "minQuantity": ticket['minimum quantity'],
                        "maxQuantity": ticket['maximum quantity'],
                        "totalTickets": ticket['ticket quantity'],
                        "ticketType": "NORMAL",
                        "currency": 'INR',
                        "ticketPrice": ticket['ticket price'],
                        "startDate": self.date_formatter(ticket['ticket start date'], ticket['ticket start time']),
                        "endDate": self.date_formatter(ticket['expiry date'], ticket['expiry time']),
                        "ticketDescription": ticket['ticket message'],
                        "orgTaxCharge": 0,
                        "addOn": False,
                        "paymentChargeOption": 0,
                        "ticketStatus": 0,
                        "ticketPosition": 1,
                    })
                    }

                    ticket_res = self.session.post("https://www.townscript.com/api/ticket/add", data=ticket_data)
                    ticket_res = json.loads(ticket_res.text)
                    # ticket_res = eval(ticket_res.text)
                    if ticket_res['result'] != "Success":
                        self.event_creation_error[event['event name']] = "Error in ticket creation."
                        continue

            # update draft status
            draftstatus = self.session.post("https://www.townscript.com/api/eventdata/updatedraftstatus",
                                            data={"id": event_res['Id'], "draft": False, "stepNumber": 7})

            # add forms
            attendee_form = self.TOWNSCRIPT_INFO['attendee_form']
            metadata = self.session.get(
                "https://www.townscript.com/api/registrationmetadata/get?id={}".format(event_res['Id']))
            metadata_id = json.loads(eval(metadata.text)['data'])['id']
            for idx, field in enumerate(attendee_form):
                FORM_URL = 'https://www.townscript.com/api/forms/add'
                form_data = {
                    "dewa_json_data":
                        json.dumps({"eventId": event_res['Id'],
                                    "metadataId": metadata_id,
                                    "questionPosition": idx,
                                    "fieldPriority": "INCLUDE",
                                    "ticketType": "ALL",
                                    "questionTicketMap": [{"ticketId": ticket_res['Id'], "eventId": event_res['Id'],
                                                           "userId": self.user_details['userId']}],
                                    "caption": field['question title'],
                                    "questionType": self.field_types[field['name']],
                                    "userId": self.user_details['userId']
                                    })
                }
                form_res = self.session.post(FORM_URL, data=form_data)

            # create-event
            finish_res = self.session.post("https://www.townscript.com/api/registrationmetadata/finish-event-create",
                                           data={"id": event_res['Id'], "dewa_json_data": json.dumps([])})
            finish = eval(finish_res.text)
            if finish['result'] != 'Success':
                self.event_creation_error[event['event name']] = "Error Occur while submitting event."
                continue

            self.success_events.append(event['event name'])
            # draftstatus = self.session.post("https://www.townscript.com/api/eventdata/updatedraftstatus", data={"id": event_res['Id'], "draft": False, "stepNumber": 8})

            # publish event
            is_publish_res = self.session.get(
                'https://www.townscript.com/api/eventdata/publish?id={}&value=true'.format(event_res['Id']))
            is_publish_res = json.loads(is_publish_res.text)
            # is_publish_res = eval(is_publish_res.text)
            if is_publish_res['result'] == 'Success':
                self.event_published = True
                self.event_url = 'https://www.townscript.com/e/{}'.format(request_data['shortName'])
            else:
                self.event_published = False

    def update_event_in_db(self, table_id):

        if self.event_published:
            update_db = '/var/www/html/crons/event_posting/manual/update_db.py'
            try:
                # URL, table_id, promotion_status, partner_status
                cmd = ['python3', update_db, self.event_url, table_id, 'published', 'approved']
                subprocess.call(cmd)
            except:
                print("Error occured while updating database")

    def process(self, table_id):

        # login
        self.login()

        # create-event
        self.create_event()

        # check parameters for database
        self.update_event_in_db(table_id)

        print("Events Created Successfully")
        pprint(self.success_events)

        print("Error in Event Creation")
        pprint(self.event_creation_error)

        print("URL: {}".format(self.event_url))