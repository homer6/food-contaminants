import gradio as gr
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Import Bokeh libraries
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, ColorBar
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral10, Category10, Viridis256
from bokeh.layouts import column
from bokeh.embed import file_html
from bokeh.resources import CDN

# Set page configuration
page_title = "FDA Food Contaminants Explorer"
page_description = "Interactive tool for analyzing FDA food contaminant data"

# Custom CSS for better styling
custom_css = """
:root {
    --main-bg-color: #f5f7fa;
    --header-color: #2c3e50;
    --accent-color: #3498db;
    --text-color: #333;
    --border-radius: 8px;
    --box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

body {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    background-color: var(--main-bg-color);
    color: var(--text-color);
}

h1, h2, h3, h4 {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--header-color);
    font-weight: 700;
}

.app-header {
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}

.app-header p {
    color: #555;
    max-width: 800px;
}

.filter-group {
    background-color: white;
    padding: 1.2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: 1.2rem;
}

.filter-group h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    color: var(--header-color);
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
}

.data-stats {
    background-color: #e8f4fc;
    border-radius: var(--border-radius);
    padding: 1rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.data-card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.chart-container {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 1rem;
    margin-bottom: 1rem;
}

.tabs-container .tab-nav button {
    font-weight: 600;
}

.footer {
    text-align: center;
    font-size: 0.85rem;
    color: #666;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0,0,0,0.1);
}
"""

# Load and preprocess the data
def load_data():
    df = pd.read_csv('data/contaminant-levels.csv')
    
    # Clean column names and data
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    
    # Add date of last update info
    last_modified = os.path.getmtime('data/contaminant-levels.csv')
    last_modified_date = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d')
    
    return df, last_modified_date

df, last_modified_date = load_data()

# Get unique values for filters with counts
def get_filter_options(column):
    """Get sorted filter options with counts for a given column"""
    value_counts = df[column].value_counts().sort_index()
    # For compatibility with different pandas/gradio versions
    try:
        # Newer pandas versions
        items = value_counts.items()
    except AttributeError:
        # Older pandas versions
        items = zip(value_counts.index, value_counts.values)
    return [f"{value} ({count})" for value, count in items]

# Extract the actual value from a filter option string like "Value (123)"
def extract_value(option):
    if not option:
        return None
    return option.split(" (")[0]

# Define filter options
contaminant_options = [""] + get_filter_options('Contaminant')
commodity_options = [""] + get_filter_options('Commodity')
level_type_options = [""] + get_filter_options('Contaminant Level Type')

# Filter data based on selections
def filter_data(contaminant, commodity, level_type, search_term, level_min, level_max):
    """Filter the dataframe based on user selections"""
    filtered_df = df.copy()
    
    # Apply dropdown filters (extract actual values from the display strings)
    if contaminant:
        # Handle single item or list of items
        if isinstance(contaminant, list):
            # Multiple contaminants selected
            contaminant_values = [extract_value(c) for c in contaminant]
            filtered_df = filtered_df[filtered_df['Contaminant'].isin(contaminant_values)]
        else:
            # Single contaminant selected
            contaminant_value = extract_value(contaminant)
            filtered_df = filtered_df[filtered_df['Contaminant'] == contaminant_value]
    
    if commodity:
        # Handle single item or list of items
        if isinstance(commodity, list):
            # Multiple commodities selected
            commodity_values = [extract_value(c) for c in commodity]
            filtered_df = filtered_df[filtered_df['Commodity'].isin(commodity_values)]
        else:
            # Single commodity selected
            commodity_value = extract_value(commodity)
            filtered_df = filtered_df[filtered_df['Commodity'] == commodity_value]
    
    if level_type:
        # Handle single item or list of items
        if isinstance(level_type, list):
            # Multiple level types selected
            level_type_values = [extract_value(lt) for lt in level_type]
            filtered_df = filtered_df[filtered_df['Contaminant Level Type'].isin(level_type_values)]
        else:
            # Single level type selected
            level_type_value = extract_value(level_type)
            filtered_df = filtered_df[filtered_df['Contaminant Level Type'] == level_type_value]
    
    # Apply search term across all columns
    if search_term:
        search_mask = filtered_df.apply(
            lambda row: any(search_term.lower() in str(cell).lower() for cell in row),
            axis=1
        )
        filtered_df = filtered_df[search_mask]
    
    # Try to numerically filter by level if possible
    if level_min is not None or level_max is not None:
        # Try to extract numeric values from the Level column
        numeric_levels = []
        for level in filtered_df['Level']:
            # Extract numbers from strings like "1 ppm" or "0.5 mg/kg"
            try:
                num = float(''.join([c for c in level if c.isdigit() or c == '.']))
                numeric_levels.append(num)
            except:
                numeric_levels.append(None)
        
        filtered_df['NumericLevel'] = numeric_levels
        
        # Apply numeric filters if values are not None
        if level_min is not None:
            filtered_df = filtered_df[filtered_df['NumericLevel'] >= level_min]
        
        if level_max is not None:
            filtered_df = filtered_df[filtered_df['NumericLevel'] <= level_max]
        
        # Drop the temporary column
        filtered_df = filtered_df.drop('NumericLevel', axis=1)
    
    return filtered_df

