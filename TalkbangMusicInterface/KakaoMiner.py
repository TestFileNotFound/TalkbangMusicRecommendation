import os
import re

import pandas as pd


def backup_platform_definer(file_path):
    """ PC에서 백업한 내용인지 모바일(Android)에서 백업한 내용인지 확인.

    - PC 예시) (Windows 10)
    ```Team Flow Music 님과 카카오톡 대화
    저장한 날짜 : 2021-01-31 00:00:00
    (공백 한줄)
    --------------- 2018년 3월 5일 월요일 ---------------
    호미님이 판다님, 구름님, 늑대님, 고래님, 물개님, 거북이님, :)님, 거인님과 요시님을 초대했습니다.
    [호미] [오후 9:05] 톡게시판 '공지': ☆ 음악 추천방 ☆```


    - Android 예시) (Galaxy Note 9, Android 9)
    ```Team Flow Music 13 카카오톡 대화
    저장한 날짜 : 2021년 1월 31일 오전 12:00
    (공백 한줄)
    (공백 한줄)
    2018년 3월 5일 오후 9:05
    2018년 3월 5일 오후 9:05, 호미님이 판다님, 구름님, 늑대님, 고래님, 물개님, 거북이님, :)님, 거인님과 요시님을 초대했습니다.
    2018년 3월 5일 오후 9:05, 회원님 : [공지] ☆ 음악 추천방 ☆```


    :param file_path: 파일 주소값
    :type file_path: str
    :return: "Windows" or "Android"
    """
    assert type(file_path) is str, "파일 주소값이 문자열이 아닙니다."
    assert os.path.exists(file_path), "파일이 존재하지 않습니다."

    windows_newdate = re.compile(r"^[- ]+\d{4}년 \d{1,2}월 \d{1,2}일 [월화수목금토일]요일[- ]+\n$")
    android_newdate = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일 오[전후] \d{1,2}:\d{2}\n$")

    with open(file_path, mode='r', encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break  # 비어 보이는 라인에도 '\n' 문자는 포함되어 있음
            elif windows_newdate.match(line) is not None:
                return "Windows"
            elif android_newdate.match(line) is not None:
                return "Android"


def backup_text_parser_windows(file_path):
    """ PC에서 백업한 내용인지 모바일(Android)에서 백업한 내용인지 확인.

    - PC 예시) (Windows 10)
    ```Team Flow Music 님과 카카오톡 대화
    저장한 날짜 : 2021-01-31 00:00:00
    (공백 한줄)
    --------------- 2018년 3월 5일 월요일 ---------------
    호미님이 판다님, 구름님, 늑대님, 고래님, 물개님, 거북이님, :)님, 거인님과 요시님을 초대했습니다.
    [호미] [오후 9:05] 톡게시판 '공지': ☆ 음악 추천방 ☆```

    :param file_path: 파일 주소값
    :type file_path: str
    :return: [dict(), dict(), dict() ...]
    """
    assert type(file_path) is str, "파일 주소값이 문자열이 아닙니다."
    assert os.path.exists(file_path), "파일이 존재하지 않습니다."

    windows_newdate = re.compile(r"^[- ]+\d{4}년 \d{1,2}월 \d{1,2}일 [월화수목금토일]요일[- ]+")
    windows_newtime = re.compile(r"^\[.*\] \[오[전후] \d{1,2}:\d{1,2}\] .*")
    windows_newmember = re.compile(r".*님이 .*님을 초대했습니다\.")
    windows_memberout = re.compile(r"^.{2,7}님이 나갔습니다\.")

    with open(file_path, mode='r', encoding="utf-8") as f:
        # 첫 대화 시작 날짜 찾기
        while True:
            line = f.readline()
            if not line:
                return None     # 빈 파일 오류 방지
            elif windows_newdate.search(line) is not None:
                break

        data = list()

        prev_member = None
        _, year, month, day, _, _ = line.split()
        prev_date = ' '.join([year, month, day])
        prev_time = None
        prev_datetime = None
        order_count = 0
        prev_line = ''

        next_loop_continue = True
        while next_loop_continue:
            line = f.readline()
            if not line:
                data.append(
                    {
                        "member": prev_member,
                        "datetime": prev_datetime,
                        "datetime_order": order_count,
                        "type": "comment",
                        "text": prev_line
                    }
                )
                next_loop_continue = False
                continue

            line = line.strip()
            if windows_newdate.search(line) is not None:
                _, year, month, day, _, _ = line.split()
                prev_date = ' '.join([year, month, day])
            elif windows_newtime.search(line) is not None:
                if prev_datetime is not None:
                    data.append(
                        {
                            "member": prev_member,
                            "datetime": prev_datetime,
                            "datetime_order": order_count,
                            "type": "comment",
                            "text": prev_line
                        }
                    )
                prev_member = line[line.index('[')+1:line.index(']')]
                line = line[line.index(']')+1:]
                curr_time = line[line.index('[')+1:line.index(']')]
                if prev_time != curr_time:
                    order_count = 0
                    prev_time = curr_time
                    prev_datetime = kakao_date_parser(prev_date + ' ' + prev_time)
                else:
                    order_count += 1
                prev_line = line[line.index(']')+1:].strip() + "\\N"
            elif (windows_newmember.search(line) is not None) or (windows_memberout.search(line) is not None):
                continue
            else:
                prev_line += line.strip() + "\\N"

    return data


def backup_text_parser_android(file_path):
    """ PC에서 백업한 내용인지 모바일(Android)에서 백업한 내용인지 확인.

    - Android 예시) (Galaxy Note 9, Android 9)
    ```Team Flow Music 13 카카오톡 대화
    저장한 날짜 : 2021년 1월 31일 오전 12:00
    (공백 한줄)
    (공백 한줄)
    2018년 3월 5일 오후 9:05
    2018년 3월 5일 오후 9:05, 호미님이 판다님, 구름님, 늑대님, 고래님, 물개님, 거북이님, :)님, 거인님과 요시님을 초대했습니다.
    2018년 3월 5일 오후 9:05, 회원님 : [공지] ☆ 음악 추천방 ☆```

    :param file_path: 파일 주소값
    :type file_path: str
    :return: [dict(), dict(), dict() ...]
    """
    assert type(file_path) is str, "파일 주소값이 문자열이 아닙니다."
    assert os.path.exists(file_path), "파일이 존재하지 않습니다."

    android_newdate = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일 오[전후] \d{1,2}:\d{2}[^,]+")
    android_newtime = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일 오[전후] \d{1,2}:\d{2}, .{2,7} : ")
    android_newmember = re.compile(r".*님이 .*님을 초대했습니다\.")
    android_memberout = re.compile(r"^.{2,7}님이 나갔습니다\.")

    with open(file_path, mode='r', encoding="utf-8") as f:
        # 첫 대화 시작 날짜 찾기
        while True:
            line = f.readline()
            if not line:
                return None  # 빈 파일 오류
            elif android_newdate.search(line) is not None:
                break

        data = list()

        prev_member = None
        prev_time = None
        prev_datetime = None
        order_count = 0
        prev_line = ''

        next_loop_continue = True
        while next_loop_continue:
            line = f.readline()
            if not line:
                data.append(
                    {
                        "member": prev_member,
                        "datetime": prev_datetime,
                        "datetime_order": order_count,
                        "type": "comment",
                        "text": prev_line
                    }
                )
                next_loop_continue = False

            if android_newdate.search(line) is not None:
                continue
            line = line.strip()
            if android_newtime.search(line) is not None:
                if (android_newmember.search(line) is not None) or (android_memberout.search(line) is not None):
                    continue

                if prev_datetime is not None:
                    data.append(
                        {
                            "member": prev_member,
                            "datetime": prev_datetime,
                            "datetime_order": order_count,
                            "type": "comment",
                            "text": prev_line
                        }
                    )

                curr_time = line[:line.index(',')]
                line = line[line.index(',')+1:]
                if prev_time != curr_time:
                    order_count = 0
                    prev_time = curr_time
                    prev_datetime = kakao_date_parser(prev_time)
                else:
                    order_count += 1

                prev_member = line[:line.index(':')].strip()
                prev_line = line[line.index(':')+1:].strip() + "\\N"
            else:
                prev_line += line.strip() + "\\N"

    return data


def kakao_date_parser(some_date):
    """ 카카오톡 날짜 형식을 DB에 저장할 형식으로 변환

    예시)
    2018년 3월 5일 오후 9:05 -> 180305_2105

    :param some_date: 0000년 0월 0일 오[전후] 00:00 형식의 날짜
    :type some_date: str
    :return:
    """
    # assert type(some_date) is str, "날짜가 문자열이 아닙니다."
    # import re
    # assert re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일 오[전후] \d{1,2}:\d{2}$").match(some_date) is not None, \
    #     "날짜 형식이 맞지 않습니다."

    year, month, day, ampm, hour_minute = some_date.split()
    hour, minute = hour_minute.split(':')
    hour = int(hour)
    if hour == 12:
        hour = 0
    if ampm == "오후":
        hour += 12

    return f"{year[2:4]:0>2}{month[:-1]:0>2}{day[:-1]:0>2}_{hour:0>2}{minute:0>2}"


def datecode_to_date(some_datecode, to_datetime=False):
    """ DB 날짜 코드 형식을 pandas 날짜 형식으로 변환

    예시)
    180305_2105 -> "2018-03-05 21:05:00"

    :param some_datecode: 0000년 0월 0일 오[전후] 00:00 형식의 날짜
    :type some_datecode: str
    :param to_datetime: False(기본값) - str으로 반환 / True - pd.Timestamp
    :type to_datetime: bool
    """
    # assert type(some_datecode) is str, "날짜 코드값이 문자열이 아닙니다."
    # assert ('_' in some_datecode) and (len(some_datecode)==11), "날짜 형식이 맞지 않습니다."

    year, month, day, = "20" + some_datecode[0:2], some_datecode[2:4], some_datecode[4:6]
    hour, minute, second = some_datecode[7:9], some_datecode[9:11], "00"

    if not to_datetime:
        return year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + second
    else:
        return pd.Timestamp(*list(map(int, [year, month, day, hour, minute, second])))
