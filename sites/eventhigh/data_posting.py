import json
import threading
from sites.eventhigh.login_crawl import login
from sites.eventhigh.update_db import get_event_id
from sites.eventhigh.data_formation import formed_data


def multi_thread_posting(payload, sess):

        headers = {
            'Origin': 'https://organizer.eventshigh.com',
            'Content-Type': 'application/json;charset=UTF-8',
            'DNT': '1',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': 'Bearer ***REMOVED_JWT_TOKEN***'
        }

        url = 'https://ticketing.eventshigh.com/_ah/api/events/v4/update'
        # import ipdb; ipdb.set_trace()
        response = sess.put(url=url, data=json.dumps(payload), headers=headers)
        print(response.status_code)
        if response.status_code == 204:
            resp = get_event_id(payload['title'])
            print(resp)

        print("EventHigh Processing Done!!!")


def eventhigh_post_data():
    threads = []
    resp, sess = login()
    payloads = formed_data()

    # print(payloads)

    if payloads:
        if resp.status_code == 200:
            for i in payloads:
                t = threading.Thread(target=multi_thread_posting, args=(i, sess))
                threads.append(t)
                t.start()

            for j in threads:
                j.join()
    else:
        print("No Events for EventHigh!!!")