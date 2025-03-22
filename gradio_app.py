import gradio as gr
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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

# Visualization Functions using Matplotlib
def create_contaminant_bar(filtered_df):
    """Create a bar chart of top contaminants using Matplotlib"""
    if filtered_df.empty:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available for visualization", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    counts = filtered_df['Contaminant'].value_counts().nlargest(15)
    
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Create the bar chart
    bars = ax.bar(counts.index, counts.values, color='#1f77b4')
    
    # Style the chart
    ax.set_title('Top 15 Contaminants by Frequency', fontsize=16)
    ax.set_xlabel('Contaminant')
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    
    # Add labels to the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    fig.tight_layout()
    return fig

def create_commodity_bar(filtered_df):
    """Create a bar chart of top commodities using Matplotlib"""
    if filtered_df.empty:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available for visualization", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    counts = filtered_df['Commodity'].value_counts().nlargest(15)
    
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Create the bar chart
    bars = ax.bar(counts.index, counts.values, color='#2ca02c')
    
    # Style the chart
    ax.set_title('Top 15 Commodities by Frequency', fontsize=16)
    ax.set_xlabel('Commodity')
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    
    # Add labels to the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    fig.tight_layout()
    return fig

def create_level_type_pie(filtered_df):
    """Create a pie chart of level types using Matplotlib"""
    if filtered_df.empty:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available for visualization", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    counts = filtered_df['Contaminant Level Type'].value_counts()
    
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(
        counts.values, 
        labels=counts.index, 
        autopct='%1.1f%%',
        startangle=90, 
        shadow=False
    )
    
    # Style the chart
    ax.set_title('Distribution of Contaminant Level Types', fontsize=16)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Improve label readability
    for text in texts:
        text.set_fontsize(9)
    
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_weight('bold')
    
    fig.tight_layout()
    return fig

def create_heatmap(filtered_df):
    """Create a heatmap of contaminants vs commodities using Matplotlib"""
    if filtered_df.empty:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available for visualization", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
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
    
    fig = Figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    
    # Create the heatmap
    im = ax.imshow(matrix, cmap='viridis')
    
    # Add a color bar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Count')
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(top_commodities)))
    ax.set_yticks(np.arange(len(top_contaminants)))
    ax.set_xticklabels(top_commodities)
    ax.set_yticklabels(top_contaminants)
    
    # Rotate the x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations
    for i in range(len(top_contaminants)):
        for j in range(len(top_commodities)):
            text = ax.text(j, i, int(matrix[i, j]),
                           ha="center", va="center", color="w" if matrix[i, j] > matrix.max() / 2 else "black")
    
    # Style the chart
    ax.set_title('Heatmap of Top Contaminants vs Top Commodities', fontsize=16)
    fig.tight_layout()
    return fig

def create_stacked_bar(filtered_df):
    """Create a stacked bar chart of level types by contaminant using Matplotlib"""
    if filtered_df.empty:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data available for visualization", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    top_contaminants = filtered_df['Contaminant'].value_counts().nlargest(10).index.tolist()
    level_types = filtered_df['Contaminant Level Type'].unique().tolist()
    
    # Prepare data
    data = {}
    for level_type in level_types:
        data[level_type] = []
        for contaminant in top_contaminants:
            count = len(filtered_df[(filtered_df['Contaminant'] == contaminant) & 
                                   (filtered_df['Contaminant Level Type'] == level_type)])
            data[level_type].append(count)
    
    fig = Figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    
    # Create the stacked bar chart
    bottoms = np.zeros(len(top_contaminants))
    for level_type in level_types:
        ax.bar(top_contaminants, data[level_type], bottom=bottoms, label=level_type)
        bottoms += np.array(data[level_type])
    
    # Style the chart
    ax.set_title('Contaminant Level Types by Top 10 Contaminants', fontsize=16)
    ax.set_xlabel('Contaminant')
    ax.set_ylabel('Count')
    ax.legend(title='Level Type')
    ax.tick_params(axis='x', rotation=45)
    
    fig.tight_layout()
    return fig

