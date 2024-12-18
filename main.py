import PySimpleGUI as sg
from PIL import Image, ImageTk
import json
import os

sg.theme("DarkBlue")
sg.set_options(font=('Courier New', 16))

pins_file="pins.json"
pins_visibility=True
add_mode=False

def load_pins():
    if os.path.exists(pins_file):
        with open(pins_file,"r") as file:
            return json.load(file)
    return []

def save_pins():
    with open(pins_file,"w") as file:
        json.dump(pins,file)

def show_map_with_pins(image_path,pins,show_pins,filtered_pin=None):
    img=Image.open(image_path)
    pin_icon=Image.open("pin.ico").resize((30, 30))
    pin_width,pin_height=pin_icon.size
    if show_pins:
        for pin in pins:
            if filtered_pin and pin!=filtered_pin:
                continue
            x,y=pin["coords"]
            pin_position=(x-pin_width//2,y-pin_height)
            img.paste(pin_icon,pin_position,pin_icon)
    return ImageTk.PhotoImage(img)

def add_entry(x,y):
    window.set_cursor("arrow")
    add_entry_layout=[
        [sg.Text("Title"),sg.Input(size=(51, 1),key='title')],
        [sg.Text("Date"),sg.Input(size=(37, 1),key='date'),
         sg.CalendarButton(button_text="Choose A Date",format='%Y-%m-%d')],
        [sg.Text("Description"),sg.Input(key='description')],
        [sg.Button("Save"),sg.Button("Cancel")]
    ]

    add_entry_window=sg.Window("Add Entry",add_entry_layout,modal=True)

    while True:
        add_entry_event,add_entry_values=add_entry_window.read()
        if add_entry_event==sg.WINDOW_CLOSED or add_entry_event=="Cancel":
            break

        if add_entry_event=="Save":
            title=add_entry_values["title"]
            date=add_entry_values["date"]
            description=add_entry_values["description"]

            if not title or not date or not description:
                sg.popup("Please input valid entries!",title="Error!")
                continue

            pin_data={
                "coords":(x,y),
                "title":add_entry_values["title"],
                "date":add_entry_values["date"],
                "description":add_entry_values["description"],
            }
            pins.append(pin_data)
            break

    add_entry_window.close()

def view_saved_entries():
    global pins_visibility

    titles=[pin["title"] for pin in pins]
    saved_layout=[
        [sg.Listbox(titles, size=(40, 10),key='listbox',enable_events=True)],
        [sg.Button("View", disabled=True), sg.Button("Remove",disabled=True),sg.Button("Exit")]
    ]

    saved_window=sg.Window("Saved Entries",saved_layout,modal=True)

    while True:
        saved_event,saved_values=saved_window.read()
        if saved_event==sg.WINDOW_CLOSED or saved_event=="Exit":
            break

        if saved_event=="listbox":
            selected=saved_values['listbox']
            saved_window["View"].update(disabled=not bool(selected))
            saved_window["Remove"].update(disabled=not bool(selected))
            if selected:
                selected_title=selected[0]
                filtered_pin=next(pin for pin in pins if pin["title"]==selected_title)
                window["image"].update(data=show_map_with_pins(image_path, pins, True, filtered_pin))

        if saved_event=="View" and saved_values["listbox"]:
            selected_title=saved_values["listbox"][0]
            selected_pin=next(pin for pin in pins if pin["title"]==selected_title)
            sg.popup(f"Title: {selected_pin['title']}\n"
                     f"Date: {selected_pin['date']}\n"
                     f"Description: {selected_pin['description']}", title="Entry Details")

        if saved_event=="Remove" and saved_values["listbox"]:
            selected_title =saved_values["listbox"][0]
            pins[:]=[pin for pin in pins if pin["title"] != selected_title]
            titles.remove(selected_title)
            saved_window["listbox"].update(values=titles)
            window["image"].update(data=show_map_with_pins(image_path,pins,pins_visibility))

    saved_window.close()
    window["image"].update(data=show_map_with_pins(image_path, pins,pins_visibility))

pins=load_pins()
image_path="galati.png"

left_column=[
    [sg.Image(key='image', enable_events=True)]
]

right_column=[
    [sg.Button("Add",size=(10,1))],
    [sg.Button("Saved",size=(10,1))],
    [sg.Button("Toggle",size=(10,1))],
    [sg.Button("Close",size=(10,1))],
]

layout=[
    [
        sg.Column(left_column,size=(800,700)),
        sg.VSep(),
        sg.Column(right_column,size=(200,700))
    ]
]

window=sg.Window("MapJournal",layout,size=(1000, 700),finalize=True)

window["image"].update(data=show_map_with_pins(image_path, pins, pins_visibility))

window["image"].bind("<Button-1>", "+CLICK")

while True:
    event,values=window.read()
    if event==sg.WINDOW_CLOSED or event=="Close":
        save_pins()
        break

    if event=="Add":
        add_mode=True
        window.set_cursor("@pin.ico")

    if event=="image+CLICK" and add_mode:
        x,y=window["image"].Widget.winfo_pointerx(),window["image"].Widget.winfo_pointery()
        x-=window["image"].Widget.winfo_rootx()
        y-=window["image"].Widget.winfo_rooty()
        add_entry(x,y)
        window["image"].update(data=show_map_with_pins(image_path,pins,pins_visibility))
        add_mode=False

    if event=="Toggle":
        pins_visibility=not pins_visibility
        window["image"].update(data=show_map_with_pins(image_path,pins,pins_visibility))

    if event=="Saved":
        view_saved_entries()

window.close()