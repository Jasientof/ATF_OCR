import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import datetime
import os
import pytesseract
from PIL import Image
import re

def select_files():
    global selected_files
    selected_files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if selected_files:
        log_message(f"Selected {len(selected_files)} files.")
        update_progress(0)
        update_status(selected=len(selected_files))
    else:
        log_message(f"No files were selected.")

def select_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory()
    if output_folder:
        log_message(f"Output folder selected: {output_folder}")
    else:
        log_message("No output folder was selected.")

def start_processing():
    log_message(f"Starting OCR processing...")
    # OCR processing logic will be added here

def update_progress(value):
    progress_bar['value'] = value
    window.update_idletasks()

def update_status(selected=0, processed=0, found=0, not_found=0):
    status_text = f"Selected: {selected}, Processed: {processed}, IDs Found: {found}, IDs Not Found: {not_found}"
    status_label.config(text=status_text)
    
def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_area.insert(tk.END, f"[{timestamp}] {message}\n")

def open_settings():
    messagebox.showinfo("Settings", "Settings window will be implemented here.")

def open_help():
    messagebox.showinfo("Help", "Help information will be implemented here.")

def setup_gui():
    global window, log_area, progress_bar, status_label
    window = tk.Tk()
    window.title("PDF OCR Renamer")
    window.geometry("520x400")
    
    # Custom styling
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10))
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TProgressbar', thickness=5)

    # Menu Bar
    menu_bar = tk.Menu(window)
    window.config(menu=menu_bar)

    # File Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Settings", command=open_settings)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Help Menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Help", command=open_help)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "PDF OCR Renamer\nVersion 1.0"))
    menu_bar.add_cascade(label="Help", menu=help_menu)

    frame = ttk.Frame(window, padding="10")
    frame.pack(expand=True, fill=tk.BOTH)

    frame = ttk.Frame(window, padding="10")
    frame.pack(expand=True, fill=tk.BOTH)

    # File selection button
    btn_select_files = ttk.Button(frame, text="Select PDF Files", command=select_files)
    btn_select_files.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    # Output folder selection button
    btn_output_folder = ttk.Button(frame, text="Select Output Folder", command=select_output_folder)
    btn_output_folder.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    # Start processing button
    btn_start = ttk.Button(frame, text="Start Processing", command=start_processing)
    btn_start.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

    # Progress bar
    progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

    # Status label
    status_label = ttk.Label(frame, text="Status: Ready")
    status_label.grid(row=3, column=0, columnspan=2, pady=5)

    # Log area
    log_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=10)
    log_area.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')

    return window

selected_files = []  # Global variable to store selected files
output_folder = ""   # Global variable to store the output folder path

def main():
    setup_gui().mainloop()

if __name__ == "__main__":
    main()