# import TalkbangMusicInterface as tmi
from TalkbangMusicInterface import KakaoMiner as tmiKM

import configparser
import json
import os

import pandas as pd

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


def fetch_db_json(mode="load", db=None):
    if mode != "reload":
        with open(TXT_DB_PATH + "FULLTXT.json", 'r', encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = db

    db_df = pd.DataFrame(db).drop(["member", "type", "text"], axis=1) \
        .groupby(["datetime"])[["datetime_order"]].count()
    db_df.columns = "count",

    return db, db_df


if __name__ == "__main__":
    mode = "update" if os.path.exists(TXT_DB_PATH + "FULLTXT.json") else "init"

    if mode == "init":
        print("initializing talk database\n")
        raw_file = fetch_file_queue(mode)
        platform = tmiKM.backup_platform_definer(RAW_TXT_PATH + raw_file)

        if platform == "Windows":
            data = tmiKM.backup_text_parser_windows(RAW_TXT_PATH + raw_file)
        elif platform == "Android":
            data = tmiKM.backup_text_parser_android(RAW_TXT_PATH + raw_file)
        else:
            raise Exception("데이터 없쪙")

        with open(TXT_DB_PATH + "FULLTXT.json", 'w', encoding="utf-8") as f:
            json.dump(data, f)

    else:  # if mode == "update":
        print("updating talk database\n")
        db, db_df = fetch_db_json()

        raw_file_queue = fetch_file_queue(mode)
        data_pointer_list = list(range(len(raw_file_queue)))
        new_records = 0
        for raw_file in raw_file_queue:
            platform = tmiKM.backup_platform_definer(RAW_TXT_PATH + raw_file)

            if platform == "Windows":
                data = tmiKM.backup_text_parser_windows(RAW_TXT_PATH + raw_file)
            elif platform == "Android":
                data = tmiKM.backup_text_parser_android(RAW_TXT_PATH + raw_file)
            else:
                import warnings
                warnings.warn("데이터 없쪙")
                data = None

            if data is not None:
                data_df = pd.DataFrame(data).drop(["member", "type", "text"], axis=1)\
                                .groupby(["datetime"])[["datetime_order"]].count()
                data_df.columns = "new_count",
                data_df = pd.merge(db_df.reset_index(), data_df.reset_index(), on="datetime", how="right")\
                                .set_index("datetime")
                data_df["count"] = data_df["count"].fillna(0).astype(int)
                data_df = data_df[data_df["count"] != data_df["new_count"]] # 레코드 수가 다른 datetime에 대해서만 업데이트

                if len(data_df) != 0:
                    new_datetimes = list(data_df.index)
                    data = list(filter(lambda record: record["datetime"] in new_datetimes, data))
                    db_df, data_df = pd.DataFrame(db), pd.DataFrame(data)

                    for new_datetime in new_datetimes:
                        if new_datetime not in db_df["datetime"]:
                            continue    # 모두 업데이트 대상
                        else:
                            print(db_df[db_df["datetime"] == new_datetime])
                            print(data_df[data_df["datetime"] == new_datetime])

                            input("미구현 마치 미구엘 : ")
                            data_df = data_df[data_df["datetime"] != new_datetime]

                    db_df = pd.concat([db_df, data_df], axis=0).sort_values(by=["datetime", "datetime_order"])
                    new_records += len(data_df)
                    print(raw_file, f": {len(data_df)} records to update.")
                    db, db_df = fetch_db_json(mode="reload", db=db_df.to_dict(orient='records'))
                    del data, data_df
                    continue    # 다음 파일로 넘어감

            print(raw_file, ": No new records to update.")

        with open(TXT_DB_PATH + "FULLTXT.json", 'w', encoding="utf-8") as f:
            json.dump(db, f)
        print(f"Total {new_records} records updated.")
