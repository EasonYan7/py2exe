import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import PyInstaller.__main__
import threading
import subprocess

class PyToExeConverter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python to EXE Converter")
        self.window.geometry("800x600")
        
        # Python file selection
        self.py_frame = ttk.LabelFrame(self.window, text="Python File", padding=10)
        self.py_frame.pack(fill="x", padx=10, pady=5)
        
        self.py_path = tk.StringVar()
        self.py_entry = ttk.Entry(self.py_frame, textvariable=self.py_path, width=50)
        self.py_entry.pack(side="left", padx=5)
        
        self.py_button = ttk.Button(self.py_frame, text="Browse", command=self.browse_python_file)
        self.py_button.pack(side="left")
        
        # Icon selection
        self.icon_frame = ttk.LabelFrame(self.window, text="Icon (Optional)", padding=10)
        self.icon_frame.pack(fill="x", padx=10, pady=5)
        
        self.use_icon = tk.BooleanVar()
        self.icon_check = ttk.Checkbutton(self.icon_frame, text="Use Custom Icon", variable=self.use_icon, command=self.toggle_icon_entry)
        self.icon_check.pack(side="left")
        
        self.icon_path = tk.StringVar()
        self.icon_entry = ttk.Entry(self.icon_frame, textvariable=self.icon_path, width=50, state="disabled")
        self.icon_entry.pack(side="left", padx=5)
        
        self.icon_button = ttk.Button(self.icon_frame, text="Browse", command=self.browse_icon, state="disabled")
        self.icon_button.pack(side="left")
        
        # Advanced options frame
        self.adv_frame = ttk.LabelFrame(self.window, text="Advanced Options", padding=10)
        self.adv_frame.pack(fill="x", padx=10, pady=5)
        
        self.console_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.adv_frame, text="Show Console Window", variable=self.console_var).pack(side="left", padx=5)
        
        self.one_file_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.adv_frame, text="One File", variable=self.one_file_var).pack(side="left", padx=5)
        
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.adv_frame, text="Debug Mode", variable=self.debug_var).pack(side="left", padx=5)
        
        # Output name
        self.name_frame = ttk.LabelFrame(self.window, text="Output Name", padding=10)
        self.name_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_name = tk.StringVar()
        self.name_entry = ttk.Entry(self.name_frame, textvariable=self.output_name, width=50)
        self.name_entry.pack(side="left", padx=5)
        
        # Output directory
        self.dir_frame = ttk.LabelFrame(self.window, text="Output Directory", padding=10)
        self.dir_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "dist"))
        self.dir_entry = ttk.Entry(self.dir_frame, textvariable=self.output_dir, width=50)
        self.dir_entry.pack(side="left", padx=5)
        
        self.dir_button = ttk.Button(self.dir_frame, text="Browse", command=self.browse_output_dir)
        self.dir_button.pack(side="left")
        
        # Convert button
        self.convert_button = ttk.Button(self.window, text="Convert to EXE", command=self.start_conversion)
        self.convert_button.pack(pady=10)
        
        # Console output
        self.console_frame = ttk.LabelFrame(self.window, text="Console Output", padding=10)
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.console = scrolledtext.ScrolledText(self.console_frame, height=10)
        self.console.pack(fill="both", expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ttk.Label(self.window, text="")
        self.status_label.pack()

    def browse_python_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if filename:
            self.py_path.set(filename)
            if not self.output_name.get():
                default_name = os.path.splitext(os.path.basename(filename))[0]
                self.output_name.set(default_name)

    def browse_icon(self):
        filename = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if filename:
            self.icon_path.set(filename)

    def browse_output_dir(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_dir.set(dirname)

    def toggle_icon_entry(self):
        state = "normal" if self.use_icon.get() else "disabled"
        self.icon_entry.config(state=state)
        self.icon_button.config(state=state)

    def update_console(self, text):
        self.console.insert(tk.END, text + '\n')
        self.console.see(tk.END)
        self.window.update()

    def start_conversion(self):
        # Run conversion in a separate thread
        threading.Thread(target=self.convert_to_exe, daemon=True).start()

    def convert_to_exe(self):
        if not self.py_path.get():
            messagebox.showerror("Error", "Please select a Python file!")
            return
            
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter an output name!")
            return
            
        if self.use_icon.get() and not self.icon_path.get():
            messagebox.showerror("Error", "Please select an icon file or uncheck the icon option!")
            return

        self.convert_button.config(state="disabled")
        self.progress["value"] = 0
        self.status_label.config(text="Converting... Please wait...")
        self.console.delete(1.0, tk.END)
        self.window.update()

        try:
            commands = [
                self.py_path.get(),
                f'--name={self.output_name.get()}',
                f'--distpath={self.output_dir.get()}'
            ]

            if self.one_file_var.get():
                commands.append('--onefile')
            
            if not self.console_var.get():
                commands.append('--windowed')
                
            if self.debug_var.get():
                commands.append('--debug=all')

            if self.use_icon.get():
                commands.extend(['--icon', self.icon_path.get()])

            # Create process
            process = subprocess.Popen(
                [sys.executable, '-m', 'PyInstaller'] + commands,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            # Read output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.update_console(output.strip())
                    if "Building EXE" in output:
                        self.progress["value"] = 50
                    elif "Building completed" in output:
                        self.progress["value"] = 100

            exe_path = os.path.join(self.output_dir.get(), self.output_name.get() + '.exe')
            if os.path.exists(exe_path):
                self.status_label.config(text="Conversion completed successfully!")
                self.update_console(f"\nEXE created successfully at:\n{exe_path}")
                messagebox.showinfo("Success", f"EXE file created successfully at:\n{exe_path}")
            else:
                raise Exception("EXE file not found after build")
            
        except Exception as e:
            self.progress["value"] = 0
            self.status_label.config(text="Conversion failed!")
            self.update_console(f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            self.convert_button.config(state="normal")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PyToExeConverter()
    app.run()
