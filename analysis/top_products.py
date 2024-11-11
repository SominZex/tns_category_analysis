import streamlit as st
import pandas as pd
import plotly.express as px

def top_products_analysis(data, selected_categories):
    st.markdown("<h1 style='text-align: center; color: green;'>Top Product Analysis by Category</h1>", unsafe_allow_html=True)

    # Filter data for selected categories
    filtered_data = data[data['categoryName'].isin(selected_categories)]

    # Calculate profit and profit margin (per item)
    filtered_data['profit'] = filtered_data['sellingPrice'] - filtered_data['costPrice']
    filtered_data['profit_margin'] = (filtered_data['profit'] / filtered_data['sellingPrice']) * 100

    # Calculate total selling price and cost by multiplying with quantity
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Group by productId, productName, categoryName, and brandName to calculate total sales, profit, cost, and quantity
    top_products = (filtered_data.groupby(['productId', 'productName', 'categoryName', 'brandName'])
                    .agg({
                        'total_selling_price': 'sum', 
                        'total_cost_price': 'sum',
                        'profit': 'sum', 
                        'profit_margin': 'mean', 
                        'quantity': 'sum'
                    })
                    .sort_values(by='total_selling_price', ascending=False)
                    .reset_index())

    # Rename columns for clarity
    top_products.rename(columns={
        'total_selling_price': 'Selling Price',
        'quantity': 'Total Quantity',
        'total_cost_price': 'Cost'
    }, inplace=True)

    # Round the profit margin to 2 decimal places and add a percentage sign
    top_products['profit_margin'] = top_products['profit_margin'].round(2).map(lambda x: f"{x}%")

    # Determine max number of top products based on unique products for selected categories
    max_top_products = len(top_products)

    # Sidebar option for top products selector with dynamic max value, using a number input box
    st.sidebar.subheader("Top Products Selector")
    num_top_products = st.sidebar.number_input("Select Number of Top Products to Display", min_value=1, max_value=max_top_products, value=max_top_products, step=1)  # Default set to max_top_products

    # Display the selected number of top products by sales, showing categoryName and brandName as well
    top_products = top_products.head(num_top_products)
    st.dataframe(top_products)

    # Sidebar options for chart customization
    st.sidebar.subheader("Top Products Chart Settings")
    
    # Assign unique keys to interactive elements
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"], key="top_products_chart_type")
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="top_products_show_data_labels")

    # Chart rendering based on user selection
    if chart_type == "Bar Chart":
        fig = px.bar(top_products, x='productName', y='Selling Price', title="Top Products by Sales",
                     labels={'Selling Price': 'Sales', 'productName': 'Product Name'},
                     color='Selling Price', color_continuous_scale='Viridis', height=600)

        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=top_products['Selling Price'].round(2), textposition="inside")

    elif chart_type == "Pie Chart":
        fig = px.pie(top_products, names='productName', values='Selling Price', title="Top Products by Sales",
                     height=600, color='Selling Price', color_discrete_sequence=px.colors.qualitative.Set1)

        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=top_products['Selling Price'].round(2), textposition="inside")

    st.plotly_chart(fig, use_container_width=True)
