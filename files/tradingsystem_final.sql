-- MySQL Script for Trading System ERD

-- Create a schema named 'TradingSystem' 
CREATE SCHEMA TradingSystem; 

-- Alternatively, you can use CREATE DATABASE (interchangeable with CREATE SCHEMA) 
-- CREATE DATABASE TradingSystem; 

-- Switch to the new schema 
USE TradingSystem;

-- 1. User Table
CREATE TABLE IF NOT EXISTS User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(50),
    firstName VARCHAR(20),
    lastName VARCHAR(20),
    userType VARCHAR(20),
    pwd VARCHAR(100),
    accountState VARCHAR(20)
);


-- 2. Account Table
-- CREATE TABLE IF NOT EXISTS Account (
--     AccountID INT AUTO_INCREMENT PRIMARY KEY,
--     UserID INT,
--     Balance DECIMAL(15, 2),
--     netProfit DECIMAL(15, 2),
--     AccountType ENUM('Cash', 'Margin'),
--     FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
-- );


-- 3. Stock Table
-- CREATE TABLE IF NOT EXISTS Stock (
--     StockID INT AUTO_INCREMENT PRIMARY KEY,
--     TickerSymbol VARCHAR(10) UNIQUE,
--     StockName VARCHAR(100),
--     Sector VARCHAR(50),
--     CurrentPrice DECIMAL(10, 2),
--     Exchange VARCHAR(50)
-- );

