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

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, or Edge)
- Either:
  - Python 3.x installed, or
  - Node.js installed

This is a purely client-side application with no backend dependencies. Python or Node.js are only needed to run a local development server.

### Installation and Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/homer6/food-contaminants.git
   cd food-contaminants
   ```

2. **IMPORTANT**: This application **cannot** be run by directly opening the HTML file in a browser due to CORS security restrictions. You **must** use a local web server.

3. Set up a development environment:

   **Using Python (recommended):**
   
   Create and activate a virtual environment:
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
   
   Start the server (this will run until you stop it with Ctrl+C):
   ```bash
   # Start server on default port 8000
   python -m http.server
   # or
   python3 -m http.server
   
   # Or specify a port
   python -m http.server 8080
   ```

   **Using Node.js:**
   ```bash
   # Install serve if you haven't already
   npm install -g serve
   
   # Start server (this will run until you stop it with Ctrl+C)
   serve
   
   # Or use npx without installing
   npx serve
   ```

4. Open a new terminal window or browser tab and navigate to:
   - Python server: http://localhost:8000
   - Node.js serve: http://localhost:3000 (default)

5. Explore the data!

6. When you're done, return to the terminal and press Ctrl+C to stop the server.

> **Note**: If you see an error like `Failed to load resource: net::ERR_FAILED` or `Access to fetch has been blocked by CORS policy`, it means you're trying to open the HTML file directly without using a web server.

## Data Source

Downloaded from FDA Chemical Contaminants Transparency Tool; http://hfpappexternal.fda.gov/scripts/fdcc/?set=contaminant-levels
- Last updated: 3/20/2025
- Downloaded: 3/22/2025

"Users of this table are encouraged to refer to the document listed in the reference column for additional explanation on how each contaminant level is applied."

Original source: https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=contaminant-levels

## License

See the [LICENSE](LICENSE) file for details.