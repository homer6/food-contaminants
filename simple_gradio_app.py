import gradio as gr
import pandas as pd
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('data/contaminant-levels.csv')

# Clean column names and data
df.columns = df.columns.str.strip()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# Create a simple visualization function
def create_plot():
    # Count occurrences of each contaminant
    counts = df['Contaminant'].value_counts().nlargest(10)
    
    # Create a simple bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=counts.index.tolist(),
            y=counts.values.tolist(),
            marker_color='rgb(55, 83, 109)'
        )
    ])
    
    fig.update_layout(
        title='Top 10 Contaminants',
        xaxis=dict(title='Contaminant', tickangle=-45),
        yaxis=dict(title='Count'),
        height=500
    )
    
    return fig

# Create a simple interface
with gr.Blocks(title="Simple FDA Contaminants Viewer") as demo:
    gr.Markdown("# FDA Food Contaminants Explorer")
    gr.Markdown("A simple version to debug visualization issues")
    
    plot = gr.Plot()
    
    button = gr.Button("Show Top 10 Contaminants")
    button.click(create_plot, inputs=None, outputs=plot)
    
    # Load the plot on startup
    demo.load(create_plot, inputs=None, outputs=plot)

# Launch the app
if __name__ == "__main__":
    demo.launch()