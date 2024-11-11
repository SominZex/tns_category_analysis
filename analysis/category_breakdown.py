import streamlit as st
import plotly.express as px

def category_breakdown_analysis(data, selected_brands):
    st.markdown("<h1 style='text-align: center; color: green;'>Category Breakdown</h1>", unsafe_allow_html=True)
    
    # Strip extra spaces from categoryName and brandName to ensure consistency
    data['categoryName'] = data['categoryName'].str.strip()
    data['brandName'] = data['brandName'].str.strip()

    # Filter data for selected brands
    filtered_data = data[data['brandName'].isin(selected_brands)]

    # Check if filtered data is empty
    if filtered_data.empty:
        st.warning("No data found for the selected brands and categories.")
        return

    # Calculate sales and cost by category
    filtered_data['total_sales'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Aggregate total_sales, total_cost, and quantity by categoryName
    category_sales = filtered_data.groupby('categoryName').agg(
        total_sales=('total_sales', 'sum'),
        total_cost=('total_cost', 'sum'),
        total_quantity=('quantity', 'sum')
    ).reset_index()

    # Calculate profit and profit margin
    category_sales['profit'] = category_sales['total_sales'] - category_sales['total_cost']
    category_sales['profit_margin'] = ((category_sales['profit'] / category_sales['total_sales']) * 100).round(2)

    # Format profit margin as a percentage
    category_sales['profit_margin'] = category_sales['profit_margin'].astype(str) + '%'

    # Sort the dataframe by total_sales in descending order
    category_sales = category_sales.sort_values(by='total_sales', ascending=False)

    # Display data table
    st.dataframe(category_sales)

    # Sidebar options for chart customization
    st.sidebar.subheader("Category Breakdown Chart Settings")
    
    chart_type = st.sidebar.selectbox(
        "Select Chart Type", 
        ["Bar Chart", "Pie Chart", "Treemap"], 
        key="category_breakdown_chart_type"
    )
    
    show_data_labels = st.sidebar.checkbox(
        "Show Data Labels", 
        False, 
        key="category_breakdown_show_data_labels"
    )

    # Define a color palette for the charts
    color_palette = px.colors.qualitative.Set3  # You can change this to another Plotly color palette
    
    # Chart rendering based on user selection
    if chart_type == "Bar Chart":
        fig = px.bar(category_sales, x='categoryName', y='total_sales', title="Category Breakdown by Sales",
                     labels={'total_sales': 'Sales'}, color='categoryName', color_discrete_sequence=color_palette)
        if show_data_labels:
            fig.update_traces(text=category_sales['total_sales'], textposition="outside")
    elif chart_type == "Pie Chart":
        fig = px.pie(category_sales, names='categoryName', values='total_sales', title="Category Breakdown by Sales",
                     color='categoryName', color_discrete_sequence=color_palette)
        if show_data_labels:
            fig.update_traces(textinfo="label+percent")
    elif chart_type == "Treemap":
        fig = px.treemap(category_sales, path=['categoryName'], values='total_sales', 
                         title="Category Breakdown by Sales", color='categoryName', color_discrete_sequence=color_palette)

    st.plotly_chart(fig, use_container_width=True)
