-- LIBRARY
DROP DATABASE IF EXISTS Library;
CREATE DATABASE Library;
USE Library;

-- USER
SET NAMES utf8 ;
SET character_set_client = utf8mb4 ;

CREATE TABLE Users (
  userID 				int(7)	 		NOT NULL AUTO_INCREMENT,
  password				varchar(50) 	NOT NULL,
  bookBorrowings		TINYINT 		NOT NULL DEFAULT '0',
  bookReservations 		TINYINT 		NOT NULL DEFAULT '0',
  PRIMARY KEY (userID)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- BOOK
CREATE TABLE Book(
	bookID				int			NOT NULL,
    title				text,
    authors				text,
    category			text,
    datePublished		text,
    borrowedBy			int(7),
    reservedBy			int(7),
    returnDate			DATE,
    dueDate				DATE,
    borrowDate			DATE,
    PRIMARY KEY (bookID));
    
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
    
    -- libbooks.json to table
CREATE TABLE `library`.`libbooks` (
	`_id` 				int,
	`title` 			text, 	
	`isbn` 				text, 	
    `pageCount` 		int,
	`publishedDate` 	text,	
    `thumbnailUrl`		text,
	`shortDescription` 	text,
	`longDescription` 	text, 
	`status` 			text, 
	`authors` 			text, 
	`categories` 		text)