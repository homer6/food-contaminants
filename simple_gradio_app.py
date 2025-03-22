import gradio as gr
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.embed import file_html
from bokeh.resources import CDN

# Load the data
df = pd.read_csv('data/contaminant-levels.csv')

# Clean column names and data
df.columns = df.columns.str.strip()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# Create visualization functions
def create_bar_chart():
    """Create a bar chart of top contaminants using Bokeh"""
    counts = df['Contaminant'].value_counts().nlargest(10)
    
    # Convert to DataFrame for Bokeh
    data = pd.DataFrame({'contaminant': counts.index, 'count': counts.values})
    
    # Create a ColumnDataSource
    source = ColumnDataSource(data)
    
    # Create the figure
    p = figure(
        title="Top 10 Contaminants",
        x_range=data['contaminant'].tolist(),
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
    
    # Convert to HTML
    html = file_html(p, CDN)
    return html

# Create a simple interface
with gr.Blocks(title="Simple FDA Contaminants Viewer") as demo:
    gr.Markdown("# FDA Food Contaminants Explorer")
    gr.Markdown("A simple version to debug visualization issues")
    
    # Use HTML component to display Bokeh visualization
    visualization = gr.HTML()
    
    # Create buttons for visualization types
    btn1 = gr.Button("Show Contaminants Bar Chart")
    btn2 = gr.Button("Show Contaminants Bar Chart Again")
    
    # Set up button click handlers to make same chart
    btn1.click(
        create_bar_chart,
        inputs=None,
        outputs=visualization
    )
    
    btn2.click(
        create_bar_chart,
        inputs=None,
        outputs=visualization
    )
    
    # Load the visualization on startup
    demo.load(
        create_bar_chart,
        inputs=None,
        outputs=visualization
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()