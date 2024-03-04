import shutil
import webbrowser
import cv2
import numpy as np
import locale

# Nono Martínez Alonso -
# youtube.com/@NonoMartinezAlonso
# https://github.com/youtube/api-samples/blob/master/python/upload_video.py

import argparse
import hashlib
import json
from datetime import datetime, timedelta
from http import client
import httplib2
import os
import random
import time
import glob
import pandas as pd
import re

import google.oauth2.credentials
import google_auth_oauthlib.flow
import keyboard as keyboard
import pyautogui as pyautogui
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from action_logger import action_logger
from collections import OrderedDict

uploaded_info_folder = f"c:/Video/api/"

channel_to_date = {
    "GeoStatisticsEn": datetime.strptime("2024-03-22T18", "%Y-%m-%dT%H"),
    "GeoStatisticsJp": datetime.strptime("2024-03-11T23", "%Y-%m-%dT%H"),
    "GeoStatisticsKo": datetime.strptime("2024-03-08T23", "%Y-%m-%dT%H"),
    "GeoStatisticsGlobal": datetime.strptime("2024-03-14T03", "%Y-%m-%dT%H"),
}


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected,
                        client.IncompleteRead, client.ImproperConnectionState,
                        client.CannotSendRequest, client.CannotSendHeader,
                        client.ResponseNotReady, client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'C:/Data/API_KEY/client_secret_886028448607-8ohhhll49db18mese4k3bsftqqdd769a.apps.googleusercontent.com.json'

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube.force-ssl']

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

channels = {
    "GeoStatisticsEn": "UCdKcjHryHRhm5Agr3Tnnh7Q",
    "GeoStatisticsJp": "UCRo6d5bODQUKvPG9AXxEnQw",
    "GeoStatisticsKo": "UCO4JMJinfPyFB5vtaKbVReQ",
    "GeoStatisticsGlobal": "UCebUiRqbIjS4F-7p-49fQxA",
}

lang_to_channel = {
    "en": "GeoStatisticsEn",
    "ja": "GeoStatisticsJp",
    "ko": "GeoStatisticsKo",
    "pl": "GeoStatisticsGlobal",
    "cs": "GeoStatisticsGlobal",
    "de": "GeoStatisticsGlobal",
    "es": "GeoStatisticsGlobal",
    "fr": "GeoStatisticsGlobal",
    "it": "GeoStatisticsGlobal",
    "ru": "GeoStatisticsGlobal",
    "th": "GeoStatisticsGlobal",
    "vi": "GeoStatisticsGlobal",
    "ar": "GeoStatisticsGlobal",
    "pt": "GeoStatisticsGlobal",
}

lang_dict = OrderedDict(
{
    "en": "English (English)",
    "ja": "日本語 (Japanese)",
    "ko": "한국인 (Korean)",
    "ru": "Русский (Russian)",
    "es": "Español (Spanish)",
    "de": "Deutsch (German)",
    "fr": "Français (French)",
    "it": "Italiano (Italian)",
    "pt": "Português (Portuguese)",
    "vi": "Tiếng Việt (Vietnamese)",
    "th": "แบบไทย (Thai)",
    "pl": "Polski (Polish)",
    "cs": "čeština (Czech)",
    "ar": "عربي (Arabic)",
})

DELAY = 0.5

from datetime import datetime, timedelta


def pub_date(d, dd, h):
    # Ensure d is a datetime object
    if isinstance(d, str):
        d = datetime.strptime(d, '%Y-%m-%d')

    # Add dd days to the date and set the hour
    target_date = d + timedelta(days=dd)
    target_hour = datetime(target_date.year, target_date.month, target_date.day, h)

    return target_hour



def format_date_russian(date):
    # Set the locale to Russian
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    # Format the datetime object into a string with the desired format
    formatted_date = date.strftime("%d %B %Y г.")

    return formatted_date

