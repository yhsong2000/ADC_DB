-- MySQL Script generated by MySQL Workbench
-- Thu Feb 17 17:50:58 2022
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema adcdb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema adcdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `adcdb` DEFAULT CHARACTER SET utf8 ;
USE `adcdb` ;

-- -----------------------------------------------------
-- Table `adcdb`.`Vision_Recipe`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Vision_Recipe` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `rcp_name` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Machine`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Machine` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `m_name` VARCHAR(45) NOT NULL,
  `facility_name` VARCHAR(45) NOT NULL,
  `resolution_x` DOUBLE NULL,
  `resolution_y` DOUBLE NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`LOT_Information`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`LOT_Information` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `product_id` VARCHAR(45) NOT NULL,
  `Recipes_ID` INT NOT NULL,
  `Machine_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_LOT_Information_Recipes1_idx` (`Recipes_ID` ASC) VISIBLE,
  INDEX `fk_LOT_Information_Machine1_idx` (`Machine_ID` ASC) VISIBLE,
  CONSTRAINT `fk_LOT_Information_Recipes1`
    FOREIGN KEY (`Recipes_ID`)
    REFERENCES `adcdb`.`Vision_Recipe` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_LOT_Information_Machine1`
    FOREIGN KEY (`Machine_ID`)
    REFERENCES `adcdb`.`Machine` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Defect_Code`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Defect_Code` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Vision_Recipe_ID` INT NOT NULL,
  `defect_code` INT NULL,
  `detect_light_r` TINYINT NULL,
  `detect_light_g` TINYINT NULL,
  `detect_light_b` TINYINT NULL,
  `detect_light_pad` TINYINT NULL,
  `detect_light_axs` TINYINT NULL,
  `detect_light_h` TINYINT NULL,
  `detect_light_i` TINYINT NULL,
  `detect_light_s` TINYINT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_Defect_Code_Vision_Recipe1_idx` (`Vision_Recipe_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Defect_Code_Vision_Recipe1`
    FOREIGN KEY (`Vision_Recipe_ID`)
    REFERENCES `adcdb`.`Vision_Recipe` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Bundle`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Bundle` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `sorter_no` INT NOT NULL,
  `cycle_no` INT NOT NULL,
  `LOT_Information_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_Bundle_LOT_Information1_idx` (`LOT_Information_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Bundle_LOT_Information1`
    FOREIGN KEY (`LOT_Information_ID`)
    REFERENCES `adcdb`.`LOT_Information` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`strips`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`strips` (
  `barcode` VARCHAR(45) NOT NULL,
  `strip_no` INT NOT NULL,
  `Bundle_ID` INT NOT NULL,
  `insp_start` DATETIME NULL,
  `insp_end` DATETIME NULL,
  INDEX `fk_strips_Bundle1_idx` (`Bundle_ID` ASC) VISIBLE,
  PRIMARY KEY (`barcode`),
  CONSTRAINT `fk_strips_Bundle1`
    FOREIGN KEY (`Bundle_ID`)
    REFERENCES `adcdb`.`Bundle` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`POINTS`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`POINTS` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `defect_index` INT NOT NULL,
  `strip_defect` VARCHAR(45) NULL,
  `unit_x` INT NULL,
  `unit_y` INT NULL,
  `pos_x` DOUBLE NULL,
  `pos_y` DOUBLE NULL,
  `Defect_Code_ID` INT NOT NULL,
  `defect_size` INT NULL,
  `defect_len` INT NULL,
  `defect_width` INT NULL,
  `defect_height` INT NULL,
  `strips_barcode` VARCHAR(45) NOT NULL,
  `critical` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_POINTS_Defect_Code1_idx` (`Defect_Code_ID` ASC) VISIBLE,
  INDEX `fk_POINTS_strips1_idx` (`strips_barcode` ASC) VISIBLE,
  CONSTRAINT `fk_POINTS_Defect_Code1`
    FOREIGN KEY (`Defect_Code_ID`)
    REFERENCES `adcdb`.`Defect_Code` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_POINTS_strips1`
    FOREIGN KEY (`strips_barcode`)
    REFERENCES `adcdb`.`strips` (`barcode`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Ai_Recipe`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Ai_Recipe` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `version` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`ADC`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`ADC` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `ai_final_bin` INT NOT NULL,
  `ai_good` VARCHAR(45) NULL,
  `ai_defect` VARCHAR(45) NULL,
  `Ai_Recipe_ID` INT NOT NULL,
  `POINTS_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_ADC_Ai_Recipe1_idx` (`Ai_Recipe_ID` ASC) VISIBLE,
  INDEX `fk_ADC_POINTS1_idx` (`POINTS_ID` ASC) VISIBLE,
  CONSTRAINT `fk_ADC_Ai_Recipe1`
    FOREIGN KEY (`Ai_Recipe_ID`)
    REFERENCES `adcdb`.`Ai_Recipe` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ADC_POINTS1`
    FOREIGN KEY (`POINTS_ID`)
    REFERENCES `adcdb`.`POINTS` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Top_multi`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Top_multi` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `softmax0` DOUBLE NOT NULL,
  `softmax1` DOUBLE NOT NULL,
  `softmax2` DOUBLE NOT NULL,
  `softmax3` DOUBLE NOT NULL,
  `softmax4` DOUBLE NOT NULL,
  `softmax5` DOUBLE NOT NULL,
  `softmax6` DOUBLE NOT NULL,
  `softmax7` DOUBLE NOT NULL,
  `softmax8` DOUBLE NOT NULL,
  `softmaxResult` INT NOT NULL,
  `ADC_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_Top_multi_ADC1_idx` (`ADC_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Top_multi_ADC1`
    FOREIGN KEY (`ADC_ID`)
    REFERENCES `adcdb`.`ADC` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`Bot_multi`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`Bot_multi` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `softmax0` DOUBLE NOT NULL,
  `softmax1` DOUBLE NOT NULL,
  `softmax2` DOUBLE NOT NULL,
  `softmax3` DOUBLE NOT NULL,
  `softmax5` DOUBLE NOT NULL,
  `softmax4` DOUBLE NOT NULL,
  `softmax6` DOUBLE NOT NULL,
  `softmax7` DOUBLE NOT NULL,
  `softmax8` DOUBLE NOT NULL,
  `softmaxResult` INT NOT NULL,
  `ADC_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_Bot_multi_ADC1_idx` (`ADC_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Bot_multi_ADC1`
    FOREIGN KEY (`ADC_ID`)
    REFERENCES `adcdb`.`ADC` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`operator`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`operator` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`vrs_dcode`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`vrs_dcode` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `dcode_name` VARCHAR(45) NOT NULL,
  `dcode_num` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `adcdb`.`VRS`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `adcdb`.`VRS` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `LOT_Information_ID` INT NOT NULL,
  `vrs_scope` TINYINT NULL,
  `vrs_blow` TINYINT NULL,
  `vrs_checktime` FLOAT NULL,
  `VRS_detailcol` VARCHAR(45) NULL,
  `vrs_sortIndex` VARCHAR(45) NULL,
  `vrs_defectfirst` VARCHAR(45) NULL,
  `vrs_datetime` VARCHAR(45) NULL,
  `operator_ID` INT NOT NULL,
  `dcode_ID` INT NOT NULL,
  `POINTS_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_VRS_detail_operator1_idx` (`operator_ID` ASC) VISIBLE,
  INDEX `fk_VRS_detail_dcode1_idx` (`dcode_ID` ASC) VISIBLE,
  INDEX `fk_VRS_POINTS1_idx` (`POINTS_ID` ASC) VISIBLE,
  CONSTRAINT `fk_VRS_detail_operator1`
    FOREIGN KEY (`operator_ID`)
    REFERENCES `adcdb`.`operator` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_VRS_detail_dcode1`
    FOREIGN KEY (`dcode_ID`)
    REFERENCES `adcdb`.`vrs_dcode` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_VRS_POINTS1`
    FOREIGN KEY (`POINTS_ID`)
    REFERENCES `adcdb`.`POINTS` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
