import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def top_n_brand_sales_analysis(store_data_filtered, all_data):
    # ---- Top N Brand Sales Analysis ----
    st.markdown("<h4 style='color: green; text-align: center;'>TOP-N BRAND ANALYSIS</h4>", unsafe_allow_html=True)
    st.markdown("---")
    # Sidebar components
    st.sidebar.header("Top-N Brands Control Panel")

    # Get unique brand names for selection
    unique_brands = store_data_filtered['brandName'].unique()
    # UI components to the sidebar
    n_brands = st.sidebar.slider("Select the number of top brands to analyze:", min_value=1, max_value=len(unique_brands), value=250)
    selected_brand_color = st.sidebar.selectbox("Select Color Scale for Brand Plot:", ['Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis'], key="brand_color_scale")
    show_data_labels_brand = st.sidebar.checkbox("Show Data Labels for Top N Brand Sales Analysis", value=True, key="show_data_labels_brand")
    chart_type = st.sidebar.selectbox("Select Chart Type:", ["Bar Chart", "Donut Chart", "Line Chart"], key="chart_type_selection")

    # Group sales by brandName for the selected store data
    brand_sales = store_data_filtered.groupby('brandName').agg(
        total_sales=('sellingPrice', 'sum'),
        total_quantity=('quantity', 'sum'),
        total_cost_price=('costPrice', 'sum')
    ).reset_index()

    # Calculate total profit for each brand
    brand_sales['total_profit'] = brand_sales['total_sales'] - brand_sales['total_cost_price']

    # Sort brands by total sales and select top N
    top_n_brands = brand_sales.nlargest(n_brands, 'total_sales')

    # Calculate total sales and total profit across all brands
    total_sales_all = brand_sales['total_sales'].sum()
    total_profit_all = brand_sales['total_profit'].sum()

    # Calculate percentage contributions for the selected store
    top_n_brands['Contribution'] = (top_n_brands['total_sales'] / total_sales_all) * 100
    top_n_brands['% Contribution Profit'] = (top_n_brands['total_profit'] / total_profit_all) * 100

    # Calculate total sales for the overall dataset
    overall_brand_sales = all_data.groupby('brandName').agg(
        total_sales=('sellingPrice', 'sum'),
        quantity=('quantity', 'sum')
    ).reset_index()

    top_n_brands = top_n_brands.merge(overall_brand_sales[['brandName', 'total_sales', 'quantity']], on='brandName', suffixes=('', '_overall'))

    # Prepare only the columns needed for display
    columns_to_display = ['brandName', 'total_sales', 'total_profit', 'total_quantity', 
                          'Contribution']
    
    top_n_brands_display = top_n_brands[columns_to_display].copy()

    # Format the contribution columns for display, retaining the original data for calculations
    top_n_brands_display['Contribution'] = top_n_brands['Contribution'].map(lambda x: f"{x:.2f}%")
    top_n_brands_display['total_sales'] = top_n_brands_display['total_sales'].apply(lambda x: f"{x:.2f}")
    top_n_brands_display['total_profit'] = top_n_brands_display['total_profit'].apply(lambda x: f"{x:.2f}")

    # Display the selected top brands in a table
    # Fixed chart dimensions (1000x600)
    chart_width, chart_height = 1000, 600

    # Create plots based on selected chart type
    if chart_type == "Bar Chart":
        # Create Horizontal Bar Chart for Top N Brand Sales
        fig_brand_bar = px.bar(
            top_n_brands,
            y='brandName',
            x='total_sales',
            title=f'Top {n_brands} Brands by Total Sales',
            labels={'total_sales': 'Total Sales', 'brandName': 'Brand'},
            color='total_sales', 
            color_continuous_scale=selected_brand_color
        )
        
        if show_data_labels_brand:
            fig_brand_bar.update_traces(
                texttemplate='%{customdata[0]:.2f}%',
                textposition='outside',
                customdata=top_n_brands[['Contribution']]
            ) 

        fig_brand_bar.update_layout(width=chart_width, height=chart_height)
        st.plotly_chart(fig_brand_bar, use_container_width=False)

    elif chart_type == "Donut Chart":
        # Create Donut Chart for Top N Brand Sales
        fig_brand_donut = px.pie(
            top_n_brands,
            names='brandName',
            values='total_sales',
            title=f'Top {n_brands} Brands by Total Sales (Donut Chart)',
            hole=0.4
        )
        if show_data_labels_brand:
            fig_brand_donut.update_traces(textinfo='percent+label')

        fig_brand_donut.update_layout(width=chart_width, height=chart_height)
        st.plotly_chart(fig_brand_donut, use_container_width=False)

    elif chart_type == "Line Chart":
        # Create Line Chart for Total Sales of Top N Brands
        fig_brand_line = px.line(
            top_n_brands,
            x='brandName',
            y='total_sales',
            title=f'Top {n_brands} Brands by Total Sales (Line Chart)',
            labels={'total_sales': 'Total Sales', 'brandName': 'Brand'},
            line_shape='linear'
        )
        if show_data_labels_brand:
            fig_brand_line.add_scatter(
                x=top_n_brands['brandName'],
                y=top_n_brands['total_sales'],
                mode='text',
                text=top_n_brands['total_sales'].round(2),
                textposition='top center'
            )

        fig_brand_line.update_layout(width=chart_width, height=chart_height)
        st.plotly_chart(fig_brand_line, use_container_width=False)

    st.markdown("---")
    st.markdown("<h4 style='color: blue;'>Selected Top Brands Table</h4>", unsafe_allow_html=True)
    st.table(top_n_brands_display)

    # # Prepare benchmark analysis from top_n_brands
    # benchmark_analysis = top_n_brands[['brandName', 'total_sales', 'total_profit', 'total_quantity', 'total_cost_price']].copy()

    # # Calculate total profit for benchmark brands
    # benchmark_analysis['total_profit'] = benchmark_analysis['total_sales'] - benchmark_analysis['total_cost_price']

    # # Calculate totals for contribution calculation
    # total_sales_benchmark = benchmark_analysis['total_sales'].sum()
    # total_profit_benchmark = benchmark_analysis['total_profit'].sum()
    
    # # Calculate contributions
    # benchmark_analysis['Contribution'] = (benchmark_analysis['total_sales'] / total_sales_benchmark) * 100
    
    # # Merge with company benchmark standards
    # benchmark_analysis = benchmark_analysis.merge(
    #     company_benchmark[['brandName', 'Company Standard']], 
    #     on='brandName', 
    #     how='inner'  
    # )
    
    # # Calculate variance
    # benchmark_analysis['Variance'] = benchmark_analysis['Contribution'] - benchmark_analysis['Company Standard']
    
    # # Format for display
    # benchmark_display = benchmark_analysis[['brandName', 'total_sales', 'total_profit', 'total_quantity', 'Contribution', 'Company Standard', 'Variance']].copy()
    
    # # Format the numeric columns
    # benchmark_display['Company Standard'] = benchmark_display['Company Standard'].map(lambda x: f"{x:.2f}%")
    # benchmark_display['Contribution'] = benchmark_display['Contribution'].map(lambda x: f"{x:.2f}%")
    # benchmark_display['Variance'] = benchmark_display['Variance'].map(lambda x: f"{x:.2f}%")
    # benchmark_display['total_sales'] = benchmark_display['total_sales'].apply(lambda x: f"{x:.2f}")
    # benchmark_display['total_profit'] = benchmark_display['total_profit'].apply(lambda x: f"{x:.2f}")
    

    # # Display benchmark comparison first
    # st.markdown("<h4 style='color: green; text-align: center;'>BENCHMARK BRANDS COMPARISON</h4>", unsafe_allow_html=True)
    # st.table(benchmark_display.style.apply(
    #     lambda x: ['background-color: red' if float(val[:-1]) < 0 else '' for val in benchmark_display['Variance']],
    #     subset=['Variance']
    # ))
    
    # # New section: Find benchmark brands not available in the selected store
    # missing_benchmark_brands = benchmark_analysis[~benchmark_analysis['brandName'].isin(store_data_filtered['brandName'])]

    # # Section: Find benchmark brands not available in the selected store
    # # Compare benchmark brands directly with the selected store's brands
    # missing_benchmark_brands = company_benchmark[
    #     ~company_benchmark['brandName'].isin(store_data_filtered['brandName'])
    # ][['brandName', 'Company Standard']].copy()  # Only keep relevant columns

    # # Format 'Company Standard' if needed
    # missing_benchmark_brands['Company Standard'] = missing_benchmark_brands['Company Standard'].map(lambda x: f"{x:.2f}%")

    # # Display missing benchmark brands, or a message if none are missing
    # if not missing_benchmark_brands.empty:
    #     st.markdown("<h4 style='color: red; text-align: center;'>MISSING BENCHMARK BRANDS IN SELECTED STORE</h4>", unsafe_allow_html=True)
    #     st.table(missing_benchmark_brands)
    # else:
    #     st.markdown("<h4 style='color: green; text-align: center;'>No missing benchmark brands in the selected store.</h4>", unsafe_allow_html=True)


    # st.markdown("<br><br><br>", unsafe_allow_html=True)
    # st.markdown("<h4 style='color: green; text-align: center;'>Contribution of brand sales VS Company Standard</h4>", unsafe_allow_html=True)

    # # Display the plot
    # st.plotly_chart(fig_comparison, use_container_width=False)



    # ---- RAG Analysis ----
    # st.markdown("<h4 style='color: green; text-align: center;'>Low Performing Brands</h4>", unsafe_allow_html=True)
    # st.markdown("---")

    # # Create separate DataFrames based on price ranges
    # df_below_100 = brand_sales[brand_sales['total_sales'] < 100]
    # df_100_to_300 = brand_sales[(brand_sales['total_sales'] >= 100) & (brand_sales['total_sales'] <= 300)]
    # df_above_300 = brand_sales[brand_sales['total_sales'] > 300]

    # # Assign RAG Status based on total sales
    # df_below_100['RAG Status'] = 'Red'
    # df_100_to_300['RAG Status'] = 'Amber'
    # df_above_300['RAG Status'] = 'Green' 

    # # Round total_sales and total_profit to 2 decimal places using apply
    # df_below_100['total_sales'] = df_below_100['total_sales'].apply(lambda x: f"{x:.2f}")
    # df_below_100['total_profit'] = df_below_100['total_profit'].apply(lambda x: f"{x:.2f}")

    # df_100_to_300['total_sales'] = df_100_to_300['total_sales'].apply(lambda x: f"{x:.2f}")
    # df_100_to_300['total_profit'] = df_100_to_300['total_profit'].apply(lambda x: f"{x:.2f}")

    # df_above_300['total_sales'] = df_above_300['total_sales'].apply(lambda x: f"{x:.2f}")
    # df_above_300['total_profit'] = df_above_300['total_profit'].apply(lambda x: f"{x:.2f}")

    # # Prepare the DataFrames for display
    # df_below_100_display = df_below_100[['brandName', 'total_sales', 'total_profit', 'RAG Status']]
    # df_100_to_300_display = df_100_to_300[['brandName', 'total_sales', 'total_profit', 'RAG Status']]
    # df_above_300_display = df_above_300[['brandName', 'total_sales', 'total_profit', 'RAG Status']]

    # csv_red = convert_df(df_below_100)
    # csv_amber = convert_df(df_100_to_300)
    # csv_green = convert_df(df_above_300)

    # st.sidebar.download_button(
    #         label="RAG red Data",
    #         data=csv_red,   
    #         file_name='red_brands.csv',
    #         mime='text/csv',
    #     )

    # st.sidebar.download_button(
    #         label="RAG Amber Data",
    #         data=csv_amber,   
    #         file_name='amber_brands.csv',
    #         mime='text/csv',
    #     )

    # st.sidebar.download_button(
    #         label="RAG Green Data",
    #         data=csv_green,   
    #         file_name='green_brands.csv',
    #         mime='text/csv',
    #     )

    # st.markdown(
    #     "<h4 style='color: red; text-align: center;'>Brands sales below 100 Rs.</h4>", 
    #     unsafe_allow_html=True
    # )
    # st.table(df_below_100_display.style.applymap(lambda x: 'background-color: red' if x == 'Red' else '', subset=['RAG Status']))

    # st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    # st.markdown(
    #     "<h4 style='color: orange; text-align: center;'>Brands sales between 100 - 300 Rs.</h4>", 
    #     unsafe_allow_html=True
    # )   
    # st.table(df_100_to_300_display.style.applymap(lambda x: 'background-color: orange' if x == 'Amber' else '', subset=['RAG Status']))

    
    # if not missing_top_brands.empty:
    #     st.markdown("<h4 style='color: red; text-align: center;'>Missing Top Brands in Selected Store</h4>", unsafe_allow_html=True)
    #     # missing_top_brands['total_sales'] = missing_top_brands['total_sales'].apply(lambda x: f"{x:.2f}")
    #     # st.table(missing_top_brands)

    #    # Create tabs for different views of missing brands
    #     tab1, tab2, tab3 = st.tabs(["Missing Brands Table", "Sales Comparison", "Brand Distribution"])

    #     with tab1:
    #         # Display the table of missing brands
    #         missing_top_brands_display = missing_top_brands.copy()
    #         missing_top_brands_display['total_sales'] = missing_top_brands_display['total_sales'].apply(lambda x:f"{x:.2f}")
            
    #         st.table(missing_top_brands_display)
        
    #     with tab2:
    #         # Create a comparison visualization
    #         # Get the brands that are present in both datasets
    #         common_brands = top_n_brands_overall[
    #             top_n_brands_overall['brandName'].isin(store_data_filtered['brandName'])
    #         ]['brandName'].tolist()
            
    #         # Prepare data for comparison
    #         comparison_data = []

    #         # Add data for common brands
    #         for brand in common_brands:
    #             quantity_sold_store = store_data_filtered[store_data_filtered['brandName'] == brand]['quantity'].sum()
    #             quantity_sold_all = all_data[all_data['brandName'] == brand]['quantity'].sum()
    #             comparison_data.append({
    #                 'brandName': brand,
    #                 'store_sales_qty': quantity_sold_store,
    #                 'all_store_qty': quantity_sold_all,
    #                 'Status': 'Present'
    #             })

    #         # Add data for missing brands
    #         for _, row in missing_top_brands.iterrows():
    #             comparison_data.append({
    #                 'brandName': row['brandName'],
    #                 'store_sales_qty': 0,
    #                 'all_store_qty': row['quantity'],
    #                 'Status': 'Missing'
    #             })
            
    #         comparison_df = pd.DataFrame(comparison_data)
            
    #         # Create a grouped bar chart
    #         fig_comparison = go.Figure()
            
    #         # Add bars for store sales
    #         fig_comparison.add_trace(go.Bar(
    #             name='Store Sales',
    #             x=comparison_df['brandName'],
    #             y=comparison_df['store_sales_qty'],
    #             marker_color='blue'
    #         ))
            
    #         # Add bars for overall sales
    #         fig_comparison.add_trace(go.Bar(
    #             name='Overall Sales',
    #             x=comparison_df['brandName'],
    #             y=comparison_df['all_store_qty'],
    #             marker_color='green'
    #         ))
            
    #         # Update layout
    #         fig_comparison.update_layout(
    #             title='Store vs Brand Quantity Comparison',
    #             xaxis_title='Brand Name',
    #             yaxis_title='Quantity',
    #             barmode='group',
    #             width=1000,
    #             height=600,
    #             showlegend=True
    #         )
            
    #         st.plotly_chart(fig_comparison)
        
    #     with tab3:
    #         # Create a visualization showing the distribution of present vs missing brands
    #         present_count = len(common_brands)
    #         missing_count = len(missing_top_brands)
            
    #         # Create a pie chart
    #         fig_distribution = px.pie(
    #             names=['Present Brands', 'Missing Brands'],
    #             values=[present_count, missing_count],
    #             title=f'Distribution of Top {n_brands} Brands in Store',
    #             color_discrete_sequence=['green', 'red']
    #         )
            
    #         fig_distribution.update_layout(
    #             width=800,
    #             height=500
    #         )
            
    #         st.plotly_chart(fig_distribution)
        
    #     # Add summary metrics
    #     st.markdown("### Key Metrics")
    #     col1, col2 = st.columns(2)
        
    #     with col1:
    #         st.metric(
    #             "Missing Brands",
    #             f"{len(missing_top_brands)}",
    #             f"{(len(missing_top_brands)/n_brands*100):.1f}% of Top {n_brands}"
    #         )
        
        
    #     with col2:
    #         st.metric(
    #             "Present Brands",
    #             f"{len(common_brands)}",
    #             f"{(len(common_brands)/n_brands*100)}% of Top {n_brands}"
    #         )
        

    #     @st.cache_data
    #     def convert_df(df):
    #         return df.to_csv(index=False).encode('utf-8')
            
    #     csv_missing = convert_df(missing_top_brands)
    #     st.sidebar.download_button(
    #         label="Missing Top Brands Data",
    #         data=csv_missing,
    #         file_name='missing_top_brands.csv',
    #         mime='text/csv',
    #     )
    # else:
    #     st.markdown(
    #     "<h6 style='color: green; text-align: center;'>All Top brands are available in the store</h6>", 
    #     unsafe_allow_html=True)  
    #     st.markdown("<hr style='border-top: 2px solid #bbb;'>", unsafe_allow_html=True)
