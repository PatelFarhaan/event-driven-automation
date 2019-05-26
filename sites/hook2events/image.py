import urllib
from urllib.request import urlopen
from sites.eventhigh.main_resp import main_dict


resp_data = main_dict()
image_file = 'sites/eventhigh/temp_images/temp_image.png'


def download_media_file():
    if resp_data:
        urllib.request.urlretrieve(
            'https://ercess.com'+resp_data[0]['event info'][0]['profile image'], image_file)
        return True
    else:
        return False
