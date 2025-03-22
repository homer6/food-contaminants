import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('data/contaminant-levels.csv')

# Clean column names and data
df.columns = df.columns.str.strip()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# Get unique values for filters
contaminants = sorted(df['Contaminant'].unique())
commodities = sorted(df['Commodity'].unique())
level_types = sorted(df['Contaminant Level Type'].unique())

def filter_data(contaminant, commodity, level_type, search_term):
    """Filter the dataframe based on user selections"""
    filtered_df = df.copy()
    
    # Apply filters
    if contaminant:
        filtered_df = filtered_df[filtered_df['Contaminant'] == contaminant]
    if commodity:
        filtered_df = filtered_df[filtered_df['Commodity'] == commodity]
    if level_type:
        filtered_df = filtered_df[filtered_df['Contaminant Level Type'] == level_type]
    
    # Apply search term across all columns
    if search_term:
        search_mask = filtered_df.apply(
            lambda row: any(search_term.lower() in str(cell).lower() for cell in row),
            axis=1
        )
        filtered_df = filtered_df[search_mask]
    
    return filtered_df

def update_table_and_chart(contaminant, commodity, level_type, search_term):
    """Update the table and chart based on filters"""
    filtered_df = filter_data(contaminant, commodity, level_type, search_term)
    
    # Prepare the table data
    if filtered_df.empty:
        table_data = [["No data found matching your filters"] + [""] * 5]
    else:
        table_data = filtered_df.values.tolist()
    
    # Create visualization - contaminant counts
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for visualization",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
    else:
        contaminant_counts = filtered_df['Contaminant'].value_counts().reset_index()
        contaminant_counts.columns = ['Contaminant', 'Count']
        
        fig = px.bar(contaminant_counts, x='Contaminant', y='Count',
                     title='Contaminant Distribution',
                     labels={'Count': 'Number of Entries'},
                     color_discrete_sequence=['#3498db'])
        
        fig.update_layout(
            xaxis_title='Contaminant',
            yaxis_title='Count',
            xaxis={'categoryorder':'total descending'},
            margin=dict(l=20, r=20, t=40, b=20),
        )
        fig.update_xaxes(tickangle=-45)
    
    # Return the table data and the figure
    return table_data, fig

def clear_filters():
    """Reset all filters to their default values"""
    return None, None, None, "", update_table_and_chart(None, None, None, "")

# Define the Gradio interface
with gr.Blocks(title="Food Contaminants Data Explorer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Food Contaminants Data Explorer")
    gr.Markdown("Explore FDA contaminant levels in various food commodities")
    
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Row():
                contaminant_dropdown = gr.Dropdown(
                    choices=[""] + contaminants,
                    label="Filter by Contaminant",
                    value=None,
                    allow_custom_value=False
                )
                
                commodity_dropdown = gr.Dropdown(
                    choices=[""] + commodities,
                    label="Filter by Commodity",
                    value=None,
                    allow_custom_value=False
                )
                
                level_type_dropdown = gr.Dropdown(
                    choices=[""] + level_types,
                    label="Filter by Level Type",
                    value=None,
                    allow_custom_value=False
                )
            
            with gr.Row():
                search_input = gr.Textbox(label="Search across all fields")
                clear_btn = gr.Button("Clear All Filters")
            
            # Output components
            output_table = gr.Dataframe(
                headers=["Contaminant", "Commodity", "Contaminant Level Type", "Level", "Reference", "Link to Reference"],
                label="Contaminant Data"
            )
            
        with gr.Column(scale=2):
            chart = gr.Plot(label="Visualization")
    
    # Set up event handlers
    filter_inputs = [contaminant_dropdown, commodity_dropdown, level_type_dropdown, search_input]
    for input_component in filter_inputs:
        input_component.change(
            update_table_and_chart,
            inputs=filter_inputs,
            outputs=[output_table, chart]
        )
    
    clear_btn.click(
        clear_filters,
        outputs=filter_inputs + [output_table, chart]
    )
    
    # Initialize with all data
    demo.load(
        lambda: update_table_and_chart(None, None, None, ""),
        outputs=[output_table, chart]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()