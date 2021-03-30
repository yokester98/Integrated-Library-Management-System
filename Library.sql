-- LIBRARY
DROP DATABASE IF EXISTS Library;
CREATE DATABASE Library;
USE Library;

-- USER
SET NAMES utf8 ;
SET character_set_client = utf8mb4 ;

CREATE TABLE Admin (
  adminID 				int(7)	 		NOT NULL,
  firstName				text			NOT NULL,
  lastName				text			NOT NULL,
  password				varchar(50) 	NOT NULL,
  PRIMARY KEY (adminID)
);

CREATE TABLE User (
  userID 				int(7)	 		NOT NULL AUTO_INCREMENT,
  firstName				text			NOT NULL,
  lastName				text			NOT NULL,
  password				varchar(50) 	NOT NULL,
  PRIMARY KEY (userID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- BOOK
CREATE TABLE Book(
	bookID				int			NOT NULL,
    title				text,
    authors				text,
    category			text,
    datePublished		DATE,
    PRIMARY KEY (bookID));
    
    -- FINE
CREATE TABLE Fine(
	userID    	int(7)      NOT NULL,
    amount    	int         NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID)	REFERENCES User(userID));
    
    -- PAYMENT
CREATE TABLE Payment(
	receiptNum  int       	NOT NULL AUTO_INCREMENT,
    amountPaid  int        	NOT NULL,
    userID    	int(7)      NOT NULL,
    datePaid  	DATE      	NOT NULL,
    PRIMARY KEY (receiptNum),
    FOREIGN KEY (userID)    REFERENCES User(userID));
    
	-- BORROWED
CREATE TABLE Borrowed(
	bookID  	int			NOT NULL,
    userID		int			NOT NULL,
    borrowDate	DATE		NOT NULL,
    dueDate		DATE		NOT NULL,
    PRIMARY KEY (bookID),
    FOREIGN KEY (bookID)    REFERENCES Book(bookID),
    FOREIGN KEY (userID)	REFERENCES User(userID));
    
	-- RESERVED
CREATE TABLE Reserved(
	bookID  	int			NOT NULL,
    userID		int			NOT NULL,
    reserveDate	DATE		NOT NULL,
    PRIMARY KEY (bookID),
    FOREIGN KEY (bookID)    REFERENCES Book(bookID),
    FOREIGN KEY (userID)	REFERENCES User(userID));
    
    -- INSERT ADMIN DATA
INSERT INTO Admin VALUES (8, 'admin', 'admin', 'abcd');
    
	-- INSERT USER DATA
INSERT INTO User VALUES (1, 'Radell', 'Ng', 'abcd');
INSERT INTO User VALUES (2, 'Yoke Yue', 'Loy', 'abcde');
INSERT INTO User VALUES (3, 'Wen Yin', 'Fun', 'abcdef');
INSERT INTO User VALUES (4, 'Jia Shang', 'Oh', 'abcdefg');
INSERT INTO User VALUES (5, 'Zheng Hong', 'Lee', 'abc');

	-- INSERT BOOK DATA
INSERT INTO Book VALUES(1, 'RANDOM', 'LUOKAI', 'SQL', DATE("21-03-07"));
INSERT INTO Book VALUES(2, 'CompClub', 'Wenyin', 'Welfare', DATE("21-03-07"));
INSERT INTO Book VALUES(3, 'SHEARES', 'Tammi', 'Hall', DATE("21-03-07"));
INSERT INTO Book VALUES(4, 'MAHJONG', 'Radell', 'Entertainment', DATE("21-03-07"));
INSERT INTO Book VALUES(5, 'BT2102', 'DPOO', 'MySQL', DATE("21-03-07"));

	-- INSERT FINE DATA
-- INSERT INTO Fine VALUES (00001, 20);
-- INSERT INTO Fine VALUES (00002, 15);
-- INSERT INTO Fine VALUES (00003, 27);
-- INSERT INTO Fine VALUES (00004, 33);
INSERT INTO Fine VALUES (00005, 15);

	-- INSERT PAYMENT DATA
INSERT INTO Payment VALUES (1, 15, 00001, DATE("21-03-07"));
INSERT INTO Payment VALUES (2, 15, 00002, DATE("21-03-07"));
INSERT INTO Payment VALUES (3, 20, 00003, DATE("21-03-07"));
-- INSERT INTO Payment VALUES (4, 33, 00004, DATE("21-03-07"));
-- INSERT INTO Payment VALUES (5, 5, 00005, DATE("21-03-07"));

	-- INSERT BORROWED DATA
INSERT INTO Borrowed VALUES(1, 2, DATE("21-02-23"), DATE("21-03-23"));
-- INSERT INTO Borrowed VALUES(3, 1, DATE("21-02-23"), DATE("21-03-23"));
INSERT INTO Borrowed VALUES(5, 2, DATE("21-02-23"), DATE("21-03-23"));

	-- INSERT RESERVED DATA
-- INSERT INTO Reserved VALUES(1, 3, DATE("21-02-23"));
-- INSERT INTO Reserved VALUES(3, 2, DATE("21-02-23"));
INSERT INTO Reserved VALUES(4, 2, DATE("21-02-23"));
-- INSERT INTO Reserved VALUES(5, 3, DATE("21-02-23"));