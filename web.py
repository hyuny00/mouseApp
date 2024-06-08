import pyautogui
import time
import webbrowser

# 크롬 브라우저 열기 (여기서는 웹브라우저 모듈을 사용)
webbrowser.open('https://www.daum.net')  # 원하는 URL로 변경

# 크롬이 열리도록 잠시 대기
time.sleep(5)  # 웹페이지 로딩 시간을 고려하여 적절히 조절

# 스크롤을 제일 아래로 내리기
# 화면의 높이에 따라 더 많은 스크롤이 필요할 수 있으므로, 여러 번 스크롤을 내립니다.
for _ in range(1):  # 이 숫자는 스크롤할 횟수를 조절합니다.
    pyautogui.scroll(-10000)  # 음수 값은 아래로 스크롤
    #time.sleep(0.5)  # 스크롤 사이에 약간의 대기 시간을 넣습니다.