def create_empty_figure(message="No data available for visualization"):
    """Create an empty figure with a message"""
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=14)
    ax.axis('off')
    return fig

# Main visualization function
def create_visualization(filtered_df, chart_type):
    """Create a visualization based on the selected chart type"""
    try:
        # Handle empty data
        if filtered_df.empty:
            return create_empty_figure()
            
        # Create the appropriate visualization based on the chart type
        if chart_type == "contaminant_distribution":
            return create_contaminant_bar(filtered_df)
        elif chart_type == "commodity_distribution":
            return create_commodity_bar(filtered_df)
        elif chart_type == "level_type_distribution":
            return create_level_type_pie(filtered_df)
        elif chart_type == "heatmap":
            return create_heatmap(filtered_df)
        elif chart_type == "level_type_by_contaminant":
            return create_stacked_bar(filtered_df)
        else:
            # Default to contaminant bar if unknown chart type
            return create_contaminant_bar(filtered_df)
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        return create_empty_figure(f"Error creating visualization: {str(e)}")

# Main interface update function
def update_interface(contaminant, commodity, level_type, search_term, level_min, level_max, chart_type):
    """Update the interface based on filters and chart type"""
    # Filter the data
    filtered_df = filter_data(contaminant, commodity, level_type, search_term, level_min, level_max)
    
    # Calculate stats
    stats_html = calculate_stats(filtered_df)
    
    # Create visualization
    fig = create_visualization(filtered_df, chart_type)
    
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
    
    return stats_html, fig, table_df, records_message

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
            chart_type_group = gr.Group(elem_classes=["filter-group"])
            with chart_type_group:
                gr.Markdown("### Visualization Type")
                chart_type = gr.Radio(
                    choices=[
                        "contaminant_distribution",
                        "commodity_distribution", 
                        "level_type_distribution",
                        "heatmap",
                        "level_type_by_contaminant"
                    ],
                    label="Chart Type",
                    value="contaminant_distribution"
                )
                
                # Add label mapping for better user display
                chart_labels = {
                    "contaminant_distribution": "Top Contaminants (Bar Chart)",
                    "commodity_distribution": "Top Commodities (Bar Chart)", 
                    "level_type_distribution": "Level Type Distribution (Pie Chart)",
                    "heatmap": "Contaminant-Commodity Relationship (Heatmap)",
                    "level_type_by_contaminant": "Level Type by Contaminant (Stacked Bars)"
                }
                
                gr.HTML(f"""
                <div style="font-size: 0.9em; margin-top: -10px; margin-bottom: 10px; color: #666;">
                  <ul style="padding-left: 20px; margin-top: 5px;">
                    <li>{chart_labels["contaminant_distribution"]}</li>
                    <li>{chart_labels["commodity_distribution"]}</li>
                    <li>{chart_labels["level_type_distribution"]}</li>
                    <li>{chart_labels["heatmap"]}</li>
                    <li>{chart_labels["level_type_by_contaminant"]}</li>
                  </ul>
                </div>
                """)
                redraw_btn = gr.Button("Redraw Visualization")
            
            # Use Plot component to display matplotlib figure
            visualization = gr.Plot(elem_classes=["chart-container"], label="Visualization")
            
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
    
    # When filter inputs change
    for component in [contaminant_dropdown, commodity_dropdown, level_type_dropdown, search_input, level_min, level_max]:
        component.change(
            update_interface,
            inputs=all_inputs,
            outputs=all_outputs
        )
    
    # Special handler just for chart type
    chart_type.change(
        update_interface,  # Use the full update interface function instead
        inputs=all_inputs,
        outputs=all_outputs
    )
    
    # Add a redraw button for visualizations
    redraw_btn.click(
        update_interface,
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