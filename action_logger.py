import os
from datetime import datetime, timedelta

log_folder = 'c:/video/UploadData/log/'
def ensure_folder_exists(folder_path):
   # Check if the folder exists
   if not os.path.exists(folder_path):
       # If the folder does not exist, create it
       os.makedirs(folder_path)
class action_logger():
    def __init__(self):
        ensure_folder_exists(log_folder)

    def log(self, action_category, video_id, info=""):
        file_name = os.path.join(log_folder, action_category + ".log")
        with open(file_name, 'a') as file:
            formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            file.write(f'{formatted_datetime},{video_id},{info}\n')
            file.close()

        pass

    def record_exists(self, action_category, video_id):
        file_name = os.path.join(log_folder, action_category + ".log")
        if not os.path.exists(file_name):
            return False
        with open(file_name, 'r') as file:
            content = file.read()
            return video_id in content

    def last_time_of_record(self, action_category, video_id):
        file_name = os.path.join(log_folder, action_category + ".log")
        if not os.path.exists(file_name):
            return False
        last_time = None
        with open(file_name, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                if video_id in line:
                    line_s = line.split(",")
                    if len(line_s) >= 3:
                        try:
                            found_time = datetime.strptime(line_s[0], "%Y-%m-%d %H:%M:%S.%f")
                        except Exception as e:
                            found_time = datetime(1900, 1, 1)
                    else:
                        found_time = datetime(1900, 1, 1)
                    if last_time is None or found_time > last_time:
                        last_time = found_time

        return last_time

    def uploads_within_24(self, action_category, langs):

        file_name = os.path.join(log_folder, action_category + ".log")
        if not os.path.exists(file_name):
            return 0
        n = 0
        with open(file_name, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                line_s = line.split(",")
                if len(line_s) >= 3 and any(f'_{lang}.mp4.inf' in line_s[1] for lang in langs):
                    try:
                        found_time = datetime.strptime(line_s[0], "%Y-%m-%d %H:%M:%S.%f")
                        if datetime.now() - found_time <= timedelta(days=1):
                            n += 1
                    except Exception as e:
                        continue
        return n


    def last_upload_slot(self, action_category, langs, n_per_day, date_from):
        file_name = os.path.join(log_folder, action_category + ".log")
        if not os.path.exists(file_name):
            return False
        last_time = None
        times = []
        with open(file_name, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                line_s = line.split(",")
                if len(line_s) >= 3 and any(f'_{lang}.mp4.inf' in line_s[1] for lang in langs):
                    try:
                        found_time = datetime.strptime(line_s[2], "%Y-%m-%d %H:%M:%S.%f")
                        if found_time > date_from:
                            times.append(datetime(found_time.year, found_time.month, found_time.day))
                    except Exception as e:
                        continue
        dt = date_from
        for i in range(1000000):
            dt = dt + timedelta(days=1)
            dt0 = datetime(dt.year, dt.month, dt.day)
            if times.count(dt0) < n_per_day:
                return dt
        return date_from
