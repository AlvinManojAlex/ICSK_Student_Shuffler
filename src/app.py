import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class StudentShufflerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICSK Student Shuffler")
        self.root.geometry("600x400")

        self.class_entries = []

        # Heading
        tk.Label(
            root,
            text="ICSK Student Shuffler",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # Frame for inputs
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=10)

        # Number of classes
        tk.Label(self.main_frame, text="Number of classes:").grid(row=0, column=0, sticky="w")
        self.num_classes_entry = tk.Entry(self.main_frame, width=10)
        self.num_classes_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            self.main_frame,
            text="Set Classes",
            command=self.create_class_inputs
        ).grid(row=0, column=2, padx=5)

        # Frame for dynamic class sizes
        self.class_frame = tk.Frame(root)
        self.class_frame.pack(pady=10)

        # Input directory
        tk.Label(root, text="File locations (Input directory):").pack(anchor="w", padx=40)
        self.input_dir_entry = tk.Entry(root, width=50)
        self.input_dir_entry.pack(padx=40)

        tk.Button(
            root,
            text="Browse",
            command=self.browse_input_directory
        ).pack(pady=5)

        # Output file
        tk.Label(root, text="Location for final excel sheet").pack(anchor="w", padx=40)
        self.output_file_entry = tk.Entry(root, width=50)
        self.output_file_entry.pack(padx=40)

        tk.Button(
            root,
            text="Save As",
            command=self.browse_output_file
        ).pack(pady=5)

        # Submit button
        tk.Button(
            root,
            text="Submit",
            command=self.submit
        ).pack(pady=20)

    def create_class_inputs(self):
        # Clear previous inputs
        for widget in self.class_frame.winfo_children():
            widget.destroy()
        self.class_entries.clear()

        try:
            num_classes = int(self.num_classes_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of classes.")
            return

        for i in range(num_classes):
            # To print it as "Class A", "Class B", etc.
            class_name = chr(65 + i)
            tk.Label(
                self.class_frame,
                text=f"Class size of section {class_name}:"
            ).grid(row=i, column=0, sticky="w", padx=5, pady=2)

            entry = tk.Entry(self.class_frame, width=10)
            entry.grid(row=i, column=1, padx=5)
            self.class_entries.append(entry)

    def browse_input_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, directory)

    def browse_output_file(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file)

    def submit(self):
        try:
            num_classes = int(self.num_classes_entry.get())
            class_sizes = [int(entry.get()) for entry in self.class_entries]
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer values.")
            return

        input_dir = self.input_dir_entry.get()
        output_file = self.output_file_entry.get()

        if not input_dir or not output_file:
            messagebox.showerror("Error", "Please select input and output locations.")
            return
        
        # Path to shuffler script
        shuffler_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "shuffler.py"
        )

        # Command to execute the shuffler script
        command = [
            sys.executable,
            shuffler_path,
            str(num_classes),
            *map(str, class_sizes),
            "--dir",
            input_dir,
            "--name",
            output_file
        ]

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Student shuffling completed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Shuffling failed:\n{e}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentShufflerApp(root)
    root.mainloop()