def format_date_english(date):
    # Set the locale to Russian
    locale.setlocale(locale.LC_TIME, 'en_EN.UTF-8')

    # Format the datetime object into a string with the desired format
    formatted_date = date.strftime("%b %d, %Y")

    return formatted_date

def format_time_english(date):
    # Set the locale to Russian
    locale.setlocale(locale.LC_TIME, 'en_EN.UTF-8')

    # Format the datetime object into a string with the desired format
    formatted_date = date.strftime("%I:%M %p")

    return formatted_date

language_dict = {
    "en": "English (United States)",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "es": "Spanish (Spain)",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "vi": "Vietnamese",
    "th": "Thai",
    "pl": "Polish",
    "cs": "Czech",
    "ar": "Arabic"
}

class YoutubeUploader:
    def __init__(self, key):
        self.log_action = action_logger()
        self.api_key = key
        self.service = None
        self.next_pub_date = pub_date(datetime.now(), 2, 9)

    def get_authenticated_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server()
        self.service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    def upload_video(self, data):
        body = data["request_body"]
        file_name = data["video_file_name"]
        lang = body["snippet"]["defaultLanguage"]
        self.upload_video_core(body, file_name, lang)

    def upload_video_core(self, body, file_name, lang):
        print(f'uploading {file_name}')
        print(json.dumps(body, indent=4))

        if self.service is None:
            self.get_authenticated_service()

        insert_request = self.service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            # The chunksize parameter specifies the size of each chunk of data, in
            # bytes, that will be uploaded at a time. Set a higher value for
            # reliable connections as fewer chunks lead to faster uploads. Set a lower
            # value for better recovery on less reliable connections.
            #
            # Setting 'chunksize' equal to -1 in the code below means that the entire
            # file will be uploaded in a single HTTP request. (If the upload fails,
            # it will still be retried where it left off.) This is usually a best
            # practice, but if you're using Python older than 2.6 or if you're
            # running on App Engine, you should set the chunksize to something like
            # 1024 * 1024 (1 megabyte).
            media_body=MediaFileUpload(file_name, chunksize=-1, resumable=True),

        )
        self.resumable_upload(insert_request)

    def resumable_upload(self, request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print('Uploading file...')
                status, response = request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print('Video id "%s" was successfully uploaded.' %
                              response['id'])
                    else:
                        exit('The upload failed with an unexpected response: %s' % response)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = 'A retriable error occurred: %s' % e

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit('No longer attempting to retry.')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print('Sleeping %f seconds and then retrying...' % sleep_seconds)
                time.sleep(sleep_seconds)

    def get_videos_for_upload(self):
        # Specify the directory you want to traverse
        directory = "c:/Video/UploadData/"

        # Use glob to match the pattern '*.inf'
        for filename in glob.glob(directory + '/*.inf'):
            with open(os.path.join(directory, filename), 'r') as file:
                # Load JSON data from file
                data = json.load(file)
                body = data["request_body"]
                file_name = data["video_file_name"]
                lang = body["snippet"]["defaultLanguage"]
                channel_name, channel_code = self.get_channel_for_lang(lang)
                if channel_code is None:
                    print(f"skipping {file_name}")
                    continue

                if channel_name not in channel_to_date:
                    print(f"skipping {file_name}")
                    continue
                #date_to_publish = datetime.strptime(channel_to_date[channel_name], "%Y-%m-%dT%H:%M:%S.%fZ")
                date_to_publish = channel_to_date[channel_name]
                #date_to_publish =  date_to_publish.replace('000.000Z', '.000Z')
                date_to_publish = datetime.strptime(date_to_publish, "%Y-%m-%dT%H")
                #datetime.strptime(date_to_publish, "%Y-%m-%dT%H:%M:%S.%fZ")
                body["status"]["publishAt"] = date_to_publish.strftime("%Y-%m-%dT%H:%M:%SZ")
                del body["status"]["publishAt"]
                body["status"]["publicStatsViewable"] = False
                body["snippet"]["channelId"] = channel_code

                channel_to_date[channel_name] = (date_to_publish + timedelta(days=1)).strftime("%Y-%m-%dT%H")

                self.upload_video_core(body, file_name, lang)

    def get_channel_for_lang(self, lang):
        if lang not in lang_to_channel:
            return None, None
        channel_name = lang_to_channel[lang]
        if channel_name not in channels:
            return None, None
        channel_code = channels[channel_name]
        return channel_name, channel_code

    def scan_uploaded_videos(self, lang):

        channel_id = channels[lang_to_channel[lang]]
        #channel_id = channels[lang_to_channel["ru"]]
        #channel_id = channels[lang_to_channel["en"]]
        #channel_id = channels[lang_to_channel["ko"]]
        #channel_id = channels[lang_to_channel["jp"]]

        self.get_channel_videos(channel_id)

    def get_channel_videos(self, channel_id):
        if self.service is None:
            self.get_authenticated_service()
        # Retrieve the latest videos from the channel
        request = self.service.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date"
        )
        response = request.execute()
        # Process the video results
        videos = []
        for item in response["items"]:
            if "id" not in item:
                continue
            if "videoId" not in item["id"]:
                continue
            video_id = item["id"]["videoId"]
            inf = self.get_video_inf(video_id)
            print(inf)

    def get_video_inf(self, video_id):
        filename = video_id + '.inf'
        filepath = os.path.join(uploaded_info_folder, filename).replace("/", "\\")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                inf = f.read()
                f.close()
                return inf

        try:
            inf = self.get_video_inf_core(video_id)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(inf, f, ensure_ascii=True, indent=4)
        except Exception as e:
            pass

    def get_video_inf_core(self, video_id):

        channel_id = channels[lang_to_channel["ja"]]
        if self.service is None:
            self.get_authenticated_service()


        # Retrieve the latest videos from the channel
        request=self.service.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id,
        )
        response = request.execute()

        """
        # Extract all possible information from the response
        video_info = {
            "video_id": video_id,
            "title": response["items"][0]["snippet"]["title"],
            "description": response["items"][0]["snippet"]["description"],
            "tags": response["items"][0]["snippet"]["tags"],
            "category_id": response["items"][0]["snippet"]["categoryId"],
            "default_language": response["items"][0]["snippet"]["defaultLanguage"],
            "default_audio_language": response["items"][0]["snippet"]["defaultAudioLanguage"],
            "privacy_status": response["items"][0]["status"]["privacyStatus"],
            "publish_at": response["items"][0]["status"]["publishAt"],
            "self_declared_made_for_kids": response["items"][0]["status"]["selfDeclaredMadeForKids"],
            "license": response["items"][0]["status"]["license"],
            "embeddable": response["items"][0]["status"]["embeddable"],
            "public_stats_viewable": response["items"][0]["status"]["publicStatsViewable"],
            "duration": response["items"][0]["contentDetails"]["duration"],
            "view_count": response["items"][0]["statistics"]["viewCount"],
            "like_count": response["items"][0]["statistics"]["likeCount"],
            "dislike_count": response["items"][0]["statistics"]["dislikeCount"],
            "comment_count": response["items"][0]["statistics"]["commentCount"]
        }
        """
        return response["items"][0]

    def py_autogi_upload(self, channel, limit = 9999):
        # Specify the directory you want to traverse
        directory = "c:/Video/UploadData/"
        move_to_directory = "c:/Video/UploadData/upload_2024/"

        c = 0
        # Get a list of all .inf files in the directory
        inf_files = glob.glob(directory + '/*.inf')
        # Get the creation time of each file and sort the files based on these times
        sorted_files = sorted(inf_files, key=os.path.getctime)
        df = pd.DataFrame(data=sorted_files, columns=["file_name"])
        df["created_time"] = df["file_name"].map(os.path.getctime)
        df["lang"] = df["file_name"].str[-10:-8]
        df['rank'] = df.sort_values(by=['lang', 'created_time'], ascending=[False, True]).groupby('lang').cumcount() + 1

        for i, row in df.iterrows():
            filename = row["file_name"]
            print(filename)

        for i, row in df.iterrows():
            filename = row["file_name"].replace("\\", "/")
            if channel not in channels.keys():
                print(f"channel {channels} not found")
                continue

            found = False
            for lang in lang_to_channel.keys():
                if filename.endswith(f"{lang}.mp4.inf"):
                    found = True
                    break

            if not found or lang_to_channel[lang] != channel:
                print(f"{filename} is not for {channel}")
                continue

            print(f"uploading {filename} to channel {channel}")
            file_name_full = os.path.join(directory, os.path.basename(filename))
            file_name_to = os.path.join(move_to_directory, os.path.basename(filename))
            with open(file_name_full, 'r') as file:
                # Load JSON data from file
                data = json.load(file)
                file.close()

            body = data["request_body"]
            video_file_name = data["video_file_name"]
            if os.path.getsize(video_file_name) < 10000:
                print(f'file too small {video_file_name}')
                continue

            lang = body["snippet"]["defaultLanguage"]
            channel_name, channel_code = self.get_channel_for_lang(lang)

            if channel_code is None:
                print(f"skipping {video_file_name}")
                continue

            if channel_name not in channel_to_date:
                print(f"skipping {video_file_name}")
                continue

            self.next_pub_date = channel_to_date[channel_name]
            channel_to_date[channel_name] = channel_to_date[channel_name] + timedelta(days=1)

            if not self.upload_autpgi(channel_code, video_file_name, body, self.next_pub_date):
                break

            shutil.move(file_name_full, file_name_to)
            self.log_action.log('uploaded_video', filename, datetime.strftime(self.next_pub_date, "%Y-%m-%d %H:%M:%S.%f"))
            print(f'uploaded video: {filename}')

            c += 1
            if c > limit:
                break

    def press_tab(self, n):
        for _ in range(n):
            pyautogui.press('tab')
            time.sleep(DELAY)
    def press_shift_tab(self, n):
        for _ in range(n):
            pyautogui.hotkey('shift', 'tab')
            time.sleep(DELAY)

    def upload_autpgi(self, channel_code, file_name, body, publication_date):
        title = body["snippet"]["title"]
        description = body["snippet"]["description"]
        lang = body["snippet"]["defaultLanguage"]
        upload_url = f"https://studio.youtube.com/channel/{channel_code}/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D"
        #upload_url = f"https://studio.youtube.com/channel/{channel_code}/videos/upload"
        #upload_url = f"https://studio.youtube.com/channel/{channel_code}/analytics/tab-overview/period-default"

        webbrowser.open(upload_url)
        time.sleep(5)

        if self.wrong_account():
            return False

        self.press_tab(1)
        time.sleep(DELAY)
        self.press_tab(1)
        time.sleep(DELAY)
        self.press_tab(1)
        pyautogui.press('enter')
        time.sleep(DELAY)

        time.sleep(5)
        keyboard.write(file_name)
        time.sleep(5)
        pyautogui.press('enter')
        time.sleep(10)

        if self.limit_reached():
            return False
        self.shift_right(100)

        keyboard.write(title)
        time.sleep(1)
        self.press_tab(2)

        keyboard.write(description, delay=0.01)
        #sleep_time = (os.path.getsize(file_name) // 1000 // 333) + 90
        #if sleep_time < 120:
        #    sleep_time = 120
        #time.sleep(sleep_time)
        while self.on_screen('images/Uploading.png'):
            time.sleep(5)
            print(f'{now().strftime("%Y-%m-%dT%H:%M:%SZ")} waiting, still uploading')

        time.sleep(15)
        print(f'sleeping {sleep_time}')
        self.press_tab(11)
        pyautogui.press('down')
        self.press_tab(2)
        pyautogui.press('enter')
        self.press_tab(9)
        time.sleep(3)

        for tag in body["snippet"]["tags"]:
            keyboard.write(tag)
            keyboard.write(",")
        time.sleep(10)
        self.press_tab(1)
        self.select_lang(lang)
        time.sleep(1)
        self.click_next()
        time.sleep(10)
        self.click_next()
        time.sleep(2)
        self.click_next()
        time.sleep(2)
        pyautogui.press('down')
        pyautogui.press('down')
        self.press_tab(3)
        pyautogui.press('enter')
        time.sleep(2)
        self.press_tab(1)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(5)
        self.enter_pub_date(publication_date)
        self.click_schedule()
        return True

    def shift_right(self, n):
        for _ in range(n):
            pyautogui.keyDown('shift')  # hold down the shift key
            pyautogui.press('right')  # press the right arrow key
            pyautogui.keyUp('shift')  # release the shift key

    def shift_left(self, n):
        for _ in range(n):
            pyautogui.keyDown('shift')  # hold down the shift key
            pyautogui.press('left')  # press the right arrow key
            pyautogui.keyUp('shift')  # release the shift key

    def enter_pub_date(self, publication_date):
        self.shift_left(20)
        keyboard.write(format_date_english(publication_date))
        pyautogui.press('enter')
        time.sleep(2)
        self.press_tab(4)
        print(format_time_english(publication_date))
        for _ in range(10):
            pyautogui.press('right')
        self.shift_left(20)
        keyboard.write(format_time_english(publication_date))
        self.press_tab(1)

        #time.sleep(0.2)
        #pyautogui.press('enter')
        pass


    def select_lang(self, lang):
        pyautogui.press('enter')
        time.sleep(3)
        """
        if lang == "en":
            keyboard.write("А")
            for _ in range(13):
                pyautogui.press('down')
                time.sleep(0.1)
        elif lang == "ja":
            keyboard.write("Я")
            for _ in range(1):
                pyautogui.press('down')
                time.sleep(0.1)
        """
        l, c = self.find_language_position(lang)
        keyboard.write(l)
        for _ in range(c):
            pyautogui.press('down')
            time.sleep(0.1)
        pyautogui.press('enter')

    def detect_image(self, image_file_name):
        # Load the template image
        template = cv2.imread(image_file_name, 0)
        w, h = template.shape[::-1]
        center_x = None
        center_y = None
        while center_x is None:
            time.sleep(0.1)
            # Take a screenshot of the entire screen
            screenshot = np.array(pyautogui.screenshot())
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            # Perform template matching
            res = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.8) # Adjust the threshold value based on your requirement

            # Find the center of the matched area
            for pt in zip(*loc[::-1]):
                cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

            if pt is None:
                continue

            # Calculate the center of the matched area
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2

        return center_x, center_y

    def on_screen(self, image):
        try:
            center_x, center_y = self.detect_image(image)
            return True
        except Exception as e:
            return False


    def click_next(self):
        while True:
            try:
                center_x, center_y = self.detect_image('images/Next.png')
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                time.sleep(10)
                return
            except Exception as e:
                time.sleep(10)
                return

    def click_video_best(self):
        while True:
            try:
                center_x, center_y = self.detect_image('images/Video_best.png')
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                time.sleep(3)
                return
            except Exception as e:
                time.sleep(10)
                return

    def click_schedule(self):
        while True:
            try:
                center_x, center_y = self.detect_image('images/Schedule.png')
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                time.sleep(10)
                return
            except Exception as e:
                time.sleep(10)
                return

    def click_save(self):
        while True:
            try:
                center_x, center_y = self.detect_image('images/Save.png')
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                time.sleep(10)
                return
            except Exception as e:
                time.sleep(10)
                return

    def click_below_video_details(self):
        self.click_below_image('images/Video_details.png', 200, 300)

    def click_below_image(self, image, dx, dy):
        while True:
            try:
                center_x, center_y = self.detect_image(image)
                pyautogui.moveTo(center_x + dx, center_y + dy)
                pyautogui.click()
                time.sleep(3)
                return
            except Exception as e:
                time.sleep(3)
                return

    def find_language_position(self, lang):
        with open("lang_html.txt", "r", encoding="utf-8") as f:
            html = f.read()

        s = '<yt-formatted-string class="item-text main-text style-scope ytcp-text-menu">'
        extracted = extract_strings_after_s(html, s)
        pletter = ""
        c = 0
        for i, l in enumerate(extracted[1:]):
            if l[:1] == pletter:
                c += 1
            else:
                c = 0
                pletter = l[:1]
            if l.startswith(language_dict[lang]):
                return pletter, c

        return None, None

    def limit_reached(self):
        try:
            self.detect_image("images/limit_reaches.png")
            return True
        except Exception as e:
            return False

    def wrong_account(self):
        try:
            self.detect_image("images/Wrong_account.png")
            return True
        except Exception as e:
            return False

    def wrong_account2(self):
        try:
            self.detect_image("images/Wrong_account2.png")
            return True
        except Exception as e:
            return False

    def save_gray(self):
        try:
            self.detect_image("images/Save_Gray.png")
            return True
        except Exception as e:
            return False
    def update_video_descriptions(self, channel_lang):
        selected_channel_id = channels[lang_to_channel[channel_lang]]
        groups_dict, files_collection = self.get_video_group()
        for g in groups_dict.keys():
            groups_dict[g] = sorted(groups_dict[g], key = lambda k:k["snippet"]["title"] )
            if len(groups_dict[g]) < 14:
                continue
            for data in groups_dict[g]:
                print(f'{g}: {data["snippet"]["title"]}')
                edit_url = f'https://studio.youtube.com/video/{data["id"]}/edit'
                video_channelId = data["snippet"]["channelId"]
                if selected_channel_id != video_channelId:
                    continue
                self.edit_published_video(data["id"], edit_url, data["code_lang"], [data for data in groups_dict[g]], data)
        print(len(files_collection))

    def update_video_end_screens(self, channel_lang):
        selected_channel_id = channels[lang_to_channel[channel_lang]]

        groups_dict, files_collection = self.get_video_group()
        for g in groups_dict.keys():
            groups_dict[g] = sorted(groups_dict[g], key = lambda k:k["snippet"]["title"] )
            if len(groups_dict[g]) < 14:
                continue
            for data in groups_dict[g]:
                print(f'{g}: {data["snippet"]["title"]}')
                edit_url = f'https://studio.youtube.com/video/{data["id"]}/edit'
                video_channelId = data["snippet"]["channelId"]
                if selected_channel_id != video_channelId:
                    continue
                self.edit_end_screens(data["id"], edit_url, data["code_lang"], [data for data in groups_dict[g]], data)
        print(len(files_collection))

    def get_video_group(self):
        files_collection = []
        for filename in glob.glob(os.path.join(uploaded_info_folder, '*.inf')):
            with open(os.path.join(uploaded_info_folder, filename), 'r') as file:
                # Load JSON data from file
                data = json.load(file)
                files_collection.append(data)

        groups_dict = dict()
        for data in files_collection:
            title = data["snippet"]["title"]
            lang = data["snippet"]["defaultAudioLanguage"]
            description = data["snippet"]["description"]
            id = data["id"]
            publishedAt = data["snippet"]["publishedAt"]

            code = get_code(description)
            if code is None:
                continue
            code_lang = code[-2:]
            code_group = code[:-2]

            data["code_lang"] = code_lang
            if code_group in groups_dict:
                groups_dict[code_group].append(data)
            else:
                groups_dict[code_group] = [data]
        return groups_dict, files_collection

    def edit_end_screens(self, id, edit_url, lang, related, data):
        if self.log_action.record_exists('edit_end_screens', id):
            return False
        related2 = self.sort_by_language_codes(related)
        if not self.open_video_edit(edit_url):
            return False
        #self.click_below_video_details()
        #time.sleep(DELAY)
        #pyautogui.press('home')
        #for _ in range(10):
        #    pyautogui.press('up')

        self.press_shift_tab(7)
        self.edit_end_screen(id, lang, data)
        #self.press_shift_tab(12)
        #time.sleep(DELAY)
        #self.press_shift_tab(13)


        #self.click_save()
        #self.log_action.log('edit_related', id)
        print(f'updated video: https://youtu.be/{id}')

    def sort_by_language_codes(self, related):
        related2 = []
        for k in lang_dict.keys():
            for d in related:
                if d["code_lang"] == k:
                    related2.append(d)
        #for d in related2:
        #    print(d["code_lang"])
        return related2

    def open_video_edit(self, edit_url):
        webbrowser.open(edit_url)
        time.sleep(10)
        if self.wrong_account() or self.wrong_account2():
            return False
        if not self.save_gray():
            return False
        return True

    def edit_published_video(self, id, edit_url, lang, related, data):
        if self.log_action.record_exists('edit_related', id):
            return False
        related2 = self.sort_by_language_codes(related)
        if not self.open_video_edit(edit_url):
            return False
        self.click_below_video_details()
        time.sleep(DELAY)
        pyautogui.press('home')
        for _ in range(10):
            pyautogui.press('up')

        #self.press_shift_tab(7)
        #self.edit_end_screen(id, lang, data)
        #self.press_shift_tab(12)
        #time.sleep(DELAY)
        #self.press_shift_tab(13)

        for _ in range(3):
            pyautogui.press('down')
        time.sleep(1)
        for data in related:
            related_lang = data["code_lang"]
            url = 'https://youtu.be/' + data["id"]
            w = f'{lang_dict[related_lang]}: {url}\n'
            keyboard.write(w, delay=0.01)
            time.sleep(0.1)

        self.press_tab(13)
        pyautogui.press('enter')
        time.sleep(DELAY)
        self.press_tab(15)
        self.select_lang(lang)
        time.sleep(DELAY)

        self.click_save()
        self.log_action.log('edit_related', id)
        print(f'updated video: https://youtu.be/{id}')

    def edit_end_screen(self, id, lang, data):
        time.sleep(DELAY)
        pyautogui.press('enter')
        time.sleep(8)
        self.press_tab(5)
        time.sleep(3)
        pyautogui.press('enter')
        self.click_video_best()
        time.sleep(1)
        self.press_shift_tab(3)
        time.sleep(DELAY)
        #pyautogui.press('down')
        #pyautogui.press('down')
        #yautogui.press('down')
        #yautogui.press('enter')
        #time.sleep(3)
        #self.press_tab(3)
        #time.sleep(1)


def get_code(s):
    # The regex pattern to match "video code:" followed by any characters until the end of the line
    patterns = [r"video code:\s*(.*)"
        , r"(CONT_TERR_[a-z]{2})\n", r"(OCEAN_TERR_[a-z]{2})\n"
                ]

    # CONT_TERR_pl"
    # OCEAN_TERR_ko

    for pattern in patterns:
        matches = re.findall(pattern, s, re.MULTILINE)
        if len(matches) == 1:
            code = matches[0]
            code = code.strip()
            return code
    return None

def extract_strings_after_s(html, s):
    # List to hold all extracted strings
    extracted_strings = []

    # Position of the substring 's'
    pos = html.find(s)

    # While 's' is found in 'html'
    while pos != -1:
        # Calculate the start of the extracted string
        start = pos + len(s)

        # Find the next '<' character
        end = html.find('<', start)

        # Extract the string if '<' was found
        if end != -1:
            extracted_strings.append(html[start:end])

        # Update the search position to after the current '<' character
        pos = html.find(s, end)

    return extracted_strings





