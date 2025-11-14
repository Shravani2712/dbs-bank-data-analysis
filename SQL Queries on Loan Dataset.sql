create database Bank;

use bank;

#01.Total Clients 
SELECT COUNT(DISTINCT `Client id`) AS Total_Clients
FROM banking_dataset;

#01.Active Clients
SELECT COUNT(DISTINCT `Client id`) AS Active_Clients
FROM banking_dataset
WHERE `Loan Status` = 'Active';

#02.New Clients
SELECT 
    `Client id`,
    MIN(`Disbursement Date`) AS First_Loan_Date
FROM banking_dataset
GROUP BY `Client id`;

SELECT 
    b.`Branch Name`,
    COUNT(*) AS New_Clients
FROM (
    SELECT 
        `Client id`,
        `Branch Name`,
        MIN(`Disbursement Date`) AS First_Loan_Date
    FROM banking_dataset
    GROUP BY `Client id`, `Branch Name`
) AS b
WHERE First_Loan_Date BETWEEN '2023-01-01' AND '2023-03-31'
GROUP BY b.`Branch Name`;

#03.Client Rotation Rate
WITH previous_period AS (
    SELECT DISTINCT `Client id`
    FROM banking_dataset
    WHERE `Disbursement Date` BETWEEN '2023-01-01' AND '2023-03-31'
),
current_period AS (
    SELECT DISTINCT `Client id`
    FROM banking_dataset
    WHERE `Disbursement Date` BETWEEN '2023-04-01' AND '2023-06-30'
),
returning_clients AS (
    SELECT c.`Client id`
    FROM current_period c
    INNER JOIN previous_period p ON c.`Client id` = p.`Client id`
)
SELECT 
    (SELECT COUNT(*) FROM returning_clients) AS Returning_Clients,
    (SELECT COUNT(*) FROM previous_period) AS Previous_Period_Clients,
    ROUND(
        (SELECT COUNT(*) FROM returning_clients) * 100.0 /
        (SELECT COUNT(*) FROM previous_period),
        2
    ) AS Client_Retention_Rate_Percentage;
    
#04.Total Loan Amount Disbursed
SELECT 
    `Branch Name`,
    round(sum(`Loan Amount`) / 1000000, 2) AS Total_Loan_Amount_Disbursed_M
FROM banking_dataset
GROUP BY `Branch Name`
ORDER BY Total_Loan_Amount_Disbursed_M DESC;

#05.Total Funded Amount
SELECT 
    `Branch Name`,
    ROUND(SUM(`Funded Amount`) / 1000000, 2) AS Total_Funded_Amount_M
FROM banking_dataset
GROUP BY `Branch Name`
ORDER BY Total_Funded_Amount_M DESC;

#06.Average Loan Size
SELECT 
    `Branch Name`,
    ROUND(AVG(`Loan Amount`) / 1000, 2) AS Average_Loan_Size_K
FROM banking_dataset
GROUP BY `Branch Name`
ORDER BY Average_Loan_Size_K DESC;

#07.Loan Growth Percentage
WITH last_period AS (
    SELECT `Branch Name`, SUM(`Loan Amount`) AS Last_Period_Loan
    FROM banking_dataset
    WHERE `Disbursement Date` BETWEEN '2023-01-01' AND '2023-03-31'
    GROUP BY `Branch Name`
),
this_period AS (
    SELECT `Branch Name`, SUM(`Loan Amount`) AS This_Period_Loan
    FROM banking_dataset
    WHERE `Disbursement Date` BETWEEN '2023-04-01' AND '2023-06-30'
    GROUP BY `Branch Name`
)
SELECT 
    t.`Branch Name`,
    ROUND(
        ((t.This_Period_Loan - l.Last_Period_Loan) / l.Last_Period_Loan) * 100,
        2
    ) AS Loan_Growth_Percentage
FROM this_period t
JOIN last_period l
    ON t.`Branch Name` = l.`Branch Name`
ORDER BY Loan_Growth_Percentage DESC;

#08.Total Repayments Collected
SELECT 
    ROUND(SUM(`Total Pymnt`) / 1000000, 2) AS Total_Repayments_Collected_M
FROM Fact_Repayment;

#09.Principle Recovery Rate
SELECT 
    ROUND(
        (SUM(r.`Total Rec Prncp`) / SUM(l.`Loan Amount`)) * 100, 
        2
    ) AS Principal_Recovery_Rate_Percentage
FROM Fact_Repayment r
CROSS JOIN banking_dataset l;

#10.Interest Income
SELECT 
    ROUND(SUM(`Total Rrec Int`) / 1000000, 2) AS Interest_Income_M
FROM Fact_Repayment;

#11.default Rate
SELECT 
    ROUND(
        (SUM(CASE WHEN `Is Default Loan` = 'Y' THEN 1 ELSE 0 END) * 100.0) /
        COUNT(*),
        2
    ) AS Default_Rate_Percentage
FROM fact_repayment;

#12.Delinquency Rate
SELECT 
    ROUND(
        (SUM(CASE WHEN `Is Delinquent Loan` = 'Y' THEN 1 ELSE 0 END) * 100.0) /
        COUNT(*),
        2
    ) AS Delinquency_Rate_Percentage
FROM Fact_repayment;

#13.On-Time Repayment %
SELECT 
    ROUND(
        (SUM(CASE WHEN `Repayment Behavior` = 'On-Time' THEN 1 ELSE 0 END) * 100.0) /
        COUNT(*),
        2
    ) AS OnTime_Repayment_Percentage
FROM Fact_Repayment;

#14.Loan Distribution by Branch
SELECT 
    `Branch Name`,
    ROUND(SUM(`Loan Amount`) / 1000000, 2) AS Total_Loan_Amount_M
FROM banking_dataset
GROUP BY `Branch Name`
ORDER BY Total_Loan_Amount_M DESC;

#15.Branch Performance Category Split
SELECT 
    `Branch Performance Category`,
    COUNT(*) AS Total_Branches
FROM Dim_Branch
GROUP BY `Branch Performance Category`
ORDER BY Total_Branches DESC;


#16.Product-wise Loan Volume 
SELECT 
    `Product ID`,
	Round(SUM(`Loan Amount`) / 1000000,2) AS Total_Loan_Amount_M
FROM Banking_dataset
GROUP BY `Product ID`
ORDER BY Total_Loan_Amount_M DESC;

#17.Product Profitability 
SELECT
    b.`Product_ID`,
    ROUND(SUM(r.`Total Rrec Int`), 2) AS Total_Interest_Income,
    ROUND(SUM(b.`Funded Amount Inv`), 2) AS Total_Funded_Inv_Amount,
    ROUND(SUM(r.`Total Rrec Int`) / SUM(b.`Funded Amount Inv`), 4) AS Product_Profitability
FROM banking_dataset b
JOIN fact_repayment r
    ON b.`Product_ID` = r.`Product_ID`
WHERE r.`Total Rrec Int` IS NOT NULL
  AND b.`Funded Amount Inv` IS NOT NULL
GROUP BY b.`Product_ID`
ORDER BY Product_Profitability DESC;







































