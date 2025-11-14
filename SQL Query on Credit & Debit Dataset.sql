Use credit_debit;

ALTER TABLE credit_debit_data
RENAME COLUMN `Account Number` TO `Account_Number`;

-- Question 1
SELECT 
    ROUND(SUM(Amount), 2) AS Total_Credit_Amount
FROM `credit_debit_data`
WHERE `Transaction Type` = 'Credit';


-- Question 2
SELECT 
    ROUND(SUM(Amount), 2) AS Total_Credit_Amount
FROM `credit_debit_data`
WHERE `Transaction Type` = 'Debit';


-- Question 3
SELECT 
SUM(CASE WHEN `Transaction Type` = 'Credit' THEN Amount ELSE 0 END) /
NULLIF(SUM(CASE WHEN `Transaction Type` = 'Debit' THEN Amount ELSE 0 END), 0) AS Credit_to_Debit_Ratio
FROM `credit_debit_data`;


-- Question 4
SELECT 
SUM(CASE 
		WHEN `Transaction Type` = 'Credit' THEN Amount
		WHEN `Transaction Type` = 'Debit' THEN -Amount
		ELSE 0 
	END) AS Net_Transaction_Amount
FROM `credit_debit_data`;


-- Question 5.Account Activity Ratio
SELECT 
    Account_Number,
    COUNT(*) AS Number_of_Transactions,
    MAX(Balance) AS Account_Balance,
    ROUND(COUNT(*) / MAX(Balance), 4) AS Account_Activity_Ratio
FROM credit_debit_data
GROUP BY Account_Number;


-- Question 6.a Transactions per Day
SELECT 
    DATE(`Transaction Date`) AS Transaction_Date,
    COUNT(*) AS Transactions_Per_Day
FROM credit_debit_data
GROUP BY DATE(`Transaction Date`)
ORDER BY Transaction_Date;


-- Question 6.b Transactions per Week
SELECT 
    YEAR(`Transaction Date`) AS Year,
    WEEK(`Transaction Date`) AS Week_Number,
    COUNT(*) AS Transactions_Per_Week
FROM credit_debit_data
GROUP BY YEAR(`Transaction Date`), WEEK(`Transaction Date`)
ORDER BY Year, Week_Number;


-- Question 6.c Transactions per Month
SELECT 
    YEAR(`Transaction Date`) AS Year,
    MONTH(`Transaction Date`) AS Month,
    COUNT(*) AS Transactions_Per_Month
FROM credit_debit_data
GROUP BY YEAR(`Transaction Date`), MONTH(`Transaction Date`)
ORDER BY Year, Month;


-- Question 7. Total Transaction Amount by Branch
SELECT 
    Branch,
    ROUND(SUM(Amount), 2) AS Total_Transaction_Amount
FROM credit_debit_data
GROUP BY Branch
ORDER BY Total_Transaction_Amount DESC;


-- Question 8. Transaction Volume by Bank
SELECT 
    `Bank Name`,
    ROUND(SUM(Amount), 2) AS Total_Transaction_Amount
FROM credit_debit_data
GROUP BY `Bank Name`
ORDER BY Total_Transaction_Amount DESC;


-- Question 9
SELECT
  t.`Transaction Method`,
  t.cnt AS transaction_count,
  ROUND(100 * t.cnt / NULLIF(s.total_count, 0), 2) AS pct_of_total
FROM (
  SELECT `Transaction Method`, COUNT(*) AS cnt
  FROM `credit_debit_data`
  GROUP BY `Transaction Method`
) AS t
CROSS JOIN (
  SELECT COUNT(*) AS total_count
  FROM `credit_debit_data`
) AS s
ORDER BY t.cnt DESC;


-- Question 10
SELECT
  Branch,
  month,
  total_amount,
  prev_amount,
  ROUND(100 * (total_amount - prev_amount) / NULLIF(prev_amount, 0), 2) AS pct_change_amount
FROM (
  SELECT
    Branch,
    DATE_FORMAT(`Transaction Date`, '%Y-%m') AS month,
    ROUND(SUM(Amount), 2) AS total_amount,
    LAG(ROUND(SUM(Amount),2)) OVER (PARTITION BY Branch ORDER BY DATE_FORMAT(`Transaction Date`, '%Y-%m')) AS prev_amount
  FROM `credit_debit_data`
  GROUP BY Branch, month
) t
ORDER BY Branch, month;


-- Question 11
SET @THRESHOLD := 4800;

SELECT 
    Risk_Flag AS 'Row Labels',
    COUNT(`Customer ID`) AS 'Count of Customer ID'
FROM (
    SELECT 
        `Customer ID`,
        CASE
            WHEN Amount >= @THRESHOLD 
                 OR Amount > 3 * AVG(Amount) OVER (PARTITION BY `Account Number`) 
            THEN 'Risky'
            ELSE 'Normal'
        END AS Risk_Flag
    FROM `credit_debit_data`
) AS sub
GROUP BY Risk_Flag WITH ROLLUP;


-- Question 12
SELECT 
    DATE_FORMAT(`Transaction Date`, '%Y-%m') AS Month,
    COUNT(*) AS Suspicious_Transaction_Frequency
FROM credit_debit_data
WHERE 
    Amount > 4999.9
    OR Description IN ('Bonus Payment', 'Refund for Overcharge', 'Freelance Payment')
GROUP BY DATE_FORMAT(`Transaction Date`, '%Y-%m')
order by month;


