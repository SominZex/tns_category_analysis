import streamlit as st
import pandas as pd
import plotly.express as px

def profit_margin_analysis(data, selected_categories):
    st.markdown("<h1 style='text-align: center; color: green;'>Profit Analysis by Category</h1>", unsafe_allow_html=True)

    # Filter data for selected categories
    filtered_data = data[data['categoryName'].isin(selected_categories)]

    # Ensure sellingPrice, costPrice, and quantity are numeric
    filtered_data['sellingPrice'] = pd.to_numeric(filtered_data['sellingPrice'], errors='coerce')
    filtered_data['costPrice'] = pd.to_numeric(filtered_data['costPrice'], errors='coerce')
    filtered_data['quantity'] = pd.to_numeric(filtered_data['quantity'], errors='coerce')

    # Calculate total selling price and total cost price by multiplying by quantity
    filtered_data['total_sellingPrice'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_costPrice'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Group by categoryName and sum the total sellingPrice and total costPrice
    category_grouped = (filtered_data.groupby('categoryName')
                        .agg({'total_sellingPrice': 'sum', 'total_costPrice': 'sum'})
                        .reset_index())

    # Calculate average profit margin based on summed values
    category_grouped['avg_profit_margin'] = ((category_grouped['total_sellingPrice'] - category_grouped['total_costPrice']) / 
                                              category_grouped['total_sellingPrice']) * 100

    # Round avg_profit_margin and add percentage symbol
    category_grouped['avg_profit_margin'] = category_grouped['avg_profit_margin'].round(2).astype(str) + '%'

    # Display data table with all required features, including total_sellingPrice and total_costPrice
    st.dataframe(category_grouped)

    # Sidebar options for chart customization
    st.sidebar.subheader("Profit Margin Chart Settings")
    
    # Assign unique keys to interactive elements
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Scatter Plot"], key="profit_margin_chart_type")
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="profit_margin_show_data_labels")

    # Chart rendering based on user selection
    color_palette = px.colors.qualitative.Set3  # A predefined colorful palette from Plotly

    if chart_type == "Bar Chart":
        fig = px.bar(category_grouped, x='categoryName', y='avg_profit_margin', title="Average Profit Margin by Category",
                     labels={'avg_profit_margin': 'Profit Margin (%)'}, color='categoryName', color_discrete_sequence=color_palette)
        
        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=category_grouped['avg_profit_margin'], textposition="inside")
            
    elif chart_type == "Scatter Plot":
        fig = px.scatter(category_grouped, x='categoryName', y='avg_profit_margin', title="Profit Margin by Category",
                         labels={'avg_profit_margin': 'Profit Margin (%)'}, color='categoryName', color_discrete_sequence=color_palette)

        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=category_grouped['avg_profit_margin'], textposition="top center")

    st.plotly_chart(fig, use_container_width=True)
