UPDATE book 
SET borrowedBy = 1, reservedBy = 3, dueDate = DATE("21-04-07"), borrowDate = DATE("21-03-07")
WHERE bookID = 1;

UPDATE book
SET borrowedBy = 2, reservedBy = 3, dueDate = DATE("21-04-11"), borrowDate = DATE("21-03-07")
WHERE bookID = 2;

UPDATE book 
SET borrowedBy = 3, reservedBy = 1, dueDate = DATE("21-04-17"), borrowDate = DATE("21-03-07")
WHERE bookID = 3;

UPDATE book 
SET borrowedBy = 1, reservedBy = 2, dueDate = DATE("21-04-15"), borrowDate = DATE("21-03-07")
WHERE bookID = 4;

UPDATE book 
SET borrowedBy = 2, reservedBy = 1, dueDate = DATE("21-04-13"), borrowDate = DATE("21-03-07")
WHERE bookID = 5;