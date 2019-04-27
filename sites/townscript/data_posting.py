import argparse
import threading
from sites.townscript.app import Townscript
from sites.townscript.main_resp import main_dict


main_json = main_dict()


def post_data(site_id):

    threads = []
    for i in main_json:
        t = threading.Thread(target=thread_mul, args=(site_id, i))
        threads.append(t)
        t.start()

    for j in threads:
        j.join()


def thread_mul(site_id, event=None):

    TOWNSCRIPT_INFO = {
        'credentials': {
            'email': 'agrawalsanket572@gmail.com',
            'password': 'Rejoice605@'
        },
        'events': event.get('event info', []),
        'tickets': event.get('tickets', []),
        'country_data': event.get('countries', {}),
        'attendee_form': event.get('attendee_questions', []),
        'category': event.get('category', None)
    }
    townscript = Townscript(TOWNSCRIPT_INFO)
    townscript.process(site_id)


def townscript_post_data():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        type=str,
        default="townscript",
        help="Name of platform where you want to publish event"
    )
    parser.add_argument(
        "--table_id",
        type=str,
        default="1",
        help="Platform ID to update event in database."
    )

    FLAGS, unparsed = parser.parse_known_args()

    if FLAGS.platform == 'townscript':
        post_data(FLAGS.table_id)