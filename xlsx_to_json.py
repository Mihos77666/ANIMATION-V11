"""
Processing Xlsx file v011
"""
import json
from tkinter import Tk, filedialog
import os
import subprocess
from openpyxl import load_workbook

# Open file dialog
Tk().withdraw()
file_path = filedialog.askopenfilename(filetypes=[("Xlsx", ".xlsx")])
file_dir = os.path.dirname(file_path)
task_name = os.path.basename(file_path).split('.')[0]
json_dir = os.path.join(file_dir, 'JSON')

if not os.path.exists(json_dir):
    os.makedirs(json_dir)

# Read Xlsx file
xlsx_book = load_workbook(filename=file_path, read_only=True)
xlsx_sheet = xlsx_book.active
xlsx_data = list(xlsx_sheet.rows)

col_names = [column.value for column in xlsx_data[0]]

# Formating Json
json_out = []
empty_line = False
list_len = len(xlsx_data) - 2
last_line = False
step_id = "None"

for i, row in enumerate(xlsx_data[1:]):
    values = [cell.value for cell in row]
    row_dict = {name: str(value) for name, value in zip(col_names, values)}

    if row_dict["INDEX"] != 'None':
        if row_dict["STEP ANIMATION ID"] != 'None':
            step_id = row_dict["STEP ANIMATION ID"]
        json_out.append(row_dict)
        empty_line = False
        if i == list_len:
            last_line = True
    elif not empty_line:
        if step_id != "None":
            json_data = json.dumps(json_out, indent=4)
            step_path = task_name + '_STEP_' + step_id + '.json'
            file_save_path = os.path.join(json_dir, step_path)

            with open(file_save_path, "w", encoding="utf-8") as file:
                file.write(json_data)
            json_out.clear()
            empty_line = True

    else:
        break
    if last_line:
        json_data = json.dumps(json_out, indent=4)
        step_path = task_name + '_STEP_' + step_id + '.json'
        file_save_path = os.path.join(json_dir, step_path)

        with open(file_save_path, "w", encoding="utf-8") as file:
            file.write(json_data)

anim_save_dir = os.path.join(file_dir, "Animation")
if not os.path.exists(anim_save_dir):
    os.makedirs(anim_save_dir)

all_dir_files = os.listdir(json_dir)
json_files = filter(lambda x: x[-5:] == ".json", all_dir_files)

BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"

for json_file in json_files:
    json_file_path = os.path.join(json_dir, json_file)
    subprocess.call([BLENDER_PATH, "-b", "--python", "blender_process.py", json_file_path, file_dir, task_name])
