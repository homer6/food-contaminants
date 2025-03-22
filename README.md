# Food Contaminants Data Explorer

An interactive web application for exploring FDA food contaminant data.

## Overview

This application provides a user-friendly interface to explore and visualize FDA contaminant levels in various food commodities. Users can filter the data, search for specific information, and view visualizations to better understand the relationships within the data.

## Features

- **Interactive Filtering**: Filter data by contaminant, commodity, and level type
- **Search Functionality**: Search across all data fields
- **Data Visualization**: View contaminant distribution in a bar chart
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

We offer two versions of this application:
1. A traditional web application using HTML/CSS/JavaScript
2. A Gradio-based Python application with enhanced filtering and visualization

### Prerequisites

- Python 3.7+ installed (required for the Gradio version)
- A modern web browser (Chrome, Firefox, Safari, or Edge)

### Installation and Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/homer6/food-contaminants.git
   cd food-contaminants
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Create a virtual environment (use python3 on macOS/Linux if python command is not found)
   python -m venv venv
   # or
   python3 -m venv venv
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 1: Run the Gradio Application (Recommended)

The Gradio application provides an enhanced user interface with better filtering options and interactive visualizations.

```bash
# Make sure your virtual environment is activated
python gradio_app.py
# or
python3 gradio_app.py
```

Open your browser and navigate to http://127.0.0.1:7860

### Option 2: Run the Traditional Web Application

**IMPORTANT**: The traditional web application **cannot** be run by directly opening the HTML file in a browser due to CORS security restrictions. You **must** use a local web server.

Start a Python HTTP server (this will run until you stop it with Ctrl+C):
```bash
# Make sure your virtual environment is activated
# Start server on default port 8000
python -m http.server
# or
python3 -m http.server
```

Open your browser and navigate to http://localhost:8000

### Using the Application

1. Use the dropdown filters to narrow down results by contaminant, commodity, or level type
2. Use the search box to search across all fields
3. Click "Clear All Filters" to reset the view
4. Examine the bar chart visualization to see contaminant distribution
5. When you're done, return to the terminal and press Ctrl+C to stop the server

> **Note**: If you see an error like `Failed to load resource: net::ERR_FAILED` or `Access to fetch has been blocked by CORS policy`, it means you're trying to open the HTML file directly without using a web server.

## Data Source

Downloaded from FDA Chemical Contaminants Transparency Tool; http://hfpappexternal.fda.gov/scripts/fdcc/?set=contaminant-levels
- Last updated: 3/20/2025
- Downloaded: 3/22/2025

"Users of this table are encouraged to refer to the document listed in the reference column for additional explanation on how each contaminant level is applied."

Original source: https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=contaminant-levels

## License

See the [LICENSE](LICENSE) file for details.