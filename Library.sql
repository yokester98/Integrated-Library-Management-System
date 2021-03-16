-- LIBRARY
DROP DATABASE IF EXISTS `Library`;
CREATE DATABASE `Library`;
USE `Library`;

-- USER
SET NAMES utf8 ;
SET character_set_client = utf8mb4 ;

CREATE TABLE `users` (
  `userID` 				int(7)	 		NOT NULL AUTO_INCREMENT,
  `password` 			varchar(50) 	NOT NULL,
  `bookBorrowings` 		TINYINT 		NOT NULL DEFAULT '0',
  `bookReservations` 	TINYINT 		NOT NULL DEFAULT '0',
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- BOOK
CREATE TABLE Book(
	bookID				INT				NOT NULL,
    title				VARCHAR(35)		NOT NULL,
    authors				VARCHAR(20)		NOT NULL,
    category			VARCHAR(10)		NOT NULL,
    publisher			VARCHAR(20)		NOT NULL,
    yearOfPublication	SMALLINT		NOT NULL,
    userID				int(7)			NOT NULL,
    returnDate			DATE,
    dueDate				DATE,
    borrowDate			DATE,
    PRIMARY KEY (bookID),
    FOREIGN KEY (userID) REFERENCES users(userID)	ON UPDATE CASCADE);
    
    -- FINE
    CREATE TABLE Fine(
	userID    	int(7)      NOT NULL,
    amount    	int         NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID)	REFERENCES users(userID));
    
    -- PAYMENT
    CREATE TABLE Payment(
	receiptNum  int       	NOT NULL,
    amountPaid  int        	NOT NULL,
    userID    	int(7)      NOT NULL,
    datePaid  	DATE      	NOT NULL,
    PRIMARY KEY (receiptNum),
    FOREIGN KEY (userID)    REFERENCES users(userID));