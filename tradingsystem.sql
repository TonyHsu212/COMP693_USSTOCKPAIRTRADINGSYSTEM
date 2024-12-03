-- MySQL Script for Trading System ERD

-- Create a schema named 'TradingSystem' 
CREATE SCHEMA TradingSystem; 

-- Alternatively, you can use CREATE DATABASE (interchangeable with CREATE SCHEMA) 
CREATE DATABASE TradingSystem; 

-- Switch to the new schema 
USE TradingSystem;

-- 1. User Table
CREATE TABLE User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(15),
    Address VARCHAR(255),
    DOB DATE
);

-- 2. Account Table
CREATE TABLE Account (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    Balance DECIMAL(15, 2),
    AccountType ENUM('Cash', 'Margin'),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

-- 3. Stock Table
CREATE TABLE Stock (
    StockID INT AUTO_INCREMENT PRIMARY KEY,
    TickerSymbol VARCHAR(10) UNIQUE,
    StockName VARCHAR(100),
    Sector VARCHAR(50),
    CurrentPrice DECIMAL(10, 2),
    Exchange VARCHAR(50)
);

-- 4. Order Table
CREATE TABLE NotArbitrageOrder (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT,
    StockID INT,
    OrderType ENUM('Buy', 'Sell'),
    Quantity INT,
    Price DECIMAL(10, 2),
    OrderDate DATETIME,
    Status ENUM('Pending', 'Completed', 'Cancelled'),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);

CREATE TABLE ArbitrageOrder (
    ArbitrageOrderID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    ArbitrageType ENUM('PriceDiff', 'Statistical', 'Other') NOT NULL,
    OrderDate DATETIME NOT NULL,
    Status ENUM('Pending', 'Completed', 'Cancelled') NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE
);

CREATE TABLE ArbitrageOrderLeg (
    ArbitrageOrderLegID INT AUTO_INCREMENT PRIMARY KEY,
    ArbitrageOrderID INT NOT NULL,
    StockID INT NOT NULL,
    Direction ENUM('Buy', 'Sell') NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Status ENUM('Pending', 'Completed', 'Cancelled'),
    FOREIGN KEY (ArbitrageOrderID) REFERENCES ArbitrageOrder(ArbitrageOrderID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);


-- 5. Transaction Table
CREATE TABLE Transaction (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT,
    StockID INT,
    Quantity INT,
    TransactionDate DATETIME,
    TransactionType ENUM('Buy', 'Sell'),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);

-- 6. Watchlist Table
CREATE TABLE Watchlist (
    WatchlistID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    StockID INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);

-- 7. Portfolio Table
CREATE TABLE Portfolio (
    PortfolioID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT,
    StockID INT,
    Quantity INT,
    AvgPurchasePrice DECIMAL(10, 2),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);


-- 8. Position Table
CREATE TABLE Position (
    PositionID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    StockID INT NOT NULL,
    OpenDate DATETIME NOT NULL,
    Quantity INT NOT NULL,
    AvgOpenPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);

-- 9. ClosePosition Table
CREATE TABLE ClosePosition (
    ClosePositionID INT AUTO_INCREMENT PRIMARY KEY,
    PositionID INT NOT NULL,
    CloseDate DATETIME NOT NULL,
    ClosePrice DECIMAL(10, 2) NOT NULL,
    CloseQuantity INT NOT NULL
);


-- 10. OrderQueue Table
CREATE TABLE OrderQueue (
    QueueID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    AccountID INT,
    StockID INT,
    QueueTime DATETIME,
    ExpirationDate DATETIME,
    QueueStatus ENUM('Pending', 'Executed', 'Cancelled'),
    FOREIGN KEY (OrderID) REFERENCES NotArbitrageOrder(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);

-- 11. ProfitLoss Table
CREATE TABLE ProfitLoss (
    PLID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT,
    StockID INT,
    HistoricalProfit DECIMAL(15, 2),
    HistoricalLoss DECIMAL(15, 2),
    NetProfitLoss DECIMAL(15, 2),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
    FOREIGN KEY (StockID) REFERENCES Stock(StockID) ON DELETE CASCADE
);
