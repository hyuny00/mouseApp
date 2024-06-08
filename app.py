import tkinter as tk
from tkinter import ttk
import pyautogui
import pyperclip
import time
import json  # For saving and loading history
import pandas as pd
import random
from tkinter import messagebox, filedialog
import threading
from PIL import Image, ImageTk
import os
import pickle

# Global variable to store the color
selected_color = ""
t = (0, 0)
wordCount = 12


def select_words(loaded_df):

    global wordCount

    """
    df = pd.read_csv("word.cvs")
    second_column = df.iloc[:, 1].str.strip()
    random_entries = random.sample(list(second_column), wordCount)
    random_entries_string = " ".join(random_entries)

    str = random_entries_string
    """

    num_rows = len(loaded_df)

    random_indices = random.sample(range(num_rows), wordCount)
    random_rows = loaded_df.iloc[random_indices]
    result_string = " ".join(random_rows.iloc[:, 1])

    return result_string


# 이벤트 처리 함수
def on_action_select(event):
    global selected_action
    selected_action = action_combobox.get()


def on_enter_button():
    description = description_entry.get()
    record = {"event": "enter", "x": 0, "y": 0, "description": description}
    records.append(record)
    record_list.insert(tk.END, f"enter - {description} (x: 0, y: 0)")
    description_entry.delete(0, tk.END)  # Clear description entry


def on_sleep_button():
    description = description_entry.get()
    record = {"event": "sleep", "x": 0, "y": 0, "description": description}
    records.append(record)
    record_list.insert(tk.END, f"sleep - {description} (x: 0, y: 0)")
    description_entry.delete(0, tk.END)  # Clear description entry


def on_stop_button():
    global outer_running, inner_running
    outer_running = False
    inner_running = False


outer_running = True
inner_running = True


isTest = False


def on_test_button():
    global isTest, outer_running, inner_running
    outer_running = True
    inner_running = True

    if len(records) == 0:
        messagebox.showinfo("Info", "No records available.")
        return

    isTest = True

    # 장기 실행 작업을 위한 새로운 스레드를 시작
    threading.Thread(target=long_running_task).start()


def on_start_button():
    global outer_running, inner_running
    outer_running = True
    inner_running = True

    isTest = False
    if len(records) == 0:
        messagebox.showinfo("Info", "No records available.")
        return

    # 장기 실행 작업을 위한 새로운 스레드를 시작
    threading.Thread(target=long_running_task).start()


def long_running_task():

    global outer_running, inner_running, wordCount, isTest

    with open("words.pkl", "rb") as f:
        loaded_df = pickle.load(f)

    testCount = 0
    while outer_running:

        if isTest:
            testCount = testCount + 1
            if testCount == 1:
                outer_running = False
                testCount = 0

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
                print("Main Event Start:" + selected_color)

                count = 0
                while inner_running:
                    count = count + 1
                    if count % 100 == 0:
                        time.sleep(10)

                    wordCount = int(record["description"])

                    result = select_words(loaded_df)

                    pyperclip.copy(result)
                    pyautogui.click(record["x"], record["y"])
                    pyautogui.hotkey("ctrl", "v")

                    screen = pyautogui.screenshot()
                    color = screen.getpixel(t)
                    hex_color = "#{:02x}{:02x}{:02x}".format(
                        color[0], color[1], color[2]
                    )

                    print("hex_color...." + hex_color)
                    print("selected_color...." + selected_color)

                    if selected_color != hex_color:
                        with open("result.txt", "a") as file:
                            file.write(result + "\n")

                        inner_running = False

            elif record["event"] == "color":
                # Finding color is a read operation, no action needed during replay

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


def on_delete_button():
    selection = record_list.curselection()
    if selection:
        index = selection[0]
        record_list.delete(index)
        records.pop(index)


def on_edit_button():
    selection = record_list.curselection()
    if selection:
        index = selection[0]
        description = description_entry.get()
        records[index]["description"] = description
        record_list.delete(index)
        record_list.insert(
            index,
            f"{records[index]['event']} - {description} (x: {records[index]['x']}, y: {records[index]['y']})",
        )
        record_list.selection_set(index)


def on_mouse_button_press(event):
    global is_dragging
    is_dragging = True


def on_mouse_button_release(event):
    global is_dragging, selected_color, t, wordCount
    description = description_entry.get()
    x, y = event.x_root, event.y_root  # Capture coordinates
    if description or selected_action in ["click", "color", "Main Event", "End Event"]:
        if selected_action == "color":
            screen = pyautogui.screenshot()
            color = screen.getpixel((x, y))
            selected_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            description = f"Color: {selected_color}"
            t = (x, y)

        record = {"event": selected_action, "x": x, "y": y, "description": description}
        records.append(record)

        if selected_action == "Main Event":

            try:
                wordCount = int(description)
            except ValueError:
                messagebox.showerror("입력 오류", "wordCount는 정수여야 합니다.")
                return

        if description:
            record_list.insert(
                tk.END, f"{selected_action} - {description} (x: {x}, y: {y})"
            )
            description_entry.delete(
                0, tk.END
            )  # Clear description entry when mouse is released
        else:
            record_list.insert(tk.END, f"{selected_action} (x: {x}, y: {y})")
        description_entry.delete(0, tk.END)  # Clear description entry


