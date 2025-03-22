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

### To serve the traditional web application:
```bash
python -m http.server
# or
npx serve
```

## Future Enhancements

Potential improvements to consider:
1. Add more advanced visualizations (heatmaps, scatter plots, time series)
2. Implement data export functionality (CSV, JSON)
3. Add statistical analysis features
4. Improve mobile responsiveness
5. Add unit tests
6. Enhance the Gradio interface with additional filter types
7. Add comparison views between different contaminants
8. Implement geographic visualization if location data becomes available

## Maintenance

When the FDA updates their contaminant data:
1. Download the new CSV file
2. Replace `data/contaminant-levels.csv` with the updated file
3. Update the "Last updated" date in the README.md file
4. Test both application versions to ensure they still work with the new data format
   - Run the traditional web application with `python -m http.server`
   - Run the Gradio application with `python gradio_app.py`