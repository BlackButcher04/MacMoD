-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.4.10-MariaDB - MariaDB Server
-- Server OS:                    Win64
-- HeidiSQL Version:             12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for macmod_db
CREATE DATABASE IF NOT EXISTS `macmod_db` /*!40100 DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci */;
USE `macmod_db`;

-- Dumping structure for table macmod_db.conditions_log
CREATE TABLE IF NOT EXISTS `conditions_log` (
  `logID` int(11) NOT NULL AUTO_INCREMENT,
  `temp` varchar(255) DEFAULT NULL,
  `vibration` varchar(255) DEFAULT NULL,
  `noise` varchar(255) DEFAULT NULL,
  `pressure` varchar(255) DEFAULT NULL,
  `rpm` varchar(255) DEFAULT NULL,
  `coolant` varchar(255) DEFAULT NULL,
  `powerwatt` varchar(255) DEFAULT NULL,
  `rul_status` varchar(255) DEFAULT NULL,
  `machines_status` longtext DEFAULT NULL,
  `time_update` timestamp NULL DEFAULT current_timestamp(),
  `machinesID` int(11) DEFAULT NULL,
  PRIMARY KEY (`logID`),
  KEY `machinesID` (`machinesID`),
  CONSTRAINT `conditions_log_ibfk_1` FOREIGN KEY (`machinesID`) REFERENCES `machines` (`machinesID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table macmod_db.conditions_log: ~10 rows (approximately)
INSERT INTO `conditions_log` (`logID`, `temp`, `vibration`, `noise`, `pressure`, `rpm`, `coolant`, `powerwatt`, `rul_status`, `machines_status`, `time_update`, `machinesID`) VALUES
	(1, '67.0', '67.0', '78.0', '78.0', '123.0', '123.0', '123.0', '131', 'Machine is in a \'Healthy\' state. Operating smoothly.', '2026-03-16 14:35:55', 4),
	(2, '12.0', '12.0', '12.0', '12.0', '12.0', '12.0', '12.0', '119', 'OKAY', '2026-03-16 14:44:45', 4),
	(3, '12.0', '12.0', '12.0', '12.0', '12.0', '12.0', '12.0', '119', 'OKAY', '2026-03-16 14:46:13', 5),
	(4, '100.0', '1678.0', '12.0', '12.0', '1278.0', '34354.0', '1223.0', '134', 'OKAY', '2026-03-16 14:46:36', 4),
	(5, '100000.0', '100000.0', '100000.0', '100000.0', '100000.0', '100000.0', '100000.0', '4', 'CRITICAL', '2026-03-16 14:46:57', 4),
	(6, '78.0', '78.0', '78.0', '90.0', '129.0', '123.0', '123.0', '136', 'OKAY', '2026-03-16 15:28:24', 4),
	(7, '90.0', '90.0', '90.0', '45.0', '123.0', '123.0', '1200.0', '58', 'WARNING', '2026-03-17 03:20:27', 4),
	(8, '78.0', '12.0', '10.0', '34.0', '1000.0', '80.0', '100.19', '129', 'OKAY', '2026-03-17 04:48:44', 7),
	(9, '78.0', '12.0', '10.0', '34.0', '130.0', '80.0', '100.19', '129', 'OKAY', '2026-03-17 06:39:22', 7),
	(10, '78.0', '12.0', '10.0', '34.0', '130.0', '80.0', '100.19', '129', 'OKAY', '2026-03-17 06:39:51', 4);

-- Dumping structure for table macmod_db.machines
CREATE TABLE IF NOT EXISTS `machines` (
  `machinesID` int(11) NOT NULL AUTO_INCREMENT,
  `machinesNAME` varchar(255) NOT NULL,
  `serial_number` varchar(255) DEFAULT NULL,
  `status_use` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`machinesID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table macmod_db.machines: ~6 rows (approximately)
INSERT INTO `machines` (`machinesID`, `machinesNAME`, `serial_number`, `status_use`) VALUES
	(3, 'Machine Chopper 001', '001', 'ACTIVE'),
	(4, 'Air Compresor', 'AC001', 'ACTIVE'),
	(5, 'Mixer M001', 'M001', 'ACTIVE'),
	(6, 'Machine Chopper C001', 'C001', 'ACTIVE'),
	(7, 'Hello world ', 'A001', 'ACTIVE'),
	(8, 'Welding Machine', 'WM0098', 'ACTIVE');

-- Dumping structure for table macmod_db.maintenance_log
CREATE TABLE IF NOT EXISTS `maintenance_log` (
  `maint_id` int(11) NOT NULL AUTO_INCREMENT,
  `machinesID` int(11) DEFAULT NULL,
  `job_description` text DEFAULT NULL,
  `priority` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'PENDING',
  `date_issued` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`maint_id`),
  KEY `machinesID` (`machinesID`),
  CONSTRAINT `maintenance_log_ibfk_1` FOREIGN KEY (`machinesID`) REFERENCES `machines` (`machinesID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table macmod_db.maintenance_log: ~9 rows (approximately)
INSERT INTO `maintenance_log` (`maint_id`, `machinesID`, `job_description`, `priority`, `status`, `date_issued`) VALUES
	(1, 5, 'No rpm data', 'CRITICAL', 'COMPLETED', '2026-03-17 11:10:05'),
	(2, 4, 'Normal Services', 'Routine', 'COMPLETED', '2026-03-17 11:15:35'),
	(3, 5, 'Normal Sevices', 'Routine', 'COMPLETED', '2026-03-17 11:16:19'),
	(4, 4, 'Normal Service', 'Routine', 'COMPLETED', '2026-03-17 11:19:50'),
	(5, 7, 'Normal Services', 'Routine', 'COMPLETED', '2026-03-17 11:20:48'),
	(6, 4, 'Belt replacement', 'High', 'COMPLETED', '2026-03-17 11:25:15'),
	(7, 4, 'Test', 'Routine', 'COMPLETED', '2026-03-17 11:40:41'),
	(8, 4, 'Test', 'Routine', 'COMPLETED', '2026-03-17 11:43:43'),
	(9, 4, 'Test', 'Routine', 'COMPLETED', '2026-03-17 11:45:40');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
