""" 이 파이썬 스크립트는 project dependency들을 설치할 때 실행합니다.
이미 아래 패키지들이 설치되어 있다면 실행하실 필요가 없습니다.

  - pandas

"""

if __name__ == "__main__":
    import os

    # 쉘로 가상환경에 requirements.txt에 적혀있는 필수 라이브러리들을 설치합니다.
    os.system('pip install -r requirements.txt')
