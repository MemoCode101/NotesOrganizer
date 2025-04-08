import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import datetime
import re

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("1100x700")
        
        # Define color scheme
        self.colors = {
            "primary": "#3498db",       # Blue
            "secondary": "#2ecc71",     # Green
            "accent": "#e74c3c",        # Red
            "bg_light": "#f5f5f5",      # Light gray
            "bg_dark": "#ecf0f1",       # Slightly darker gray
            "text_dark": "#2c3e50",     # Dark blue/gray
            "text_light": "#7f8c8d"     # Medium gray
        }
        
        # Configure styles
        self.configure_styles()
        
        # Set up the main container with background color
        self.root.configure(bg=self.colors["bg_light"])
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL, style="App.TPanedwindow")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames
        self.sidebar_frame = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.notes_list_frame = ttk.Frame(self.main_container, style="NotesList.TFrame")
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        
        self.main_container.add(self.sidebar_frame, weight=1)
        self.main_container.add(self.notes_list_frame, weight=1)
        self.main_container.add(self.content_frame, weight=3)
        
        # Initialize variables
        self.current_subject = None
        self.current_note = None
        self.notes_data = []
        self.subjects = []
        
        # Set up UI components
        self.setup_sidebar()
        self.setup_notes_list()
        self.setup_content_area()
        
        # Load existing notes
        self.load_notes()
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        
        # Configure fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        heading_font = font.Font(family="Segoe UI", size=12, weight="bold")
        
        # Configure frame styles
        style.configure("Sidebar.TFrame", background=self.colors["bg_dark"])
        style.configure("NotesList.TFrame", background=self.colors["bg_light"])
        style.configure("Content.TFrame", background=self.colors["bg_light"])
        style.configure("App.TPanedwindow", background=self.colors["bg_light"])
        
        # Configure button styles
        style.configure("TButton", 
                        font=("Segoe UI", 10),
                        background=self.colors["primary"],
                        foreground="white")
        
        style.configure("Primary.TButton", 
                        background=self.colors["primary"],
                        foreground="white")
        
        style.configure("Secondary.TButton", 
                        background=self.colors["secondary"],
                        foreground="white")
        
        style.configure("Accent.TButton", 
                        background=self.colors["accent"],
                        foreground="white")
        
        style.configure("Folder.TButton", 
                        font=("Segoe UI", 10),
                        background=self.colors["bg_dark"],
                        foreground=self.colors["text_dark"])
        
        style.map("TButton",
                 background=[('active', self.colors["primary"])],
                 foreground=[('active', 'white')])
        
        # Configure label styles
        style.configure("Header.TLabel", 
                        font=("Segoe UI", 14, "bold"),
                        background=self.colors["bg_dark"],
                        foreground=self.colors["primary"])
        
        style.configure("Subheader.TLabel", 
                        font=("Segoe UI", 12, "bold"),
                        background=self.colors["bg_light"],
                        foreground=self.colors["text_dark"])
        
        style.configure("NoteTitle.TLabel", 
                        font=("Segoe UI", 14, "bold"),
                        background=self.colors["bg_light"],
                        foreground=self.colors["text_dark"])
        
        style.configure("NoteDate.TLabel", 
                        font=("Segoe UI", 9),
                        background=self.colors["bg_light"],
                        foreground=self.colors["text_light"])
        
        # Configure entry styles
        style.configure("TEntry", 
                        font=("Segoe UI", 10),
                        fieldbackground="white")
    
    def setup_sidebar(self):
        # App title
        title_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        title_frame.pack(fill=tk.X, pady=(10, 20))
        
        app_title = ttk.Label(title_frame, text="📝 Notes App", style="Header.TLabel")
        app_title.pack(pady=10)
        
        # Search box
        search_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="🔍 Search:", background=self.colors["bg_dark"]).pack(anchor=tk.W, pady=(5, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_notes)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=5)
        
        # New note button
        button_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        new_note_btn = ttk.Button(button_frame, text="➕ New Note", command=self.new_note, style="Primary.TButton")
        new_note_btn.pack(fill=tk.X, pady=5)
        
        # Separator
        separator = ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Subjects list
        folders_label = ttk.Label(self.sidebar_frame, text="📁 Folders", style="Subheader.TLabel")
        folders_label.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        # Scrollable frame for subjects
        self.subjects_canvas = tk.Canvas(self.sidebar_frame, bg=self.colors["bg_dark"], highlightthickness=0)
        self.subjects_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.subjects_frame = ttk.Frame(self.subjects_canvas, style="Sidebar.TFrame")
        scrollbar = ttk.Scrollbar(self.sidebar_frame, orient=tk.VERTICAL, command=self.subjects_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.subjects_canvas.configure(yscrollcommand=scrollbar.set)
        self.subjects_canvas.create_window((0, 0), window=self.subjects_frame, anchor=tk.NW, width=180)
        self.subjects_frame.bind("<Configure>", lambda e: self.subjects_canvas.configure(scrollregion=self.subjects_canvas.bbox("all")))
        
        # All notes option
        self.all_notes_btn = ttk.Button(
            self.subjects_frame, 
            text="📋 All Notes", 
            command=lambda: self.select_subject(None),
            style="Folder.TButton"
        )
        self.all_notes_btn.pack(fill=tk.X, pady=2)
    
    def setup_notes_list(self):
        # Notes list header frame
        header_frame = ttk.Frame(self.notes_list_frame, style="NotesList.TFrame")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.notes_list_header = ttk.Label(header_frame, text="All Notes", style="Subheader.TLabel")
        self.notes_list_header.pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(self.notes_list_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Notes list with custom styling
        self.notes_listbox_frame = ttk.Frame(self.notes_list_frame, style="NotesList.TFrame")
        self.notes_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas and scrollbar for smooth scrolling
        self.notes_canvas = tk.Canvas(self.notes_listbox_frame, bg=self.colors["bg_light"], highlightthickness=0)
        self.notes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        notes_scrollbar = ttk.Scrollbar(self.notes_listbox_frame, orient=tk.VERTICAL, command=self.notes_canvas.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notes_canvas.configure(yscrollcommand=notes_scrollbar.set)
        
        # Frame to hold note items
        self.notes_items_frame = ttk.Frame(self.notes_canvas, style="NotesList.TFrame")
        self.notes_canvas.create_window((0, 0), window=self.notes_items_frame, anchor=tk.NW, width=230)
        self.notes_items_frame.bind("<Configure>", lambda e: self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all")))
    
    def setup_content_area(self):
        # Content area for viewing/editing notes
        self.content_view_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.content_view_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Default message when no note is selected
        default_frame = ttk.Frame(self.content_view_frame, style="Content.TFrame")
        default_frame.pack(expand=True)
        
        default_icon = ttk.Label(
            default_frame, 
            text="📝", 
            font=("Segoe UI", 36),
            background=self.colors["bg_light"],
            foreground=self.colors["primary"]
        )
        default_icon.pack(pady=10)
        
        self.default_message = ttk.Label(
            default_frame, 
            text="Select a note or create a new one", 
            font=("Segoe UI", 14),
            background=self.colors["bg_light"],
            foreground=self.colors["text_dark"]
        )
        self.default_message.pack(expand=True)
        
        # Note editing frame (initially hidden)
        self.note_edit_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        
        edit_header = ttk.Label(
            self.note_edit_frame, 
            text="✏️ Edit Note", 
            style="NoteTitle.TLabel"
        )
        edit_header.pack(anchor=tk.W, padx=5, pady=(10, 20))
        
        # Subject entry
        ttk.Label(
            self.note_edit_frame, 
            text="Subject:", 
            font=("Segoe UI", 11, "bold"),
            background=self.colors["bg_light"],
            foreground=self.colors["text_dark"]
        ).pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.subject_var = tk.StringVar()
        self.subject_entry = ttk.Entry(self.note_edit_frame, textvariable=self.subject_var, font=("Segoe UI", 11))
        self.subject_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Content text area
        ttk.Label(
            self.note_edit_frame, 
            text="Content:", 
            font=("Segoe UI", 11, "bold"),
            background=self.colors["bg_light"],
            foreground=self.colors["text_dark"]
        ).pack(anchor=tk.W, padx=5, pady=(15, 0))
        
        self.content_text = scrolledtext.ScrolledText(
            self.note_edit_frame, 
            wrap=tk.WORD, 
            height=20,
            font=("Segoe UI", 11),
            background="white",
            foreground=self.colors["text_dark"]
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.note_edit_frame, style="Content.TFrame")
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        save_btn = ttk.Button(buttons_frame, text="💾 Save", command=self.save_note, style="Secondary.TButton")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(buttons_frame, text="❌ Cancel", command=self.cancel_edit)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Note view frame (initially hidden)
        self.note_view_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        
        # Note title and date
        self.view_title_frame = ttk.Frame(self.note_view_frame, style="Content.TFrame")
        self.view_title_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.view_title = ttk.Label(
            self.view_title_frame, 
            text="", 
            style="NoteTitle.TLabel"
        )
        self.view_title.pack(side=tk.LEFT)
        
        self.view_date = ttk.Label(
            self.view_title_frame, 
            text="", 
            style="NoteDate.TLabel"
        )
        self.view_date.pack(side=tk.RIGHT)
        
        # Separator
        view_separator = ttk.Separator(self.note_view_frame, orient=tk.HORIZONTAL)
        view_separator.pack(fill=tk.X, padx=5, pady=10)
        
        # Note content
        self.view_content = scrolledtext.ScrolledText(
            self.note_view_frame, 
            wrap=tk.WORD, 
            height=20,
            font=("Segoe UI", 11),
            background="white",
            foreground=self.colors["text_dark"]
        )
        self.view_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.view_content.config(state=tk.DISABLED)
        
        # Action buttons
        view_buttons_frame = ttk.Frame(self.note_view_frame, style="Content.TFrame")
        view_buttons_frame.pack(fill=tk.X, padx=5, pady=15)
        
        edit_btn = ttk.Button(view_buttons_frame, text="✏️ Edit", command=self.edit_note, style="Primary.TButton")
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(view_buttons_frame, text="🗑️ Delete", command=self.delete_note, style="Accent.TButton")
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(view_buttons_frame, text="📤 Export", command=self.export_note)
        export_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_note_item(self, note, index):
        """Create a styled note item for the notes list"""
        # Create a frame for the note item with padding and border
        item_frame = ttk.Frame(self.notes_items_frame, style="NotesList.TFrame")
        item_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Create a card-like effect with a border and background
        card = tk.Frame(
            item_frame, 
            bg="white", 
            bd=1, 
            relief=tk.SOLID, 
            highlightbackground=self.colors["bg_dark"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, padx=2, pady=2)
        
        # Add padding inside the card
        inner_frame = tk.Frame(card, bg="white")
        inner_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # Subject label with emoji
        subject_frame = tk.Frame(inner_frame, bg="white")
        subject_frame.pack(fill=tk.X, anchor=tk.W)
        
        subject_emoji = "📝"
        subject_label = tk.Label(
            subject_frame, 
            text=f"{subject_emoji} {note['subject']}", 
            font=("Segoe UI", 10, "bold"),
            bg="white", 
            fg=self.colors["primary"]
        )
        subject_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Date in small text
        date_label = tk.Label(
            subject_frame, 
            text=note["created_at"].strftime("%m/%d/%Y"), 
            font=("Segoe UI", 8),
            bg="white", 
            fg=self.colors["text_light"]
        )
        date_label.pack(side=tk.RIGHT, anchor=tk.E)
        
        # Preview of content
        preview_text = note["content"][:50] + ("..." if len(note["content"]) > 50 else "")
        preview_label = tk.Label(
            inner_frame, 
            text=preview_text, 
            font=("Segoe UI", 9),
            bg="white", 
            fg=self.colors["text_dark"],
            justify=tk.LEFT,
            wraplength=200
        )
        preview_label.pack(fill=tk.X, anchor=tk.W, pady=(5, 0))
        
        # Make the whole card clickable
        for widget in [card, inner_frame, subject_frame, subject_label, date_label, preview_label]:
            widget.bind("<Button-1>", lambda e, idx=index: self.select_note_by_index(idx))
            widget.bind("<Enter>", lambda e, f=card: self.on_card_hover(f, True))
            widget.bind("<Leave>", lambda e, f=card: self.on_card_hover(f, False))
    
    def on_card_hover(self, card, is_hover):
        """Change card appearance on hover"""
        if is_hover:
            card.config(highlightbackground=self.colors["primary"], highlightthickness=2)
        else:
            card.config(highlightbackground=self.colors["bg_dark"], highlightthickness=1)
    
    def load_notes(self):
        """Load all notes from the file system"""
        self.notes_data = []
        self.subjects = []
        
        # Create notes directory if it doesn't exist
        if not os.path.exists("notes"):
            os.makedirs("notes")
        
        # Get all subject folders
        for subject_folder in os.listdir("notes"):
            folder_path = os.path.join("notes", subject_folder)
            if os.path.isdir(folder_path):
                self.subjects.append(subject_folder)
                
                # Get all notes in this subject folder
                for note_file in os.listdir(folder_path):
                    if note_file.endswith(".txt"):
                        file_path = os.path.join(folder_path, note_file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Get creation date from file metadata
                        created_at = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        # Add note to the list
                        self.notes_data.append({
                            "id": note_file[:-4],  # Remove .txt extension
                            "subject": subject_folder,
                            "content": content,
                            "created_at": created_at,
                            "file_path": file_path
                        })
        
        # Update the UI
        self.update_subjects_list()
        self.update_notes_list()
    
    def update_subjects_list(self):
        """Update the subjects list in the sidebar"""
        # Clear existing subject buttons (except All Notes)
        for widget in self.subjects_frame.winfo_children():
            if widget != self.all_notes_btn:
                widget.destroy()
        
        # Add a button for each subject
        for subject in sorted(self.subjects):
            subject_btn = ttk.Button(
                self.subjects_frame, 
                text=f"📁 {subject}",
                command=lambda s=subject: self.select_subject(s),
                style="Folder.TButton"
            )
            subject_btn.pack(fill=tk.X, pady=2)
    
    def update_notes_list(self):
        """Update the notes list based on the current subject and search query"""
        # Clear all note items
        for widget in self.notes_items_frame.winfo_children():
            widget.destroy()
        
        # Filter notes by subject and search query
        search_query = self.search_var.get().lower()
        filtered_notes = []
        
        for note in self.notes_data:
            # Filter by subject if a subject is selected
            if self.current_subject and note["subject"] != self.current_subject:
                continue
            
            # Filter by search query if there is one
            if search_query and search_query not in note["subject"].lower() and search_query not in note["content"].lower():
                continue
            
            filtered_notes.append(note)
        
        # Sort notes by creation date (newest first)
        filtered_notes.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Add notes to the list
        for i, note in enumerate(filtered_notes):
            self.create_note_item(note, i)
        
        # Update the header
        subject_text = self.current_subject if self.current_subject else "All Notes"
        self.notes_list_header.config(text=f"{subject_text} ({len(filtered_notes)})")
        
        # Clear the current note
        self.current_note = None
        self.show_default_view()
        
        # Update the canvas scroll region
        self.notes_items_frame.update_idletasks()
        self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all"))
    
    def select_subject(self, subject):
        """Select a subject to filter notes"""
        self.current_subject = subject
        self.update_notes_list()
    
    def search_notes(self, *args):
        """Search notes based on the search query"""
        self.update_notes_list()
    
    def select_note_by_index(self, index):
        """Select a note by its index in the filtered list"""
        # Get the filtered notes
        search_query = self.search_var.get().lower()
        filtered_notes = []
        
        for note in self.notes_data:
            if self.current_subject and note["subject"] != self.current_subject:
                continue
            if search_query and search_query not in note["subject"].lower() and search_query not in note["content"].lower():
                continue
            filtered_notes.append(note)
        
        # Sort notes by creation date (newest first)
        filtered_notes.sort(key=lambda x: x["created_at"], reverse=True)
        
        if index < len(filtered_notes):
            self.current_note = filtered_notes[index]
            self.show_note_view()
    
    def show_default_view(self):
        """Show the default view when no note is selected"""
        self.note_edit_frame.pack_forget()
        self.note_view_frame.pack_forget()
        self.content_view_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def show_note_view(self):
        """Show the note view for the current note"""
        if not self.current_note:
            return
        
        self.content_view_frame.pack_forget()
        self.note_edit_frame.pack_forget()
        self.note_view_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Update the view with the note data
        self.view_title.config(text=f"📝 {self.current_note['subject']}")
        self.view_date.config(text=f"Created: {self.current_note['created_at'].strftime('%Y-%m-%d %H:%M')}")
        
        self.view_content.config(state=tk.NORMAL)
        self.view_content.delete(1.0, tk.END)
        self.view_content.insert(tk.END, self.current_note["content"])
        self.view_content.config(state=tk.DISABLED)
    
    def show_note_edit(self, is_new=False):
        """Show the note edit form"""
        self.content_view_frame.pack_forget()
        self.note_view_frame.pack_forget()
        self.note_edit_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        if is_new:
            # Clear the form for a new note
            self.subject_var.set("")
            self.content_text.delete(1.0, tk.END)
            
            # Pre-fill the subject if a subject is selected
            if self.current_subject:
                self.subject_var.set(self.current_subject)
        else:
            # Fill the form with the current note data
            self.subject_var.set(self.current_note["subject"])
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, self.current_note["content"])
    
    def new_note(self):
        """Create a new note"""
        self.current_note = None
        self.show_note_edit(is_new=True)
    
    def edit_note(self):
        """Edit the current note"""
        if not self.current_note:
            return
        self.show_note_edit(is_new=False)
    
    def save_note(self):
        """Save the current note"""
        subject = self.subject_var.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not subject:
            messagebox.showerror("Error", "Subject cannot be empty")
            return
        
        if not content:
            messagebox.showerror("Error", "Content cannot be empty")
            return
        
        # Create a valid filename from the subject
        valid_subject = re.sub(r'[\\/*?:"<>|]', "_", subject)
        
        # Create the subject folder if it doesn't exist
        subject_folder = os.path.join("notes", valid_subject)
        if not os.path.exists(subject_folder):
            os.makedirs(subject_folder)
        
        # Generate a unique ID for the note if it's new
        if not self.current_note:
            note_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = os.path.join(subject_folder, f"{note_id}.txt")
        else:
            # If we're editing an existing note
            if self.current_note["subject"] != valid_subject:
                # Subject has changed, so we need to move the file
                note_id = self.current_note["id"]
                file_path = os.path.join(subject_folder, f"{note_id}.txt")
                
                # Delete the old file
                if os.path.exists(self.current_note["file_path"]):
                    os.remove(self.current_note["file_path"])
            else:
                # Subject hasn't changed, use the existing file path
                file_path = self.current_note["file_path"]
        
        # Save the note to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Reload all notes
        self.load_notes()
        
        # Show the default view
        self.show_default_view()
    
    def cancel_edit(self):
        """Cancel editing and return to the previous view"""
        if self.current_note:
            self.show_note_view()
        else:
            self.show_default_view()
    
    def delete_note(self):
        """Delete the current note"""
        if not self.current_note:
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?")
        if not confirm:
            return
        
        # Delete the file
        if os.path.exists(self.current_note["file_path"]):
            os.remove(self.current_note["file_path"])
        
        # Reload all notes
        self.load_notes()
        
        # Show the default view
        self.show_default_view()
    
    def export_note(self):
        """Export the current note to a text file in a user-specified location"""
        if not self.current_note:
            return
        
        from tkinter import filedialog
        
        # Ask the user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.current_note['subject']}.txt"
        )
        
        if file_path:
            # Copy the note content to the selected file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.current_note["content"])
            
            messagebox.showinfo("Export Successful", f"Note exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