-- 4. Order Table
-- CREATE TABLE IF NOT EXISTS NotArbitrageOrder (
--     OrderID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT,
--     StockID INT,
--     OrderType ENUM('Buy', 'Sell'),
--     Quantity INT,
--     Price DECIMAL(10, 2),
--     OrderDate DATETIME,
--     Status ENUM('Pending', 'Completed', 'Cancelled'),
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- CREATE TABLE IF NOT EXISTS ArbitrageOrder (
--     ArbitrageOrderID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT NOT NULL,
--     ArbitrageType ENUM('PriceDiff', 'Statistical', 'Other') NOT NULL,
--     OrderDate DATETIME NOT NULL,
--     Status ENUM('Pending', 'Completed', 'Cancelled') NOT NULL,
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE
-- );

-- CREATE TABLE IF NOT EXISTS ArbitrageOrderLeg (
--     ArbitrageOrderLegID INT AUTO_INCREMENT PRIMARY KEY,
--     ArbitrageOrderID INT NOT NULL,
--     StockID INT NOT NULL,
--     Direction ENUM('Buy', 'Sell') NOT NULL,
--     Quantity INT NOT NULL,
--     Price DECIMAL(10, 2) NOT NULL,
--     Status ENUM('Pending', 'Completed', 'Cancelled'),
--     FOREIGN KEY (ArbitrageOrderID) REFERENCES ArbitrageOrder(ArbitrageOrderID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );


-- 5. Transaction Table
-- CREATE TABLE IF NOT EXISTS Transaction (
--     TransactionID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT,
--     StockID INT,
--     Quantity INT,
--     TransactionDate DATETIME,
--     TransactionType ENUM('Buy', 'Sell'),
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 6. Watchlist Table
-- CREATE TABLE IF NOT EXISTS Watchlist (
--     WatchlistID INT AUTO_INCREMENT PRIMARY KEY,
--     UserID INT,
--     StockID INT,
--     FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 7. Portfolio Table
-- CREATE TABLE IF NOT EXISTS Portfolio (
--     PortfolioID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT,
--     StockID INT,
--     Quantity INT,
--     AvgPurchasePrice DECIMAL(10, 2),
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );


-- 8. Position Table
-- CREATE TABLE IF NOT EXISTS Position (
--     PositionID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT NOT NULL,
--     StockID INT NOT NULL,
--     OpenDate DATETIME NOT NULL,
--     Quantity INT NOT NULL,
--     AvgOpenPrice DECIMAL(10, 2) NOT NULL,
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 9. ClosePosition Table
-- CREATE TABLE IF NOT EXISTS ClosePosition (
--     ClosePositionID INT AUTO_INCREMENT PRIMARY KEY,
--     PositionID INT NOT NULL,
--     CloseDate DATETIME NOT NULL,
--     ClosePrice DECIMAL(10, 2) NOT NULL,
--     CloseQuantity INT NOT NULL
-- );


-- 10. OrderQueue Table
-- CREATE TABLE IF NOT EXISTS OrderQueue (
--     QueueID INT AUTO_INCREMENT PRIMARY KEY,
--     OrderID INT,
--     AccountID INT,
--     StockID INT,
--     QueueTime DATETIME,
--     ExpirationDate DATETIME,
--     QueueStatus ENUM('Pending', 'Executed', 'Cancelled'),
--     FOREIGN KEY (OrderID) REFERENCES NotArbitrageOrder(OrderID) ON DELETE CASCADE,
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 11. ProfitLoss Table
-- CREATE TABLE IF NOT EXISTS ProfitLoss (
--     PLID INT AUTO_INCREMENT PRIMARY KEY,
--     AccountID INT,
--     StockID INT,
--     HistoricalProfit DECIMAL(15, 2),
--     HistoricalLoss DECIMAL(15, 2),
--     NetProfitLoss DECIMAL(15, 2),
--     FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 12. US Stock Financial Indicators Table
-- CREATE TABLE IF NOT EXISTS UsStockFinancialStatements (
--     IndicatorID INT AUTO_INCREMENT PRIMARY KEY,
--     StockID INT NOT NULL, -- Foreign key referencing Stock table
--     Revenue DECIMAL(15, 2), -- Total revenue in USD
--     NetIncome DECIMAL(15, 2), -- Net income in USD
--     EPS DECIMAL(10, 2), -- Earnings Per Share
--     PE_Ratio DECIMAL(10, 2), -- Price to Earnings ratio
--     DividendYield DECIMAL(5, 2), -- Dividend yield in percentage
--     MarketCap DECIMAL(20, 2), -- Market capitalization in USD
--     ROE DECIMAL(5, 2), -- Return on Equity in percentage
--     ROA DECIMAL(5, 2), -- Return on Assets in percentage
--     DebtToEquity DECIMAL(5, 2), -- Debt-to-Equity ratio
--     EBITDA DECIMAL(15, 2), -- Earnings Before Interest, Taxes, Depreciation, and Amortization
--     ProfitMargin DECIMAL(5, 2), -- Profit margin in percentage
--     LastUpdated DATETIME, -- Timestamp for the last update
--     FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
-- );

-- 13. US Stock historical data Table
-- CREATE TABLE us_stock_history_alpacapy (
--     Date DATE NOT NULL,
--     Open FLOAT,
--     High FLOAT,
--     Low FLOAT,
--     Close FLOAT,
--     Volume BIGINT,
--     Symbol VARCHAR(10),
--     PRIMARY KEY (Date, Symbol)
-- );

-- 14. US Stock historical data Table
-- CREATE TABLE us_stock_history_yfinance (
--     Date DATE NOT NULL,
--     Open FLOAT,
--     High FLOAT,
--     Low FLOAT,
--     Close FLOAT,
--     Volume BIGINT,
--     Symbol VARCHAR(10),
--     PRIMARY KEY (Date, Symbol)
-- );

-- 15. US Stock analysis Table
CREATE TABLE stock_analysis (
    Symbol_1 VARCHAR(10),
    Symbol_2 VARCHAR(10),
    Correlation DECIMAL(5, 2),
    p_value DECIMAL(5, 2),
    PRIMARY KEY (Symbol_1, Symbol_2)
);

-- 16. US Stock analysis Table2
CREATE TABLE stock_analysis_2 (
    Symbol_1 VARCHAR(10),
    Symbol_2 VARCHAR(10),
    min_distance DECIMAL(5, 2),
    PRIMARY KEY (Symbol_1, Symbol_2)
);


SELECT USER();
SELECT User, Host FROM mysql.user;