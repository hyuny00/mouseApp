import tkinter as tk
from tkinter import ttk
import pyautogui
import pyperclip

# Global variable to store the color
selected_color = ""

# 이벤트 처리 함수
def on_action_select(event):
    global selected_action
    selected_action = action_combobox.get()

def on_enter_button():
    description = description_entry.get()
    record = {'event': 'enter', 'x': 0, 'y': 0, 'description': description}
    records.append(record)
    record_list.insert(tk.END, f"enter - {description} (x: 0, y: 0)")
    description_entry.delete(0, tk.END)  # Clear description entry


def on_main_event_button():
    description = description_entry.get()
    record = {'event': 'Main Event', 'x': 0, 'y': 0, 'description': description}
    records.append(record)
    record_list.insert(tk.END, f"Main Event - {description} (x: 0, y: 0)")    
    description_entry.delete(0, tk.END)  # Clear description entry

def on_start_button():
 
    for record in records:
        if record['event'] != 'enter' and  record['event'] != 'Main Event':
            pyautogui.moveTo(record['x'], record['y'])


        if record['event'] == 'click':
            pyautogui.click(record['x'], record['y'])
        elif record['event'] == 'input':
            pyautogui.click(record['x'], record['y'])
            pyperclip.copy(record['description'])
            pyautogui.hotkey('ctrl', 'v')
        elif record['event'] == 'enter':
            pyautogui.press('enter')
        elif record['event'] == 'Main Event':
                print("Main Event Start:"+selected_color)
        elif record['event'] == 'color':
            # Finding color is a read operation, no action needed during replay
            pass

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
        records[index]['description'] = description
        record_list.delete(index)
        record_list.insert(index, f"{records[index]['event']} - {description} (x: {records[index]['x']}, y: {records[index]['y']})")
        record_list.selection_set(index)

def on_mouse_button_press(event):
    global is_dragging
    is_dragging = True

def on_mouse_button_release(event):
    global is_dragging, selected_color
    description = description_entry.get()
    x, y = event.x_root, event.y_root  # Capture coordinates
    if description or selected_action in ['click', 'color']:
        if selected_action == 'color':
            screen = pyautogui.screenshot()
            color = screen.getpixel((x, y))
            selected_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            description = f"Color: {selected_color}"
        record = {'event': selected_action, 'x': x, 'y': y, 'description': description}
        records.append(record)
        if description:
            record_list.insert(tk.END, f"{selected_action} - {description} (x: {x}, y: {y})")
            description_entry.delete(0, tk.END)  # Clear description entry when mouse is released
        else:
            record_list.insert(tk.END, f"{selected_action} (x: {x}, y: {y})")
        description_entry.delete(0, tk.END)  # Clear description entry

def on_mouse_motion(event):
    if is_dragging:
        coordinates_label.config(text=f'x: {event.x_root}, y: {event.y_root}')

def on_record_list_select(event):
    selection = record_list.curselection()
    if selection:
        index = selection[0]
        description = records[index]['description']
        if records[index]['event'] != 'description':
            description_entry.delete(0, tk.END)
            description_entry.insert(tk.END, description)

# 메인 윈도우 생성
window = tk.Tk()
window.title('Mouse Automation App')

# 버튼 프레임
button_frame = ttk.Frame(window)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

mouse_button = ttk.Button(button_frame, text='마우스', width=8)
mouse_button.pack(side=tk.LEFT, padx=5)
mouse_button.bind('<ButtonPress-1>', on_mouse_button_press)
mouse_button.bind('<ButtonRelease-1>', on_mouse_button_release)
mouse_button.bind('<Motion>', on_mouse_motion)

action_combobox = ttk.Combobox(button_frame, values=['click', 'input', 'color'], width=10)
action_combobox.set('click')  # Default selection
action_combobox.pack(side=tk.LEFT, padx=5)
action_combobox.bind("<<ComboboxSelected>>", on_action_select)

enter_button = ttk.Button(button_frame, text='enter', command=on_enter_button, width=8)
enter_button.pack(side=tk.LEFT, padx=5)

main_event_button = ttk.Button(button_frame, text='Main Event', command=on_main_event_button, width=12)
main_event_button.pack(side=tk.LEFT, padx=5)

start_button = ttk.Button(button_frame, text='시작', command=on_start_button, width=8)
start_button.pack(side=tk.RIGHT, padx=5)

# 설명 입력 필드
description_frame = ttk.Frame(window)
description_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

description_label = ttk.Label(description_frame, text='설명:')
description_label.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

description_entry = ttk.Entry(description_frame)
description_entry.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

# 좌표 표시
coordinates_label = ttk.Label(window, text='좌표:')
coordinates_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# 기록 리스트
record_frame = ttk.Frame(window)
record_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

record_label = ttk.Label(record_frame, text='기록:')
record_label.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

record_list = tk.Listbox(record_frame)
record_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
record_list.bind('<<ListboxSelect>>', on_record_list_select)

button_frame = ttk.Frame(window)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

delete_button = ttk.Button(button_frame, text='삭제', command=on_delete_button, width=8)
delete_button.pack(side=tk.LEFT, padx=5)

edit_button = ttk.Button(button_frame, text='편집', command=on_edit_button, width=8)
edit_button.pack(side=tk.LEFT, padx=5)

# 기록 저장 리스트
records = []

# 드래그 중인지 여부
is_dragging = False

# 선택된 작업
selected_action = 'click'  # Default action

window.mainloop()