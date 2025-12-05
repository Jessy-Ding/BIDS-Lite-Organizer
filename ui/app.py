"""
BIDS Lite Organizer - GUI Application

A user-friendly graphical interface for organizing neuroimaging data into BIDS format.
"""

import sys
from pathlib import Path

# Add project root to Python path to enable imports
_project_root = Path(__file__).parent.parent.absolute()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import tkinter first (lightweight)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from typing import Optional, List, Dict, Any
import threading
import json

# Try to import tkinterdnd2 for drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    # Fallback: use regular Tk if tkinterdnd2 is not available
    TkinterDnD = None

# Lazy imports - only import heavy modules when needed
# This significantly speeds up startup time


class BIDSLiteApp:
    """Main application class for BIDS Lite Organizer GUI."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BIDS Lite Organizer")
        self.root.geometry("800x600")  # Smaller initial height, user can resize
        self.root.resizable(True, True)
        self.root.minsize(600, 400)  # Set minimum window size
        
        # Variables
        self.in_dir_var = tk.StringVar()
        self.meta_var = tk.StringVar()
        self.out_dir_var = tk.StringVar()
        self.readme_template_var = tk.StringVar()
        self.copy_files_var = tk.BooleanVar(value=True)
        self.dataset_type_var = tk.StringVar(value="raw")
        self.pipeline_name_var = tk.StringVar()
        self.match_all_modalities_var = tk.BooleanVar(value=True)
        
        # Phenotype files list
        self.phenotype_files: List[str] = []
        
        # Publication files list (for paper-related files)
        self.publication_files: List[str] = []
        
        # Validation issues storage
        self.current_issues: List[Dict[str, Any]] = []
        
        # Lazy-loaded modules (will be imported when first needed)
        self._checklist = None
        self._validator = None
        self._normalizer = None
        self._planner = None
        self._writer = None
        
        self._create_widgets()
        self._layout_widgets()
    
    def _lazy_import_engine(self):
        """Lazy import engine modules only when needed."""
        if self._checklist is None:
            from bids_lite.engine.checklist import load_minimal_spec
            self._checklist = load_minimal_spec
        if self._validator is None:
            from bids_lite.engine.validator import read_metadata, validate_inputs
            self._validator = type('obj', (object,), {
                'read_metadata': read_metadata,
                'validate_inputs': validate_inputs
            })
        if self._normalizer is None:
            from bids_lite.engine.normalizer import normalize_ids
            self._normalizer = normalize_ids
        if self._planner is None:
            from bids_lite.engine.planner import plan_transforms
            self._planner = plan_transforms
        if self._writer is None:
            from bids_lite.engine.writer import (
                apply_transforms,
                write_dataset_description,
                write_participants_tsv,
                write_readme,
                write_report,
                write_phenotype_files,
                write_publication_files
            )
            self._writer = type('obj', (object,), {
                'apply_transforms': apply_transforms,
                'write_dataset_description': write_dataset_description,
                'write_participants_tsv': write_participants_tsv,
                'write_readme': write_readme,
                'write_report': write_report,
                'write_phenotype_files': write_phenotype_files,
                'write_publication_files': write_publication_files
            })
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create a canvas with scrollbar for scrollable content
        # Outer container
        outer_frame = ttk.Frame(self.root)
        outer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        # Main container with padding (this will be scrollable)
        main_frame = ttk.Frame(canvas, padding="10")
        main_frame.columnconfigure(1, weight=1)
        
        # Create scrollable window
        scrollable_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configure scrollbar
        def configure_scroll_region(event=None):
            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(scrollable_window, width=canvas_width)
        
        main_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # Mouse wheel support (works on both Windows and macOS)
        def on_mousewheel(event):
            # macOS uses delta differently
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Some systems use different event format
                canvas.yview_scroll(int(-1 * event.delta), "units")
        
        # Bind mouse wheel events
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # macOS trackpad up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # macOS trackpad down
        
        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        canvas.config(yscrollcommand=scrollbar.set)
        
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.rowconfigure(0, weight=1)
        
        # Store reference to main_frame for later use
        self.main_frame = main_frame
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="BIDS Lite Organizer",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input directory
        ttk.Label(main_frame, text="Input Directory:", font=("Helvetica", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.in_dir_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._choose_input_dir).grid(
            row=1, column=2, padx=5, pady=5
        )
        
        # Metadata file
        ttk.Label(main_frame, text="Metadata File:", font=("Helvetica", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.meta_var, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._choose_metadata).grid(
            row=2, column=2, padx=5, pady=5
        )
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:", font=("Helvetica", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.out_dir_var, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._choose_output_dir).grid(
            row=3, column=2, padx=5, pady=5
        )
        
        # README template (optional)
        ttk.Label(main_frame, text="README Template (optional):", font=("Helvetica", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.readme_template_var, width=50).grid(
            row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._choose_readme_template).grid(
            row=4, column=2, padx=5, pady=5
        )
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Dataset type
        ttk.Label(options_frame, text="Dataset Type:", font=("Helvetica", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        dataset_type_combo = ttk.Combobox(
            options_frame,
            textvariable=self.dataset_type_var,
            values=["raw", "derivatives"],
            state="readonly",
            width=20
        )
        dataset_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        dataset_type_combo.bind("<<ComboboxSelected>>", self._on_dataset_type_change)
        
        # Pipeline name (for derivatives)
        ttk.Label(options_frame, text="Pipeline Name:", font=("Helvetica", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.pipeline_name_entry = ttk.Entry(
            options_frame,
            textvariable=self.pipeline_name_var,
            width=30,
            state=tk.DISABLED
        )
        self.pipeline_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(
            options_frame,
            text="(required for derivatives)",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # Match all modalities option
        ttk.Checkbutton(
            options_frame,
            text="One metadata row matches all files for that participant/session",
            variable=self.match_all_modalities_var
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(
            options_frame,
            text="(Recommended: Check this if one patient has multiple scan types like T1w, T2w, FLAIR, etc.)",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # Copy/Move option
        ttk.Checkbutton(
            options_frame,
            text="Copy files (keep originals)",
            variable=self.copy_files_var
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(
            options_frame,
            text="(Uncheck to move files instead)",
            font=("Helvetica", 8),
            foreground="gray"
        ).grid(row=3, column=2, sticky=tk.W, padx=5)
        
        # Phenotype files section (available for both raw and derivatives)
        phenotype_frame = ttk.LabelFrame(main_frame, text="Phenotype Files (Additional Data Files)", padding="10")
        phenotype_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        phenotype_frame.columnconfigure(0, weight=1)
        
        # Help text for phenotype files
        help_text = (
            "Upload additional data files (e.g., clinical data, demographics, questionnaires).\n"
            "Supported formats: CSV, TSV, Excel (.xls, .xlsx), PDF, and other file types.\n"
            "You can drag and drop files here or use the 'Add' button to browse.\n"
            "These files will be copied to the phenotype/ folder in your BIDS output directory.\n"
            "Note: Available for both raw and derivatives dataset types."
        )
        help_label = ttk.Label(
            phenotype_frame,
            text=help_text,
            font=("Helvetica", 9),
            foreground="gray",
            wraplength=600,
            justify=tk.LEFT
        )
        help_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Listbox for phenotype files
        phenotype_list_frame = ttk.Frame(phenotype_frame)
        phenotype_list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        phenotype_list_frame.columnconfigure(0, weight=1)
        
        self.phenotype_listbox = tk.Listbox(phenotype_list_frame, height=4, selectmode=tk.SINGLE)
        self.phenotype_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        phenotype_scrollbar = ttk.Scrollbar(phenotype_list_frame, orient=tk.VERTICAL, command=self.phenotype_listbox.yview)
        phenotype_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.phenotype_listbox.config(yscrollcommand=phenotype_scrollbar.set)
        
        # Enable drag and drop for phenotype files
        if DND_AVAILABLE:
            try:
                self.phenotype_listbox.drop_target_register(DND_FILES)
                self.phenotype_listbox.dnd_bind('<<Drop>>', self._on_phenotype_drop)
            except Exception:
                pass  # If drag and drop fails, continue without it
        
        # Buttons for phenotype files
        phenotype_btn_frame = ttk.Frame(phenotype_frame)
        phenotype_btn_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Button(
            phenotype_btn_frame,
            text="Add Phenotype File...",
            command=self._add_phenotype_file,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            phenotype_btn_frame,
            text="Remove Selected",
            command=self._remove_phenotype_file,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            phenotype_btn_frame,
            text="Clear All",
            command=self._clear_phenotype_files,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Publication files section (for paper-related files)
        publication_frame = ttk.LabelFrame(main_frame, text="Publication Files (Paper-Related Key Files - Derivatives Only)", padding="10")
        publication_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        publication_frame.columnconfigure(0, weight=1)
        
        # Help text for publication files
        pub_help_text = (
            "Upload key files from papers that use this dataset (e.g., circuit diagrams, connectivity results, key images).\n"
            "You can drag and drop files here or use the 'Add' button to browse.\n"
            "These files will be stored in derivatives/publications/[pipeline_name]/ for easy access by other researchers.\n"
            "Note: Only available when dataset type is set to 'derivatives'."
        )
        pub_help_label = ttk.Label(
            publication_frame,
            text=pub_help_text,
            font=("Helvetica", 9),
            foreground="gray",
            wraplength=600,
            justify=tk.LEFT
        )
        pub_help_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Listbox for publication files
        pub_list_frame = ttk.Frame(publication_frame)
        pub_list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        pub_list_frame.columnconfigure(0, weight=1)
        
        self.publication_listbox = tk.Listbox(pub_list_frame, height=4, selectmode=tk.SINGLE, state=tk.DISABLED)
        self.publication_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        pub_scrollbar = ttk.Scrollbar(pub_list_frame, orient=tk.VERTICAL, command=self.publication_listbox.yview)
        pub_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.publication_listbox.config(yscrollcommand=pub_scrollbar.set)
        
        # Note: Drag and drop will be registered when dataset type is set to derivatives
        # (in _on_dataset_type_change)
        
        # Buttons for publication files
        self.pub_btn_frame = ttk.Frame(publication_frame)
        self.pub_btn_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        self.add_pub_btn = ttk.Button(
            self.pub_btn_frame,
            text="Add Publication File...",
            command=self._add_publication_file,
            width=20,
            state=tk.DISABLED  # Initially disabled (only for derivatives)
        )
        self.add_pub_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_pub_btn = ttk.Button(
            self.pub_btn_frame,
            text="Remove Selected",
            command=self._remove_publication_file,
            width=20,
            state=tk.DISABLED  # Initially disabled (only for derivatives)
        )
        self.remove_pub_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_pub_btn = ttk.Button(
            self.pub_btn_frame,
            text="Clear All",
            command=self._clear_publication_files,
            width=20,
            state=tk.DISABLED  # Initially disabled (only for derivatives)
        )
        self.clear_pub_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons frame (Validate, Plan, Apply)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.validate_btn = ttk.Button(
            button_frame,
            text="Validate",
            command=self._run_validate,
            width=15
        )
        self.validate_btn.pack(side=tk.LEFT, padx=5)
        
        self.plan_btn = ttk.Button(
            button_frame,
            text="Preview Plan",
            command=self._run_plan,
            width=15
        )
        self.plan_btn.pack(side=tk.LEFT, padx=5)
        
        self.apply_btn = ttk.Button(
            button_frame,
            text="Apply",
            command=self._run_apply,
            width=15
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        
        # Validation issues display
        issues_label = ttk.Label(
            main_frame,
            text="Validation Results:",
            font=("Helvetica", 10, "bold")
        )
        issues_label.grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.issues_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.issues_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(10, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        status_bar.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def _layout_widgets(self):
        """Layout widgets (already done in _create_widgets)."""
        pass
    
    def _on_dataset_type_change(self, event=None):
        """Handle dataset type change - enable/disable pipeline name field and publication section."""
        if self.dataset_type_var.get() == "derivatives":
            self.pipeline_name_entry.config(state=tk.NORMAL)
            # Phenotype section is now available for both raw and derivatives
            # Enable publication section for derivatives
            try:
                self.publication_listbox.config(state=tk.NORMAL)
                # Re-register drag and drop when enabling (in case it was lost)
                if DND_AVAILABLE:
                    try:
                        self.publication_listbox.drop_target_register(DND_FILES)
                        self.publication_listbox.dnd_bind('<<Drop>>', self._on_publication_drop)
                    except Exception:
                        pass
                # Enable all buttons in publication frame
                if hasattr(self, 'add_pub_btn'):
                    self.add_pub_btn.config(state=tk.NORMAL)
                if hasattr(self, 'remove_pub_btn'):
                    self.remove_pub_btn.config(state=tk.NORMAL)
                if hasattr(self, 'clear_pub_btn'):
                    self.clear_pub_btn.config(state=tk.NORMAL)
            except:
                pass
        else:
            self.pipeline_name_entry.config(state=tk.DISABLED)
            self.pipeline_name_var.set("")
            # Disable publication section for raw data
            try:
                self.publication_listbox.config(state=tk.DISABLED)
                # Disable all buttons in publication frame
                if hasattr(self, 'add_pub_btn'):
                    self.add_pub_btn.config(state=tk.DISABLED)
                if hasattr(self, 'remove_pub_btn'):
                    self.remove_pub_btn.config(state=tk.DISABLED)
                if hasattr(self, 'clear_pub_btn'):
                    self.clear_pub_btn.config(state=tk.DISABLED)
            except:
                pass
        # Phenotype section is always enabled (for both raw and derivatives)
    
    def _add_phenotype_file(self):
        """Add a phenotype file to the list."""
        try:
            # macOS tkinter crashes with filetypes parameter - remove it entirely
            # This allows user to select any file type, which is acceptable for phenotype files
            # The program just copies files without validating content
            filename = filedialog.askopenfilename(
                title="Select Phenotype File (CSV, TSV, Excel, PDF, or other data files)"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file dialog: {str(e)}")
            self._update_status(f"Error: {str(e)}")
            return
        if filename:
            if filename not in self.phenotype_files:
                self.phenotype_files.append(filename)
                self._update_phenotype_listbox()
                self._update_status(f"Added phenotype file: {Path(filename).name}")
            else:
                messagebox.showinfo("Already Added", "This file is already in the list.")
    
    def _remove_phenotype_file(self):
        """Remove selected phenotype file from the list."""
        selection = self.phenotype_listbox.curselection()
        if selection:
            index = selection[0]
            removed = self.phenotype_files.pop(index)
            self._update_phenotype_listbox()
            self._update_status(f"Removed phenotype file: {Path(removed).name}")
    
    def _clear_phenotype_files(self):
        """Clear all phenotype files."""
        if self.phenotype_files:
            count = len(self.phenotype_files)
            self.phenotype_files.clear()
            self._update_phenotype_listbox()
            self._update_status(f"Cleared {count} phenotype file(s)")
    
    def _update_phenotype_listbox(self):
        """Update the phenotype files listbox."""
        # Temporarily enable if disabled to allow updates
        was_disabled = self.phenotype_listbox.cget('state') == tk.DISABLED
        if was_disabled:
            self.phenotype_listbox.config(state=tk.NORMAL)
        
        self.phenotype_listbox.delete(0, tk.END)
        for file_path in self.phenotype_files:
            # Show full path or just filename - using filename for cleaner display
            display_name = Path(file_path).name
            self.phenotype_listbox.insert(tk.END, display_name)
        
        # Restore previous state
        if was_disabled:
            self.phenotype_listbox.config(state=tk.DISABLED)
        
        # Force update to ensure visibility
        self.phenotype_listbox.update_idletasks()
    
    def _add_publication_file(self):
        """Add a publication file to the list."""
        # Check if dataset type is derivatives
        if self.dataset_type_var.get().lower() != "derivatives":
            messagebox.showwarning(
                "Not Available",
                "Publication files are only available for derivatives dataset type.\n"
                "Please select 'derivatives' as the dataset type first."
            )
            return
        
        try:
            # macOS tkinter crashes with filetypes - use no filetypes filter
            # This allows user to select any file type, which is acceptable for publication files
            filename = filedialog.askopenfilename(
                title="Select Publication File (any file type)"
            )
            if filename and filename not in self.publication_files:
                self.publication_files.append(filename)
                self._update_publication_listbox()
                self._update_status(f"Added publication file: {Path(filename).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file dialog: {str(e)}")
            self._update_status(f"Error: {str(e)}")
    
    def _remove_publication_file(self):
        """Remove selected publication file from the list."""
        selection = self.publication_listbox.curselection()
        if selection:
            index = selection[0]
            removed = self.publication_files.pop(index)
            self._update_publication_listbox()
            self._update_status(f"Removed publication file: {Path(removed).name}")
        else:
            messagebox.showwarning("No Selection", "Please select a file to remove.")
    
    def _clear_publication_files(self):
        """Clear all publication files from the list."""
        if self.publication_files:
            if messagebox.askyesno("Clear All", "Remove all publication files from the list?"):
                self.publication_files.clear()
                self._update_publication_listbox()
                self._update_status("Cleared all publication files")
        else:
            messagebox.showinfo("Empty List", "No publication files to clear.")
    
    def _update_publication_listbox(self):
        """Update the publication files listbox."""
        # Temporarily enable if disabled to allow updates
        was_disabled = self.publication_listbox.cget('state') == tk.DISABLED
        if was_disabled:
            self.publication_listbox.config(state=tk.NORMAL)
        
        self.publication_listbox.delete(0, tk.END)
        for filepath in self.publication_files:
            # Show full path or just filename - using filename for cleaner display
            display_name = Path(filepath).name
            self.publication_listbox.insert(tk.END, display_name)
        
        # Restore previous state
        if was_disabled:
            self.publication_listbox.config(state=tk.DISABLED)
        
        # Force update to ensure visibility
        self.publication_listbox.update_idletasks()
    
    def _on_phenotype_drop(self, event):
        """Handle drag and drop for phenotype files."""
        if not DND_AVAILABLE:
            return
        
        try:
            # Parse dropped files/folders
            # event.data contains space-separated paths, with {} around paths with spaces
            data = event.data.strip()
            
            # Handle tkinterdnd2 format: paths may be wrapped in {}
            files = []
            current_path = ""
            in_braces = False
            
            i = 0
            while i < len(data):
                if data[i] == '{':
                    in_braces = True
                    i += 1
                elif data[i] == '}':
                    if current_path:
                        files.append(current_path)
                        current_path = ""
                    in_braces = False
                    i += 1
                elif data[i] == ' ' and not in_braces:
                    if current_path:
                        files.append(current_path)
                        current_path = ""
                    i += 1
                else:
                    current_path += data[i]
                    i += 1
            
            if current_path:
                files.append(current_path)
            
            # Add all dropped files/folders
            added_count = 0
            for file_path in files:
                file_path = file_path.strip()
                if not file_path:
                    continue
                
                # Remove leading/trailing braces if any
                file_path = file_path.strip('{}')
                
                # Convert to Path and check if exists
                path_obj = Path(file_path)
                if path_obj.exists():
                    if str(path_obj) not in self.phenotype_files:
                        self.phenotype_files.append(str(path_obj))
                        added_count += 1
            
            if added_count > 0:
                self._update_phenotype_listbox()
                self._update_status(f"Added {added_count} file(s) via drag and drop")
            else:
                messagebox.showinfo("No New Files", "All dropped files are already in the list.")
                
        except Exception as e:
            messagebox.showerror("Drag and Drop Error", f"Failed to process dropped files:\n{str(e)}")
            self._update_status(f"Error processing dropped files: {str(e)}")
    
    def _on_publication_drop(self, event):
        """Handle drag and drop for publication files."""
        if not DND_AVAILABLE:
            return
        
        # Check if dataset type is derivatives
        if self.dataset_type_var.get().lower() != "derivatives":
            messagebox.showwarning(
                "Publication Files Not Available",
                "Publication files are only available for derivatives dataset type.\n\n"
                "To use this feature:\n"
                "1. Change 'Dataset Type' to 'derivatives'\n"
                "2. Enter a pipeline name\n"
                "3. Then you can add publication files"
            )
            return
        
        try:
            # Parse dropped files/folders (same logic as phenotype)
            data = event.data.strip()
            
            files = []
            current_path = ""
            in_braces = False
            
            i = 0
            while i < len(data):
                if data[i] == '{':
                    in_braces = True
                    i += 1
                elif data[i] == '}':
                    if current_path:
                        files.append(current_path)
                        current_path = ""
                    in_braces = False
                    i += 1
                elif data[i] == ' ' and not in_braces:
                    if current_path:
                        files.append(current_path)
                        current_path = ""
                    i += 1
                else:
                    current_path += data[i]
                    i += 1
            
            if current_path:
                files.append(current_path)
            
            # Add all dropped files/folders
            added_count = 0
            for file_path in files:
                file_path = file_path.strip()
                if not file_path:
                    continue
                
                # Remove leading/trailing braces if any
                file_path = file_path.strip('{}')
                
                # Convert to Path and check if exists
                path_obj = Path(file_path)
                if path_obj.exists():
                    if str(path_obj) not in self.publication_files:
                        self.publication_files.append(str(path_obj))
                        added_count += 1
            
            if added_count > 0:
                self._update_publication_listbox()
                self._update_status(f"Added {added_count} file(s) via drag and drop")
            else:
                messagebox.showinfo("No New Files", "All dropped files are already in the list.")
                
        except Exception as e:
            messagebox.showerror("Drag and Drop Error", f"Failed to process dropped files:\n{str(e)}")
            self._update_status(f"Error processing dropped files: {str(e)}")
    
    def _choose_input_dir(self):
        """Open dialog to choose input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.in_dir_var.set(directory)
            self._update_status(f"Input directory: {directory}")
    
    def _choose_metadata(self):
        """Open dialog to choose metadata file."""
        filename = filedialog.askopenfilename(
            title="Select Metadata File (CSV/TSV/Excel)",
            filetypes=[
                ("All supported", "*.csv *.tsv *.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("TSV files", "*.tsv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.meta_var.set(filename)
            self._update_status(f"Metadata file: {filename}")
    
    def _choose_output_dir(self):
        """Open dialog to choose output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.out_dir_var.set(directory)
            self._update_status(f"Output directory: {directory}")
    
    def _choose_readme_template(self):
        """Open dialog to choose README template file."""
        filename = filedialog.askopenfilename(
            title="Select README Template",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.readme_template_var.set(filename)
            self._update_status(f"README template: {filename}")
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def _clear_issues(self):
        """Clear the validation issues display."""
        self.issues_text.config(state=tk.NORMAL)
        self.issues_text.delete(1.0, tk.END)
        self.issues_text.config(state=tk.DISABLED)
    
    def _display_issues(self, issues: List[Dict[str, Any]]):
        """Display validation issues in the text widget."""
        self.issues_text.config(state=tk.NORMAL)
        self.issues_text.delete(1.0, tk.END)
        
        if not issues:
            self.issues_text.insert(tk.END, "✓ No validation issues found.\n", "success")
        else:
            error_count = sum(1 for it in issues if it.get("level") == "ERROR")
            warn_count = sum(1 for it in issues if it.get("level") == "WARN")
            
            summary = f"Found {len(issues)} issue(s): {error_count} error(s), {warn_count} warning(s)\n\n"
            self.issues_text.insert(tk.END, summary, "summary")
            
            for issue in issues:
                level = issue.get("level", "INFO")
                code = issue.get("code", "")
                msg = issue.get("msg", "")
                
                if level == "ERROR":
                    tag = "error"
                    prefix = "ERROR"
                elif level == "WARN":
                    tag = "warning"
                    prefix = "WARN"
                else:
                    tag = "info"
                    prefix = "INFO"
                
                line = f"{prefix} [{code}]: {msg}\n"
                self.issues_text.insert(tk.END, line, tag)
        
        # Configure text tags for colors
        self.issues_text.tag_config("success", foreground="green", font=("Helvetica", 10, "bold"))
        self.issues_text.tag_config("summary", font=("Helvetica", 10, "bold"))
        self.issues_text.tag_config("error", foreground="red")
        self.issues_text.tag_config("warning", foreground="orange")
        self.issues_text.tag_config("info", foreground="blue")
        
        self.issues_text.config(state=tk.DISABLED)
        self.current_issues = issues
    
    def _validate_inputs(self) -> bool:
        """Validate inputs and return True if validation passes."""
        try:
            # Lazy load engine modules
            self._lazy_import_engine()
            
            in_dir = Path(self.in_dir_var.get())
            meta_path = Path(self.meta_var.get())
            
            if not in_dir.exists():
                messagebox.showerror("Error", "Input directory does not exist.")
                return False
            
            if not meta_path.exists():
                messagebox.showerror("Error", "Metadata file does not exist.")
                return False
            
            self._update_status("Loading specification and metadata...")
            spec = self._checklist()
            meta = self._validator.read_metadata(meta_path)
            
            self._update_status("Validating inputs...")
            issues = self._validator.validate_inputs(in_dir, meta, spec)
            
            self._display_issues(issues)
            
            if issues and any(it.get("level") == "ERROR" for it in issues):
                self._update_status("Validation failed: ERROR-level issues found.")
                return False
            
            self._update_status("Validation passed: No blocking issues found.")
            return True
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"An error occurred during validation:\n{str(e)}")
            self._update_status(f"Error: {str(e)}")
            return False
    
    def _run_validate(self):
        """Run validation in a separate thread."""
        def validate_thread():
            self.validate_btn.config(state=tk.DISABLED)
            try:
                self._validate_inputs()
            finally:
                self.validate_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=validate_thread, daemon=True).start()
    
    def _run_plan(self):
        """Run planning (dry run) in a separate thread."""
        def plan_thread():
            self.plan_btn.config(state=tk.DISABLED)
            try:
                if not self._validate_inputs():
                    return
                
                # Get dataset type and pipeline name
                dataset_type = self.dataset_type_var.get().lower()
                pipeline_name = self.pipeline_name_var.get().strip() if self.pipeline_name_var.get() else None
                
                if dataset_type == "derivatives" and not pipeline_name:
                    messagebox.showerror("Error", "Pipeline name is required for derivatives dataset type.")
                    return
                
                # Lazy load engine modules
                self._lazy_import_engine()
                
                in_dir = Path(self.in_dir_var.get())
                out_dir = Path(self.out_dir_var.get())
                meta_path = Path(self.meta_var.get())
                
                self._update_status("Planning transformations...")
                spec = self._checklist()
                meta = self._validator.read_metadata(meta_path)
                meta_norm = self._normalizer(meta)
                match_all_modalities = self.match_all_modalities_var.get()
                
                # Validate that plan_transforms returns a list
                plan = self._planner(in_dir, out_dir, meta_norm, dataset_type, pipeline_name, match_all_modalities=match_all_modalities)
                
                # Check if plan is valid
                if not isinstance(plan, list):
                    raise ValueError(f"plan_transforms returned unexpected type: {type(plan)}, expected list. Value: {plan}")
                
                if len(plan) == 0:
                    messagebox.showwarning(
                        "No Files Matched",
                        "No files were matched to your metadata.\n\n"
                        "Please check:\n"
                        "• Input directory contains image files (NIfTI format: .nii, .nii.gz)\n"
                        "• Participant IDs in metadata match file or folder names\n"
                        "• File formats are supported\n\n"
                        "Tips:\n"
                        "• The program can match IDs even with different formats\n"
                        "  (e.g., 'patient_001' matches 'patient-001' or 'patient 001')\n"
                        "• For one-patient-per-folder structure, put participant ID in folder name\n"
                        "• Check the 'Match All Modalities' option if one patient has multiple scans"
                    )
                    self._update_status("Preview complete: No files matched.")
                    return
                
                # Ask user if they want to save plan.json
                save_json = messagebox.askyesno(
                    "Save Preview Plan?",
                    f"Found {len(plan)} file(s) to organize.\n\n"
                    "Would you like to save the preview plan to a JSON file?",
                    icon=messagebox.QUESTION
                )
                
                if save_json:
                    # Ask for save location
                    json_path = filedialog.asksaveasfilename(
                        title="Save Plan JSON",
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        initialfile="plan.json"
                    )
                    if json_path:
                        try:
                            # Ensure parent directory exists
                            json_file = Path(json_path)
                            json_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Ensure all paths in plan are strings (not Path objects)
                            plan_serializable = []
                            for op in plan:
                                plan_serializable.append({
                                    "src": str(op["src"]),
                                    "dst": str(op["dst"]),
                                    "action": str(op.get("action", "copy"))
                                })
                            
                            # Write JSON file
                            json_file.write_text(json.dumps(plan_serializable, indent=2))
                            
                            # Update status and show success message
                            try:
                                self._update_status(f"Plan saved to: {json_path}")
                                messagebox.showinfo(
                                    "Plan Saved",
                                    f"Plan JSON saved to:\n{json_path}\n\n"
                                    f"Total operations: {len(plan)}"
                                )
                            except Exception as msg_error:
                                # If showing message fails, at least update status
                                self._update_status(f"Plan saved to: {json_path} (message display failed)")
                        except Exception as e:
                            # Only show error if file actually failed to save
                            error_msg = str(e)
                            # Check if file was actually created despite the error
                            if json_path and Path(json_path).exists():
                                # File exists, so save was successful despite error
                                self._update_status(f"Plan saved to: {json_path} (with warnings)")
                                messagebox.showwarning(
                                    "Save Warning",
                                    f"Plan JSON saved, but encountered a warning:\n{error_msg}"
                                )
                            else:
                                # File doesn't exist, save actually failed
                                messagebox.showerror(
                                    "Save Error",
                                    f"Failed to save plan JSON:\n{error_msg}\n\n"
                                    f"Please check file permissions and path."
                                )
                            # Still show summary even if save failed
                            summary = f"Preview: {len(plan)} file(s) will be organized.\n\nFirst 10 files:\n"
                            for op in plan[:10]:
                                summary += f"  {Path(op['src']).name}\n    → {Path(op['dst']).name}\n"
                            if len(plan) > 10:
                                summary += f"\n... and {len(plan) - 10} more file(s)."
                            messagebox.showinfo("Preview Complete", summary)
                            self._update_status(f"Preview complete: {len(plan)} file(s) ready to organize.")
                    else:
                        # User cancelled save, just show summary
                        summary = f"Preview: {len(plan)} file(s) will be organized.\n\nFirst 10 files:\n"
                        for op in plan[:10]:
                            summary += f"  {Path(op['src']).name}\n    → {Path(op['dst']).name}\n"
                        if len(plan) > 10:
                            summary += f"\n... and {len(plan) - 10} more file(s)."
                        messagebox.showinfo("Preview Complete", summary)
                        self._update_status(f"Preview complete: {len(plan)} file(s) ready to organize.")
                else:
                    # Show plan summary without saving
                    summary = f"Preview: {len(plan)} file(s) will be organized.\n\nFirst 10 files:\n"
                    for op in plan[:10]:
                        summary += f"  {Path(op['src']).name}\n    → {Path(op['dst']).name}\n"
                    if len(plan) > 10:
                        summary += f"\n... and {len(plan) - 10} more file(s)."
                    messagebox.showinfo("Preview Complete", summary)
                    self._update_status(f"Preview complete: {len(plan)} file(s) ready to organize.")
                
            except Exception as e:
                # Provide more detailed error information
                import traceback
                error_details = traceback.format_exc()
                error_msg = f"An error occurred during planning:\n\n{str(e)}\n\nDetails:\n{error_details}"
                messagebox.showerror("Planning Error", error_msg)
                self._update_status(f"Error: {str(e)}")
            finally:
                self.plan_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=plan_thread, daemon=True).start()
    
    def _run_apply(self):
        """Run apply operation in a separate thread."""
        def apply_thread():
            self.apply_btn.config(state=tk.DISABLED)
            self.validate_btn.config(state=tk.DISABLED)
            self.plan_btn.config(state=tk.DISABLED)
            
            try:
                if not self._validate_inputs():
                    return
                
                # Get dataset type and pipeline name
                dataset_type = self.dataset_type_var.get().lower()
                pipeline_name = self.pipeline_name_var.get().strip() if self.pipeline_name_var.get() else None
                
                if dataset_type == "derivatives" and not pipeline_name:
                    messagebox.showerror("Error", "Pipeline name is required for derivatives dataset type.")
                    return
                
                # Lazy load engine modules
                self._lazy_import_engine()
                
                in_dir = Path(self.in_dir_var.get())
                out_dir = Path(self.out_dir_var.get())
                meta_path = Path(self.meta_var.get())
                readme_template = Path(self.readme_template_var.get()) if self.readme_template_var.get() else None
                copy_files = self.copy_files_var.get()
                
                # Determine where to write dataset_description.json
                if dataset_type == "derivatives":
                    desc_dir = out_dir / "derivatives" / pipeline_name
                else:
                    desc_dir = out_dir
                
                self._update_status("Loading specification and metadata...")
                spec = self._checklist()
                meta = self._validator.read_metadata(meta_path)
                
                self._update_status("Normalizing IDs...")
                meta_norm = self._normalizer(meta)
                
                self._update_status("Planning transformations...")
                match_all_modalities = self.match_all_modalities_var.get()
                plan = self._planner(in_dir, out_dir, meta_norm, dataset_type, pipeline_name, match_all_modalities=match_all_modalities)
                
                self._update_status(f"Applying {len(plan)} transformations...")
                summary = self._writer.apply_transforms(plan, copy=copy_files)
                
                self._update_status("Writing BIDS metadata files...")
                self._writer.write_dataset_description(desc_dir, dataset_type, pipeline_name)
                # participants.tsv: for raw data goes in BIDS root, for derivatives goes in derivatives/pipeline_name/
                if dataset_type == "raw":
                    self._writer.write_participants_tsv(out_dir, meta_norm)
                else:
                    # For derivatives, write participants.tsv in the derivatives/pipeline_name/ directory
                    self._writer.write_participants_tsv(desc_dir, meta_norm)
                self._writer.write_readme(desc_dir, readme_template)
                self._writer.write_report(desc_dir, plan, summary, self.current_issues)
                
                # Write phenotype files (available for both raw and derivatives)
                if self.phenotype_files:
                    self._update_status("Copying phenotype files...")
                    phenotype_paths = [Path(p) for p in self.phenotype_files]
                    self._writer.write_phenotype_files(out_dir, phenotype_paths, dataset_type, pipeline_name)
                    if dataset_type == "derivatives":
                        self._update_status(f"Copied {len(phenotype_paths)} phenotype file(s) to derivatives/{pipeline_name}/phenotype/ folder.")
                    else:
                        self._update_status(f"Copied {len(phenotype_paths)} phenotype file(s) to phenotype/ folder.")
                
                # Copy publication files if any (only for derivatives)
                if dataset_type == "derivatives" and self.publication_files:
                    publication_paths = [Path(f) for f in self.publication_files]
                    self._writer.write_publication_files(out_dir, publication_paths, pipeline_name)
                
                # Show completion message
                success_msg = (
                    f"✓ Apply complete!\n\n"
                    f"Operations: {summary['n_ok']} successful, {summary['n_failed']} failed\n"
                    f"Output directory: {out_dir}\n"
                )
                if self.phenotype_files:
                    if dataset_type == "derivatives":
                        success_msg += f"\nPhenotype files: {len(self.phenotype_files)} file(s) copied to derivatives/{pipeline_name}/phenotype/ folder."
                    else:
                        success_msg += f"\nPhenotype files: {len(self.phenotype_files)} file(s) copied to phenotype/ folder."
                if dataset_type == "derivatives" and self.publication_files:
                    success_msg += f"\nPublication files: {len(self.publication_files)} file(s) copied to derivatives/publications/ folder."
                if summary.get('errors'):
                    success_msg += f"\n\nErrors:\n" + "\n".join(f"  - {e}" for e in summary['errors'][:5])
                    if len(summary['errors']) > 5:
                        success_msg += f"\n  ... and {len(summary['errors']) - 5} more errors."
                
                messagebox.showinfo("Apply Complete", success_msg)
                self._update_status(f"Apply complete: {summary['n_ok']} operations successful.")
                
            except Exception as e:
                messagebox.showerror("Apply Error", f"An error occurred during apply:\n{str(e)}")
                self._update_status(f"Error: {str(e)}")
            finally:
                self.apply_btn.config(state=tk.NORMAL)
                self.validate_btn.config(state=tk.NORMAL)
                self.plan_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=apply_thread, daemon=True).start()


def run_app():
    """Run the BIDS Lite Organizer GUI application."""
    try:
        # On macOS, ensure we're using the right Python framework
        import platform
        if platform.system() == "Darwin":
            # Try to use the system's Python framework for better GUI support
            pass
        
        # Use TkinterDnD.Tk() if available for drag and drop support
        if DND_AVAILABLE and TkinterDnD:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        # Update the window immediately to show it's loading
        root.update()
        
        app = BIDSLiteApp(root)
        # Center the window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_app()
