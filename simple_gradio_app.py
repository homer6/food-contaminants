import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('data/contaminant-levels.csv')

# Clean column names and data
df.columns = df.columns.str.strip()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# Create a simple visualization function
def create_plot():
    """Create a simple bar chart using matplotlib"""
    plt.figure(figsize=(10, 6))
    
    # Get top 10 contaminants
    counts = df['Contaminant'].value_counts().nlargest(10)
    
    # Create bar chart
    plt.bar(counts.index, counts.values, color='blue')
    
    # Style the chart
    plt.title('Top 10 Contaminants')
    plt.xlabel('Contaminant')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return plt

# Create a simple interface
with gr.Blocks(title="Simple FDA Contaminants Viewer") as demo:
    gr.Markdown("# FDA Food Contaminants Explorer")
    gr.Markdown("A simple version to debug visualization issues")
    
    # Use Plot component to display matplotlib figure
    plot = gr.Plot()
    
    # Button to show the visualization
    button = gr.Button("Show Top 10 Contaminants")
    button.click(create_plot, inputs=None, outputs=plot)
    
    # Load the plot on startup
    demo.load(create_plot, inputs=None, outputs=plot)

# Launch the app
if __name__ == "__main__":
    demo.launch()