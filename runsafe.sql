-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema runsafe
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `runsafe` ;

-- -----------------------------------------------------
-- Schema runsafe
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `runsafe` DEFAULT CHARACTER SET utf8 ;
USE `runsafe` ;

-- -----------------------------------------------------
-- Table `runsafe`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`users` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`users` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_user`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `runsafe`.`events`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`events` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`events` (
  `id_event` INT NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(255) NULL DEFAULT NULL,
  `host` INT NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_event`),
  INDEX `fk_events_users1_idx` (`host` ASC) VISIBLE,
  CONSTRAINT `fk_events_users1`
    FOREIGN KEY (`host`)
    REFERENCES `runsafe`.`users` (`id_user`))
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `runsafe`.`friends`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`friends` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`friends` (
  `friender` INT NOT NULL,
  `friended` INT NOT NULL,
  PRIMARY KEY (`friender`, `friended`),
  INDEX `fk_users_has_users_users2_idx` (`friended` ASC) VISIBLE,
  INDEX `fk_users_has_users_users1_idx` (`friender` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_users_users1`
    FOREIGN KEY (`friender`)
    REFERENCES `runsafe`.`users` (`id_user`),
  CONSTRAINT `fk_users_has_users_users2`
    FOREIGN KEY (`friended`)
    REFERENCES `runsafe`.`users` (`id_user`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `runsafe`.`joined_events`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`joined_events` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`joined_events` (
  `event_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`event_id`, `user_id`),
  INDEX `fk_events_has_users_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_events_has_users_events_idx` (`event_id` ASC) VISIBLE,
  CONSTRAINT `fk_events_has_users_events`
    FOREIGN KEY (`event_id`)
    REFERENCES `runsafe`.`events` (`id_event`),
  CONSTRAINT `fk_events_has_users_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `runsafe`.`users` (`id_user`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `runsafe`.`rates`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`rates` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`rates` (
  `rater` INT NOT NULL,
  `rated` INT NOT NULL,
  PRIMARY KEY (`rater`, `rated`),
  INDEX `fk_users_has_users_users4_idx` (`rated` ASC) VISIBLE,
  INDEX `fk_users_has_users_users3_idx` (`rater` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_users_users3`
    FOREIGN KEY (`rater`)
    REFERENCES `runsafe`.`users` (`id_user`),
  CONSTRAINT `fk_users_has_users_users4`
    FOREIGN KEY (`rated`)
    REFERENCES `runsafe`.`users` (`id_user`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `runsafe`.`messages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runsafe`.`messages` ;

CREATE TABLE IF NOT EXISTS `runsafe`.`messages` (
  `joined_event_id` INT NOT NULL,
  `joined_user_id` INT NOT NULL,
  `content` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  INDEX `fk_messages_joined_events1_idx` (`joined_event_id` ASC, `joined_user_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_joined_events1`
    FOREIGN KEY (`joined_event_id` , `joined_user_id`)
    REFERENCES `runsafe`.`joined_events` (`event_id` , `user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
