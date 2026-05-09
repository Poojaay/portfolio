# E-Commerce Data Analytics Project

An end-to-end data analytics pipeline demonstrating synthetic data generation, advanced SQL querying, and an interactive web dashboard built entirely in Python using Streamlit.

## Project Overview

This project showcases the ability to:
1. **Generate Mock Data**: Use Python to create a realistic, synthetic e-commerce dataset encompassing Customers, Products, Orders, and Order Items.
2. **Database Design**: Store the data in a SQLite database using a **Star Schema** architecture.
3. **Advanced SQL Analysis**: Write complex SQL queries (Window functions, CTEs, Aggregations) to extract key business insights such as Customer Lifetime Value (LTV), Month-over-Month growth, and Profit Margins.
4. **Data Visualization**: Build an interactive web dashboard using **Streamlit** and **Plotly** to visualize the KPIs and trends dynamically.

## Technology Stack
- **Language**: Python 3
- **Database**: SQLite
- **Libraries**: Pandas, Streamlit, Plotly, CSV

## How to Run the Project

### 1. Install Requirements
Make sure you have Python installed. Install the necessary libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 2. Generate the Data (Optional)
The SQLite database `ecommerce.db` is already generated in this repository. If you want to regenerate the data with a different seed or size, run:
```bash
python generate_data.py
```
*Note: This will overwrite `ecommerce.db` and the CSV files.*

### 3. Run the Dashboard
To start the interactive web application, run the following command in your terminal:
```bash
streamlit run dashboard.py
```
This will open the dashboard in your default web browser (usually at `http://localhost:8501`).

## SQL Queries Showcase
The `analysis_queries.sql` file contains several advanced queries designed to answer critical business questions:
- **Overall Sales & Profit KPI**: Calculates revenue, cost, and profit margin by product category.
- **MoM Revenue Growth**: Uses `LAG()` window functions to calculate Month-over-Month growth rates.
- **Customer Lifetime Value (LTV)**: Identifies the top 10 most valuable customers.
- **Top Products**: Uses `ROW_NUMBER()` to find the best-selling product in each subcategory.
- **Shipping Delay Analysis**: Analyzes average shipping times based on shipping modes.
