import tkinter as tk
from tkinter import filedialog, messagebox
import os

import tkinter as tk
from tkinter import ttk
import pyautogui
import pyperclip
import time
import json  # For saving and loading history
import random
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
import os
from mnemonic import Mnemonic

# 기록 저장 리스트
records = []

# 파일 선택 여부를 추적하기 위한 변수
file_loaded = False

# 드래그 중인지 여부
is_dragging = False

def on_mouse_button_press(event):
    global is_dragging
    is_dragging = True


def on_mouse_button_release(event):
    global is_dragging, selected_color, t, wordCount
    x, y = event.x_root, event.y_root  # Capture coordinates



    if(len(records)==0):
        messagebox.showwarning("경고", "먼저 데이터를 로드하세요.")
        return

    if records:
        records.pop(0)

    file_label.config(text=f"x: {event.x_root}, y: {event.y_root}")    

    # 첫 번째 클릭 레코드 추가
    records.insert(0, {"event": "click", "x": x, "y": y, "description": ""})

    if records:
        print("Records:")
        for record in records:
            print(record)
    else:
        print("Records are empty")


def load_history():
    global file_loaded
    file_path = filedialog.askopenfilename(title="파일 선택", filetypes=[("json 파일", "*.json"), ("모든 파일", "*.*")])
    if file_path:
        file_name = os.path.basename(file_path)
        file_label.config(text=file_name)
        file_loaded = True
        start_button.config(state=tk.NORMAL)  # 파일이 선택되면 시작 버튼 활성화

        global records
        with open(file_path, "r") as file:
            records = json.load(file)
  

def on_start_button():
    global outer_running, inner_running
    outer_running = True
    inner_running = True

    if not file_loaded:
        messagebox.showwarning("경고", "먼저 데이터를 로드하세요.")
        return
    
    if len(records) == 0:
        messagebox.showinfo("Info", "No records available.")
        return

    # 장기 실행 작업을 위한 새로운 스레드를 시작
  
    threading.Thread(target=long_running_task).start()

def on_stop_button():
    global outer_running, inner_running
    outer_running = False
    inner_running = False

# Tkinter 창 설정
root = tk.Tk()
root.title("RUN")

# 고정 크기 설정
root.geometry("400x400")
#root.resizable(False, False)

# 상단 프레임 (로드데이터 버튼과 파일명 표시)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, pady=10)

mouse_button = ttk.Button(top_frame, text="마우스")
mouse_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
mouse_button.bind("<ButtonPress-1>", on_mouse_button_press)
mouse_button.bind("<ButtonRelease-1>", on_mouse_button_release)


# 로드데이터 버튼
load_button = tk.Button(top_frame, text="로드데이터", command=load_history)
load_button.pack(side=tk.LEFT, padx=5)

# 파일명 표시 레이블
file_label = tk.Label(top_frame, text="파일이 선택되지 않았습니다.")
file_label.pack(side=tk.LEFT, padx=5)




# 중앙 프레임 (시작 버튼과 중지 버튼)
center_frame = tk.Frame(root)
center_frame.pack(expand=True)




# 시작 버튼
start_button = tk.Button(center_frame, text="시작", command=on_start_button, state=tk.DISABLED, width=10, height=5)
start_button.grid(row=0, column=0, padx=10, pady=10)

# 중지 버튼
stop_button = tk.Button(center_frame, text="중지", command=on_stop_button, width=10, height=5)
stop_button.grid(row=0, column=1, padx=10, pady=10)

selected_color = ""
t = (0, 0)
wordCount=12

outer_running = True
inner_running = True

def select_words():
    
    global wordCount

    # Initialize BIP-39 mnemonic generator
    mnemo = Mnemonic("english")

    # Generate a 24-word seed phrase
    if(wordCount == 12):
        strength=128
    elif (wordCount == 15):
        strength=160
    elif (wordCount == 18):
        strength=192 
    elif (wordCount == 21):
        strength=224 
    elif (wordCount == 24):
        strength=256

    seed_phrase = mnemo.generate(strength=strength)

    return seed_phrase

def long_running_task():

    global outer_running, inner_running, wordCount

   
    while outer_running:

        inner_running = True
        for record in records:
            if record["event"] != "enter" and record["event"] != "sleep":
                pyautogui.moveTo(record["x"], record["y"])

            if record["event"] == "click":
                str = record["description"]
                check = str.isdigit()
                if check:
                    for i in range(int(str)):
                        pyautogui.click(record["x"], record["y"])
                else:
                    pyautogui.click(record["x"], record["y"])
            elif record["event"] == "input":
                pyautogui.click(record["x"], record["y"])
                pyperclip.copy(record["description"])
                pyautogui.hotkey("ctrl", "v")
            elif record["event"] == "enter":
                pyautogui.press("enter")
            elif record["event"] == "sleep":
                time.sleep(int(record["description"]))
            elif record["event"] == "Main Event":
                #print("Main Event Start:" + selected_color)

                count = 0
                while inner_running:
                    count = count + 1
                    if(count%100==0):
                        time.sleep(10)

                    wordCount = int(record["description"])
                    result = select_words()

                    pyperclip.copy(result)
                    pyautogui.click(record["x"], record["y"])
                    pyautogui.hotkey("ctrl", "v")

                    time.sleep(1)

                    """
                    screen = pyautogui.screenshot()
                    color = screen.getpixel(t)
                    hex_color = "#{:02x}{:02x}{:02x}".format(
                        color[0], color[1], color[2]
                    )

                    if selected_color != hex_color:
                        with open("result.txt", "a") as file:
                            file.write(result + "\n")

                        inner_running = False
                    """ 

                    with open("result.txt", "a") as file:
                        file.write(result + "\n")

                    inner_running = False
                    
            elif record["event"] == "color":
                
                screen = pyautogui.screenshot()
                color = screen.getpixel((record["x"], record["y"]))
                selected_color = "#{:02x}{:02x}{:02x}".format(
                    color[0], color[1], color[2]
                )
                t = (record["x"], record["y"])

            elif record["event"] == "End Event":
                screen = pyautogui.screenshot()
                file_path = "capture/" + result[:3] + ".png"
                screen.save(file_path)

                pyautogui.click(record["x"], record["y"])

# Bind Ctrl + Q to exit application
def exit_application(event=None):
    global outer_running, inner_running
    outer_running = False
    inner_running = False

    time.sleep(2)
    root.destroy()
    
root.bind('<Control-q>', exit_application)

# Tkinter 이벤트 루프 시작
root.mainloop()
