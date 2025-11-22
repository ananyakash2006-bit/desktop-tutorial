import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# =========================
#   DATA & CORE LOGIC
# =========================

DATA_FILE = Path("library_data.json")

def load_data():
    """Load data from JSON file or return default structure."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"books": [], "issued": []}

def save_data(data):
    """Save current data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_book_id(data):
    """Generate a new unique book ID."""
    if not data["books"]:
        return 1
    return max(book["id"] for book in data["books"]) + 1


# =========================
#         GUI APP
# =========================

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("📚 Library Management System")
        self.geometry("900x500")
        self.resizable(False, False)

        # App data
        self.data = load_data()

        # Main style
        self.configure(bg="#f5f5f5")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.create_widgets()

    # ---------- UI Layout ----------

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill="x")

        title_lbl = ttk.Label(
            header_frame,
            text="Library Management System",
            style="Header.TLabel"
        )
        title_lbl.pack(side="left")

        sub_lbl = ttk.Label(
            header_frame,
            text="Manage books • Issue & return • Search",
            foreground="#555"
        )
        sub_lbl.pack(side="left", padx=10)

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.books_tab = ttk.Frame(notebook, padding=10)
        self.issued_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.books_tab, text="📘 Books")
        notebook.add(self.issued_tab, text="📄 Issued Books")

        self.build_books_tab()
        self.build_issued_tab()

    # ---------- Books Tab ----------

    def build_books_tab(self):
        # Top section: Add Book
        add_frame = ttk.LabelFrame(self.books_tab, text="Add New Book", padding=10)
        add_frame.pack(fill="x")

        ttk.Label(add_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(add_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky="w", pady=2, padx=5)

        ttk.Label(add_frame, text="Author:").grid(row=0, column=2, sticky="w", pady=2)
        self.author_entry = ttk.Entry(add_frame, width=25)
        self.author_entry.grid(row=0, column=3, sticky="w", pady=2, padx=5)

        ttk.Label(add_frame, text="Total copies:").grid(row=0, column=4, sticky="w", pady=2)
        self.copies_entry = ttk.Entry(add_frame, width=10)
        self.copies_entry.grid(row=0, column=5, sticky="w", pady=2, padx=5)

        add_btn = ttk.Button(add_frame, text="➕ Add Book", command=self.gui_add_book)
        add_btn.grid(row=0, column=6, padx=10)

        for i in range(7):
            add_frame.columnconfigure(i, weight=0)

        # Search section
        search_frame = ttk.LabelFrame(self.books_tab, text="Search", padding=10)
        search_frame.pack(fill="x", pady=(10, 5))

        ttk.Label(search_frame, text="Title/Author:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, sticky="w", padx=5)

        search_btn = ttk.Button(search_frame, text="🔍 Search", command=self.gui_search_books)
        search_btn.grid(row=0, column=2, padx=5)

        show_all_btn =
