import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import re

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("1000x600")
        
        # Set up the main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frames
        self.sidebar_frame = ttk.Frame(self.main_container, width=200)
        self.notes_list_frame = ttk.Frame(self.main_container, width=250)
        self.content_frame = ttk.Frame(self.main_container)
        
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
    
    def setup_sidebar(self):
        # App title
        ttk.Label(self.sidebar_frame, text="Notes App", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Search box
        ttk.Label(self.sidebar_frame, text="Search:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_notes)
        search_entry = ttk.Entry(self.sidebar_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # New note button
        new_note_btn = ttk.Button(self.sidebar_frame, text="New Note", command=self.new_note)
        new_note_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Subjects list
        ttk.Label(self.sidebar_frame, text="Folders:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        # All notes option
        self.subjects_frame = ttk.Frame(self.sidebar_frame)
        self.subjects_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.all_notes_btn = ttk.Button(self.subjects_frame, text="All Notes", command=lambda: self.select_subject(None))
        self.all_notes_btn.pack(fill=tk.X, pady=2)
    
    def setup_notes_list(self):
        # Notes list header
        self.notes_list_header = ttk.Label(self.notes_list_frame, text="All Notes", font=("Arial", 10, "bold"))
        self.notes_list_header.pack(anchor=tk.W, padx=5, pady=5)
        
        # Notes list
        self.notes_listbox_frame = ttk.Frame(self.notes_list_frame)
        self.notes_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notes_listbox = tk.Listbox(self.notes_listbox_frame, selectmode=tk.SINGLE)
        self.notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)
        
        # Scrollbar for notes list
        notes_scrollbar = ttk.Scrollbar(self.notes_listbox_frame, orient=tk.VERTICAL, command=self.notes_listbox.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_listbox.config(yscrollcommand=notes_scrollbar.set)
    
    def setup_content_area(self):
        # Content area for viewing/editing notes
        self.content_view_frame = ttk.Frame(self.content_frame)
        self.content_view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Default message when no note is selected
        self.default_message = ttk.Label(self.content_view_frame, text="Select a note or create a new one", font=("Arial", 12))
        self.default_message.pack(expand=True)
        
        # Note editing frame (initially hidden)
        self.note_edit_frame = ttk.Frame(self.content_frame)
        
        # Subject entry
        ttk.Label(self.note_edit_frame, text="Subject:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        self.subject_var = tk.StringVar()
        self.subject_entry = ttk.Entry(self.note_edit_frame, textvariable=self.subject_var)
        self.subject_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Content text area
        ttk.Label(self.note_edit_frame, text="Content:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        self.content_text = scrolledtext.ScrolledText(self.note_edit_frame, wrap=tk.WORD, height=20)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.note_edit_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        save_btn = ttk.Button(buttons_frame, text="Save", command=self.save_note)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=self.cancel_edit)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Note view frame (initially hidden)
        self.note_view_frame = ttk.Frame(self.content_frame)
        
        # Note title and date
        self.view_title_frame = ttk.Frame(self.note_view_frame)
        self.view_title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.view_title = ttk.Label(self.view_title_frame, text="", font=("Arial", 14, "bold"))
        self.view_title.pack(side=tk.LEFT)
        
        self.view_date = ttk.Label(self.view_title_frame, text="")
        self.view_date.pack(side=tk.RIGHT)
        
        # Note content
        self.view_content = scrolledtext.ScrolledText(self.note_view_frame, wrap=tk.WORD, height=20)
        self.view_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.view_content.config(state=tk.DISABLED)
        
        # Action buttons
        view_buttons_frame = ttk.Frame(self.note_view_frame)
        view_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        edit_btn = ttk.Button(view_buttons_frame, text="Edit", command=self.edit_note)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(view_buttons_frame, text="Delete", command=self.delete_note)
        delete_btn.pack(side=tk.LEFT, padx=5)
    
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
                text=subject,
                command=lambda s=subject: self.select_subject(s)
            )
            subject_btn.pack(fill=tk.X, pady=2)
    
    def update_notes_list(self):
        """Update the notes list based on the current subject and search query"""
        # Clear the listbox
        self.notes_listbox.delete(0, tk.END)
        
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
        
        # Add notes to the listbox
        for note in filtered_notes:
            # Format the note title for display
            display_text = f"{note['subject']}: {note['content'][:30]}..."
            self.notes_listbox.insert(tk.END, display_text)
        
        # Update the header
        subject_text = self.current_subject if self.current_subject else "All Notes"
        self.notes_list_header.config(text=f"{subject_text} ({len(filtered_notes)})")
        
        # Clear the current note
        self.current_note = None
        self.show_default_view()
    
    def select_subject(self, subject):
        """Select a subject to filter notes"""
        self.current_subject = subject
        self.update_notes_list()
    
    def search_notes(self, *args):
        """Search notes based on the search query"""
        self.update_notes_list()
    
    def on_note_select(self, event):
        """Handle note selection from the listbox"""
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        
        # Get the selected note
        index = selection[0]
        search_query = self.search_var.get().lower()
        
        # Filter notes to match the current view
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
        self.content_view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def show_note_view(self):
        """Show the note view for the current note"""
        if not self.current_note:
            return
        
        self.content_view_frame.pack_forget()
        self.note_edit_frame.pack_forget()
        self.note_view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Update the view with the note data
        self.view_title.config(text=self.current_note["subject"])
        self.view_date.config(text=self.current_note["created_at"].strftime("%Y-%m-%d %H:%M"))
        
        self.view_content.config(state=tk.NORMAL)
        self.view_content.delete(1.0, tk.END)
        self.view_content.insert(tk.END, self.current_note["content"])
        self.view_content.config(state=tk.DISABLED)
    
    def show_note_edit(self, is_new=False):
        """Show the note edit form"""
        self.content_view_frame.pack_forget()
        self.note_view_frame.pack_forget()
        self.note_edit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()