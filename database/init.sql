-- create the databases
CREATE DATABASE IF NOT EXISTS vinyl_records;

USE vinyl_records;

CREATE TABLE IF NOT EXISTS `vinyl_records`.`vinyl` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(75) NULL,
  `media_condition` VARCHAR(75) NULL,
  `sleeve_condition` VARCHAR(75) NULL,
  `price` DECIMAL(10,2) NULL,
  `buy_url` VARCHAR(120) NULL,
  `seller_rating` DECIMAL(10,2) NULL,
  `seller_url` VARCHAR(120) NULL,
  PRIMARY KEY (`id`));
