import streamlit as st
import pandas as pd
import plotly.express as px

def weekly_sales_analysis(data, selected_brands_sidebar, top_brands):
    st.markdown("<h1 style='text-align: center; color: green;'>Weekly Sales</h1>", unsafe_allow_html=True)

    # Ensure data and top_brands are available
    if data is None or (selected_brands_sidebar is None and top_brands is None):
        st.warning("Please upload data and select at least one brand.")
        return

    # Filter data for the selected brands (sidebar filter)
    if len(selected_brands_sidebar) > 0:
        filtered_data = data[data['brandName'].isin(selected_brands_sidebar)]
    else:
        filtered_data = data

    # Further filter data based on top N brands if top_brands is provided
    if top_brands:
        filtered_data = filtered_data[filtered_data['brandName'].isin(top_brands)]

    # Check if filtered data is empty
    if filtered_data.empty:
        st.warning("No sales data available for the selected brands.")
        return

    # Extract the day of the week and month from orderDate
    filtered_data['day'] = filtered_data['orderDate'].dt.day_name()
    filtered_data['month'] = filtered_data['orderDate'].dt.month_name()

    # Calculate total selling price by multiplying sellingPrice with quantity
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Aggregate sales data based on brand, month, and dynamic week label
    filtered_data['month_year'] = filtered_data['orderDate'].dt.to_period('M') 
    filtered_data['week_number'] = filtered_data.groupby('month_year')['orderDate'].transform(
        lambda x: (x.dt.day - 1) // 7 + 1 
    )
    filtered_data['week_label'] = 'Week ' + filtered_data['week_number'].astype(str)
    
    weekly_sales_by_week = (
        filtered_data.groupby(['month', 'brandName', 'week_label'], as_index=False)
        .agg(
            total_selling_price=('total_selling_price', 'sum'),
            total_cost_price=('total_cost_price', 'sum'),
            total_quantity=('quantity', 'sum'),
            category_count=('categoryName', 'nunique')
        )
        .sort_values(by=['month', 'week_label'])
    )

    # Pivot the DataFrame to create separate columns for each week label
    sales_by_week = weekly_sales_by_week.pivot_table(
        index=['month', 'brandName'],
        columns='week_label',
        values='total_selling_price',
        fill_value=0
    ).reset_index()

    # Calculate weekly sales growth percentage
    sales_by_week_growth = sales_by_week.copy()
    week_columns = sales_by_week.columns[2:]  # All week columns

    # Calculate percentage growth for each week column relative to the previous week
    for i in range(1, len(week_columns)):
        week, prev_week = week_columns[i], week_columns[i - 1]
        sales_by_week_growth[f"{week}_growth"] = (
            (sales_by_week[week] - sales_by_week[prev_week]) / sales_by_week[prev_week]
        ) * 100

    # Display the weekly sales with growth percentage
    st.markdown("<h4 style='text-align: center; color: green;'>Week-wise Sales with Growth Percentage</h4>", unsafe_allow_html=True)
    st.dataframe(sales_by_week_growth)

    # Sidebar options for chart customization
    st.sidebar.subheader("Weekly Sales Chart Settings")
    chart_type = st.sidebar.selectbox(
        "Select Chart Type", 
        ["Line Chart", "Bar Chart", "Area Chart", "Donut Chart"], 
        index=1
    )
    color_scheme = px.colors.qualitative.Plotly
    
    # Chart rendering based on user selection
    if chart_type == "Line Chart":
        fig = px.line(
            weekly_sales_by_week,
            x='week_label',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend by Brand",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Bar Chart":
        fig = px.bar(
            weekly_sales_by_week,
            x='week_label',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend by Brand",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Area Chart":
        fig = px.area(
            weekly_sales_by_week,
            x='week_label',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend by Brand",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Donut Chart":
        donut_data = sales_by_week.melt(id_vars=['month', 'brandName'], value_vars=sales_by_week.columns[2:], 
                                         var_name='week_label', value_name='total_selling_price')
        fig = px.pie(
            donut_data,
            names='week_label',
            values='total_selling_price',
            title="Sales Distribution by Week",
            hole=0.4,
            color_discrete_sequence=color_scheme
        )
        fig.update_layout(height=600)

    # Display the selected chart type
    st.plotly_chart(fig, use_container_width=True)

