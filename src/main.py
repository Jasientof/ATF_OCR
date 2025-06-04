import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import datetime
import os
from pathlib import Path
import pytesseract
import re
from pdf2image import convert_from_path
import threading
import shutil
import json
import webbrowser
from queue import Queue


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    default = {
        "tesseract_path": "",
        "poppler_path": "",
        "regex_patterns": {
            "MAN": "\\b([0O]{1}[0-9]{1}|[0-9]{2})[A-Z]{1}[A-Z0-9]{4}\\b",
            "SCANIA": "\\b[(2|5)]{1}[0-9]{6}\\b",
            "MERCEDES": "\\b[1]{1}[0-9]{9}\\b",
            "VOLVO": "\\b[A-B]{1}[0-9]{6}\\b"
        }
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2)
    return default


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


config = load_config()


def detect_tesseract(path=None):
    candidates = [
        path,
        os.environ.get("TESSERACT_PATH"),
        shutil.which("tesseract"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def detect_poppler(path=None):
    candidates = [
        path,
        os.environ.get("POPPLER_PATH"),
    ]
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        candidates.append(str(Path(pdftoppm).parent))
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


tesseract_cmd = detect_tesseract(config.get("tesseract_path"))
poppler_bin = detect_poppler(config.get("poppler_path"))

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


regex_patterns = {k: re.compile(v) for k, v in config.get("regex_patterns", {}).items()}

# Function to process a single PDF file and extract text using OCR
def process_pdf(file_path):
    if not poppler_bin:
        raise RuntimeError("Poppler path is not configured")
    pages = convert_from_path(file_path, 500, poppler_path=Path(poppler_bin))
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
    threads = [threading.Thread(target=process_file_thread, daemon=True) for _ in range(num_threads)]
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
    """Thread-safe logging of messages to the GUI."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _insert():
        log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        log_area.yview(tk.END)

    if threading.current_thread() is threading.main_thread():
        _insert()
    else:
        window.after(0, _insert)


def check_dependencies():
    missing = []
    if not tesseract_cmd:
        missing.append("Tesseract")
    if not poppler_bin:
        missing.append("Poppler")
    if missing:
        msg = (
            "Missing dependencies: " + ", ".join(missing) +
            "\nPlease install them or configure their paths in Settings."
        )
        messagebox.showerror("Missing Dependencies", msg)

def open_settings():
    settings_win = tk.Toplevel(window)
    settings_win.title("Settings")

    tk.Label(settings_win, text="Tesseract Path:").grid(row=0, column=0, sticky="w", pady=2)
    tess_entry = tk.Entry(settings_win, width=60)
    tess_entry.insert(0, config.get("tesseract_path", ""))
    tess_entry.grid(row=0, column=1, pady=2)

    tk.Label(settings_win, text="Poppler Path:").grid(row=1, column=0, sticky="w", pady=2)
    pop_entry = tk.Entry(settings_win, width=60)
    pop_entry.insert(0, config.get("poppler_path", ""))
    pop_entry.grid(row=1, column=1, pady=2)

    tk.Label(settings_win, text="Regex Patterns (JSON):").grid(row=2, column=0, sticky="nw", pady=2)
    regex_text = scrolledtext.ScrolledText(settings_win, width=60, height=10)
    regex_text.insert(tk.END, json.dumps(config.get("regex_patterns", {}), indent=2))
    regex_text.grid(row=2, column=1, pady=2)

    def save():
        config["tesseract_path"] = tess_entry.get().strip()
        config["poppler_path"] = pop_entry.get().strip()
        try:
            patterns = json.loads(regex_text.get("1.0", tk.END))
            config["regex_patterns"] = patterns
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
            return
        save_config(config)
        global tesseract_cmd, poppler_bin, regex_patterns
        tesseract_cmd = detect_tesseract(config.get("tesseract_path"))
        poppler_bin = detect_poppler(config.get("poppler_path"))
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        regex_patterns = {k: re.compile(v) for k, v in config.get("regex_patterns", {}).items()}
        settings_win.destroy()

    tk.Button(settings_win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=5)

def open_help():
    help_win = tk.Toplevel(window)
    help_win.title("Help")
    text = scrolledtext.ScrolledText(help_win, width=80, height=25)
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        content = "README not found."
    text.insert(tk.END, content)
    text.configure(state="disabled")
    text.pack(fill=tk.BOTH, expand=True)

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

    window.after(100, check_dependencies)
    return window

selected_files = []  # Global variable to store selected files
output_folder = ""   # Global variable to store the output folder path

def main():
    setup_gui().mainloop()

if __name__ == "__main__":
    main()
