# Notes for Claude

## Project Overview

This is an application for exploring FDA food contaminant data. The application comes in two versions:
1. Traditional web app using vanilla HTML, CSS, and JavaScript with D3.js for visualization
2. Python-based Gradio application with enhanced filtering and visualization capabilities

## File Structure

### Traditional Web App:
- `index.html`: Main HTML file with the application structure
- `styles.css`: CSS styling for the application
- `app.js`: JavaScript code that handles data loading, filtering, and visualization

### Gradio App:
- `gradio_app.py`: Python script for the Gradio-based application
- `requirements.txt`: Python dependencies for the Gradio application

### Shared Resources:
- `data/contaminant-levels.csv`: The dataset of FDA contaminant levels

## Development Tasks

### To run the Gradio application (recommended):
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Gradio app
python gradio_app.py
```

#### Python 3.13+ Compatibility Note:
If you're using Python 3.13 or newer, you may encounter a "No module named 'distutils'" error. This is because distutils was removed from the standard library in Python 3.13. To fix this:

1. Make sure setuptools is installed (included in requirements.txt)
2. If still having issues, try installing setuptools explicitly:
   ```bash
   pip install setuptools
   ```

#### Troubleshooting Visualization Issues:
If you encounter issues with visualizations not displaying properly:

1. Try the simplified version which focuses just on visualization:
   ```bash
   python simple_gradio_app.py
   ```

2. Common visualization issues and solutions:
   - **Plotly version compatibility**: The app uses Plotly for charts - ensure version 5.18.0+ is installed
   - **Empty data**: Check that the CSV file is correctly formatted and loaded
   - **Browser compatibility**: Try a different browser if charts don't appear
   - **Filter issues**: The full app has multi-select filters - try clearing all filters

### To serve the traditional web application:
```bash
python -m http.server
# or
npx serve
```

## Application Features

### Enhanced Filtering in Gradio App
- **Multi-select Filters**: Select multiple contaminants, commodities, or level types
- **Live Updates**: Visualizations and data tables update automatically when filters change
- **Numeric Filtering**: Filter by minimum and maximum contaminant levels
- **Search**: Search across all data fields

### Visualizations
The Gradio application now includes multiple visualization types:
1. **Top Contaminants**: Bar chart showing the most frequent contaminants
2. **Top Commodities**: Bar chart showing the most frequent food commodities
3. **Level Type Distribution**: Pie chart showing the distribution of level types
4. **Contaminant-Commodity Heatmap**: Heat map showing relationships between top contaminants and commodities
5. **Level Type by Contaminant**: Stacked bar chart showing level types for top contaminants

## Future Enhancements

Potential improvements to consider:
1. Add more advanced visualizations (scatter plots, time series)
2. Implement data export functionality (CSV, JSON)
3. Add statistical analysis features
4. Improve mobile responsiveness
5. Add unit tests
6. Add comparison views for specific contaminant pairs
7. Implement geographic visualization if location data becomes available 
8. Add trend analysis over time if temporal data becomes available

## Maintenance

When the FDA updates their contaminant data:
1. Download the new CSV file
2. Replace `data/contaminant-levels.csv` with the updated file
3. Update the "Last updated" date in the README.md file
4. Test both application versions to ensure they still work with the new data format
   - Run the traditional web application with `python -m http.server`
   - Run the Gradio application with `python gradio_app.py`