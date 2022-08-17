"""
Parsing PDF file, save Xlsx file v011
"""
from tkinter import Tk, filedialog
import os
from tabula import read_pdf
import openpyxl
from openpyxl.styles import Font, Color

# Open Pdf file dialog
Tk().withdraw()
file_path = filedialog.askopenfilename(filetypes=[("PDF file", ".pdf")])
pdf_dir = os.path.dirname(file_path)

# Reading tables from pdf
table_list = read_pdf(file_path, pages="all")
guide_name = table_list[0].columns[2]  # Get guide name

# Save files paths
xlsx_file_path = os.path.join(pdf_dir, guide_name + ".xlsx")

# New table for excel
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["INDEX", "PART NUMBER", "PART DESCRIPTION", "COLOR CODING", "STEP ANIMATION ID", "DIRECTION"])

obj_index = 1
step_id = 0

# Table processing cycle, data preparing for Excel
for pdf_tab_num in table_list:
    if pdf_tab_num.columns[0] == 'Unnamed: 0':  # Check if the first column is blank, if true then it's a header table (0-2351-333 OMS ESC) and need to skip it
        print("skip")
        continue

    step_id += 1
    for row in pdf_tab_num.itertuples():
        exc_data = [obj_index, row[2], row[3], "INNACTIVE", step_id]
        ws.append(exc_data)

        check_file_name = row[2] + ".glb"
        check_file_path = os.path.join(pdf_dir, check_file_name)

        if not os.path.exists(check_file_path):
            ws.cell(row=ws._current_row, column=2).font = Font(color="FF0000")

        obj_index += 1
    ws.append([''])
    obj_index = 1

# Save Excel file
wb.save(xlsx_file_path)
