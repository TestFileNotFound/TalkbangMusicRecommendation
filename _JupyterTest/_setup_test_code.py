""" 이 파이썬 스크립트는 Talkbang_Music_Recommendation 폴더 전체를
Pycharm 프로젝트로 열어 가상환경 venv를 설정할 때 처음 한번만 실행합니다.

* 경고:
  이 스크립트 파일을 절대 가상환경 외부의 터미널로 실행하지 마십시오.
  로컬 ipykernel 패키지를 삭제하여 정상적으로 쥬피터 노트북이 실행되지 
  않을 수도 있습니다!

이 파이썬 스크립트로 다음과 같이 환경설정을 실행 하실 수 있습니다.
  - 프로젝트 가상환경(venv)에 필요한 모듈 설치
    - ...
  - 쥬피터 커널에 Python 가상환경을 설치
  - ipykernel: 쥬피터 노트북 가상환경에 프로젝트 가상환경을 등록할 때
             필요하며, 등록 후 바로 삭제됩니다.

"""

PROJECT_NAME = "TalkbangMusic"
VENV_NAME = f"{PROJECT_NAME.lower()}venv"
VENV_PYTHON_KERNEL_DISPLAY_NAME = f"Python 3 [{PROJECT_NAME}]"

if __name__ == "__main__":
    import os

    # 1. 프로젝트 가상환경(venv)에 필요한 모듈 설치

    # 쉘로 가상환경에 requirements.txt에 적혀있는 필수 라이브러리들을 설치합니다.
    os.system('pip install -r ../requirements.txt')
    os.system('pip install -r requirements_test_code.txt')

    # 2. 프로젝트 가상환경을 로컬 쥬피터 노트북으로도 이용 가능하게 설치

    print("설치된 가상환경을 쥬피터 노트북에서 별개 커널로 이용 가능하게 할 수 있습니다.")
    check = input("쥬피터 노트북 커널 리스트에 해당 가상환경을 추가합니까? [Y/n]: ")
    while check.lower() not in ('y', 'n'):
        print("Y 또는 n을 입력하여 주십시오.")
        check = input("쥬피터 노트북 커널 리스트에 해당 가상환경을 추가합니까? [Y/n]: ")

    if check.lower() == 'y':
        # 쥬피터 노트북 가상환경 설치에 필요합니다.
        os.system('pip install ipykernel')

        # 가상환경의 python.exe와 ipykernel 패키지를 이용하여 로컬 쥬피터에 커널을 등록합니다.
        os.system(f'python -m ipykernel install --user --name {VENV_NAME} --display-name "{VENV_PYTHON_KERNEL_DISPLAY_NAME}"')
