PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;


CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT DEFAULT 'pending'
);


INSERT INTO orders (id, item_name, quantity, status) VALUES (1, 'Bàn phím cơ Keychron', 1, 'pending');
INSERT INTO orders (id, item_name, quantity, status) VALUES (2, 'Chuột Logitech G502', 2, 'completed');
INSERT INTO orders (id, item_name, quantity, status) VALUES (3, 'Màn hình Dell Ultrasharp', 1, 'pending');


DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('orders', 3);

COMMIT;