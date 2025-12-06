# Amazon QuickSight Dashboard Setup Guide

This guide walks you through creating an interactive analytics dashboard in Amazon QuickSight for the e-commerce transaction data.

## Prerequisites

1. Amazon QuickSight account (sign up at https://quicksight.aws.amazon.com/)
2. Processed data available in S3 (after Glue ETL job completes)
3. Glue Data Catalog table created (`transactions` table in `ecommerce_analytics_db`)

## Step 1: Connect QuickSight to Athena

1. **Open QuickSight Console**
   - Navigate to https://quicksight.aws.amazon.com/
   - Sign in with your AWS account

2. **Create a New Data Source**
   - Click "Manage data" → "New data set"
   - Select "Athena" as the data source

3. **Configure Athena Connection**
   - **Data source name**: `E-Commerce Analytics`
   - **Athena workgroup**: Select your workgroup (e.g., `ecommerce-analytics-workgroup`)
   - Click "Create data source"

4. **Select Database and Table**
   - **Database**: `ecommerce_analytics_db`
   - **Table**: `transactions`
   - Click "Select"

5. **Prepare Data**
   - QuickSight will show a preview of your data
   - Verify the schema looks correct
   - Click "Visualize" to proceed

## Step 2: Create Visualizations

### Visualization 1: Revenue Trends (Line Chart)

**Purpose**: Show revenue trends over time

1. **Create Line Chart**
   - Visual type: Line chart
   - X-axis: `transaction_date` (grouped by day)
   - Y-axis: `total_amount` (Sum)
   - Title: "Daily Revenue Trends"

2. **Add Filters**
   - Add date range filter for `transaction_date`
   - Add category filter for drill-down analysis

### Visualization 2: Top Categories (Horizontal Bar Chart)

**Purpose**: Display top-selling categories by revenue

1. **Create Horizontal Bar Chart**
   - Visual type: Horizontal bar chart
   - Y-axis: `category`
   - X-axis: `total_amount` (Sum)
   - Title: "Top Categories by Revenue"
   - Sort: Descending by revenue

2. **Add Color Coding**
   - Color by `category` for visual distinction

### Visualization 3: Peak Transaction Hours (Column Chart)

**Purpose**: Identify peak transaction hours

1. **Create Column Chart**
   - Visual type: Column chart
   - X-axis: `hour`
   - Y-axis: `transaction_count` (Count)
   - Title: "Transaction Volume by Hour"
   - Sort: By hour (ascending)

2. **Add Trend Line**
   - Add a trend line to show overall pattern

### Visualization 4: Revenue by Region (Map/Bar Chart)

**Purpose**: Geographic revenue distribution

1. **Create Bar Chart**
   - Visual type: Vertical bar chart
   - X-axis: `region`
   - Y-axis: `total_amount` (Sum)
   - Title: "Revenue by Region"

2. **Add Secondary Metric**
   - Add `transaction_count` (Count) as secondary Y-axis

### Visualization 5: Payment Method Distribution (Pie Chart)

**Purpose**: Payment method usage breakdown

1. **Create Pie Chart**
   - Visual type: Pie chart
   - Group by: `payment_method`
   - Value: `total_amount` (Sum)
   - Title: "Revenue by Payment Method"

### Visualization 6: Key Performance Indicators (KPI Cards)

**Purpose**: Display critical business metrics

1. **Create KPI Visual**
   - Visual type: KPI
   - Primary value: `total_amount` (Sum)
   - Title: "Total Revenue"
   - Format: Currency

2. **Create Additional KPIs**
   - **Total Transactions**: `transaction_id` (Count distinct)
   - **Average Transaction Value**: `total_amount` (Average)
   - **Unique Customers**: `customer_id` (Count distinct)
   - **Total Items Sold**: `quantity` (Sum)

### Visualization 7: Top Products Table

**Purpose**: Detailed product performance

1. **Create Table**
   - Visual type: Table
   - Columns:
     - `product_name`
     - `category`
     - `total_amount` (Sum)
     - `quantity` (Sum)
     - `transaction_count` (Count)
   - Title: "Top Products Performance"
   - Sort: By revenue (descending)
   - Limit: Top 20

### Visualization 8: Customer Segmentation (Scatter Plot)

**Purpose**: Analyze customer behavior patterns

1. **Create Scatter Plot**
   - Visual type: Scatter plot
   - X-axis: `transaction_count` (Count per customer)
   - Y-axis: `total_amount` (Sum per customer)
   - Size: `total_amount` (Sum)
   - Color: `region`
   - Title: "Customer Value vs Frequency"

## Step 3: Create Dashboard

1. **Arrange Visualizations**
   - Drag and drop visualizations onto the canvas
   - Resize and position for optimal layout
   - Use grid layout for alignment

2. **Add Filters**
   - Create global filters:
     - Date range picker for `transaction_date`
     - Dropdown for `category`
     - Dropdown for `region`
     - Dropdown for `payment_method`

3. **Add Parameters**
   - Create parameters for dynamic thresholds:
     - `MinTransactionValue` (numeric)
     - `DateRange` (date range)

4. **Add Calculated Fields**
   - **Revenue Growth**: Calculate month-over-month growth
   - **Customer Lifetime Value**: Sum of total_amount per customer
   - **Basket Size**: Average quantity per transaction

## Step 4: Configure Dashboard Settings

1. **Dashboard Title**
   - Set title: "E-Commerce Analytics Dashboard"

2. **Theme**
   - Choose a professional theme
   - Customize colors to match brand (optional)

3. **Auto-Refresh**
   - Enable auto-refresh (e.g., every 1 hour)
   - This ensures data stays current

4. **Export Settings**
   - Enable export to PDF/Excel
   - Configure email scheduling (optional)

## Step 5: Share Dashboard

1. **Publish Dashboard**
   - Click "Share" → "Publish dashboard"
   - Set access permissions

2. **Create Reader Access**
   - Add users or groups who should have read-only access
   - Or make it publicly accessible (if appropriate)

3. **Schedule Reports** (Optional)
   - Set up scheduled email reports
   - Configure report frequency and recipients

## Step 6: Advanced Features

### Custom Calculations

Add calculated fields for advanced analytics:

```sql
-- Revenue Growth Rate
(SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY month)) 
/ LAG(SUM(total_amount)) OVER (ORDER BY month) * 100

-- Customer Retention Rate
COUNT(DISTINCT customer_id) / LAG(COUNT(DISTINCT customer_id)) OVER (ORDER BY month) * 100
```

### Parameterized Queries

Create dynamic queries using parameters:
- Filter by date range using parameters
- Adjust revenue thresholds dynamically
- Switch between different time periods

### Drill-Down Capabilities

Enable drill-downs:
- Category → Product
- Region → Store
- Month → Day → Hour

## Best Practices

1. **Performance Optimization**
   - Use aggregated data where possible
   - Limit data refresh frequency
   - Use filters to reduce data scanned

2. **Visual Design**
   - Use consistent color schemes
   - Keep visualizations simple and clear
   - Add titles and descriptions

3. **Data Governance**
   - Set appropriate access controls
   - Document calculated fields
   - Version control dashboard changes

## Troubleshooting

### Issue: Data not appearing
- **Solution**: Verify Athena table exists and has data
- Check S3 bucket permissions for QuickSight
- Verify Glue Data Catalog permissions

### Issue: Slow query performance
- **Solution**: Ensure data is partitioned correctly
- Use date filters to limit data scanned
- Consider materialized views for complex queries

### Issue: Missing columns
- **Solution**: Refresh data source in QuickSight
- Verify Glue table schema matches expectations
- Re-run Glue ETL job if schema changed

## Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│         E-Commerce Analytics Dashboard                  │
├─────────────────────────────────────────────────────────┤
│ [Date Filter] [Category] [Region] [Payment Method]     │
├──────────────┬──────────────┬──────────────┬───────────┤
│ Total Revenue│ Total Trans. │ Avg. Txn Val │ Items Sold│
│   $2,450,000 │    125,000   │    $19.60    │  250,000  │
├──────────────┴──────────────┴──────────────┴───────────┤
│                                                         │
│  Daily Revenue Trends (Line Chart)                     │
│                                                         │
├──────────────────────────┬──────────────────────────────┤
│ Top Categories          │ Peak Transaction Hours       │
│ (Horizontal Bar)        │ (Column Chart)               │
├──────────────────────────┴──────────────────────────────┤
│                                                         │
│  Revenue by Region (Bar Chart)                         │
│                                                         │
├──────────────────────────┬──────────────────────────────┤
│ Payment Methods         │ Top Products Table           │
│ (Pie Chart)             │                              │
└──────────────────────────┴──────────────────────────────┘
```

## Next Steps

1. **Monitor Dashboard Usage**
   - Track which visualizations are most viewed
   - Gather user feedback

2. **Iterate and Improve**
   - Add new metrics based on business needs
   - Refine visualizations for clarity

3. **Automate Reporting**
   - Set up scheduled email reports
   - Create alerts for key metrics

4. **Scale for Production**
   - Consider QuickSight Enterprise for advanced features
   - Implement row-level security if needed

## Resources

- [QuickSight User Guide](https://docs.aws.amazon.com/quicksight/)
- [QuickSight Best Practices](https://aws.amazon.com/quicksight/features/)
- [Athena Data Source Documentation](https://docs.aws.amazon.com/quicksight/latest/user/athena-data-source.html)

