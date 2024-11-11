import streamlit as st
import pandas as pd
import plotly.express as px

def category_performance_analysis(filtered_data, selected_categories, selected_stores):
    st.markdown("<h1 style='text-align: center; color: green;'>Category Performance Analysis</h1>", unsafe_allow_html=True)

    # Calculate total selling and cost prices for the filtered data
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Calculate overall total sales and profit based on the filtered data
    overall_total_selling_price = filtered_data['total_selling_price'].sum()
    overall_total_cost_price = filtered_data['total_cost_price'].sum()
    overall_profit = overall_total_selling_price - overall_total_cost_price

    # Filter data for selected categories and stores
    filtered_data = filtered_data[filtered_data['categoryName'].isin(selected_categories) & filtered_data['storeName'].isin(selected_stores)]

    # Aggregate the data based on each unique categoryName and brandName
    aggregated_data = (
        filtered_data.groupby(['categoryName', 'brandName'], as_index=False)
        .agg(
            total_selling_price=('total_selling_price', 'sum'),
            total_cost_price=('total_cost_price', 'sum'),
            total_quantity=('quantity', 'sum'),
            store_count=('storeName', 'nunique')
        )
        .sort_values(by='total_selling_price', ascending=False)
    )
    
    # Calculate profit and add it to the aggregated data
    aggregated_data['profit'] = aggregated_data['total_selling_price'] - aggregated_data['total_cost_price']
    
    # Calculate profit margin and format it as a percentage
    aggregated_data['profit_margin'] = (aggregated_data['profit'] / aggregated_data['total_selling_price']) * 100
    aggregated_data['profit_margin'] = aggregated_data['profit_margin'].apply(lambda x: f"{x:.2f}%")

    # Calculate contribution percentages based on overall totals
    aggregated_data['sales_contribution'] = (aggregated_data['total_selling_price'] / overall_total_selling_price) * 100
    aggregated_data['profit_contribution'] = (aggregated_data['profit'] / overall_profit) * 100
    
    # Format contribution percentages for better readability
    aggregated_data['sales_contribution'] = aggregated_data['sales_contribution'].apply(lambda x: f"{x:.2f}%")
    aggregated_data['profit_contribution'] = aggregated_data['profit_contribution'].apply(lambda x: f"{x:.2f}%")

    # Chart options for customization in the sidebar
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Area Chart"], key="chart_type_selector")
    show_data_labels = st.sidebar.checkbox("Show Data Labels", value=False, key="show_data_labels_checkbox")

    # Generate the Plotly chart based on selected options
    if chart_type == "Bar Chart":
        fig = px.bar(
            aggregated_data,
            x="categoryName",
            y="total_selling_price",
            title="Total Sales by Category and Brand",
            color="brandName",
            color_discrete_sequence=px.colors.qualitative.Set1,
            text="total_selling_price" if show_data_labels else None
        )
    elif chart_type == "Line Chart":
        fig = px.line(
            aggregated_data,
            x="categoryName",
            y="total_selling_price",
            title="Total Sales by Category and Brand",
            markers=True,
            line_shape='linear',
            color_discrete_sequence=["green"],
        )
        if show_data_labels:
            fig.update_traces(text=aggregated_data['total_selling_price'], textposition="top center")
    elif chart_type == "Area Chart":
        fig = px.area(
            aggregated_data,
            x="categoryName",
            y="total_selling_price",
            title="Total Sales by Category and Brand",
            color="brandName", 
            color_discrete_sequence=px.colors.qualitative.Set1,
        )
        if show_data_labels:
            fig.update_traces(text=aggregated_data['total_selling_price'], textposition="top center")

    # Configure the chart layout for better visuals
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Total Sales",
        hovermode="x unified",
        showlegend=True 
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h4 style='text-align: center; color: green;'>Selected Category and Brand Dataframe</h4>", unsafe_allow_html=True)

    # Display the aggregated data with contribution percentages
    st.write(aggregated_data)
