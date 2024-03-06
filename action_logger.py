import os
from datetime import datetime


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
