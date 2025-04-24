import csv
import tkinter as tk
from tkinter import ttk, StringVar, messagebox
from collections import defaultdict

class WarehouseGridVisualizer:
    def __init__(self, root, csv_file):
        self.root = root
        self.root.title("Warehouse Grid Visualizer")
        self.root.geometry("1400x800")
        
        # Define column and row names
        self.columns = ['1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', 
                        '1N', '1O', '1P', '1Q', '1R', '1S', '1T', '1U', '1V', '1W', '1X', '1Y', '1Z', 
                        '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', 
                        '2N', '2O', '2P', '2Q', '2R', '2S', '3A', '3B', '3C', '3D', '3E', '3F', '3G', 
                        '3H', '3I', '3J', '3K', '3L', '3M', '3N', '3P', '3Q', '3R']
        self.rows = [str(i).zfill(2) for i in range(1, 91)]  # 01-90, zero-padded
        
        # Load data from CSV
        self.csv_data = []
        self.grid_data = self.load_csv_data(csv_file)
        
        # Default cell size
        self.cell_width = 4
        self.cell_height = 1
        
        # Dictionary to store grid buttons for easy access
        self.grid_buttons = {}
        
        # Create UI
        self.create_ui()
    
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
                # Location format: R2G45-S-BD2
                # Grid is 2nd and 3rd chars (column) + 4th and 5th chars (row)
                if len(location) >= 5:
                    column = location[1:3]  # 2G
                    row_num = location[3:5]  # 45
                    bin_code = location  # Full bin location
                    
                    # Add SKU to the grid's bin list
                    grid_data[column][row_num].append((sku, bin_code))
        
        return grid_data
    
    def create_ui(self):
        """Create the main UI components"""
        # Create control panel at the top
        control_panel = tk.Frame(self.root)
        control_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Search section
        search_frame = tk.LabelFrame(control_panel, text="Search")
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
        
        # Zoom section
        zoom_frame = tk.LabelFrame(control_panel, text="Zoom")
        zoom_frame.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        zoom_in_btn = tk.Button(zoom_frame, text="+", command=self.zoom_in, width=3)
        zoom_in_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        zoom_out_btn = tk.Button(zoom_frame, text="-", command=self.zoom_out, width=3)
        zoom_out_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        fit_btn = tk.Button(zoom_frame, text="Fit to Window", command=self.fit_to_window)
        fit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create a frame with scrollbars
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add horizontal scrollbar
        h_scrollbar = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(main_frame, 
                              yscrollcommand=v_scrollbar.set,
                              xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        # Create a frame inside the canvas for the grid
        self.grid_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor=tk.NW)
        
        # Draw the grid
        self.draw_grid()
        
        # Bind mouse wheel for zooming
        self.canvas.bind("<Control-MouseWheel>", self.on_mousewheel)
        
        # Add key bindings for search
        sku_entry.bind("<Return>", lambda event: self.search_grid())
        loc_entry.bind("<Return>", lambda event: self.search_grid())
    
    def draw_grid(self):
        """Draw the warehouse grid"""
        # Clear previous grid if it exists
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Reset grid buttons dictionary
        self.grid_buttons = {}
        
        # Create grid header (column labels)
        tk.Label(self.grid_frame, text="", width=self.cell_width, borderwidth=1, relief="solid").grid(row=0, column=0)
        for col_idx, col_name in enumerate(self.columns):
            tk.Label(self.grid_frame, text=col_name, width=self.cell_width, borderwidth=1, relief="solid").grid(row=0, column=col_idx+1)
        
        # Create grid cells with row labels
        for row_idx, row_name in enumerate(self.rows):
            # Row label
            tk.Label(self.grid_frame, text=row_name, width=self.cell_width, borderwidth=1, relief="solid").grid(row=row_idx+1, column=0)
            
            # Create cells for each column
            for col_idx, col_name in enumerate(self.columns):
                # Determine if the grid has any SKUs
                has_items = col_name in self.grid_data and row_name in self.grid_data[col_name]
                
                # Create button with appropriate color
                color = "green" if has_items else "white"
                btn = tk.Button(self.grid_frame, width=self.cell_width, height=self.cell_height, bg=color,
                               command=lambda c=col_name, r=row_name: self.show_grid_details(c, r))
                btn.grid(row=row_idx+1, column=col_idx+1)
                
                # Store button reference
                self.grid_buttons[(col_name, row_name)] = btn
        
        # Update canvas scroll region
        self.grid_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def show_grid_details(self, column, row):
        """Show details of bins and SKUs for a specific grid location"""
        # Create a new toplevel window for details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Grid Details: {column}{row}")
        details_window.geometry("500x400")
        
        # Create a frame with scrollbar for the treeview
        frame = tk.Frame(details_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add label
        tk.Label(frame, text=f"SKUs and Bins at Location {column}{row}", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Create treeview for displaying data
        columns = ("SKU", "Bin Location")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Add data to treeview
        if column in self.grid_data and row in self.grid_data[column]:
            for sku, bin_location in self.grid_data[column][row]:
                tree.insert("", tk.END, values=(sku, bin_location))
        
        # Pack treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def search_grid(self):
        """Search the grid and highlight matching locations"""
        # Reset all cell colors first
        self.clear_search()
        
        sku_query = self.sku_search_var.get().strip().upper()
        loc_query = self.loc_search_var.get().strip().upper()
        
        # If no search terms provided, return
        if not sku_query and not loc_query:
            return
        
        # Find matching locations
        matching_locations = set()
        
        for timestamp, sku, location in self.csv_data:
            # Skip if location is too short
            if len(location) < 5:
                continue
                
            # Extract column and row
            column = location[1:3]
            row = location[3:5]
            
            # Check if SKU or location matches search criteria
            if (sku_query and sku_query in sku) or (loc_query and loc_query in location):
                matching_locations.add((column, row))
        
        # Highlight matching locations
        for column, row in matching_locations:
            if (column, row) in self.grid_buttons:
                self.grid_buttons[(column, row)].config(bg="orange")
        
        # If no matches found, show message
        if not matching_locations:
            tk.messagebox.showinfo("Search Results", "No matching locations found.")
    
    def clear_search(self):
        """Clear search results and reset grid colors"""
        # Reset search fields
        self.sku_search_var.set("")
        self.loc_search_var.set("")
        
        # Reset cell colors
        for (column, row), btn in self.grid_buttons.items():
            has_items = column in self.grid_data and row in self.grid_data[column]
            color = "green" if has_items else "white"
            btn.config(bg=color)
    
    def zoom_in(self):
        """Increase the cell size"""
        self.cell_width += 1
        self.cell_height += 1
        self.draw_grid()
    
    def zoom_out(self):
        """Decrease the cell size"""
        if self.cell_width > 2:
            self.cell_width -= 1
        if self.cell_height > 1:
            self.cell_height -= 1
        self.draw_grid()
    
    def fit_to_window(self):
        """Resize the grid to fit the window"""
        # Get window size
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()
        
        # Calculate optimal cell size
        optimal_width = max(2, int(window_width / (len(self.columns) + 1) / 10))
        optimal_height = max(1, int(window_height / (len(self.rows) + 1) / 25))
        
        # Set new cell size
        self.cell_width = optimal_width
        self.cell_height = optimal_height
        
        # Redraw grid
        self.draw_grid()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel events for zooming"""
        # Zoom in/out with Ctrl + mouse wheel
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseGridVisualizer(root, "combined_sku_locations.csv")
    root.mainloop() 