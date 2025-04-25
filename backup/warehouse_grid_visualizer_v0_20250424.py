import csv
import tkinter as tk
from tkinter import ttk, StringVar, messagebox, filedialog
from collections import defaultdict

class WarehouseGridVisualizer:
    def __init__(self, root, csv_file=None):
        self.root = root
        self.root.title("Warehouse Grid Visualizer")
        self.root.geometry("1400x800")
        
        # Define column and row names - use the same ones from the original visualizer
        self.columns = ['1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', 
                        '1N', '1O', '1P', '1Q', '1R', '1S', '1T', '1U', '1V', '1W', '1X', '1Y', '1Z', 
                        '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', 
                        '2N', '2O', '2P', '2Q', '2R', '2S', '3A', '3B', '3C', '3D', '3E', '3F', '3G', 
                        '3H', '3I', '3J', '3K', '3L', '3M', '3N', '3P', '3Q', '3R']
        self.rows = [str(i).zfill(2) for i in range(1, 91)]  # 01-90, zero-padded
        
        # Cell size (in pixels)
        self.cell_size = 25
        self.cell_padding = 2
        self.header_height = 30
        self.header_width = 40
        
        # Track highlighted cells
        self.highlighted_cells = set()
        
        # Track last clicked position
        self.last_clicked = None
        
        # Track current filter mode
        self.current_filter = None
        
        # Initialize data structures
        self.csv_data = []
        self.grid_data = defaultdict(lambda: defaultdict(list))
        self.cell_objects = {}
        
        # Track duplicate SKUs and empty bins
        self.duplicate_skus = set()
        self.empty_bins_locations = set()
        
        # Create UI
        self.create_ui()
        
        # Load data from CSV if file is provided
        if csv_file:
            self.load_data_from_file(csv_file)
    
    def load_data_from_file(self, csv_file):
        """Load CSV data and redraw the grid"""
        try:
            self.csv_data = []
            self.grid_data = self.load_csv_data(csv_file)
            self.current_file_label.config(text=f"Current file: {csv_file}")
            
            # Analyze the data for duplicates and empty bins
            self.analyze_data()
            
            self.draw_grid()
            
            # Update status bar
            occupied_count = sum(1 for c in self.columns for r in self.rows 
                               if c in self.grid_data and r in self.grid_data[c])
            total_cells = len(self.columns) * len(self.rows)
            self.status_bar.config(text=f"Grid: {len(self.columns)}x{len(self.rows)} = {total_cells} cells, Occupied: {occupied_count}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.status_bar.config(text="Error loading file")
    
    def analyze_data(self):
        """Analyze the data to find duplicate SKUs and empty bins"""
        sku_locations = defaultdict(list)
        self.duplicate_skus = set()
        self.empty_bins_locations = set()
        
        # Find duplicate SKUs and empty bins
        for column in self.grid_data:
            for row in self.grid_data[column]:
                for sku, bin_location in self.grid_data[column][row]:
                    # Track locations for each SKU
                    sku_locations[sku].append((column, row))
                    
                    # Check for empty bins - including both "EMPTY" SKUs and empty SKU fields
                    if sku.upper() == "EMPTY" or not sku:
                        self.empty_bins_locations.add((column, row))
        
        # Find which SKUs appear in multiple locations
        for sku, locations in sku_locations.items():
            # Only consider non-empty SKUs for duplicates
            if len(locations) > 1 and sku.upper() != "EMPTY" and sku.strip():
                self.duplicate_skus.add(sku)
        
        # Update status
        self.status_bar.config(text=f"Loaded data with {len(self.duplicate_skus)} duplicate SKUs and {len(self.empty_bins_locations)} empty bins")
    
    def load_csv_data(self, csv_file):
        """Load and organize data from the CSV file"""
        # Dictionary to store SKUs by grid location
        grid_data = defaultdict(lambda: defaultdict(list))
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                # Make sure we have enough columns
                if len(row) < 3:
                    continue
                    
                timestamp, sku, location = row
                
                # Save all data for search functionality
                self.csv_data.append((timestamp, sku, location))
                
                # Extract grid location from bin location
                # Example format: R1S32-N-AT1
                # We need to extract R[1] (rack/level) and [S] (column) to form "1S"
                # Then we need to extract [32] (row number)
                if len(location) >= 5 and location.startswith('R'):
                    level = location[1:2]  # e.g., 1 from R1S32-N-AT1
                    column_letter = location[2:3]  # e.g., S from R1S32-N-AT1
                    row_num = location[3:5]  # e.g., 32 from R1S32-N-AT1
                    
                    column = level + column_letter  # e.g., 1S
                    bin_code = location  # Full bin location
                    
                    # Add SKU to the grid's bin list
                    grid_data[column][row_num].append((sku, bin_code))
        
        return grid_data
    
    def open_file_dialog(self):
        """Open file dialog to select a CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_data_from_file(file_path)
            self.clear_search()
    
    def create_ui(self):
        """Create the main UI components"""
        # Create top-level control panel
        control_panel = tk.Frame(self.root)
        control_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Create top row for File and Zoom
        top_row = tk.Frame(control_panel)
        top_row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # File selection section
        file_frame = tk.LabelFrame(top_row, text="File")
        file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        open_file_btn = tk.Button(file_frame, text="Open CSV File", command=self.open_file_dialog)
        open_file_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.current_file_label = tk.Label(file_frame, text="No file loaded")
        self.current_file_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Zoom section
        zoom_frame = tk.LabelFrame(top_row, text="Zoom")
        zoom_frame.pack(side=tk.RIGHT, padx=5)
        
        # Zoom controls
        zoom_in_btn = tk.Button(zoom_frame, text="+", command=self.zoom_in, width=3)
        zoom_in_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        zoom_out_btn = tk.Button(zoom_frame, text="-", command=self.zoom_out, width=3)
        zoom_out_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        fit_btn = tk.Button(zoom_frame, text="Fit to Window", command=self.fit_to_window)
        fit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create bottom row for Search and Filter
        bottom_row = tk.Frame(control_panel)
        bottom_row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Search section
        search_frame = tk.LabelFrame(bottom_row, text="Search")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # SKU search
        sku_frame = tk.Frame(search_frame)
        sku_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        tk.Label(sku_frame, text="SKU:").pack(side=tk.LEFT)
        self.sku_search_var = StringVar()
        sku_entry = tk.Entry(sku_frame, textvariable=self.sku_search_var, width=20)
        sku_entry.pack(side=tk.LEFT, padx=5)
        
        # Location search
        loc_frame = tk.Frame(search_frame)
        loc_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        tk.Label(loc_frame, text="Location:").pack(side=tk.LEFT)
        self.loc_search_var = StringVar()
        loc_entry = tk.Entry(loc_frame, textvariable=self.loc_search_var, width=20)
        loc_entry.pack(side=tk.LEFT, padx=5)
        
        # Search button
        search_btn = tk.Button(search_frame, text="Search", command=self.search_grid)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(search_frame, text="Clear", command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Filter section
        filter_frame = tk.LabelFrame(bottom_row, text="Filter")
        filter_frame.pack(side=tk.RIGHT, fill=tk.X, padx=5)
        
        # Duplicate SKUs button
        duplicate_btn = tk.Button(filter_frame, text="Duplicate SKUs", command=self.show_duplicate_skus)
        duplicate_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Empty Bins button
        empty_bins_btn = tk.Button(filter_frame, text="Empty Bins", command=self.show_empty_bins)
        empty_bins_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Clear filter button
        clear_filter_btn = tk.Button(filter_frame, text="Clear Filter", command=self.clear_filter)
        clear_filter_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a frame with scrollbars for the canvas
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add horizontal scrollbar
        h_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for drawing the grid
        self.canvas = tk.Canvas(self.main_frame, 
                              yscrollcommand=v_scrollbar.set,
                              xscrollcommand=h_scrollbar.set,
                              highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        # Calculate canvas dimensions
        self.update_canvas_dimensions()
        
        # Draw the grid
        self.draw_grid()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Control-MouseWheel>", self.on_mousewheel)
        
        # Key bindings for search
        sku_entry.bind("<Return>", lambda event: self.search_grid())
        loc_entry.bind("<Return>", lambda event: self.search_grid())
    
    def update_canvas_dimensions(self):
        """Update canvas dimensions based on grid size"""
        total_width = self.header_width + (len(self.columns) * (self.cell_size + self.cell_padding))
        total_height = self.header_height + (len(self.rows) * (self.cell_size + self.cell_padding))
        self.canvas.config(scrollregion=(0, 0, total_width, total_height))
    
    def draw_grid(self):
        """Draw the warehouse grid on the canvas"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Store cell IDs and coordinates for later use
        self.cell_objects = {}
        
        # Draw column headers
        for col_idx, col_name in enumerate(self.columns):
            x = self.header_width + col_idx * (self.cell_size + self.cell_padding)
            self.canvas.create_rectangle(x, 0, x + self.cell_size, self.header_height, 
                                       fill="lightgray", outline="black")
            self.canvas.create_text(x + self.cell_size/2, self.header_height/2, 
                                  text=col_name, font=("Arial", max(8, int(self.cell_size/4))))
        
        # Draw row headers
        for row_idx, row_name in enumerate(self.rows):
            y = self.header_height + row_idx * (self.cell_size + self.cell_padding)
            self.canvas.create_rectangle(0, y, self.header_width, y + self.cell_size, 
                                       fill="lightgray", outline="black")
            self.canvas.create_text(self.header_width/2, y + self.cell_size/2, 
                                  text=row_name, font=("Arial", max(8, int(self.cell_size/4))))
        
        # Draw grid cells
        for row_idx, row_name in enumerate(self.rows):
            y = self.header_height + row_idx * (self.cell_size + self.cell_padding)
            
            for col_idx, col_name in enumerate(self.columns):
                x = self.header_width + col_idx * (self.cell_size + self.cell_padding)
                
                # Determine if cell has items
                has_items = col_name in self.grid_data and row_name in self.grid_data[col_name]
                
                # Determine color
                if (col_name, row_name) in self.highlighted_cells:
                    color = "orange"
                else:
                    color = "green" if has_items else "white"
                
                # Create cell rectangle
                cell_id = self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, 
                                                   fill=color, outline="black", tags=("cell",))
                
                # Store cell object reference and coordinates
                self.cell_objects[(col_name, row_name)] = {
                    'id': cell_id,
                    'x1': x,
                    'y1': y,
                    'x2': x + self.cell_size,
                    'y2': y + self.cell_size
                }
    
    def on_canvas_click(self, event):
        """Handle canvas click event"""
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find which cell was clicked
        for (col_name, row_name), cell in self.cell_objects.items():
            if (cell['x1'] <= canvas_x <= cell['x2'] and 
                cell['y1'] <= canvas_y <= cell['y2']):
                # Cell found, show details
                self.show_grid_details(col_name, row_name)
                self.last_clicked = (col_name, row_name)
                break
    
    def on_canvas_configure(self, event):
        """Handle canvas resize event"""
        # Update when window is resized
        if event.width > 1 and event.height > 1:  # Ignore trivial resize events
            self.fit_to_window()
    
    def show_grid_details(self, column, row):
        """Show details of bins and SKUs for a specific grid location"""
        # Create a new toplevel window for details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Grid Details: {column}{row}")
        details_window.geometry("600x400")
        details_window.transient(self.root)  # Make it modal
        details_window.grab_set()  # Prevent interaction with main window
        
        # Create a frame with scrollbar for the treeview
        frame = tk.Frame(details_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add label
        tk.Label(frame, text=f"SKUs and Bins at Location {column}{row}", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Create treeview for displaying data
        columns = ("SKU", "Bin Location", "Timestamp")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        tree.heading("SKU", text="SKU")
        tree.heading("Bin Location", text="Bin Location")
        tree.heading("Timestamp", text="Timestamp")
        tree.column("SKU", width=150)
        tree.column("Bin Location", width=200)
        tree.column("Timestamp", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Track items to highlight
        items_to_highlight = []
        
        # Get current search criteria
        sku_query = self.sku_search_var.get().strip().upper()
        loc_query = self.loc_search_var.get().strip().upper()
        has_search = bool(sku_query or loc_query)
        
        # Add data to treeview
        if column in self.grid_data and row in self.grid_data[column]:
            # Find full details for each SKU at this location
            for idx, (sku, bin_location) in enumerate(self.grid_data[column][row]):
                # Find the timestamp for this exact SKU/location
                timestamp = ""
                for t, s, loc in self.csv_data:
                    if s == sku and loc == bin_location:
                        timestamp = t
                        break
                
                item_id = tree.insert("", tk.END, values=(sku, bin_location, timestamp))
                
                # Check if this item should be highlighted based on current filter
                if self.current_filter == "duplicates" and sku in self.duplicate_skus:
                    items_to_highlight.append(item_id)
                elif self.current_filter == "empty" and (sku.upper() == "EMPTY" or not sku.strip()):
                    items_to_highlight.append(item_id)
                # Highlight search matches
                elif has_search:
                    sku_match = sku_query and sku_query in sku.upper()
                    loc_match = loc_query and loc_query in bin_location.upper()
                    if sku_match or loc_match:
                        items_to_highlight.append(item_id)
        else:
            tree.insert("", tk.END, values=("No items found", "", ""))
        
        # Highlight items if needed
        for item_id in items_to_highlight:
            tree.item(item_id, tags=("highlight",))
        
        # Configure tag for highlighted items
        tree.tag_configure("highlight", background="light yellow")
        
        # Create a function to copy selected item
        def copy_selected_item():
            selected_item = tree.selection()
            if not selected_item:
                return
            
            item_values = tree.item(selected_item[0], "values")
            if not item_values:
                return
            
            # Create copy menu options
            copy_menu = tk.Menu(details_window, tearoff=0)
            copy_menu.add_command(label="Copy SKU", 
                                 command=lambda: self.copy_to_clipboard(details_window, item_values[0]))
            copy_menu.add_command(label="Copy Bin Location", 
                                 command=lambda: self.copy_to_clipboard(details_window, item_values[1]))
            copy_menu.add_command(label="Copy Timestamp", 
                                 command=lambda: self.copy_to_clipboard(details_window, item_values[2]))
            copy_menu.add_separator()
            copy_menu.add_command(label="Copy All", 
                                 command=lambda: self.copy_to_clipboard(details_window, 
                                                                      f"SKU: {item_values[0]}\nBin: {item_values[1]}\nTimestamp: {item_values[2]}"))
            
            # Display the menu at the cursor position
            copy_menu.tk_popup(details_window.winfo_pointerx(), details_window.winfo_pointery())
        
        # Create copy buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        copy_button = tk.Button(button_frame, text="Copy Selected", command=copy_selected_item)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        help_text = tk.Label(button_frame, text="Right-click or press Ctrl+C to copy items", fg="gray")
        help_text.pack(side=tk.RIGHT, padx=5)
        
        # Create a popup menu
        popup_menu = tk.Menu(tree, tearoff=0)
        popup_menu.add_command(label="Copy SKU", 
                             command=lambda: self.copy_column_value(tree, 0))
        popup_menu.add_command(label="Copy Bin Location", 
                             command=lambda: self.copy_column_value(tree, 1))
        popup_menu.add_command(label="Copy Timestamp", 
                             command=lambda: self.copy_column_value(tree, 2))
        popup_menu.add_separator()
        popup_menu.add_command(label="Copy Row", 
                             command=lambda: self.copy_row(tree))
        
        # Bind right-click to show popup menu
        def show_popup(event):
            # Select the item under the cursor
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                popup_menu.tk_popup(event.x_root, event.y_root)
        
        tree.bind("<Button-3>", show_popup)
        
        # Bind Ctrl+C to copy the selected item values
        def copy_with_keyboard(event):
            self.copy_row(tree)
        
        tree.bind("<Control-c>", copy_with_keyboard)
        
        # Pack treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def copy_to_clipboard(self, window, text):
        """Copy text to clipboard"""
        window.clipboard_clear()
        window.clipboard_append(text)
        self.status_bar.config(text=f"Copied to clipboard: {text[:30]}...")
    
    def copy_column_value(self, tree, column_index):
        """Copy a specific column value from the selected row"""
        selected_items = tree.selection()
        if not selected_items:
            return
        
        item_values = tree.item(selected_items[0], "values")
        if not item_values or column_index >= len(item_values):
            return
        
        value = item_values[column_index]
        
        # Copy to clipboard
        tree.master.master.clipboard_clear()
        tree.master.master.clipboard_append(value)
        self.status_bar.config(text=f"Copied to clipboard: {value[:30]}...")
    
    def copy_row(self, tree):
        """Copy all values from the selected row"""
        selected_items = tree.selection()
        if not selected_items:
            return
        
        item_values = tree.item(selected_items[0], "values")
        if not item_values:
            return
        
        # Format as SKU, Bin Location, Timestamp
        column_names = tree["columns"]
        text = "\n".join([f"{column_names[i]}: {value}" for i, value in enumerate(item_values)])
        
        # Copy to clipboard
        tree.master.master.clipboard_clear()
        tree.master.master.clipboard_append(text)
        self.status_bar.config(text=f"Copied row to clipboard")
    
    def search_grid(self):
        """Search the grid and highlight matching locations"""
        # Clear previous highlights
        self.clear_search(keep_fields=True)
        
        sku_query = self.sku_search_var.get().strip().upper()
        loc_query = self.loc_search_var.get().strip().upper()
        
        # If no search terms provided, return
        if not sku_query and not loc_query:
            return
        
        print(f"Searching for SKU='{sku_query}', Location='{loc_query}'")
        
        # Find matching locations
        matching_locations = set()
        
        for timestamp, sku, location in self.csv_data:
            # Skip if location is too short
            if len(location) < 5:
                continue
                
            # Extract grid location using the same logic as load_csv_data
            if location.startswith('R'):
                level = location[1:2]          # e.g., 1 from R1S32-N-AT1
                column_letter = location[2:3]  # e.g., S from R1S32-N-AT1
                row = location[3:5]            # e.g., 32 from R1S32-N-AT1
                column = level + column_letter  # e.g., 1S
                
                # Check if SKU or location matches search criteria
                sku_match = sku_query and sku_query in sku.upper()
                loc_match = loc_query and loc_query in location.upper()
                
                if sku_match or loc_match:
                    matching_locations.add((column, row))
                    print(f"Match found: SKU={sku}, Location={location}, Grid={column}{row}")
        
        # Highlight matching locations
        self.highlighted_cells = matching_locations
        
        # Update cell colors for matches
        match_count = 0
        for (col_name, row_name), cell in self.cell_objects.items():
            if (col_name, row_name) in matching_locations:
                self.canvas.itemconfig(cell['id'], fill="orange")
                match_count += 1
        
        # If no matches found, show message
        if match_count == 0:
            tk.messagebox.showinfo("Search Results", "No matching locations found.")
        else:
            self.status_bar.config(text=f"Found {match_count} matching locations")
    
    def clear_search(self, keep_fields=False):
        """Clear search results and reset grid colors"""
        # Reset search fields if requested
        if not keep_fields:
            self.sku_search_var.set("")
            self.loc_search_var.set("")
        
        # Reset cell colors for all cells
        for (col_name, row_name), cell in self.cell_objects.items():
            has_items = col_name in self.grid_data and row_name in self.grid_data[col_name]
            color = "green" if has_items else "white"
            self.canvas.itemconfig(cell['id'], fill=color)
        
        # Clear highlighted cells and filter
        self.highlighted_cells = set()
        self.current_filter = None
        
        # Update status
        occupied_count = sum(1 for c in self.columns for r in self.rows 
                           if c in self.grid_data and r in self.grid_data[c])
        total_cells = len(self.columns) * len(self.rows)
        
        if keep_fields:
            self.status_bar.config(text=f"Search cleared. Grid: {len(self.columns)}x{len(self.rows)} = {total_cells} cells, Occupied: {occupied_count}")
        else:
            self.status_bar.config(text=f"Grid: {len(self.columns)}x{len(self.rows)} = {total_cells} cells, Occupied: {occupied_count}")
    
    def zoom_in(self):
        """Increase the cell size"""
        self.cell_size += 5
        self.header_height = max(30, self.cell_size + 5)
        self.header_width = max(40, self.cell_size + 15)
        self.update_canvas_dimensions()
        self.draw_grid()
        
        # Reapply highlighting if needed
        if self.highlighted_cells:
            for (col_name, row_name), cell in self.cell_objects.items():
                if (col_name, row_name) in self.highlighted_cells:
                    self.canvas.itemconfig(cell['id'], fill="orange")
    
    def zoom_out(self):
        """Decrease the cell size"""
        if self.cell_size > 10:
            self.cell_size -= 5
            self.header_height = max(30, self.cell_size + 5)
            self.header_width = max(40, self.cell_size + 15)
            self.update_canvas_dimensions()
            self.draw_grid()
            
            # Reapply highlighting if needed
            if self.highlighted_cells:
                for (col_name, row_name), cell in self.cell_objects.items():
                    if (col_name, row_name) in self.highlighted_cells:
                        self.canvas.itemconfig(cell['id'], fill="orange")
    
    def fit_to_window(self):
        """Resize the grid to fit the window"""
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Ensure we have valid dimensions
        if canvas_width < 50 or canvas_height < 50:
            return
        
        # Calculate optimal cell size
        width_per_cell = (canvas_width - self.header_width) / (len(self.columns) + 1)
        height_per_cell = (canvas_height - self.header_height) / (len(self.rows) + 1)
        
        optimal_size = min(width_per_cell, height_per_cell) - self.cell_padding
        
        # Set cell size (with minimum constraint)
        self.cell_size = max(10, int(optimal_size))
        self.header_height = max(30, self.cell_size + 5)
        self.header_width = max(40, self.cell_size + 15)
        
        # Update canvas and redraw
        self.update_canvas_dimensions()
        self.draw_grid()
        
        # Reapply highlighting if needed
        if self.highlighted_cells:
            for (col_name, row_name), cell in self.cell_objects.items():
                if (col_name, row_name) in self.highlighted_cells:
                    self.canvas.itemconfig(cell['id'], fill="orange")
        
        # Keep last clicked cell in view if possible
        if self.last_clicked and self.last_clicked in self.cell_objects:
            self.scroll_to_cell(self.last_clicked)
    
    def scroll_to_cell(self, cell_key):
        """Scroll to make a specific cell visible"""
        if cell_key in self.cell_objects:
            cell = self.cell_objects[cell_key]
            x = cell['x1'] - self.header_width
            y = cell['y1'] - self.header_height
            self.canvas.xview_moveto(x / self.canvas.bbox("all")[2])
            self.canvas.yview_moveto(y / self.canvas.bbox("all")[3])
    
    def on_mousewheel(self, event):
        """Handle mouse wheel events for zooming"""
        # Zoom in/out with Ctrl + mouse wheel
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def find_duplicate_skus(self):
        """Find all SKUs that appear in multiple locations (excluding EMPTY and blank SKUs)"""
        sku_locations = defaultdict(list)
        duplicate_skus = set()
        duplicate_locations = set()
        
        # First, gather all the locations for each SKU
        for timestamp, sku, location in self.csv_data:
            # Skip invalid locations or empty/EMPTY SKUs
            if (len(location) < 5 or not location.startswith('R') or 
                sku.upper() == "EMPTY" or not sku.strip()):
                continue
                
            # Extract grid coordinates
            try:
                level = location[1:2]
                column_letter = location[2:3]
                row_num = location[3:5]
                
                column = level + column_letter
                sku_locations[sku].append((column, row_num))
            except:
                # Skip invalid formats
                pass
        
        # Now find the SKUs that appear in multiple locations
        for sku, locations in sku_locations.items():
            if len(locations) > 1:
                duplicate_skus.add(sku)
                duplicate_locations.update(locations)
                
        return duplicate_locations
        
    def show_duplicate_skus(self):
        """Highlight grid cells with duplicate SKUs"""
        # Clear previous highlights
        self.clear_search(keep_fields=True)
        
        # Find all locations with duplicate SKUs
        duplicate_locations = self.find_duplicate_skus()
        
        # Highlight the cells
        highlighted_count = 0
        for (col_name, row_name), cell in self.cell_objects.items():
            if (col_name, row_name) in duplicate_locations:
                self.canvas.itemconfig(cell['id'], fill="orange")
                highlighted_count += 1
        
        # Update highlighted cells and current filter
        self.highlighted_cells = duplicate_locations
        self.current_filter = "duplicates"
        
        # Update status bar
        if duplicate_locations:
            self.status_bar.config(text=f"Found {len(duplicate_locations)} locations with duplicate SKUs")
        else:
            self.status_bar.config(text="No duplicate SKUs found")
    
    def find_empty_bins(self):
        """Find all locations with empty bins in the CSV data"""
        empty_bins = set()
        
        for timestamp, sku, location in self.csv_data:
            # Skip invalid locations
            if len(location) < 5 or not location.startswith('R'):
                continue
                
            # Check if this is an empty SKU (either 'EMPTY' or a blank string)
            if sku.upper() == "EMPTY" or not sku.strip():
                # Extract grid coordinates
                try:
                    level = location[1:2]
                    column_letter = location[2:3]
                    row_num = location[3:5]
                    
                    column = level + column_letter
                    empty_bins.add((column, row_num))
                except:
                    # Skip invalid formats
                    pass
                    
        return empty_bins
        
    def show_empty_bins(self):
        """Highlight grid cells with empty bins"""
        # Clear previous highlights
        self.clear_search(keep_fields=True)
        
        # Get all empty bin locations
        empty_locations = self.find_empty_bins()
        
        # Highlight the cells with empty bins
        highlighted_count = 0
        for (col_name, row_name), cell in self.cell_objects.items():
            # Check if this cell is in our empty locations
            if (col_name, row_name) in empty_locations:
                self.canvas.itemconfig(cell['id'], fill="orange")
                highlighted_count += 1
        
        # Update highlighted cells and current filter
        self.highlighted_cells = empty_locations
        self.current_filter = "empty"
        
        # Update status bar
        if empty_locations:
            self.status_bar.config(text=f"Found {len(empty_locations)} locations with empty bins")
        else:
            self.status_bar.config(text="No empty bins found")
    
    def clear_filter(self):
        """Clear filter highlighting"""
        self.current_filter = None
        self.clear_search()

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseGridVisualizer(root)
    root.mainloop() 