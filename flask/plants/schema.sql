CREATE TABLE `providers` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`username` VARCHAR(20) NOT NULL
);

CREATE UNIQUE INDEX `providername` ON `providers`(`username`);

CREATE TABLE `consumers` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`username` VARCHAR(20) NOT NULL
);

CREATE UNIQUE INDEX `consumername` ON `consumers`(`username`);

CREATE TABLE `jobs` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`description` TEXT NOT NULL,
	`location` TEXT NOT NULL,
	`requester` INTEGER NOT NULL,
	`claimer` INTEGER,
	`completed` INTEGER DEFAULT 0,

	FOREIGN KEY(`claimer`) REFERENCES `providers`(`id`)
);