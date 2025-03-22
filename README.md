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

1. Clone this repository
2. Open `index.html` in your browser
3. Explore the data!

For local development with live reload, you can use a simple HTTP server:

```bash
# Using Python
python -m http.server

# Using Node.js
npx serve
```

## Data Source

Downloaded from FDA Chemical Contaminants Transparency Tool; http://hfpappexternal.fda.gov/scripts/fdcc/?set=contaminant-levels
- Last updated: 3/20/2025
- Downloaded: 3/22/2025

"Users of this table are encouraged to refer to the document listed in the reference column for additional explanation on how each contaminant level is applied."

Original source: https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=contaminant-levels

## License

See the [LICENSE](LICENSE) file for details.