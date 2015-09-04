-- MySQL dump 10.13  Distrib 5.5.38, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: lolalerter
-- ------------------------------------------------------
-- Server version 5.5.38-0ubuntu0.12.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary table structure for view `active_summoners`
--

DROP TABLE IF EXISTS `active_summoners`;
/*!50001 DROP VIEW IF EXISTS `active_summoners`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `active_summoners` (
  `ID` tinyint NOT NULL,
  `User` tinyint NOT NULL,
  `SummonerName` tinyint NOT NULL,
  `SummonerID` tinyint NOT NULL,
  `Alerter` tinyint NOT NULL,
  `Timestamp` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `active_users`
--

DROP TABLE IF EXISTS `active_users`;
/*!50001 DROP VIEW IF EXISTS `active_users`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `active_users` (
  `ID` tinyint NOT NULL,
  `APIKey` tinyint NOT NULL,
  `TwitchUsername` tinyint NOT NULL,
  `TwitchDisplay` tinyint NOT NULL,
  `TwitchToken` tinyint NOT NULL,
  `Timestamp` tinyint NOT NULL,
  `CreateDate` tinyint NOT NULL,
  `RememberToken` tinyint NOT NULL,
  `TwitchAlertsKey` tinyint NOT NULL,
  `MinimumDonation` tinyint NOT NULL,
  `ShowResubs` tinyint NOT NULL,
  `LastNotice` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `alerter_friends`
--

DROP TABLE IF EXISTS `alerter_friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alerter_friends` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `Alerter` int(10) NOT NULL,
  `SummonerID` int(10) NOT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  KEY `ShadowFriendID` (`Alerter`),
  CONSTRAINT `AlerterFriendID` FOREIGN KEY (`Alerter`) REFERENCES `alerters` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alerter_statistics`
--

DROP TABLE IF EXISTS `alerter_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alerter_statistics` (
  `Alerter` int(11) NOT NULL,
  `OnlineUsers` int(11) NOT NULL DEFAULT '0',
  `TotalSubscribed` int(11) NOT NULL DEFAULT '0',
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Alerter`),
  UNIQUE KEY `Shadow` (`Alerter`),
  CONSTRAINT `AlerterStatistics` FOREIGN KEY (`Alerter`) REFERENCES `alerters` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerter_statistics`
--

LOCK TABLES `alerter_statistics` WRITE;
/*!40000 ALTER TABLE `alerter_statistics` DISABLE KEYS */;
INSERT INTO `alerter_statistics` VALUES (1,0,0,'2015-09-04 02:00:00');
/*!40000 ALTER TABLE `alerter_statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alerters`
--

DROP TABLE IF EXISTS `alerters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alerters` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) NOT NULL,
  `Region` int(11) NOT NULL,
  `SummonerID` int(11) NOT NULL,
  `SummonerName` varchar(50) NOT NULL,
  `Password` varchar(50) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `Message` varchar(200) NOT NULL,
  `Enabled` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `TrackerRegion` (`Region`),
  CONSTRAINT `TrackerRegion` FOREIGN KEY (`Region`) REFERENCES `regions` (`ID`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerters`
--

LOCK TABLES `alerters` WRITE;
/*!40000 ALTER TABLE `alerters` DISABLE KEYS */;
INSERT INTO `alerters` VALUES (1,'lolalerter',1,51012155,'LoLAlerter','PlaintextPassword','lolalerter@gmail.com','NA Bot Online!',1);
/*!40000 ALTER TABLE `alerters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `User` int(11) NOT NULL,
  `InGame` varchar(100) DEFAULT '{} has just subscribed!',
  `InChat` varchar(100) DEFAULT '♥ Thanks for subscribing, {}!',
  `NewDonation` varchar(100) DEFAULT '{user} has donated ${amount}!',
  PRIMARY KEY (`User`),
  UNIQUE KEY `User` (`User`),
  CONSTRAINT `MessageUser` FOREIGN KEY (`User`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'{sub} has just joined the club!','★ Thanks for subscribing, {sub}!','{user} has donated ${amount}!');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notices`
--

DROP TABLE IF EXISTS `notices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notices` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `Message` varchar(200) NOT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notices`
--

LOCK TABLES `notices` WRITE;
/*!40000 ALTER TABLE `notices` DISABLE KEYS */;
INSERT INTO `notices` VALUES (1,'Welcome to open-source LoLAlerter!','2015-09-04 02:00:00');
/*!40000 ALTER TABLE `notices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regions`
--

DROP TABLE IF EXISTS `regions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `regions` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `RegionName` varchar(50) NOT NULL,
  `RegionCode` varchar(50) NOT NULL,
  `RegionChat` varchar(50) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `RegionName` (`RegionName`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regions`
--

LOCK TABLES `regions` WRITE;
/*!40000 ALTER TABLE `regions` DISABLE KEYS */;
INSERT INTO `regions` VALUES (1,'North America','NA','na2'),(2,'EU West','EUW','euw1'),(3,'Korea','KR','kr'),(4,'Oceania','OCE','oc1'),(5,'Latin America North','LAN','la1'),(6,'Latin America South','LAS','la2'),(7,'EU Nordic and East','EUNE','eun1'),(8,'Brazil','BR','br'),(9,'Russia','RU','ru'),(10,'Turkey','TR','tr');
/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `Key` varchar(50) NOT NULL,
  `Value` varchar(50) NOT NULL,
  PRIMARY KEY (`Key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES ('AdminSummoner','31186414'),('LargestDonation','10'),('MaxFriends','300'),('PayPalEmail','XXXXXXXXXXXXX@gmail.com'),('RiotAPI','XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'),('SubscriptionMonthly','5'),('TwitchAuth','oauth:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'),('TwitchUsername','LoLAlerterBot');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscribers`
--

DROP TABLE IF EXISTS `subscribers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subscribers` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `User` int(11) NOT NULL,
  `TwitchID` int(11) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `DisplayName` varchar(50) NOT NULL,
  `AddDate` datetime NOT NULL,
  `UnsubDate` datetime DEFAULT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `user_subscribers` (`User`,`TwitchID`),
  KEY `SubscriberUser` (`User`),
  CONSTRAINT `SubscriberUser` FOREIGN KEY (`User`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subscription_payments`
--

DROP TABLE IF EXISTS `subscription_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subscription_payments` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `User` int(10) NOT NULL,
  `PayerEmail` varchar(50) NOT NULL,
  `FirstName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `TXNID` varchar(50) NOT NULL,
  `GrossAmount` double NOT NULL,
  `FeeAmount` double NOT NULL,
  `PaymentDate` datetime NOT NULL,
  `ExpiryDate` datetime NOT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  KEY `User` (`User`),
  CONSTRAINT `PaymentUser` FOREIGN KEY (`User`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_payments`
--

LOCK TABLES `subscription_payments` WRITE;
/*!40000 ALTER TABLE `subscription_payments` DISABLE KEYS */;
INSERT INTO `subscription_payments` VALUES (1,1,'XXXXXXXXXX@gmail.com','Redback','Thomson','XXXXXXXXXXXXXXXXX',5,0.48,'2015-09-04 02:30:00','2015-10-04 02:30:00','2015-09-04 02:30:00');
/*!40000 ALTER TABLE `subscription_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `summoners`
--

DROP TABLE IF EXISTS `summoners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `summoners` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `User` int(10) NOT NULL,
  `SummonerName` varchar(16) NOT NULL,
  `SummonerID` int(10) NOT NULL,
  `Alerter` int(11) NOT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  KEY `UserSummoner` (`User`),
  KEY `SummonerShadow` (`Alerter`),
  CONSTRAINT `SummonerAlerter` FOREIGN KEY (`Alerter`) REFERENCES `alerters` (`ID`) ON UPDATE CASCADE,
  CONSTRAINT `UserSummoner` FOREIGN KEY (`User`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `summoners`
--

LOCK TABLES `summoners` WRITE;
/*!40000 ALTER TABLE `summoners` DISABLE KEYS */;
INSERT INTO `summoners` VALUES (1,1,'Intercontinent',31186414,1,'2015-09-04 12:00:00');
/*!40000 ALTER TABLE `summoners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_statistics`
--

DROP TABLE IF EXISTS `user_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_statistics` (
  `User` int(10) NOT NULL,
  `TotalSubscribed` int(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`User`),
  CONSTRAINT `StatisticsUser` FOREIGN KEY (`User`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_statistics`
--

LOCK TABLES `user_statistics` WRITE;
/*!40000 ALTER TABLE `user_statistics` DISABLE KEYS */;
INSERT INTO `user_statistics` VALUES (1,0);
/*!40000 ALTER TABLE `user_statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `ID` int(10) NOT NULL AUTO_INCREMENT,
  `APIKey` varchar(36) DEFAULT NULL,
  `TwitchUsername` varchar(25) NOT NULL,
  `TwitchDisplay` varchar(25) NOT NULL,
  `TwitchToken` varchar(31) DEFAULT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `CreateDate` datetime NOT NULL,
  `RememberToken` varchar(60) DEFAULT NULL,
  `TwitchAlertsKey` varchar(50) DEFAULT NULL,
  `MinimumDonation` double DEFAULT NULL,
  `ShowResubs` tinyint(1) NOT NULL DEFAULT '1',
  `LastNotice` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `TwitchUsername` (`TwitchUsername`),
  KEY `UserNotice` (`LastNotice`),
  CONSTRAINT `UserNotice` FOREIGN KEY (`LastNotice`) REFERENCES `notices` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ABCDEFGH-1234-IJKL-5678-MNOPQRSTUVWX','redbackthomson','RedbackThomson','XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX','2015-09-04 12:00:00','2015-09-04 12:00:00','',NULL,NULL,1,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `active_summoners`
--

/*!50001 DROP TABLE IF EXISTS `active_summoners`*/;
/*!50001 DROP VIEW IF EXISTS `active_summoners`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `active_summoners` AS select `lolalerter`.`summoners`.`ID` AS `ID`,`lolalerter`.`summoners`.`User` AS `User`,`lolalerter`.`summoners`.`SummonerName` AS `SummonerName`,`lolalerter`.`summoners`.`SummonerID` AS `SummonerID`,`lolalerter`.`summoners`.`Alerter` AS `Alerter`,`lolalerter`.`summoners`.`Timestamp` AS `Timestamp` from `summoners` where `lolalerter`.`summoners`.`User` in (select `active_users`.`ID` from `active_users`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `active_users`
--

/*!50001 DROP TABLE IF EXISTS `active_users`*/;
/*!50001 DROP VIEW IF EXISTS `active_users`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `active_users` AS select `lolalerter`.`users`.`ID` AS `ID`,`lolalerter`.`users`.`APIKey` AS `APIKey`,`lolalerter`.`users`.`TwitchUsername` AS `TwitchUsername`,`lolalerter`.`users`.`TwitchDisplay` AS `TwitchDisplay`,`lolalerter`.`users`.`TwitchToken` AS `TwitchToken`,`lolalerter`.`users`.`Timestamp` AS `Timestamp`,`lolalerter`.`users`.`CreateDate` AS `CreateDate`,`lolalerter`.`users`.`RememberToken` AS `RememberToken`,`lolalerter`.`users`.`TwitchAlertsKey` AS `TwitchAlertsKey`,`lolalerter`.`users`.`MinimumDonation` AS `MinimumDonation`,`lolalerter`.`users`.`ShowResubs` AS `ShowResubs`,`lolalerter`.`users`.`LastNotice` AS `LastNotice` from `users` where `lolalerter`.`users`.`ID` in (select `lolalerter`.`subscription_payments`.`User` from `subscription_payments` where (`lolalerter`.`subscription_payments`.`ExpiryDate` > (utc_timestamp() - interval 8 hour))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-09-04  3:00:00
