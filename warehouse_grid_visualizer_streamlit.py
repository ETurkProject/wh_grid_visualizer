import streamlit as st
import pandas as pd
import csv
import io
import base64
from collections import defaultdict
import plotly.graph_objects as go
import numpy as np

class WarehouseGridVisualizerStreamlit:
    def __init__(self):
        st.set_page_config(page_title="Warehouse Grid Visualizer", layout="wide")
        
        # Define column and row names - use the same ones from the original visualizer
        self.columns = ['1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', 
                        '1N', '1O', '1P', '1Q', '1R', '1S', '1T', '1U', '1V', '1W', '1X', '1Y', '1Z', 
                        '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', 
                        '2N', '2O', '2P', '2Q', '2R', '2S', '3A', '3B', '3C', '3D', '3E', '3F', '3G', 
                        '3H', '3I', '3J', '3K', '3L', '3M', '3N', '3P', '3Q', '3R', '3S', '3T', '3U', 
                        '3V', '3W', '3X', '3Y', '3Z']
        
        self.rows = [str(i).zfill(2) for i in range(1, 91)]  # 01-90, zero-padded in reverse order
        self.rows.reverse()  # Now ordered from 90 to 01
        
        # State variables
        if 'csv_data' not in st.session_state:
            st.session_state['csv_data'] = []
        
        if 'grid_data' not in st.session_state:
            st.session_state['grid_data'] = defaultdict(lambda: defaultdict(list))
        
        if 'duplicate_skus' not in st.session_state:
            st.session_state['duplicate_skus'] = set()
            
        if 'empty_bins_locations' not in st.session_state:
            st.session_state['empty_bins_locations'] = set()
            
        if 'highlighted_cells' not in st.session_state:
            st.session_state['highlighted_cells'] = set()
            
        if 'current_filter' not in st.session_state:
            st.session_state['current_filter'] = None
            
        # Grid visualization settings
        if 'zoom_level' not in st.session_state:
            st.session_state['zoom_level'] = 1.0  # Default zoom level
            
    def run(self):
        st.title("Warehouse Grid Visualizer")
        
        # Create sidebar for controls
        with st.sidebar:
            st.header("Controls")
            
            # File upload section
            st.subheader("Upload Data")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            
            if uploaded_file is not None:
                try:
                    self.load_data_from_file(uploaded_file)
                    st.success(f"Data loaded successfully!")
                except Exception as e:
                    st.error(f"Failed to load file: {str(e)}")
            
            # Zoom controls section
            st.subheader("Zoom")
            zoom_col1, zoom_col2, zoom_col3 = st.columns([1, 1, 2])
            with zoom_col1:
                if st.button("➕"):
                    st.session_state['zoom_level'] = min(2.0, st.session_state['zoom_level'] + 0.1)
                    st.rerun()
            with zoom_col2:
                if st.button("➖"):
                    st.session_state['zoom_level'] = max(0.5, st.session_state['zoom_level'] - 0.1)
                    st.rerun()
            with zoom_col3:
                if st.button("Fit to Window"):
                    st.session_state['zoom_level'] = 1.0
                    st.rerun()
            
            # Search section
            st.subheader("Search")
            sku_query = st.text_input("SKU:", key="sku_search")
            loc_query = st.text_input("Location:", key="loc_search")
            
            search_col1, search_col2 = st.columns(2)
            with search_col1:
                if st.button("Search"):
                    self.search_grid(sku_query, loc_query)
            with search_col2:
                if st.button("Clear Search"):
                    st.session_state['highlighted_cells'] = set()
                    st.session_state['current_filter'] = None
                    # Reset search fields
                    st.session_state['sku_search'] = ""
                    st.session_state['loc_search'] = ""
                    st.rerun()
            
            # Filter section
            st.subheader("Filter Options")
            
            # Filter buttons in uniform size
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                if st.button("Duplicate SKUs", use_container_width=True):
                    self.show_duplicate_skus()
            with filter_col2:
                if st.button("Empty Bins", use_container_width=True):
                    self.show_empty_bins()
            
            # Clear filter button with full width
            if st.button("Clear Filter", use_container_width=True):
                st.session_state['highlighted_cells'] = set()
                st.session_state['current_filter'] = None
                st.rerun()
            
            # Export section (separate from filter)
            st.subheader("Export Options")
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                csv_data = self.prepare_duplicate_skus_export()
                if csv_data:
                    st.download_button(
                        label="Export Duplicates",
                        data=self.convert_to_csv(csv_data, ["SKU", "Bin Locations"]),
                        file_name="duplicate_skus.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("Export Duplicates", disabled=True, use_container_width=True)
            
            with export_col2:
                csv_data = self.prepare_empty_bins_export()
                if csv_data:
                    st.download_button(
                        label="Export Empty",
                        data=self.convert_to_csv(csv_data, ["Grid Location", "Bin Locations"]),
                        file_name="empty_bins.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("Export Empty", disabled=True, use_container_width=True)
        
        # Main content area
        if st.session_state['csv_data']:
            # Display the grid visualization
            st.subheader("Warehouse Grid")
            
            # Display statistics above the grid
            occupied_count = sum(1 for c in self.columns for r in self.rows 
                              if c in st.session_state['grid_data'] and r in st.session_state['grid_data'][c])
            total_cells = len(self.columns) * len(self.rows)
            st.caption(f"Grid: {len(self.columns)}x{len(self.rows)} = {total_cells} cells, Occupied: {occupied_count}")
            
            # Create the grid visualization
            fig = self.create_grid_visualization()
            
            # Display the Plotly figure with fixed ratio
            container = st.container()
            with container:
                clicked_point = plotly_chart = st.plotly_chart(fig, use_container_width=True, key="grid_chart")
            
            # Add cell selection interface below the grid
            st.subheader("Cell Details")
            col1, col2 = st.columns(2)
            with col1:
                selected_column = st.selectbox("Column", self.columns)
            with col2:
                selected_row = st.selectbox("Row", self.rows)
            
            if st.button("View Cell Details"):
                self.show_grid_details(selected_column, selected_row)
        else:
            st.info("Upload a CSV file to visualize the warehouse grid.")
            
    def load_data_from_file(self, uploaded_file):
        # Clear existing data
        st.session_state['csv_data'] = []
        st.session_state['grid_data'] = defaultdict(lambda: defaultdict(list))
        st.session_state['highlighted_cells'] = set()
        st.session_state['current_filter'] = None
        
        # Load CSV data
        # Convert BytesIO to StringIO for proper CSV parsing
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        reader = csv.reader(stringio)
        
        # Read the header row to find column indices
        headers = next(reader)
        
        # Find the indices of garment_sku and location_id columns (case insensitive)
        sku_idx = None
        location_idx = None
        
        for idx, header in enumerate(headers):
            if header.lower() == "garment_sku":
                sku_idx = idx
            elif header.lower() == "location_id":
                location_idx = idx
        
        # Verify we found the required columns
        if sku_idx is None or location_idx is None:
            raise ValueError("CSV file must contain 'garment_sku' and 'location_id' columns")
        
        # Process data rows
        for row in reader:
            # Skip rows that don't have enough columns
            if len(row) <= max(sku_idx, location_idx):
                continue
            
            # Extract sku and location values
            sku = row[sku_idx]
            location = row[location_idx]
            
            # Save data for search functionality
            st.session_state['csv_data'].append((sku, location))
            
            # Extract grid location from bin location
            if len(location) >= 5 and location.startswith('R'):
                level = location[1:2]  # e.g., 1 from R1S32-N-AT1
                column_letter = location[2:3]  # e.g., S from R1S32-N-AT1
                row_num = location[3:5]  # e.g., 32 from R1S32-N-AT1
                
                column = level + column_letter  # e.g., 1S
                bin_code = location  # Full bin location
                
                # Add SKU to the grid's bin list
                st.session_state['grid_data'][column][row_num].append((sku, bin_code))
        
        # Analyze the data for duplicates and empty bins
        self.analyze_data()
    
    def analyze_data(self):
        sku_locations = defaultdict(list)
        st.session_state['duplicate_skus'] = set()
        st.session_state['empty_bins_locations'] = set()
        
        # Find duplicate SKUs and empty bins
        for column in st.session_state['grid_data']:
            for row in st.session_state['grid_data'][column]:
                for sku, bin_location in st.session_state['grid_data'][column][row]:
                    # Track locations for each SKU
                    sku_locations[sku].append((column, row))
                    
                    # Check for empty bins - including both "EMPTY" SKUs and empty SKU fields
                    if sku.upper() == "EMPTY" or not sku:
                        st.session_state['empty_bins_locations'].add((column, row))
        
        # Find which SKUs appear in multiple locations
        for sku, locations in sku_locations.items():
            # Only consider non-empty SKUs for duplicates
            if len(locations) > 1 and sku.upper() != "EMPTY" and sku.strip() and len(sku) == 9:
                st.session_state['duplicate_skus'].add(sku)
    
    def create_grid_visualization(self):
        """Create grid visualization using Plotly with labeled axes, bordered cells, and click events"""
        # Create a matrix for the heatmap (this is the standard approach)
        grid_values = []
        hover_texts = []
        
        # Populate the grid: 0 = empty, 1 = occupied, 2 = highlighted
        for col_idx, col_name in enumerate(self.columns):
            row_values = []
            hover_row = []
            for row_idx, row_name in enumerate(self.rows):
                # Check if cell has items
                has_items = col_name in st.session_state['grid_data'] and row_name in st.session_state['grid_data'][col_name]
                
                # Check if cell is highlighted
                is_highlighted = (col_name, row_name) in st.session_state['highlighted_cells']
                
                # Set cell value based on state
                if is_highlighted:
                    row_values.append(2)  # Highlighted
                elif has_items:
                    row_values.append(1)  # Occupied
                else:
                    row_values.append(0)  # Empty
                
                # Create hover text
                if has_items:
                    items_count = len(st.session_state['grid_data'][col_name][row_name])
                    hover_row.append(f"Location: {col_name}{row_name}<br>Items: {items_count}")
                else:
                    hover_row.append(f"Location: {col_name}{row_name}<br>Empty")
            
            grid_values.append(row_values)
            hover_texts.append(hover_row)
        
        # Apply current zoom level to figure dimensions
        base_height = 800
        base_width = 1200
        height = base_height * st.session_state['zoom_level']
        width = base_width * st.session_state['zoom_level']
        
        # Create a heatmap with standard matrix structure
        fig = go.Figure()
        
        # Add the heatmap with named axes
        fig.add_trace(go.Heatmap(
            z=grid_values,
            x=self.rows,
            y=self.columns,
            colorscale=[[0, '#303030'], [0.5, '#50C878'], [1, '#FF8C00']],  # Darker empty cells, vibrant green and orange
            showscale=False,
            hoverinfo='text',
            text=hover_texts
        ))
        
        # Update layout to make cells square and add borders
        fig.update_layout(
            height=height,
            width=width,
            title='Warehouse Grid',
            margin=dict(l=50, r=50, t=100, b=50),
            # Make cells square and add borders
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                title='Column',
                autorange='reversed',
                showgrid=True,
                gridwidth=2,  # Thicker grid lines
                gridcolor='#888888',  # Lighter gray for contrast
                tickmode='array',
                tickvals=self.columns,
                ticktext=self.columns,
                tickfont=dict(color='#FFFFFF'),  # White text for tick labels
                title_font=dict(color='#FFFFFF'),  # White text for axis title
                constrain='domain'  # This helps maintain aspect ratio
            ),
            xaxis=dict(
                title='Row',
                side='top',
                showgrid=True,
                gridwidth=2,  # Thicker grid lines
                gridcolor='#888888',  # Lighter gray for contrast
                tickmode='array',
                tickvals=self.rows,
                ticktext=self.rows,
                tickangle=-90,
                tickfont=dict(color='#FFFFFF'),  # White text for tick labels
                title_font=dict(color='#FFFFFF'),  # White text for axis title
                constrain='domain',  # This helps maintain aspect ratio
                scaleanchor='y',
                scaleratio=1
            ),
            clickmode='event+select'
        )
        
        # Configure for dark theme
        fig.update_layout(
            plot_bgcolor='#1E1E1E',  # Dark gray background
            paper_bgcolor='#121212',  # Very dark gray paper
            title_font=dict(color='#FFFFFF'),  # White title text
            font=dict(color='#FFFFFF'),  # White font for all other text
            autosize=False,  # Prevent automatic resizing
            uniformtext=dict(mode='hide', minsize=8)  # Ensure uniform text size
        )
        
        # Add grid shaping to ensure all cells have visible borders
        shapes = []
        
        # Add vertical grid lines
        for i in range(len(self.rows) + 1):
            x_pos = i - 0.5 if i > 0 else i  # Adjust line position
            shapes.append(
                dict(
                    type='line',
                    xref='x',
                    yref='paper',
                    x0=x_pos,
                    y0=0,
                    x1=x_pos,
                    y1=1,
                    line=dict(color='#888888', width=1.5)
                )
            )
        
        # Add horizontal grid lines
        for i in range(len(self.columns) + 1):
            y_pos = i - 0.5 if i > 0 else i  # Adjust line position
            shapes.append(
                dict(
                    type='line',
                    xref='paper',
                    yref='y',
                    x0=0,
                    y0=y_pos,
                    x1=1,
                    y1=y_pos,
                    line=dict(color='#888888', width=1.5)
                )
            )
        
        fig.update_layout(shapes=shapes)
        
        return fig
    
    def show_grid_details(self, column, row):
        st.subheader(f"Details for Cell {column}{row}")
        
        if column in st.session_state['grid_data'] and row in st.session_state['grid_data'][column]:
            # Create a DataFrame to display the items
            items = []
            for sku, bin_location in st.session_state['grid_data'][column][row]:
                items.append({"SKU": sku, "Bin Location": bin_location})
            
            # Create DataFrame
            df = pd.DataFrame(items)
            
            # Highlight rows based on current filter
            def highlight_rows(row):
                sku = row['SKU']
                style = ''
                
                if st.session_state['current_filter'] == 'duplicates' and sku in st.session_state['duplicate_skus']:
                    style = 'background-color: lightyellow'
                elif st.session_state['current_filter'] == 'empty' and (sku.upper() == "EMPTY" or not sku.strip()):
                    style = 'background-color: lightyellow'
                
                return [style, style]
            
            # Apply styling
            styled_df = df.style.apply(highlight_rows, axis=1)
            
            # Display the dataframe
            st.dataframe(styled_df)
            
            # Export options
            if st.button("Export Cell Data"):
                csv_data = self.convert_df_to_csv(df)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"cell_{column}{row}.csv",
                    mime="text/csv",
                )
        else:
            st.info("No items found in this cell.")
    
    def search_grid(self, sku_query, loc_query):
        # If no search terms provided, return
        if not sku_query and not loc_query:
            st.warning("Please enter an SKU or location to search.")
            return
        
        # Clear current highlights
        st.session_state['highlighted_cells'] = set()
        st.session_state['current_filter'] = None
        
        # Find matching locations
        matching_locations = set()
        
        for sku, location in st.session_state['csv_data']:
            # Skip if location is too short
            if len(location) < 5:
                continue
                
            # Extract grid location
            if location.startswith('R'):
                level = location[1:2]
                column_letter = location[2:3]
                row = location[3:5]
                column = level + column_letter
                
                # Check if SKU or location matches search criteria
                sku_match = sku_query and sku_query.upper() in sku.upper()
                loc_match = loc_query and loc_query.upper() in location.upper()
                
                if sku_match or loc_match:
                    matching_locations.add((column, row))
        
        # Update highlighted cells
        st.session_state['highlighted_cells'] = matching_locations
        
        if matching_locations:
            st.success(f"Found {len(matching_locations)} matching locations.")
        else:
            st.warning("No matching locations found.")
    
    def show_duplicate_skus(self):
        # Find all locations with duplicate SKUs
        duplicate_locations = self.find_duplicate_skus()
        
        # Update highlighted cells
        st.session_state['highlighted_cells'] = duplicate_locations
        st.session_state['current_filter'] = "duplicates"
        
        if duplicate_locations:
            st.success(f"Found {len(duplicate_locations)} locations with duplicate SKUs.")
        else:
            st.warning("No duplicate SKUs found.")
    
    def find_duplicate_skus(self):
        """Find all SKUs that appear in multiple locations (excluding EMPTY and blank SKUs)"""
        sku_locations = defaultdict(list)
        duplicate_locations = set()
        
        # First pass: collect all bin locations for each SKU
        for sku, location in st.session_state['csv_data']:
            # Skip empty, EMPTY, or SKUs that aren't exactly 9 characters
            if not sku.strip() or sku.upper() == "EMPTY" or len(sku) != 9:
                continue
                
            if len(location) >= 5 and location.startswith('R'):
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
                duplicate_locations.update(locations)
                
        return duplicate_locations
    
    def show_empty_bins(self):
        # Find all locations with empty bins
        empty_locations = self.find_empty_bins()
        
        # Update highlighted cells
        st.session_state['highlighted_cells'] = empty_locations
        st.session_state['current_filter'] = "empty"
        
        if empty_locations:
            st.success(f"Found {len(empty_locations)} locations with empty bins.")
        else:
            st.warning("No empty bins found.")
    
    def find_empty_bins(self):
        """Find all locations with empty bins in the CSV data"""
        empty_bins = set()
        
        for sku, location in st.session_state['csv_data']:
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
    
    def prepare_duplicate_skus_export(self):
        """Prepare data for duplicate SKUs export"""
        # Dictionary to store all locations for each SKU
        sku_locations = defaultdict(list)
        
        # First pass: collect all bin locations for each SKU
        for sku, location in st.session_state['csv_data']:
            # Skip empty, EMPTY, or SKUs that aren't exactly 9 characters
            if not sku.strip() or sku.upper() == "EMPTY" or len(sku) != 9:
                continue
                
            if len(location) >= 5 and location.startswith('R'):
                sku_locations[sku].append(location)
        
        # Second pass: filter to only keep duplicates and format for export
        export_data = []
        
        for sku, locations in sku_locations.items():
            if len(locations) > 1:  # It's a duplicate
                # Sort locations for consistency
                locations.sort()
                # Join all locations with commas
                locations_text = ", ".join(locations)
                export_data.append((sku, locations_text))
        
        # Sort by SKU for easier reading
        export_data.sort(key=lambda x: x[0])
        
        return export_data
    
    def prepare_empty_bins_export(self):
        """Prepare data for empty bins export"""
        # Dictionary to store bin locations for each grid location
        grid_locations = defaultdict(list)
        
        # Find all empty bins
        for sku, location in st.session_state['csv_data']:
            # Check if this is an empty bin
            if sku.upper() == "EMPTY" or not sku.strip():
                if len(location) >= 5 and location.startswith('R'):
                    try:
                        # Extract grid coordinates
                        level = location[1:2]
                        column_letter = location[2:3]
                        row_num = location[3:5]
                        
                        grid_loc = f"{level}{column_letter}{row_num}"
                        
                        # Add this bin location to the appropriate grid location
                        grid_locations[grid_loc].append(location)
                    except:
                        # Skip invalid formats
                        continue
        
        # Format for export
        export_data = []
        
        for grid_loc, bin_locations in grid_locations.items():
            # Sort locations for consistency
            bin_locations.sort()
            # Join all locations with commas
            locations_text = ", ".join(bin_locations)
            export_data.append((grid_loc, locations_text))
        
        # Sort by grid location for easier reading
        export_data.sort(key=lambda x: x[0])
        
        return export_data
    
    def convert_to_csv(self, data, headers):
        """Convert data to CSV format for download"""
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(headers)
        writer.writerows(data)
        return csv_buffer.getvalue()
    
    def convert_df_to_csv(self, df):
        """Convert DataFrame to CSV for download"""
        return df.to_csv(index=False).encode('utf-8')


if __name__ == "__main__":
    app = WarehouseGridVisualizerStreamlit()
    app.run() 