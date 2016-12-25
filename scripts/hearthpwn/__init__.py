# coding=utf-8
"""
scripts/hearthpwn

By pro player
Thijs - http://www.hearthpwn.com/decks?filter-player=126
Savjz - http://www.hearthpwn.com/decks?filter-player=62

check scripts/hearthpwn/proplayers.csv

decks can be obtained by id

Tables
======

cards
-----

+---------+----------------------------------------------+
| title   | type                                         |
+=========+==============================================+
| id      | INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT   |
+---------+----------------------------------------------+
| herf    | TEXT NOT NULL UNIQUE                         |
+---------+----------------------------------------------+
| cost    | INTEGER NOT NULL DEFAULT 0                   |
+---------+----------------------------------------------+

decks
-----

+----------+----------------------------------------------+
| title    | type                                         |
+==========+==============================================+
| id       | INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT   |
+----------+----------------------------------------------+
| herf     | TEXT NOT NULL UNIQUE                         |
+----------+----------------------------------------------+
| class    | INTEGER NOT NULL DEFAULT 0                   |
+----------+----------------------------------------------+
| format   | INTEGER NOT NULL DEFAULT 1                   |
+----------+----------------------------------------------+

cards in decks
--------------

+------------+----------------------------------------------+
| title      | type                                         |
+============+==============================================+
| id         | INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT   |
+------------+----------------------------------------------+
| deck\_id   | INTEGER NOT NULL                             |
+------------+----------------------------------------------+
| card\_id   | INTEGER NOT NULL                             |
+------------+----------------------------------------------+
| count      | INTEGER NOT NULL DEFAULT 1                   |
+------------+----------------------------------------------+

Requests
========
INSERT OR IGNORE INTO cards (href, cost) VALUES (‘%s’, %d);

INSERT OR IGNORE INTO decks (href, class, format) VALUES (‘%s’, 1, 1); 1 - for warrior, 1 - for standard

INSERT INTO cards\_in\_decks (deck\_id, card\_id, count) VALUES (%d, %d, %d);
"""
