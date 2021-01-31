# import TalkbangMusicInterface as tmi
from TalkbangMusicInterface import KakaoMiner as tmiKM

import configparser
import json
import os

config_hidden = configparser.ConfigParser()
config_hidden.read("./_config/config_hidden.ini")

config = configparser.ConfigParser()
config.read("./_config/config.ini")

PROJECT_HOME = config_hidden["Path Variables"]["PROJECT_HOME"]
RAW_TXT_PATH = config["Path Variables"]["RAW_TXT_PATH"].replace("PROJECT_HOME", PROJECT_HOME)
TXT_DB_PATH = config["Path Variables"]["TXT_DB_PATH"].replace("PROJECT_HOME", PROJECT_HOME)

del config_hidden, config, PROJECT_HOME


def fetch_file_queue(mode="init"):
    temp_raw_file_list = os.listdir(RAW_TXT_PATH)

    for file in temp_raw_file_list:
        if ".txt" not in file:
            temp_raw_file_list.pop(temp_raw_file_list.index(file))  # 텍스트 파일만 남김

    temp_file_size_dict = dict()
    for file in temp_raw_file_list:
        file_size = os.path.getsize(RAW_TXT_PATH + file)
        if file_size not in temp_file_size_dict:
            temp_file_size_dict[file_size] = [file]
        else:
            temp_file_size_dict[file_size] += [file]

    raw_file_queue = list()
    for file_size in sorted(temp_file_size_dict.keys(), reverse=True):          # 파일 크기가 큰 순서대로 처리
        raw_file_queue += sorted(temp_file_size_dict[file_size], reverse=True)  # 이름 역순 - 파일 이름에 날짜 활용

    if mode == "init":
        return raw_file_queue.pop(0)
    else:
        return raw_file_queue


if __name__ == "__main__":
    mode = "update" if os.path.exists(TXT_DB_PATH + "FULLTXT.json") else "init"

    if mode == "init":
        raw_file = fetch_file_queue(mode)
        platform = tmiKM.backup_platform_definer(RAW_TXT_PATH + raw_file)
        if platform == "Windows":
            data = tmiKM.backup_text_parser_windows(RAW_TXT_PATH + raw_file)
            with open(TXT_DB_PATH + "FULLTXT.json", 'w', encoding="utf-8") as f:
                json.dump(data, f)

    else:  # if mode == "update":
        raw_file_queue = fetch_file_queue(mode)
        for file in raw_file_queue:
            print(tmiKM.backup_platform_definer(RAW_TXT_PATH + file))
