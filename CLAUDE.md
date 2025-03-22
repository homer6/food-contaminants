# Notes for Claude

## Project Overview

This is a web application for exploring FDA food contaminant data. The application uses vanilla HTML, CSS, and JavaScript with D3.js for visualization.

## File Structure

- `index.html`: Main HTML file with the application structure
- `styles.css`: CSS styling for the application
- `app.js`: JavaScript code that handles data loading, filtering, and visualization
- `data/contaminant-levels.csv`: The dataset of FDA contaminant levels

## Development Tasks

To serve the application locally:
```bash
python -m http.server
# or
npx serve
```

## Future Enhancements

Potential improvements to consider:
1. Add more advanced visualizations (heatmaps, scatter plots)
2. Implement data export functionality (CSV, JSON)
3. Add statistical analysis features
4. Improve mobile responsiveness
5. Add unit tests

## Maintenance

When the FDA updates their contaminant data:
1. Download the new CSV file
2. Replace `data/contaminant-levels.csv` with the updated file
3. Update the "Last updated" date in the README.md file