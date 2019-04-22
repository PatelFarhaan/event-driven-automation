import threading
from common_utils.common_files import main_process


def main_dict():
    threads = []
    event_details_all = []

    with open('sites/doattend/event_details.txt', 'r') as f:
        event_details = f.readlines()

    for i in event_details:
        temp = i.replace('\n', '')
        temp = tuple(temp.split(','))
        event_details_all.append(temp)

    if event_details_all == []:
        return False

    else:
        response = [None] * len(event_details_all)

        for index, j in enumerate(event_details_all):
            event_id = int(j[0])
            site_id = int(j[1])
            t = threading.Thread(target=main_process,args=(event_id, site_id, response, index))
            threads.append(t)
            t.start()

        for k in threads:
            k.join()

        return response