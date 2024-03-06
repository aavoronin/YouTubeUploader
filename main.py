# https://www.youtube.com/watch?v=N5jMX6erNeo
"""
python.exe -m pip install --upgrade pip
pip install google-api-python-client
pip install google_auth_oauthlib
python -c "from apiclient.discovery import build;print(build)"



"""
import argparse
import json
import os
import time

from apiclient.discovery import build
from googleapiclient.errors import HttpError

print(build)

from Youtube_Uploader import YoutubeUploader, channels, lang_to_channel, language_dict

key_file = "c:/Data/API_KEY/aavoronin_api_key.txt"
with open(key_file, "r", encoding='utf-8') as f:
    API_KEY = f.readline()

y = YoutubeUploader(API_KEY)

#time.sleep(10)
#print(y.image_exists('images/limit_reaches.png', 0.95))
print(y.image_exists_test2())
#y.image_exists('images/Show_more.png', 0.95)
#y.detect_image4('images/Show_more.png', 0.95)
#for i in range(100):
#    threasold = 1.0 - 0.009 * i
#    #print(threasold, y.is_image_present('images/Schedule.jpg', threasold))
#    print(threasold, y.is_image_present('images/Show_more2.jpg', threasold))
#y.click_image('images/Show_more.png')
#y.press_until_show_more()
#y.click_next()

#y.py_autogi_upload("GeoStatisticsKo")
#y.py_autogi_upload("GeoStatisticsJp")
#y.py_autogi_upload("GeoStatisticsEn", 8)
#y.py_autogi_upload("GeoStatisticsGlobal", 11)

#y.scan_uploaded_videos("ru")
#y.scan_uploaded_videos("ja")
#y.scan_uploaded_videos("ko")
#y.scan_uploaded_videos("en")

#y.update_video_descriptions("en")
#y.update_video_descriptions("ja")
#y.update_video_descriptions("ko")
#y.update_video_descriptions("ru")


#y.update_video_descriptions2("en")
#y.update_video_descriptions2("ja")
#y.update_video_descriptions2("ko")
#y.update_video_descriptions2("ru")

#y.update_video_end_screens("en")
#y.update_video_end_screens("ja")
#y.update_video_end_screens("ko")
#y.update_video_end_screens("ru")



#time.sleep(8)
#y.click_next()
#y.get_videos_for_upload()
#y.get_video_inf("ecAzzYmb3Qg")
#y.upload_video(data)
#y.get_channel_videos(channels[lang_to_channel["ru"]])


#config = json.load(open('config.json'))
#youtube = build('youtube', 'v3', developerKey=API_KEY)
# #

