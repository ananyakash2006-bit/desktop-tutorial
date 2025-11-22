import json
from pathlib import Path

# Data will be stored in this JSON file
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

def add_book(data):
    print("\n=== Add New Book ===")
    title = input("Enter title: ").strip()
    author = input("Enter author: ").strip()
    try:
        total_copies = int(input("Total copies: "))
    except ValueError:
        print("❌ Invalid number. Book not added.")
        return

    book = {
        "id": generate_book_id(data),
        "title": title,
        "author": author,
        "total_copies": total_copies,
        "available_copies": total_copies,
    }
    data["books"].append(book)
    save_data(data)
    print(f"✅ Book added with ID: {book['id']}")

def list_books(data):
    print("\n=== All Books ===")
    if not data["books"]:
        print("No books in library.")
        return

    print(f"{'ID':<5} {'Title':<25} {'Author':<20} {'Avail/Total':<10}")
    print("-" * 65)
    for b in data["books"]:
        print(f"{b['id']:<5} {b['title']:<25} {b['author']:<20} "
              f"{b['available_copies']}/{b['total_copies']}")

def search_book(data):
    print("\n=== Search Book ===")
    keyword = input("Enter title or author keyword: ").strip().lower()
    results = [
        b for b in data["books"]
        if keyword in b["title"].lower() or keyword in b["author"].lower()
    ]

    if not results:
        print("No matching books found.")
        return

    for b in results:
        print(f"ID: {b['id']} | {b['title']} by {b['author']} "
              f"| Avail: {b['available_copies']}")

def issue_book(data):
    print("\n=== Issue Book ===")
    try:
        book_id = int(input("Enter book ID: "))
    except ValueError:
        print("❌ Invalid ID.")
        return

    student = input("Student name: ").strip()

    # find book
    book = next((b for b in data["books"] if b["id"] == book_id), None)
    if not book:
        print("Book not found.")
        return

    if book["available_copies"] <= 0:
        print("No copies available.")
        return

    # record issue
    issue_record = {
        "book_id": book_id,
        "student": student,
    }
    data["issued"].append(issue_record)
    book["available_copies"] -= 1
    save_data(data)
    print(f"✅ Issued '{book['title']}' to {student}")

def return_book(data):
    print("\n=== Return Book ===")
    try:
        book_id = int(input("Enter book ID: "))
    except ValueError:
        print("❌ Invalid ID.")
        return

    student = input("Student name: ").strip()

    # find issue record
    for i, rec in enumerate(data["issued"]):
        if rec["book_id"] == book_id and rec["student"].lower() == student.lower():
            # remove record
            data["issued"].pop(i)

            # increment book copies
            book = next((b for b in data["books"] if b["id"] == book_id), None)
            if book:
                book["available_copies"] += 1

            save_data(data)
            print("✅ Book returned successfully.")
            return

    print("No matching issue record found.")

def view_issued(data):
    print("\n=== Issued Books ===")
    if not data["issued"]:
        print("No books are issued.")
        return

    for rec in data["issued"]:
        book = next((b for b in data["books"] if b["id"] == rec["book_id"]), None)
        title = book["title"] if book else "Unknown"
        print(f"Book ID: {rec['book_id']} | Title: {title} | Student: {rec['student']}")

def main():
    data = load_data()
    while True:
        print("\n=== Library Management System ===")
        print("1. Add book")
        print("2. List all books")
        print("3. Search book")
        print("4. Issue book")
        print("5. Return book")
        print("6. View issued books")
        print("0. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_book(data)
        elif choice == "2":
            list_books(data)
        elif choice == "3":
            search_book(data)
        elif choice == "4":
            issue_book(data)
        elif choice == "5":
            return_book(data)
        elif choice == "6":
            view_issued(data)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()
