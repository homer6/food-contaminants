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
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for visualization",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=16))
        fig.update_layout(height=400)
        return fig
    
    if chart_type == "contaminant_distribution":
        # Contaminant distribution chart
        contaminant_counts = filtered_df['Contaminant'].value_counts().reset_index()
        contaminant_counts.columns = ['Contaminant', 'Count']
        contaminant_counts = contaminant_counts.sort_values('Count', ascending=False).head(15)
        
        fig = px.bar(contaminant_counts, 
                     x='Contaminant', 
                     y='Count',
                     title='Top 15 Contaminants by Frequency',
                     labels={'Count': 'Number of Entries', 'Contaminant': 'Contaminant'},
                     color='Count',
                     color_continuous_scale='blues')
        
        fig.update_layout(
            xaxis_title='Contaminant',
            yaxis_title='Count',
            xaxis={'categoryorder':'total descending'},
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_tickangle=-45,
            height=500
        )
        
    elif chart_type == "commodity_distribution":
        # Commodity distribution chart
        commodity_counts = filtered_df['Commodity'].value_counts().reset_index()
        commodity_counts.columns = ['Commodity', 'Count']
        commodity_counts = commodity_counts.sort_values('Count', ascending=False).head(15)
        
        fig = px.bar(commodity_counts, 
                     x='Commodity', 
                     y='Count',
                     title='Top 15 Commodities by Frequency',
                     labels={'Count': 'Number of Entries', 'Commodity': 'Commodity'},
                     color='Count',
                     color_continuous_scale='greens')
        
        fig.update_layout(
            xaxis_title='Commodity',
            yaxis_title='Count',
            xaxis={'categoryorder':'total descending'},
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis_tickangle=-45,
            height=500
        )
        
    elif chart_type == "level_type_distribution":
        # Level type distribution chart
        level_type_counts = filtered_df['Contaminant Level Type'].value_counts().reset_index()
        level_type_counts.columns = ['Level Type', 'Count']
        
        fig = px.pie(level_type_counts, 
                     values='Count', 
                     names='Level Type',
                     title='Distribution of Contaminant Level Types',
                     hole=0.3,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=500
        )
        
    elif chart_type == "heatmap":
        # Heatmap of top contaminants vs top commodities
        top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index
        top_commodities = filtered_df['Commodity'].value_counts().nlargest(10).index
        
        # Filter DataFrame to only include top contaminants and commodities
        heatmap_df = filtered_df[filtered_df['Contaminant'].isin(top_contaminants) & 
                                filtered_df['Commodity'].isin(top_commodities)]
        
        # Create a pivot table for the heatmap
        pivot_df = pd.crosstab(heatmap_df['Contaminant'], heatmap_df['Commodity'])
        
        # Fill NaN values with 0
        pivot_df = pivot_df.fillna(0)
        
        fig = px.imshow(pivot_df,
                        labels=dict(x="Commodity", y="Contaminant", color="Count"),
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        title="Heatmap of Top Contaminants vs Top Commodities",
                        color_continuous_scale="Viridis")
        
        fig.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=40, r=20, t=50, b=80),
            height=600
        )
        
    elif chart_type == "level_type_by_contaminant":
        # Stacked bar chart of level types by top contaminants
        top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index
        stacked_df = filtered_df[filtered_df['Contaminant'].isin(top_contaminants)]
        
        # Create a pivot table
        pivot_df = pd.crosstab(stacked_df['Contaminant'], stacked_df['Contaminant Level Type'])
        
        # Convert to long format for plotly
        stacked_data = pivot_df.reset_index().melt(id_vars=['Contaminant'], 
                                                  value_vars=pivot_df.columns,
                                                  var_name='Level Type', 
                                                  value_name='Count')
        
        fig = px.bar(stacked_data, 
                     x='Contaminant', 
                     y='Count', 
                     color='Level Type',
                     title='Contaminant Level Types by Top 10 Contaminants',
                     labels={'Count': 'Number of Entries', 'Contaminant': 'Contaminant', 'Level Type': 'Level Type'},
                     color_discrete_sequence=px.colors.qualitative.Bold)
        
        fig.update_layout(
            xaxis_title='Contaminant',
            yaxis_title='Count',
            xaxis_tickangle=-45,
            legend_title='Level Type',
            margin=dict(l=40, r=20, t=50, b=80),
            height=500
        )
    
    return fig

# Main interface update function
def update_interface(contaminant, commodity, level_type, search_term, level_min, level_max, chart_type):
    """Update the interface based on filters and chart type"""
    filtered_df = filter_data(contaminant, commodity, level_type, search_term, level_min, level_max)
    
    # Calculate stats
    stats_html = calculate_stats(filtered_df)
    
    # Create visualization
    fig = create_visualizations(filtered_df, chart_type)
    
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
    return None, None, None, "", None, None, "contaminant_distribution", update_interface(None, None, None, "", None, None, "contaminant_distribution")

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
    
    # Initialize with all data
    demo.load(
        lambda: update_interface(None, None, None, "", None, None, "contaminant_distribution"),
        outputs=filter_outputs
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=False)