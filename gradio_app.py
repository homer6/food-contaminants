import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime

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

# Create visualizations
def create_visualizations(filtered_df, chart_type):
    """Create different types of visualizations based on the filtered data"""
    # Debug information
    print(f"Creating visualization with {len(filtered_df)} rows of data")
    print(f"Chart type: {chart_type}")
    
    # Force chart_type to be a string in case it's None or another type
    if chart_type is None:
        chart_type = "contaminant_distribution"
    
    # Create a basic bar chart if something fails
    def create_simple_bar():
        try:
            counts = filtered_df['Contaminant'].value_counts().nlargest(10)
            fig = go.Figure(data=[
                go.Bar(
                    x=counts.index.tolist(),
                    y=counts.values.tolist(),
                    marker_color='rgb(55, 83, 109)'
                )
            ])
            fig.update_layout(
                title='Top 10 Contaminants',
                xaxis=dict(title='Contaminant'),
                yaxis=dict(title='Count'),
                height=500
            )
            return fig
        except Exception as e:
            print(f"Error in create_simple_bar: {e}")
            # Create an empty figure with error message
            fig = go.Figure()
            fig.add_annotation(text="Error creating visualization",
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False,
                              font=dict(size=16))
            fig.update_layout(height=400)
            return fig
    
    # If no data, return empty figure with message
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for visualization",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=16))
        fig.update_layout(height=400)
        return fig
    
    # Use try-except to catch any issues
    try:
        if chart_type == "contaminant_distribution":
            # Simplified contaminant distribution chart using go.Figure
            counts = filtered_df['Contaminant'].value_counts().nlargest(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=counts.index.tolist(),
                    y=counts.values.tolist(),
                    marker_color='rgb(55, 83, 109)'
                )
            ])
            
            fig.update_layout(
                title='Top 15 Contaminants by Frequency',
                xaxis=dict(title='Contaminant', tickangle=-45),
                yaxis=dict(title='Count'),
                height=500
            )
            
        elif chart_type == "commodity_distribution":
            # Simplified commodity distribution chart
            counts = filtered_df['Commodity'].value_counts().nlargest(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=counts.index.tolist(),
                    y=counts.values.tolist(),
                    marker_color='rgb(67, 160, 71)'
                )
            ])
            
            fig.update_layout(
                title='Top 15 Commodities by Frequency',
                xaxis=dict(title='Commodity', tickangle=-45),
                yaxis=dict(title='Count'),
                height=500
            )
            
        elif chart_type == "level_type_distribution":
            # Simplified pie chart
            counts = filtered_df['Contaminant Level Type'].value_counts()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=counts.index.tolist(),
                    values=counts.values.tolist(),
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title='Distribution of Contaminant Level Types',
                height=500
            )
            
        elif chart_type == "heatmap":
            # Simplified heatmap
            top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index.tolist()
            top_commodities = filtered_df['Commodity'].value_counts().nlargest(10).index.tolist()
            
            # Create a simple matrix for the heatmap
            matrix = np.zeros((len(top_contaminants), len(top_commodities)))
            
            # Fill in the matrix
            for i, contaminant in enumerate(top_contaminants):
                for j, commodity in enumerate(top_commodities):
                    count = len(filtered_df[(filtered_df['Contaminant'] == contaminant) & 
                                           (filtered_df['Commodity'] == commodity)])
                    matrix[i, j] = count
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=top_commodities,
                y=top_contaminants,
                colorscale='Viridis'
            ))
            
            fig.update_layout(
                title='Heatmap of Top Contaminants vs Top Commodities',
                xaxis=dict(title='Commodity', tickangle=-45),
                yaxis=dict(title='Contaminant'),
                height=600
            )
            
        elif chart_type == "level_type_by_contaminant":
            # Simplified stacked bar
            top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index.tolist()
            level_types = filtered_df['Contaminant Level Type'].unique().tolist()
            
            # Create a simple figure
            fig = go.Figure()
            
            # Add a trace for each level type
            for level_type in level_types:
                y_values = []
                for contaminant in top_contaminants:
                    count = len(filtered_df[(filtered_df['Contaminant'] == contaminant) & 
                                           (filtered_df['Contaminant Level Type'] == level_type)])
                    y_values.append(count)
                
                fig.add_trace(go.Bar(
                    name=level_type,
                    x=top_contaminants,
                    y=y_values
                ))
            
            fig.update_layout(
                title='Contaminant Level Types by Top 10 Contaminants',
                xaxis=dict(title='Contaminant', tickangle=-45),
                yaxis=dict(title='Count'),
                barmode='stack',
                height=500
            )
        
        else:
            # Default to simple bar chart if chart type not recognized
            return create_simple_bar()
            
    except Exception as e:
        print(f"Error creating visualization: {e}")
        # If anything fails, return a simple bar chart
        return create_simple_bar()
    
    return fig

