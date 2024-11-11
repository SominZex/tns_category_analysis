import streamlit as st
import pandas as pd
import plotly.express as px

def category_comparison_analysis(data, selected_categories):
    st.subheader("Category vs. Category Comparison Analysis")

    # Filter data for selected categories
    filtered_data = data[data['categoryName'].isin(selected_categories)]

    # Group by categoryName and calculate total sales
    category_comparison = (filtered_data.groupby('categoryName')['sellingPrice']
                           .sum()
                           .sort_values(ascending=False)
                           .reset_index())

    # Display the category comparison data
    st.dataframe(category_comparison)

    # Sidebar options for chart customization
    st.sidebar.subheader("Category Comparison Chart Settings")
    
    # Assign unique keys to interactive elements
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart", "Box Plot"], key="category_comparison_chart_type")  # Unique key for selectbox
    color_scheme = st.sidebar.color_picker("Select Chart Color", "#3498DB", key="category_comparison_color_picker")  # Unique key for color picker
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="category_comparison_show_data_labels")  # Unique key for checkbox

    # Chart rendering based on user selection
    if chart_type == "Bar Chart":
        fig = px.bar(category_comparison, x='categoryName', y='sellingPrice', title="Category Comparison by Sales",
                     labels={'sellingPrice': 'Sales', 'categoryName': 'Category'}, color_discrete_sequence=[color_scheme])
    elif chart_type == "Pie Chart":
        fig = px.pie(category_comparison, names='categoryName', values='sellingPrice', title="Category Comparison by Sales",
                     color_discrete_sequence=[color_scheme])
    elif chart_type == "Box Plot":
        # Box plot requires sales data to be grouped by category for distribution analysis
        fig = px.box(filtered_data, x='categoryName', y='sellingPrice', title="Category Sales Distribution",
                     labels={'sellingPrice': 'Sales', 'categoryName': 'Category'}, color_discrete_sequence=[color_scheme])

    if show_data_labels and chart_type != "Box Plot":
        fig.update_traces(textposition="inside" if chart_type == "Pie Chart" else "top center")

    st.plotly_chart(fig)
