import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import datetime
import os
from pathlib import Path
import pytesseract
from PIL import Image
import re
from pdf2image import convert_from_path
import threading
import shutil
from queue import Queue
import time


pytesseract.pytesseract.tesseract_cmd = r"lib\tesseract\tesseract.exe"


# Regex patterns for different IDs
regex_patterns = {
    'MAN': re.compile(r"\b([0O]{1}[0-9]{1}|[0-9]{2})[A-Z]{1}[A-Z0-9]{4}\b"),
    'SCANIA': re.compile(r"\b[(2|5)]{1}[0-9]{6}\b"),
    'MERCEDES': re.compile(r"\b[1]{1}[0-9]{9}\b"),
    'VOLVO': re.compile(r"\b[A-B]{1}[0-9]{6}\b")
}

# Function to process a single PDF file and extract text using OCR
def process_pdf(file_path):
    #poppler_path = os.path.join(os.getcwd(), 'poppler', 'bin')  # Adjust the path accordingly
    poppler_path = Path(r"lib\poppler-23.11.0\bin")
    pages = convert_from_path(file_path, 500, poppler_path=poppler_path)
    extracted_text = ""

    for page in pages:
        extracted_text += pytesseract.image_to_string(page)

    return extracted_text

# Function to rename a file based on the extracted ID
def rename_file(original_path, new_name):
    new_path = os.path.join(output_folder, new_name + ".pdf")
    os.rename(original_path, new_path)
    log_message(f"Renamed file to: {new_name}.pdf")

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

# Updated start_processing function to include OCR and renaming
def start_processing():
    if not selected_files or not output_folder:
        log_message("Please select files and an output folder.")
        return

    log_message("Starting OCR processing...")
    file_queue = Queue()
    for file_path in selected_files:
        file_queue.put(file_path)

    processed_count = [0]  # Using a list as a mutable object
    found_count = [0]
    not_found_count = [0]

    def process_file_thread():
        while not file_queue.empty():
            file_path = file_queue.get()
            text = process_pdf(file_path)
            file_id = None

            # Apply regex patterns to text to find the ID
            for key, pattern in regex_patterns.items():
                match = pattern.search(text)
                if match:
                    file_id = match.group()
                    # Special handling for 'MAN' category
                    if key == 'MAN' and file_id[0] == 'O':
                        file_id = '0' + file_id[1:]
                    found_count[0] += 1
                    break

            if file_id:
                new_filename = file_id
            else:
                not_found_count[0] += 1
                new_filename = f'not_found{not_found_count[0]}'

            new_file_path = os.path.join(output_folder, new_filename + '.pdf')
            shutil.copy2(file_path, new_file_path)
            log_message(f"Copied file to: {new_filename}.pdf")

            processed_count[0] += 1
            file_queue.task_done()

    def schedule_gui_updates():
        if any(thread.is_alive() for thread in threads):
            update_progress((processed_count[0] / len(selected_files)) * 100)
            update_status(selected=len(selected_files), processed=processed_count[0], found=found_count[0], not_found=not_found_count[0])
            window.after(100, schedule_gui_updates)
        else:
            # Final update after all processing is done
            update_progress(100)
            update_status(selected=len(selected_files), processed=processed_count[0], found=found_count[0], not_found=not_found_count[0])
            log_message("OCR processing completed.")

    # Creating and starting file processing threads
    num_threads = min(10, len(selected_files))  # Adjust as needed
    threads = [threading.Thread(target=process_file_thread) for _ in range(num_threads)]
    for thread in threads:
        thread.start()

    # Schedule GUI updates
    window.after(100, schedule_gui_updates)

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