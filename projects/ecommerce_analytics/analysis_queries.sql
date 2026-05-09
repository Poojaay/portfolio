-- ==============================================================================
-- E-COMMERCE DATA ANALYTICS PROJECT - SQL SCRIPTS
-- ==============================================================================
-- These queries showcase advanced SQL skills including CTEs, Window Functions,
-- Aggregations, and complex JOINs. You can run these in any SQLite environment.

-- ------------------------------------------------------------------------------
-- 1. OVERALL SALES & PROFIT KPI BY CATEGORY
-- ------------------------------------------------------------------------------
-- Calculates total revenue, total cost, profit, and profit margin for each 
-- product category.
SELECT 
    p.Category,
    ROUND(SUM(oi.Quantity * p.Price), 2) AS TotalRevenue,
    ROUND(SUM(oi.Quantity * p.Cost), 2) AS TotalCost,
    ROUND(SUM(oi.Quantity * (p.Price - p.Cost)), 2) AS TotalProfit,
    ROUND(SUM(oi.Quantity * (p.Price - p.Cost)) / SUM(oi.Quantity * p.Price) * 100, 2) AS ProfitMargin_Percent
FROM 
    Order_Items oi
JOIN 
    Products p ON oi.ProductID = p.ProductID
GROUP BY 
    p.Category
ORDER BY 
    TotalProfit DESC;


-- ------------------------------------------------------------------------------
-- 2. MONTH-OVER-MONTH REVENUE GROWTH (Using Window Functions)
-- ------------------------------------------------------------------------------
-- Calculates total revenue per month and uses the LAG() window function to 
-- compare it with the previous month's revenue to find the MoM growth rate.
WITH MonthlyRevenue AS (
    SELECT 
        STRFTIME('%Y-%m', o.OrderDate) AS OrderMonth,
        ROUND(SUM(oi.Quantity * p.Price), 2) AS Revenue
    FROM 
        Orders o
    JOIN 
        Order_Items oi ON o.OrderID = oi.OrderID
    JOIN 
        Products p ON oi.ProductID = p.ProductID
    GROUP BY 
        STRFTIME('%Y-%m', o.OrderDate)
)
SELECT 
    OrderMonth,
    Revenue,
    LAG(Revenue) OVER (ORDER BY OrderMonth) AS PrevMonthRevenue,
    ROUND(((Revenue - LAG(Revenue) OVER (ORDER BY OrderMonth)) / LAG(Revenue) OVER (ORDER BY OrderMonth)) * 100, 2) AS MoM_Growth_Percent
FROM 
    MonthlyRevenue;


-- ------------------------------------------------------------------------------
-- 3. CUSTOMER LIFETIME VALUE (LTV) - TOP 10 VALUABLE CUSTOMERS
-- ------------------------------------------------------------------------------
-- Identifies the top 10 customers based on their total lifetime spending.
SELECT 
    c.CustomerID,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    c.Country,
    c.Segment,
    COUNT(DISTINCT o.OrderID) AS TotalOrders,
    SUM(oi.Quantity) AS TotalItemsBought,
    ROUND(SUM(oi.Quantity * p.Price * (1 - oi.Discount)), 2) AS TotalLifetimeValue
FROM 
    Customers c
JOIN 
    Orders o ON c.CustomerID = o.CustomerID
JOIN 
    Order_Items oi ON o.OrderID = oi.OrderID
JOIN 
    Products p ON oi.ProductID = p.ProductID
GROUP BY 
    c.CustomerID, CustomerName, c.Country, c.Segment
ORDER BY 
    TotalLifetimeValue DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- 4. PRODUCT PERFORMANCE: TOP SELLING PRODUCT BY SUBCATEGORY
-- ------------------------------------------------------------------------------
-- Uses the ROW_NUMBER() window function to find the top selling product within 
-- each subcategory based on total revenue.
WITH ProductSales AS (
    SELECT 
        p.SubCategory,
        p.ProductName,
        ROUND(SUM(oi.Quantity * p.Price), 2) AS TotalRevenue
    FROM 
        Order_Items oi
    JOIN 
        Products p ON oi.ProductID = p.ProductID
    GROUP BY 
        p.SubCategory, p.ProductName
),
RankedProducts AS (
    SELECT 
        SubCategory,
        ProductName,
        TotalRevenue,
        ROW_NUMBER() OVER(PARTITION BY SubCategory ORDER BY TotalRevenue DESC) as Rank
    FROM 
        ProductSales
)
SELECT 
    SubCategory,
    ProductName,
    TotalRevenue
FROM 
    RankedProducts
WHERE 
    Rank = 1
ORDER BY 
    TotalRevenue DESC;


-- ------------------------------------------------------------------------------
-- 5. ORDER SHIPPING DELAY ANALYSIS
-- ------------------------------------------------------------------------------
-- Analyzes the average time taken to ship orders based on the ShipMode.
SELECT 
    ShipMode,
    COUNT(OrderID) AS TotalOrders,
    ROUND(AVG(JULIANDAY(ShippingDate) - JULIANDAY(OrderDate)), 2) AS AvgShippingDelayDays
FROM 
    Orders
GROUP BY 
    ShipMode
ORDER BY 
    AvgShippingDelayDays ASC;
