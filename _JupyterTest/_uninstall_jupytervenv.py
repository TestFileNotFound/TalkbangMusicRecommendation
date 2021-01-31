""" 로컬 쥬피터에 등록된 프로젝트 가상환경을 제거합니다.

"""

if __name__ == "__main__":
    import os

    print("로컬 쥬피터에 등록된 가상환경 커널을 정말 삭제합니까?")
    print("(_setup_test_code.py 스크립트 파일을 실행시켜서 다시 설치할 수 있습니다.)")
    check = input("[Y/n] : ")
    while check.lower() not in ('y', 'n'):
        print("Y 또는 n을 입력하여 주십시오.")
        check = input("[Y/n] : ")

    if check.lower() == 'n':
        print("로컬 쥬피터에 등록된 가상환경 커널을 영구 삭제하지 않습니다.")
    else:
    
        from _JupyterTest._setup_test_code import VENV_NAME
        print("로컬 쥬피터에 등록된 가상환경 커널을 영구 삭제합니다.")
        os.system(f'jupyter kernelspec uninstall {VENV_NAME}')

        print("ipykernel 및 관련 패키지를 가상환경에서 삭제합니다.")
        # *참고: six와 python-dateutil은 pandas dependency 내용과 겹치기 때문에 삭제하지 않습니다.
        os.system('pip uninstall -r requirements_ipykernel.txt')
