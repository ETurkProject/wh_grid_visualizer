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
        
        # Initialize data structures
        self.csv_data = []
        self.grid_data = defaultdict(lambda: defaultdict(list))
        self.cell_objects = {}
        
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
            self.draw_grid()
            
            # Update status bar
            occupied_count = sum(1 for c in self.columns for r in self.rows 
                               if c in self.grid_data and r in self.grid_data[c])
            total_cells = len(self.columns) * len(self.rows)
            self.status_bar.config(text=f"Grid: {len(self.columns)}x{len(self.rows)} = {total_cells} cells, Occupied: {occupied_count}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.status_bar.config(text="Error loading file")
    
    def load_csv_data(self, csv_file):
        """Load and organize data from the CSV file"""
        # Dictionary to store SKUs by grid location
        grid_data = defaultdict(lambda: defaultdict(list))
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
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
        
        # Create bottom row for Search
        bottom_row = tk.Frame(control_panel)
        bottom_row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Search section
        search_frame = tk.LabelFrame(bottom_row, text="Search")
        search_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        
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
        
        # Add data to treeview
        if column in self.grid_data and row in self.grid_data[column]:
            # Find full details for each SKU at this location
            for sku, bin_location in self.grid_data[column][row]:
                # Find the timestamp for this exact SKU/location
                timestamp = ""
                for t, s, loc in self.csv_data:
                    if s == sku and loc == bin_location:
                        timestamp = t
                        break
                        
                tree.insert("", tk.END, values=(sku, bin_location, timestamp))
        else:
            tree.insert("", tk.END, values=("No items found", "", ""))
        
        # Pack treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
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
        
        # Clear highlighted cells
        self.highlighted_cells = set()
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseGridVisualizer(root)
    root.mainloop() 