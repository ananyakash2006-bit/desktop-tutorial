import sqlite3
from tkinter import ttk
from tkinter import Tk, Frame  # Add Tk and Frame import
from tkinter import messagebox  # Import messagebox for dialogs

root = Tk()  # Create the main window if not already created elsewhere

# The button frame and buttons should be created inside the LibraryApp class, not in the global scope.


# Remove this line, as 'self' is not defined in the global scope
# self.load_issues()


class LibraryApp:
	def __init__(self, db):
		self.db = db
		self.root = root
		self.btn_frame = Frame(self.root)
		self.btn_frame.pack(fill='x', padx=10)
		ttk.Button(self.btn_frame, text='Refresh', command=self.load_issues).pack(side='left')
		ttk.Button(self.btn_frame, text='Return Selected', command=self.return_selected_issue).pack(side='left', padx=5)
		# Initialize other widgets and variables here

	# ... other methods and initializations ...
		bid = self.issue_book_id.get().strip()
		if not bid:
			self.issue_book_label.config(text='')
			return
		try:
			bid = int(bid)
		except ValueError:
			self.issue_book_label.config(text='Invalid ID')
			return
		rows = self.db.get_books()
		for r in rows:
			if r[0] == bid:
				self.issue_book_label.config(text=f'{r[1]} - copies: {r[4]}')
				return
		self.issue_book_label.config(text='Not found')


class LibraryApp:
	# ... other methods and initializations ...

	def lookup_student(self):
		sid = self.issue_student_id.get().strip()
		if not sid:
			self.issue_student_label.config(text='')
			return
		try:
			sid = int(sid)
		except ValueError:
			self.issue_student_label.config(text='Invalid ID')
			return
		rows = self.db.get_students()
		for r in rows:
			if r[0] == sid:
				self.issue_student_label.config(text=f'{r[1]}')
				return
		self.issue_student_label.config(text='Not found')


def issue_book(self):
	try:
		bid = int(self.issue_book_id.get().strip())
		sid = int(self.issue_student_id.get().strip())
	except ValueError:
		messagebox.showerror('Error', 'Enter valid numeric IDs for book and student')
		return
	ok, info = self.db.issue_book(bid, sid)
	if ok:
		messagebox.showinfo('Success', 'Book issued')
		self.issue_book_id.delete(0, 'end')
		self.issue_student_id.delete(0, 'end')
		self.issue_book_label.config(text='')
		self.issue_student_label.config(text='')
		self.load_books()
		self.load_issues()
	else:
		messagebox.showerror('Error', f'Could not issue book: {info}')


def load_issues(self):
	for r in self.issues_tree.get_children():
		self.issues_tree.delete(r)
	rows = self.db.get_issues(only_open=True)
	for r in rows:
		self.issues_tree.insert('', 'end', values=r)


def return_selected_issue(self):
	sel = self.issues_tree.selection()
	if not sel:
		messagebox.showwarning('Warning', 'Select an issue record')
		return
	item = self.issues_tree.item(sel[0])
	issue_id = item['values'][0]
	if messagebox.askyesno('Confirm', 'Mark selected as returned?'):
		ok, info = self.db.return_book(issue_id)
		if ok:
			messagebox.showinfo('Success', 'Book returned')
			self.load_books()
			self.load_issues()
		else:
			messagebox.showerror('Error', f'Could not return book: {info}')


# ---------- Run App ----------
# Import or define Database before using it
try:
	from database import Database  # pyright: ignore[reportMissingImports] # Make sure you have a database.py file with Database class
except ImportError:
	messagebox.showerror('Error', 'Could not import Database. Ensure database.py is in the same directory.')
	exit(1)

if __name__ == '__main__':
	db = Database()
	app = LibraryApp(db)
	app.mainloop()