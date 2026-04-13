import tkinter as tk
from tkinter import filedialog, messagebox
import sv_ttk
import shuffler
import os

class StudentShufflerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICSK Student Shuffler")
        self.root.geometry("700x700")

        self.class_entries = []

        # Scrollable container
        container = tk.Frame(root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.content = tk.Frame(self.scrollable_frame)
        self.content.pack(padx=30, pady=20, fill="x")

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Frame for inputs
        self.main_frame = tk.Frame(self.content)
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
        self.class_frame = tk.Frame(self.content)
        self.class_frame.pack(pady=10)

        # Input files
        self.input_files = []
        self.input_files_var = tk.StringVar(value="No files selected")
        tk.Label(self.content, text="Select student excel files").pack(pady=(10,2))

        tk.Button(
            self.content,
            text="Browse",
            command=self.browse_input_files
        ).pack(pady=5)

        # Label to print the chosen input directory
        tk.Label(
            self.content,
            textvariable=self.input_files_var,
            wraplength=600,
            fg="gray"
        ).pack(pady=(2, 10))

        # Output file
        self.output_file = ""
        self.output_file_var = tk.StringVar(value="No file selected")
        tk.Label(self.content, text="Choose where the final Excel file should be saved").pack(pady=(10, 2))

        tk.Button(
            self.content,
            text="Save As",
            command=self.browse_output_file
        ).pack(pady=5)

        # Label to print the output file
        tk.Label(
            self.content,
            textvariable=self.output_file_var,
            wraplength=600,
            fg="gray"
        ).pack(pady=(2, 10))

        # Submit button
        tk.Button(
            self.content,
            text="Shuffle",
            command=self.submit
        ).pack(pady=20)

        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

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

    def browse_input_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )

        if files:
            self.input_files = list(files)
            display = "\n".join(os.path.basename(f) for f in self.input_files)
            self.input_files_var.set(f"Selected:\n{display}")

    def browse_output_file(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file:
            self.output_file = file
            self.output_file_var.set(f"Selected: {file}")

    def submit(self):
        try:
            num_classes = int(self.num_classes_entry.get())
            class_sizes = [int(entry.get()) for entry in self.class_entries]
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer values.")
            return

        if not self.input_files or not self.output_file:
            messagebox.showerror("Error", "Please select input files and output location.")
            return
        
        try:
            shuffler.run_shuffler(
                num_classes=num_classes,
                class_sizes=class_sizes,
                files=self.input_files,
                output_file=self.output_file
            )
            messagebox.showinfo("Success", "Student shuffling completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Shuffling failed: \n{e}")

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentShufflerApp(root)
    sv_ttk.set_theme("light")
    root.mainloop()