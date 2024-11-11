import streamlit as st
import pandas as pd
import plotly.express as px

# Load the GPS coordinates from the CSV file
def load_coordinates(file_path="gps_co_ordinates/co_ordinates.csv"):
    gps_df = pd.read_csv(file_path)
    return gps_df[['storeName', 'latitude', 'longitude']]

def store_performance_analysis(data, date_filtered_data, selected_categories, selected_stores):
    st.markdown("<h1 style='text-align: center; color: green;'>Stores Performance</h1>", unsafe_allow_html=True)

    # Calculate sales for all categories by store (using entire data, not just filtered data)
    all_categories_store_sales = date_filtered_data.groupby('storeName').agg(
        total_store_sales=('sellingPrice', lambda x: (x * date_filtered_data.loc[x.index, 'quantity']).sum())
    ).reset_index()

    # Filter data for selected categories
    filtered_data = data[data['categoryName'].isin(selected_categories)]
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']
    filtered_data['profit'] = filtered_data['total_selling_price'] - filtered_data['total_cost_price']

    # Filter data for selected stores
    filtered_data = filtered_data[filtered_data['storeName'].isin(selected_stores)]

    # Aggregate data by storeName for filtered data
    store_performance = filtered_data.groupby('storeName').agg(
        total_selling_price=('total_selling_price', 'sum'),
        total_quantity=('quantity', 'sum'),
        profit=('profit', 'sum'),
    ).reset_index()

    # Sort the DataFrame by total_selling_price in descending order
    store_performance = store_performance.sort_values(by='total_selling_price', ascending=False)

    # Merge with all_categories_store_sales to get total store sales (from the entire dataset, not just filtered categories)
    store_performance = store_performance.merge(all_categories_store_sales, on='storeName', how='left')

    # Ensure the relevant columns are numeric
    store_performance['total_selling_price'] = pd.to_numeric(store_performance['total_selling_price'], errors='coerce')
    store_performance['total_store_sales'] = pd.to_numeric(store_performance['total_store_sales'], errors='coerce')

    # Calculate the contribution percentage of total_selling_price to total_store_sales
    store_performance['contribution_percentage'] = (
        (store_performance['total_selling_price'] / store_performance['total_store_sales']) * 100
    )

    # Format contribution_percentage for better readability (2 decimals)
    store_performance['contribution_percentage'] = store_performance['contribution_percentage'].apply(lambda x: f"{x:.2f}%")

    # Format profit contribution for better readability
    overall_profit = store_performance['profit'].sum()
    store_performance['profit_contribution'] = (store_performance['profit'] / overall_profit) * 100
    store_performance['profit_contribution'] = store_performance['profit_contribution'].apply(lambda x: f"{x:.2f}%")

    # Sidebar options for chart customization
    st.sidebar.subheader("Store Performance Chart Settings")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart", "Line Chart"])
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="store_performance_show_data_labels")

    # Define a color palette for the charts
    color_palette = px.colors.qualitative.Plotly

    # Chart rendering based on user selection
    if chart_type == "Bar Chart":
        fig = px.bar(
            store_performance, 
            x='storeName', 
            y='total_selling_price', 
            title="Top Stores by Total Selling Price",
            labels={'total_selling_price': 'Total Selling Price'},
            color='storeName',  
            color_discrete_sequence=color_palette  
        )
        if show_data_labels:
            fig.update_traces(text=store_performance['total_selling_price'], textposition="outside")
    elif chart_type == "Pie Chart":
        fig = px.pie(
            store_performance, 
            names='storeName', 
            values='total_selling_price', 
            title="Top Stores by Total Selling Price",
            color='storeName',  
            color_discrete_sequence=color_palette  
        )
        if show_data_labels:
            fig.update_traces(textinfo='label+value', textposition="inside")
    elif chart_type == "Line Chart":
        fig = px.line(
            store_performance, 
            x='storeName', 
            y='total_selling_price', 
            title="Top Stores by Total Selling Price",
            labels={'total_selling_price': 'Total Selling Price'},
            color='storeName',  
            markers=True,
            color_discrete_sequence=color_palette
        )
        if show_data_labels:
            fig.update_traces(text=store_performance['total_selling_price'], textposition="top center")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h4 style='text-align: center; color: green;'>Store performance dataframe</h4>", unsafe_allow_html=True)

    # Conditional formatting for negative and positive sales_difference_percentage
    def format_contribution_percentage(val):
        if isinstance(val, str) and val.endswith('%'):
            percentage = float(val[:-1])
            if percentage < 0:
                return 'color: red'
            else:
                return 'color: green'
        return ''

    # Ensure numeric columns are correctly formatted (convert to numeric if necessary)
    store_performance['total_selling_price'] = pd.to_numeric(store_performance['total_selling_price'], errors='coerce')
    store_performance['profit'] = pd.to_numeric(store_performance['profit'], errors='coerce')
    store_performance['total_store_sales'] = pd.to_numeric(store_performance['total_store_sales'], errors='coerce')

    # Round the relevant columns to 2 decimal places
    store_performance['total_selling_price'] = store_performance['total_selling_price'].round(2)
    store_performance['profit'] = store_performance['profit'].round(2)
    store_performance['total_store_sales'] = store_performance['total_store_sales'].round(2)

    # Apply formatting to these columns (keeping them numeric)
    store_performance['total_selling_price'] = store_performance['total_selling_price'].apply(lambda x: f"{x:.2f}")
    store_performance['profit'] = store_performance['profit'].apply(lambda x: f"{x:.2f}")
    store_performance['total_store_sales'] = store_performance['total_store_sales'].apply(lambda x: f"{x:.2f}")


    # Display data table with conditional formatting
    st.dataframe(store_performance.style.applymap(format_contribution_percentage, subset=['contribution_percentage']))

    # Load GPS coordinates for stores from CSV file
    gps_df = load_coordinates()
    
    # Merge preloaded GPS coordinates with store_performance
    store_performance = store_performance.merge(gps_df, on='storeName', how='left')

    # Filter out stores without valid latitude and longitude
    store_performance = store_performance.dropna(subset=['latitude', 'longitude'])

    # Separate section for map visualization
    st.markdown("<h3 style='text-align: center; color: blue;'>Store Location Map</h3>", unsafe_allow_html=True)

    # Ensure numeric columns are correctly formatted (convert to numeric if necessary)
    store_performance['total_selling_price'] = pd.to_numeric(store_performance['total_selling_price'], errors='coerce')

    # Ensure that total_selling_price is numeric before calculating size
    size_variable = store_performance['total_selling_price'].fillna(0)
    
    # Now proceed with the scatter_mapbox plot using this separate size_variable
    fig_map = px.scatter_mapbox(
        store_performance,
        lat='latitude',
        lon='longitude',
        size=size_variable,
        size_max=50,
        color='storeName',
        hover_name='storeName', 
        hover_data={'storeName': True, 'total_selling_price': True},
        title="Store Locations",
        zoom=5,
    )

    # Increase the height of the map
    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=800,
    )

    st.plotly_chart(fig_map, use_container_width=True)