def on_mouse_motion(event):
    if is_dragging:
        coordinates_label.config(text=f"x: {event.x_root}, y: {event.y_root}")


def on_record_list_select(event):
    selection = record_list.curselection()
    if selection:
        index = selection[0]
        description = records[index]["description"]
        if records[index]["event"] != "description":
            description_entry.delete(0, tk.END)
            description_entry.insert(tk.END, description)


def save_history():
    description = description_entry.get()

    if description == "":
        messagebox.showerror("입력 오류", "입력은 정수여야 합니다.")
        return

    history_file = "history_" + description + ".json"
    with open(history_file, "w") as file:
        json.dump(records, file)
    print("History saved to " + history_file)


def load_history():

    file_path = filedialog.askopenfilename(
        title="파일 선택", filetypes=[("json 파일", "*.json"), ("모든 파일", "*.*")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        file_label.config(text=file_name)

        global records
        with open(file_path, "r") as file:
            records = json.load(file)
        record_list.delete(0, tk.END)
        for record in records:
            record_list.insert(
                tk.END,
                f"{record['event']} - {record['description']} (x: {record['x']}, y: {record['y']})",
            )
        print("History loaded from " + file_name)
        pass


# 메인 윈도우 생성
window = tk.Tk()
window.title("Mouse Automation App")

# 버튼 프레임
button_frame = ttk.Frame(window)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)


mouse_button = ttk.Button(button_frame, text="마우스", width=8)
mouse_button.pack(side=tk.LEFT, padx=5)
mouse_button.bind("<ButtonPress-1>", on_mouse_button_press)
mouse_button.bind("<ButtonRelease-1>", on_mouse_button_release)
mouse_button.bind("<Motion>", on_mouse_motion)

action_combobox = ttk.Combobox(
    button_frame,
    values=["click", "input", "color", "Main Event", "End Event"],
    width=10,
)
action_combobox.set("click")  # Default selection
action_combobox.pack(side=tk.LEFT, padx=5)
action_combobox.bind("<<ComboboxSelected>>", on_action_select)

enter_button = ttk.Button(button_frame, text="enter", command=on_enter_button, width=8)
enter_button.pack(side=tk.LEFT, padx=5)

main_event_button = ttk.Button(
    button_frame, text="Sleep", command=on_sleep_button, width=10
)
main_event_button.pack(side=tk.LEFT, padx=5)

test_button = ttk.Button(button_frame, text="Test", command=on_test_button, width=8)
test_button.pack(side=tk.RIGHT, padx=5)

start_button = ttk.Button(button_frame, text="시작", command=on_start_button, width=8)
start_button.pack(side=tk.RIGHT, padx=5)

stop_button = ttk.Button(button_frame, text="중지", command=on_stop_button, width=8)
stop_button.pack(side=tk.RIGHT, padx=5)

# 설명 입력 필드
description_frame = ttk.Frame(window)
description_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

description_label = ttk.Label(description_frame, text="설명:")
description_label.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

description_entry = ttk.Entry(description_frame)
description_entry.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

# 좌표 표시
coordinates_label = ttk.Label(window, text="좌표:")
coordinates_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# 파일 표시
file_label = ttk.Label(window, text="파일:")
file_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# 기록 리스트
record_frame = ttk.Frame(window)
record_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

record_label = ttk.Label(record_frame, text="기록:")
record_label.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

record_list = tk.Listbox(record_frame)
record_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
record_list.bind("<<ListboxSelect>>", on_record_list_select)

button_frame = ttk.Frame(window)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

delete_button = ttk.Button(button_frame, text="삭제", command=on_delete_button, width=8)
delete_button.pack(side=tk.LEFT, padx=5)

edit_button = ttk.Button(button_frame, text="편집", command=on_edit_button, width=8)
edit_button.pack(side=tk.LEFT, padx=5)

save_button = ttk.Button(
    button_frame, text="Save History", command=save_history, width=12
)
save_button.pack(side=tk.LEFT, padx=5)

load_button = ttk.Button(
    button_frame, text="Load History", command=load_history, width=12
)
load_button.pack(side=tk.LEFT, padx=5)

# 기록 저장 리스트
records = []

# 드래그 중인지 여부
is_dragging = False

# 선택된 작업
selected_action = "click"  # Default action


# Bind Ctrl + Q to exit application
def exit_application(event=None):
    global outer_running, inner_running
    outer_running = False
    inner_running = False

    time.sleep(2)
    window.destroy()


window.bind("<Control-q>", exit_application)

window.mainloop()
