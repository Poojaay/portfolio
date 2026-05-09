import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# Set page config
st.set_page_config(page_title="E-Commerce Analytics", page_icon="📈", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        border-left: 5px solid #00E676;
    }
    .metric-title {
        font-size: 1.2rem;
        color: #BDBDBD;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Function to get database connection
@st.cache_resource
def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecommerce.db')
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

# Sidebar for filters
st.sidebar.header("Dashboard Filters")

# We can query some basic info to populate filters
categories_df = pd.read_sql_query("SELECT DISTINCT Category FROM Products", conn)
selected_categories = st.sidebar.multiselect(
    "Filter by Category", 
    options=categories_df['Category'].tolist(),
    default=categories_df['Category'].tolist()
)

# If no categories are selected, use all to avoid empty charts
if not selected_categories:
    selected_categories = categories_df['Category'].tolist()

# SQL placeholders for the selected categories
cat_placeholders = ','.join(['?'] * len(selected_categories))


# Main Dashboard Header
st.title("🛍️ E-Commerce Global Sales Performance")
st.markdown("An interactive dashboard built with Python, Streamlit, and SQLite. Explore synthetic sales data and key business metrics.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 1. KPI Metrics
# -----------------------------------------------------------------------------
kpi_query = f"""
SELECT 
    ROUND(SUM(oi.Quantity * p.Price), 2) AS TotalRevenue,
    ROUND(SUM(oi.Quantity * (p.Price - p.Cost)), 2) AS TotalProfit,
    COUNT(DISTINCT o.OrderID) AS TotalOrders,
    ROUND(SUM(oi.Quantity * (p.Price - p.Cost)) / SUM(oi.Quantity * p.Price) * 100, 2) AS ProfitMargin
FROM 
    Order_Items oi
JOIN Products p ON oi.ProductID = p.ProductID
JOIN Orders o ON oi.OrderID = o.OrderID
WHERE p.Category IN ({cat_placeholders})
"""
kpi_df = pd.read_sql_query(kpi_query, conn, params=selected_categories)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${kpi_df['TotalRevenue'].iloc[0]:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Profit</div>
            <div class="metric-value">${kpi_df['TotalProfit'].iloc[0]:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Profit Margin</div>
            <div class="metric-value">{kpi_df['ProfitMargin'].iloc[0]:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{kpi_df['TotalOrders'].iloc[0]:,}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Charts Layout (Row 1)
# -----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Monthly Revenue Trend")
    trend_query = f"""
        SELECT 
            STRFTIME('%Y-%m', o.OrderDate) AS OrderMonth,
            ROUND(SUM(oi.Quantity * p.Price), 2) AS Revenue
        FROM 
            Orders o
        JOIN Order_Items oi ON o.OrderID = oi.OrderID
        JOIN Products p ON oi.ProductID = p.ProductID
        WHERE p.Category IN ({cat_placeholders})
        GROUP BY 
            STRFTIME('%Y-%m', o.OrderDate)
        ORDER BY OrderMonth
    """
    trend_df = pd.read_sql_query(trend_query, conn, params=selected_categories)
    fig_trend = px.line(trend_df, x='OrderMonth', y='Revenue', markers=True, 
                        template='plotly_dark', line_shape='spline')
    fig_trend.update_traces(line_color='#00E676', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.subheader("Sales by Product Category")
    cat_query = f"""
        SELECT 
            p.Category,
            ROUND(SUM(oi.Quantity * p.Price), 2) AS TotalRevenue
        FROM 
            Order_Items oi
        JOIN Products p ON oi.ProductID = p.ProductID
        WHERE p.Category IN ({cat_placeholders})
        GROUP BY p.Category
    """
    cat_df = pd.read_sql_query(cat_query, conn, params=selected_categories)
    fig_cat = px.bar(cat_df, x='Category', y='TotalRevenue', color='Category', 
                     template='plotly_dark')
    st.plotly_chart(fig_cat, use_container_width=True)


# -----------------------------------------------------------------------------
# 3. Charts Layout (Row 2)
# -----------------------------------------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Customer Segments")
    seg_query = f"""
        SELECT 
            c.Segment,
            ROUND(SUM(oi.Quantity * p.Price), 2) AS TotalRevenue
        FROM 
            Order_Items oi
        JOIN Products p ON oi.ProductID = p.ProductID
        JOIN Orders o ON oi.OrderID = o.OrderID
        JOIN Customers c ON o.CustomerID = c.CustomerID
        WHERE p.Category IN ({cat_placeholders})
        GROUP BY c.Segment
    """
    seg_df = pd.read_sql_query(seg_query, conn, params=selected_categories)
    fig_seg = px.pie(seg_df, values='TotalRevenue', names='Segment', hole=0.4, 
                     template='plotly_dark', color_discrete_sequence=px.colors.sequential.Tealgrn)
    fig_seg.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_seg, use_container_width=True)

with row2_col2:
    st.subheader("Top 10 Valuable Customers")
    ltv_query = f"""
        SELECT 
            c.FirstName || ' ' || c.LastName AS CustomerName,
            ROUND(SUM(oi.Quantity * p.Price * (1 - oi.Discount)), 2) AS TotalLifetimeValue
        FROM 
            Customers c
        JOIN Orders o ON c.CustomerID = o.CustomerID
        JOIN Order_Items oi ON o.OrderID = oi.OrderID
        JOIN Products p ON oi.ProductID = p.ProductID
        WHERE p.Category IN ({cat_placeholders})
        GROUP BY c.CustomerID, CustomerName
        ORDER BY TotalLifetimeValue DESC
        LIMIT 10
    """
    ltv_df = pd.read_sql_query(ltv_query, conn, params=selected_categories)
    fig_ltv = px.bar(ltv_df, x='TotalLifetimeValue', y='CustomerName', orientation='h',
                     template='plotly_dark', color='TotalLifetimeValue', color_continuous_scale='Greens')
    fig_ltv.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ltv, use_container_width=True)

st.markdown("---")
st.markdown("Developed by Pooja Yadav | Powered by Streamlit & SQLite")
