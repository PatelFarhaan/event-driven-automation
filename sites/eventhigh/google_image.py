import urllib
from gcloud import storage
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


def implicit():
    resp = download_media_file()

    if resp:
        # bucket_name = 'farhaan_eventhigh'
        # object_name = 'obj_name'
        # client = storage.Client()
        # bucket = client.get_bucket(bucket_name)
        # blob = bucket.blob(object_name)
        # blob.upload_from_filename(filename=image_file, content_type='image/jpeg')
        # blob.make_public()
        # return blob.public_url
        return "gcloud acc"

    else:
        return False