# Data analysis functions
def calculate_stats(filtered_df):
    """Calculate statistics for the filtered data"""
    total_records = len(filtered_df)
    unique_contaminants = filtered_df['Contaminant'].nunique()
    unique_commodities = filtered_df['Commodity'].nunique()
    
    if total_records > 0:
        # Find most common values
        most_common_contaminant = filtered_df['Contaminant'].value_counts().idxmax()
        most_common_commodity = filtered_df['Commodity'].value_counts().idxmax()
        most_common_level_type = filtered_df['Contaminant Level Type'].value_counts().idxmax()
    else:
        most_common_contaminant = "N/A"
        most_common_commodity = "N/A"
        most_common_level_type = "N/A"
    
    stats_html = f"""
    <div class="data-stats">
        <div><strong>Records:</strong> {total_records}</div>
        <div><strong>Unique Contaminants:</strong> {unique_contaminants}</div>
        <div><strong>Unique Commodities:</strong> {unique_commodities}</div>
        <div><strong>Most Common Contaminant:</strong> {most_common_contaminant}</div>
        <div><strong>Most Common Commodity:</strong> {most_common_commodity}</div>
        <div><strong>Most Common Level Type:</strong> {most_common_level_type}</div>
    </div>
    """
    
    return stats_html

# Visualization Functions using Bokeh
def create_contaminant_bar(filtered_df):
    """Create a bar chart of top contaminants using Bokeh"""
    counts = filtered_df['Contaminant'].value_counts().nlargest(15)
    
    # Convert to DataFrame for Bokeh
    data = pd.DataFrame({'contaminant': counts.index, 'count': counts.values})
    
    # Create a ColumnDataSource
    source = ColumnDataSource(data)
    
    # Create the figure
    p = figure(
        title="Top 15 Contaminants by Frequency",
        x_range=data['contaminant'].tolist(),  # Use as categorical range
        height=500,
        width=700,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    # Add bars
    p.vbar(
        x='contaminant',
        top='count',
        width=0.9,
        source=source,
        fill_color="#1f77b4",
        line_color="#1f77b4"
    )
    
    # Add hover tooltip
    hover = HoverTool()
    hover.tooltips = [
        ("Contaminant", "@contaminant"),
        ("Count", "@count")
    ]
    p.add_tools(hover)
    
    # Style the chart
    p.xaxis.major_label_orientation = 3.14/4  # ~45 degrees
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.title.text_font_size = "16px"
    
    return p

def create_commodity_bar(filtered_df):
    """Create a bar chart of top commodities using Bokeh"""
    counts = filtered_df['Commodity'].value_counts().nlargest(15)
    
    # Convert to DataFrame for Bokeh
    data = pd.DataFrame({'commodity': counts.index, 'count': counts.values})
    
    # Create a ColumnDataSource
    source = ColumnDataSource(data)
    
    # Create the figure
    p = figure(
        title="Top 15 Commodities by Frequency",
        x_range=data['commodity'].tolist(),  # Use as categorical range
        height=500,
        width=700,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    # Add bars
    p.vbar(
        x='commodity',
        top='count',
        width=0.9,
        source=source,
        fill_color="#2ca02c",  # Green
        line_color="#2ca02c"
    )
    
    # Add hover tooltip
    hover = HoverTool()
    hover.tooltips = [
        ("Commodity", "@commodity"),
        ("Count", "@count")
    ]
    p.add_tools(hover)
    
    # Style the chart
    p.xaxis.major_label_orientation = 3.14/4  # ~45 degrees
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.title.text_font_size = "16px"
    
    return p

def create_level_type_pie(filtered_df):
    """Create a pie chart of level types using Bokeh"""
    # Bokeh doesn't have a built-in pie chart, so we need to create one manually
    
    counts = filtered_df['Contaminant Level Type'].value_counts()
    
    # Convert to DataFrame for Bokeh
    data = pd.DataFrame({
        'level_type': counts.index, 
        'count': counts.values,
        'angle': counts.values / counts.values.sum() * 2 * np.pi,
        'color': Category10[len(counts) if len(counts) <= 10 else 10][:len(counts)]
    })
    
    # Create a ColumnDataSource
    source = ColumnDataSource(data)
    
    # Create the figure
    p = figure(
        title="Distribution of Contaminant Level Types",
        height=500,
        width=700,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        x_range=(-0.5, 1.0)  # Center the pie
    )
    
    # Add wedges
    p.wedge(
        x=0, y=0,
        radius=0.4,
        start_angle=0,
        end_angle='angle',
        line_color="white",
        fill_color='color',
        source=source,
        legend_field='level_type'
    )
    
    # Add hover tooltip
    hover = HoverTool()
    hover.tooltips = [
        ("Level Type", "@level_type"),
        ("Count", "@count"),
        ("Percentage", "@angle{0.0%}")  # Format as percentage
    ]
    hover.formatters = {"@angle": "printf"}
    p.add_tools(hover)
    
    # Style the chart
    p.axis.visible = False
    p.grid.grid_line_color = None
    p.legend.location = "center_right"
    p.title.text_font_size = "16px"
    
    return p

def create_heatmap(filtered_df):
    """Create a heatmap of contaminants vs commodities using Bokeh"""
    top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index.tolist()
    top_commodities = filtered_df['Commodity'].value_counts().nlargest(10).index.tolist()
    
    # Create a matrix for the heatmap
    matrix = np.zeros((len(top_contaminants), len(top_commodities)))
    
    # Fill in the matrix
    for i, contaminant in enumerate(top_contaminants):
        for j, commodity in enumerate(top_commodities):
            count = len(filtered_df[(filtered_df['Contaminant'] == contaminant) & 
                                    (filtered_df['Commodity'] == commodity)])
            matrix[i, j] = count
    
    # Create a DataFrame
    heatmap_data = []
    for i, contaminant in enumerate(top_contaminants):
        for j, commodity in enumerate(top_commodities):
            heatmap_data.append({
                'contaminant': contaminant,
                'commodity': commodity,
                'count': matrix[i, j]
            })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create a ColumnDataSource
    source = ColumnDataSource(heatmap_df)
    
    # Create a color mapper
    max_count = heatmap_df['count'].max()
    mapper = LinearColorMapper(palette=Viridis256, low=0, high=max_count)
    
    # Create the figure
    p = figure(
        title="Heatmap of Top Contaminants vs Top Commodities",
        x_range=top_commodities,
        y_range=list(reversed(top_contaminants)),  # Reverse for better display
        height=600,
        width=700,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    # Add rectangles for heatmap
    p.rect(
        x='commodity', 
        y='contaminant',
        width=1, 
        height=1,
        source=source,
        fill_color={'field': 'count', 'transform': mapper},
        line_color=None
    )
    
    # Add color bar
    color_bar = ColorBar(
        color_mapper=mapper, 
        location=(0, 0),
        title="Count"
    )
    p.add_layout(color_bar, 'right')
    
    # Add hover tooltip
    hover = HoverTool()
    hover.tooltips = [
        ("Contaminant", "@contaminant"),
        ("Commodity", "@commodity"),
        ("Count", "@count")
    ]
    p.add_tools(hover)
    
    # Style the chart
    p.xaxis.major_label_orientation = 3.14/4  # ~45 degrees
    p.grid.grid_line_color = None
    p.title.text_font_size = "16px"
    
    return p

def create_stacked_bar(filtered_df):
    """Create a stacked bar chart of level types by contaminant using Bokeh"""
    top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index.tolist()
    level_types = filtered_df['Contaminant Level Type'].unique().tolist()
    
    # Prepare data
    data = pd.DataFrame(index=top_contaminants)
    
    # Add columns for each level type
    for level_type in level_types:
        counts = []
        for contaminant in top_contaminants:
            count = len(filtered_df[(filtered_df['Contaminant'] == contaminant) & 
                                   (filtered_df['Contaminant Level Type'] == level_type)])
            counts.append(count)
        data[level_type] = counts
    
    # Reset index to make contaminant a column
    data = data.reset_index().rename(columns={'index': 'contaminant'})
    
    # Create a ColumnDataSource
    source = ColumnDataSource(data)
    
    # Create the figure
    p = figure(
        title="Contaminant Level Types by Top 10 Contaminants",
        x_range=top_contaminants,
        height=500,
        width=700,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    # Add stacked bars
    colors = Category10[len(level_types) if len(level_types) <= 10 else 10]
    
    # For stacked bars, we track the previous level's top position
    previous = np.zeros(len(top_contaminants))
    
    for i, level_type in enumerate(level_types):
        p.vbar(
            x='contaminant',
            top=level_type,
            bottom=previous,
            width=0.9,
            source=source,
            fill_color=colors[i % len(colors)],
            line_color="white",
            legend_label=level_type
        )
        
        # Add current level values to previous for the next series
        previous += np.array(data[level_type])
    
    # Add hover tooltip
    hover = HoverTool()
    hover.tooltips = [
        ("Contaminant", "@contaminant"),
    ] + [(level_type, f"@{{{level_type}}}") for level_type in level_types]
    
    p.add_tools(hover)
    
    # Style the chart
    p.xaxis.major_label_orientation = 3.14/4  # ~45 degrees
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.title.text_font_size = "16px"
    p.legend.location = "top_right"
    
    return p

def create_empty_figure(message="No data available for visualization"):
    """Create an empty figure with a message"""
    p = figure(
        title="No Data",
        x_range=[0, 1],
        y_range=[0, 1],
        height=400,
        width=700
    )
    
    # Add the message
    p.text(
        x=0.5, y=0.5,
        text=[message],
        text_align="center",
        text_baseline="middle",
        text_font_size="16px"
    )
    
    # Hide axes and grid
    p.axis.visible = False
    p.grid.grid_line_color = None
    
    return p

# Main visualization function
def create_visualization(filtered_df, chart_type):
    """Create a visualization based on the selected chart type"""
    try:
        # Handle empty data
        if filtered_df.empty:
            fig = create_empty_figure()
            return file_html(fig, CDN)
            
        # Create the appropriate visualization based on the chart type
        if chart_type == "contaminant_distribution":
            fig = create_contaminant_bar(filtered_df)
        elif chart_type == "commodity_distribution":
            fig = create_commodity_bar(filtered_df)
        elif chart_type == "level_type_distribution":
            fig = create_level_type_pie(filtered_df)
        elif chart_type == "heatmap":
            fig = create_heatmap(filtered_df)
        elif chart_type == "level_type_by_contaminant":
            fig = create_stacked_bar(filtered_df)
        else:
            # Default to contaminant bar if unknown chart type
            fig = create_contaminant_bar(filtered_df)
        
        # Convert Bokeh figure to HTML and return
        return file_html(fig, CDN)
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        fig = create_empty_figure(f"Error creating visualization: {str(e)}")
        return file_html(fig, CDN)

# Main interface update function
def update_interface(contaminant, commodity, level_type, search_term, level_min, level_max, chart_type):
    """Update the interface based on filters and chart type"""
    # Filter the data
    filtered_df = filter_data(contaminant, commodity, level_type, search_term, level_min, level_max)
    
    # Calculate stats
    stats_html = calculate_stats(filtered_df)
    
    # Create visualization as HTML
    viz_html = create_visualization(filtered_df, chart_type)
    
    # Prepare the table data
    if filtered_df.empty:
        table_df = pd.DataFrame({
            "Contaminant": [],
            "Commodity": [],
            "Level Type": [],
            "Level": [],
            "Reference": [],
            "Link": []
        })
    else:
        # Create a clean DataFrame for display
        table_df = filtered_df.copy()
        table_df = table_df.rename(columns={
            'Contaminant Level Type': 'Level Type',
            'Link to Reference': 'Link'
        })
        
        # Limit to relevant columns and first 1000 rows to avoid performance issues
        table_df = table_df[['Contaminant', 'Commodity', 'Level Type', 'Level', 'Reference', 'Link']]
        if len(table_df) > 1000:
            table_df = table_df.head(1000)
    
    # Add warning message if results were limited
    if len(filtered_df) > 1000:
        records_message = f"⚠️ Showing top 1,000 records of {len(filtered_df)} total matching records"
    else:
        records_message = f"Showing all {len(filtered_df)} matching records"
    
    return stats_html, viz_html, table_df, records_message

def clear_filters():
    """Reset all filters to their default values"""
    empty_filter_result = update_interface([], [], [], "", None, None, "contaminant_distribution")
    return [], [], [], "", None, None, "contaminant_distribution", empty_filter_result

# Build the Gradio interface
with gr.Blocks(css=custom_css, title=page_title) as demo:
    gr.HTML(f"""
    <div class="app-header">
        <h1>{page_title}</h1>
        <p>This interactive tool allows you to explore FDA contaminant levels in various food commodities. 
        Use the filters below to narrow down the data and switch between different visualization types.</p>
        <p><small>Dataset last updated: {last_modified_date}</small></p>
    </div>
    """)
    
    with gr.Row():
        # Left column - filters
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["filter-group"]):
                gr.Markdown("### Data Filters")
                
                contaminant_dropdown = gr.Dropdown(
                    choices=contaminant_options,
                    label="Contaminant",
                    value=[],
                    multiselect=True,
                    elem_id="contaminant-filter"
                )
                
                commodity_dropdown = gr.Dropdown(
                    choices=commodity_options,
                    label="Commodity",
                    value=[],
                    multiselect=True,
                    elem_id="commodity-filter"
                )
                
                level_type_dropdown = gr.Dropdown(
                    choices=level_type_options,
                    label="Level Type",
                    value=[],
                    multiselect=True,
                    elem_id="level-type-filter"
                )
                
                search_input = gr.Textbox(
                    label="Search across all fields",
                    placeholder="Enter search terms...",
                    elem_id="search-input"
                )
                
                with gr.Row():
                    level_min = gr.Number(label="Min Level Value", value=None)
                    level_max = gr.Number(label="Max Level Value", value=None)
                
                clear_btn = gr.Button("Clear All Filters")
            
            stats_html = gr.HTML(elem_classes=["data-card"])
        
        # Right column - visualizations and data
        with gr.Column(scale=2):
            # Use Radio buttons for chart type
            chart_type = gr.Radio(
                choices=[
                    "contaminant_distribution",
                    "commodity_distribution", 
                    "level_type_distribution",
                    "heatmap",
                    "level_type_by_contaminant"
                ],
                labels=[
                    "Top Contaminants (Bar Chart)",
                    "Top Commodities (Bar Chart)", 
                    "Level Type Distribution (Pie Chart)",
                    "Contaminant-Commodity Relationship (Heatmap)",
                    "Level Type by Contaminant (Stacked Bars)"
                ],
                value="contaminant_distribution",
                label="Visualization Type"
            )
            
            # Use HTML component to display Bokeh visualization
            visualization = gr.HTML(elem_classes=["chart-container"])
            
            records_message = gr.Markdown(elem_classes=["records-message"])
            
            with gr.Group(elem_classes=["data-card"]):
                gr.Markdown("### Data Table")
                data_table = gr.DataFrame(
                    headers=[
                        "Contaminant",
                        "Commodity",
                        "Level Type",
                        "Level",
                        "Reference",
                        "Link"
                    ],
                    wrap=True,
                    elem_id="data-table",
                    max_rows=20
                )
    
    gr.HTML("""
    <div class="footer">
        <p>Data source: FDA Chemical Contaminants Transparency Tool | 
        <a href="https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=contaminant-levels" target="_blank">
        FDA Website</a></p>
    </div>
    """)
    
    # All inputs needed for update_interface
    all_inputs = [
        contaminant_dropdown, 
        commodity_dropdown, 
        level_type_dropdown, 
        search_input, 
        level_min, 
        level_max,
        chart_type
    ]
    
    # All outputs from update_interface
    all_outputs = [
        stats_html,
        visualization, 
        data_table,
        records_message
    ]
    
    # Set up the events
    
    # When filters change
    def on_any_change(*args):
        return update_interface(*args)
    
    # Any component change triggers full update
    for component in all_inputs:
        component.change(
            on_any_change,
            inputs=all_inputs,
            outputs=all_outputs
        )
    
    # Clear button handler
    clear_btn.click(
        clear_filters,
        outputs=all_inputs + all_outputs
    )
    
    # Initialize the interface with default values
    demo.load(
        lambda: update_interface([], [], [], "", None, None, "contaminant_distribution"),
        outputs=all_outputs
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=False)