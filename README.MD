# Cryptcurrency-Tracker
Simple telegram bot for tracking cryptocurrency price. [Crypto Tracker](https://t.me/CryptocurrTrackerBot)

# What this project do
Fetch information about cryptocurrency price using coinmarketcap API v2, and give this information to users from database.

# How to install
For this bot you need requests, and pyTelegramBotAPI. Change line with token and db in config.py. Cretate db with this table:

Main table with all cryptocurrency
```
CREATE TABLE `crypto_json` (
	`id`	INTEGER NOT NULL UNIQUE,
	`name`	TEXT UNIQUE,
	`symbol`	TEXT,
	`price`	REAL,
	`percent_change_1h`	REAL,
	`percent_change_24h`	REAL,
	`percent_change_7d`	REAL,
	PRIMARY KEY(`id`) );
```
Table with cryptocurrency which have users
```
CREATE TABLE `users_crypto` (
	`user_id`	INTEGER,
	`crypto_id`	INTEGER,
	`amount`	REAL NOT NULL DEFAULT 0 );
```
Table with states for FSM
```
CREATE TABLE `users_state` (
	`user_id`	INTEGER UNIQUE,
	`state`	TEXT,
	PRIMARY KEY(`user_id`) );
```
Table with status for notifications
```
CREATE TABLE `users_status` (
	`user_id`	INTEGER UNIQUE,
	`status`	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY(`user_id`) );
```
