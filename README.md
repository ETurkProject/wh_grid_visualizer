# Warehouse Grid Visualizer

A Python application for visualizing warehouse inventory data in a grid format, allowing users to search, filter, and analyze warehouse bin locations.

## Purpose

The Warehouse Grid Visualizer is designed to help warehouse managers and inventory specialists visualize the physical layout of a warehouse and locate specific SKUs within the storage grid. It provides an intuitive graphical interface that maps inventory data from CSV files onto a warehouse grid, making it easier to:

- Identify where specific items are stored
- Find duplicate SKUs across multiple locations
- Track empty bins
- View and copy detailed bin information

## Features

- **Grid Visualization**: Display warehouse layout in a customizable grid format
- **CSV Data Import**: Load inventory data from standard CSV files
- **Search Functionality**: 
  - Search by SKU or bin location
  - Highlight matching locations on the grid
- **Filtering Options**:
  - Show locations with duplicate SKUs
  - Show empty bin locations
- **Detailed View**: Click on grid cells to see detailed information about stored items
- **Clipboard Integration**: Copy SKU, bin location, and timestamp information
- **Zoom Controls**: Adjust grid size for better visibility
- **Responsive Layout**: Grid automatically adjusts to window size

## Data Format

The application expects CSV files with the following columns:
- Timestamp
- SKU
- Location (in format like "R1S32-N-AT1")

The location format is parsed to extract:
- Rack/Level (e.g., "1" from R1S32-N-AT1)
- Column (e.g., "S" from R1S32-N-AT1)
- Row number (e.g., "32" from R1S32-N-AT1)

## Usage

1. **Starting the Application**:
   ```
   python warehouse_grid_visualizer_v0.py
   ```

2. **Loading Data**:
   - Click "Open CSV File" to browse and select your inventory data file
   - The grid will update to show occupied locations in green

3. **Navigating the Grid**:
   - Use scrollbars to move around the grid
   - Use zoom controls (+/-) to adjust cell size
   - Click "Fit to Window" to optimize the view

4. **Searching**:
   - Enter an SKU or location in the search fields
   - Click "Search" to highlight matching locations in orange
   - Click "Clear" to reset the view

5. **Filtering**:
   - Click "Duplicate SKUs" to highlight locations with duplicate items
   - Click "Empty Bins" to highlight empty storage locations
   - Click "Clear Filter" to reset the view

6. **Viewing Details**:
   - Click on any cell to open a detailed view of items at that location
   - Right-click or use Ctrl+C to copy information to the clipboard

## Requirements

- Python 3.x
- Tkinter (usually included with Python)

## Future Development

Potential future enhancements:
- Export functionality for search results
- Heat map visualization based on inventory metrics
- Integration with real-time inventory systems
- Conversion to standalone executable (.exe) for easier distribution
- Web-based version for access from multiple devices
# wh_grid_visualizer
