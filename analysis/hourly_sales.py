import streamlit as st
import pandas as pd
import plotly.express as px

def hourly_sales_analysis(data, selected_categories):
    st.markdown("<h1 style='text-align: center; color: green;'>Hourly Sales</h1>", unsafe_allow_html=True)

    # Filter data for selected categories from main.py input
    filtered_data = data[data['categoryName'].isin(selected_categories)]
    
    # Extract hour from the time column and calculate total selling price and cost price
    filtered_data['hour'] = filtered_data['time'].apply(lambda x: x.hour if pd.notnull(x) else None)
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']
    
    hourly_sales = filtered_data.groupby(['categoryName', 'hour']).agg(
        total_selling_price=('total_selling_price', 'sum'),
        total_cost_price=('total_cost_price', 'sum'),
        quantity=('quantity', 'sum')
    ).reset_index()

    # Pivoting data for 24 columns (one for each hour) for each category
    hourly_sales_pivot = hourly_sales.pivot_table(
        index='categoryName', 
        columns='hour', 
        values='total_selling_price', 
        aggfunc='sum', 
        fill_value=0
    ).reset_index()

    # Display the pivoted data (category-wise hourly sales)
    st.dataframe(hourly_sales_pivot)

    # Sidebar options for category-wise chart
    st.sidebar.subheader("Category-wise Hourly Sales Chart Settings")
    
    chart_type_categories = st.sidebar.selectbox(
        "Select Chart Type (Category-wise)", 
        ["Line Chart", "Bar Chart", "Area Chart"], 
        key="hourly_sales_chart_type_category"
    )
    
    show_data_labels_categories = st.sidebar.checkbox(
        "Show Data Labels (Category-wise)", 
        False, 
        key="hourly_sales_show_data_labels_category"
    )
    
    # Reshaping the data for plotting (long format)
    hourly_sales_long = hourly_sales_pivot.melt(id_vars='categoryName', 
                                                value_vars=hourly_sales_pivot.columns[1:], 
                                                var_name='hour', 
                                                value_name='total_selling_price')
    
    # Chart rendering for category-wise analysis
    if chart_type_categories == "Line Chart":
        fig_categories = px.line(hourly_sales_long, x='hour', y='total_selling_price', color='categoryName',
                                 title="Category-wise Hourly Sales",
                                 labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})
    elif chart_type_categories == "Bar Chart":
        fig_categories = px.bar(hourly_sales_long, x='hour', y='total_selling_price', color='categoryName',
                                title="Category-wise Hourly Sales",
                                labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})
    else:
        fig_categories = px.area(hourly_sales_long, x='hour', y='total_selling_price', color='categoryName',
                                  title="Category-wise Hourly Sales",
                                  labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})
    
    # Ensure all hours (0-23) are on the x-axis
    fig_categories.update_xaxes(range=[0, 23], tickmode='linear', tick0=0, dtick=1)
    
    if show_data_labels_categories:
        fig_categories.update_traces(textposition="top center")
    
    # Display the Category-wise Hourly Sales chart
    st.plotly_chart(fig_categories, use_container_width=True)

    # Aggregated Hourly Sales Analysis (with 24 columns for total sales)
    st.subheader("Total Hourly Sales")

    # Aggregated hourly sales data (with 24 columns for each hour)
    total_hourly_sales = filtered_data.groupby('hour').agg(
        total_selling_price=('total_selling_price', 'sum'),
        total_cost_price=('total_cost_price', 'sum'),
        quantity=('quantity', 'sum')
    ).reset_index()

    # Display aggregated data table (with 24 columns representing each hour)
    st.dataframe(total_hourly_sales)

    # Sidebar options for aggregated chart
    st.sidebar.subheader("Aggregated Hourly Sales Chart Settings")

    chart_type_total = st.sidebar.selectbox(
        "Select Chart Type (Aggregated)", 
        ["Line Chart", "Bar Chart", "Area Chart"], 
        key="hourly_sales_chart_type_total"
    )

    show_data_labels_total = st.sidebar.checkbox(
        "Show Data Labels (Aggregated)", 
        False, 
        key="hourly_sales_show_data_labels_total"
    )

    # Chart rendering for aggregated analysis
    if chart_type_total == "Line Chart":
        fig_total = px.line(total_hourly_sales, x='hour', y='total_selling_price',
                            title="Total Hourly Sales",
                            labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})
    elif chart_type_total == "Bar Chart":
        fig_total = px.bar(total_hourly_sales, x='hour', y='total_selling_price',
                           title="Total Hourly Sales",
                           labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})
    else:
        fig_total = px.area(total_hourly_sales, x='hour', y='total_selling_price',
                            title="Total Hourly Sales",
                            labels={'total_selling_price': 'Total Sales', 'hour': 'Hour'})

    # Ensure all hours (0-23) are on the x-axis
    fig_total.update_xaxes(range=[0, 23], tickmode='linear', tick0=0, dtick=1)

    if show_data_labels_total:
        fig_total.update_traces(textposition="outside")

    # Display the Aggregated Hourly Sales chart
    st.plotly_chart(fig_total, use_container_width=True)