# Main interface update function
def update_interface(contaminant, commodity, level_type, search_term, level_min, level_max, chart_type):
    """Update the interface based on filters and chart type"""
    filtered_df = filter_data(contaminant, commodity, level_type, search_term, level_min, level_max)
    
    # Calculate stats
    stats_html = calculate_stats(filtered_df)
    
    # Create visualization
    print(f"Creating visualization with chart type: {chart_type} and {len(filtered_df)} rows")
    fig = create_visualizations(filtered_df, chart_type)
    print(f"Visualization created successfully: {fig is not None}")
    
    # Prepare the table data
    if filtered_df.empty:
        table_data = [["No data found matching your filters"] + [""] * 5]
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
            records_limited = True
        else:
            records_limited = False
    
    # Add warning message if results were limited
    if len(filtered_df) > 1000:
        records_message = f"⚠️ Showing top 1,000 records of {len(filtered_df)} total matching records"
    else:
        records_message = f"Showing all {len(filtered_df)} matching records"
    
    return stats_html, fig, table_df, records_message

def clear_filters():
    """Reset all filters to their default values"""
    # Use empty lists for multi-select dropdowns instead of None
    return [], [], [], "", None, None, "contaminant_distribution", update_interface([], [], [], "", None, None, "contaminant_distribution")

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
                    value=None,
                    multiselect=True,  # Allow selecting multiple contaminants
                    # Older versions don't have allow_custom_value
                    # allow_custom_value=False,
                    elem_id="contaminant-filter"
                )
                
                commodity_dropdown = gr.Dropdown(
                    choices=commodity_options,
                    label="Commodity",
                    value=None,
                    multiselect=True,  # Allow selecting multiple commodities
                    # Older versions don't have allow_custom_value
                    # allow_custom_value=False,
                    elem_id="commodity-filter"
                )
                
                level_type_dropdown = gr.Dropdown(
                    choices=level_type_options,
                    label="Level Type",
                    value=None,
                    multiselect=True,  # Allow selecting multiple level types
                    # Older versions don't have allow_custom_value
                    # allow_custom_value=False,
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
                
                clear_btn = gr.Button("Clear All Filters")  # Removed variant="secondary" for compatibility
            
            stats_html = gr.HTML(elem_classes=["data-card"])
        
        # Right column - visualizations and data
        with gr.Column(scale=2):
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
                label="Visualization Type",
                # Removed info parameter for compatibility
                elem_id="chart-type",
                elem_classes=["chart-selector"]
            )
            
            visualization = gr.Plot(elem_classes=["chart-container"])
            
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
    
    # Set up event handlers
    filter_inputs = [
        contaminant_dropdown, 
        commodity_dropdown, 
        level_type_dropdown, 
        search_input, 
        level_min, 
        level_max,
        chart_type
    ]
    
    filter_outputs = [
        stats_html,
        visualization, 
        data_table,
        records_message
    ]
    
    # Update interface when any filter changes
    for input_component in filter_inputs:
        if input_component == chart_type:
            # Specifically handle chart_type changes with a click event
            input_component.change(
                update_interface,
                inputs=filter_inputs,
                outputs=filter_outputs,
                api_name=False  # Ensure the event is processed immediately
            )
        else:
            input_component.change(
                update_interface,
                inputs=filter_inputs,
                outputs=filter_outputs
            )
    
    # Set up clear button
    clear_btn.click(
        clear_filters,
        outputs=filter_inputs + filter_outputs
    )
    
    # Add a specific click handler for chart type radio buttons
    # Define a specific function to handle chart type changes
    def handle_chart_type_change(contaminant, commodity, level_type, search_term, level_min, level_max, new_chart_type):
        print(f"Chart type changed to: {new_chart_type}")
        return update_interface(contaminant, commodity, level_type, search_term, level_min, level_max, new_chart_type)
    
    chart_type.select(
        handle_chart_type_change,
        inputs=filter_inputs,
        outputs=filter_outputs
    )
    
    # Initialize with all data
    demo.load(
        lambda: update_interface([], [], [], "", None, None, "contaminant_distribution"),
        outputs=filter_outputs
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=False)