-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.32-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for spotify_recommender_database
CREATE DATABASE IF NOT EXISTS `spotify_recommender_database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci */;
USE `spotify_recommender_database`;

-- Dumping structure for table spotify_recommender_database.albums
CREATE TABLE IF NOT EXISTS `albums` (
  `id` varchar(50) NOT NULL,
  `name` varchar(40) NOT NULL,
  `genres` text DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `popularity` smallint(6) DEFAULT NULL,
  `year` smallint(6) DEFAULT NULL,
  `img` text DEFAULT NULL,
  `uri` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Dumping data for table spotify_recommender_database.albums: 0 rows
/*!40000 ALTER TABLE `albums` DISABLE KEYS */;
/*!40000 ALTER TABLE `albums` ENABLE KEYS */;

-- Dumping structure for table spotify_recommender_database.artists
CREATE TABLE IF NOT EXISTS `artists` (
  `id` varchar(50) NOT NULL,
  `name` varchar(40) NOT NULL,
  `genres` text DEFAULT NULL,
  `popularity` smallint(6) DEFAULT NULL,
  `img` text DEFAULT NULL,
  `uri` text DEFAULT NULL,
  `tracks_dumped` tinyint(1) DEFAULT NULL,
  `processed` tinyint(1) unsigned zerofill NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Dumping data for table spotify_recommender_database.artists: 0 rows
/*!40000 ALTER TABLE `artists` DISABLE KEYS */;
/*!40000 ALTER TABLE `artists` ENABLE KEYS */;

-- Dumping structure for table spotify_recommender_database.artists_albums
CREATE TABLE IF NOT EXISTS `artists_albums` (
  `artist_id` varchar(50) NOT NULL,
  `album_id` varchar(50) NOT NULL,
  KEY `FK_artists_albums_artists` (`artist_id`),
  KEY `FK_artists_albums_albums` (`album_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Dumping data for table spotify_recommender_database.artists_albums: 0 rows
/*!40000 ALTER TABLE `artists_albums` DISABLE KEYS */;
/*!40000 ALTER TABLE `artists_albums` ENABLE KEYS */;

-- Dumping structure for table spotify_recommender_database.artists_tracks
CREATE TABLE IF NOT EXISTS `artists_tracks` (
  `artist_id` varchar(50) NOT NULL,
  `track_id` varchar(50) NOT NULL,
  KEY `FK_artists_tracks_artists` (`artist_id`),
  KEY `FK_artists_tracks_tracks` (`track_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Dumping data for table spotify_recommender_database.artists_tracks: 0 rows
/*!40000 ALTER TABLE `artists_tracks` DISABLE KEYS */;
/*!40000 ALTER TABLE `artists_tracks` ENABLE KEYS */;

-- Dumping structure for table spotify_recommender_database.tracks
CREATE TABLE IF NOT EXISTS `tracks` (
  `id` varchar(50) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `explicit` tinyint(1) DEFAULT NULL,
  `uri` text DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `KEY` int(11) DEFAULT NULL,
  `mode` int(11) DEFAULT NULL,
  `time_signature` int(11) DEFAULT NULL,
  `acousticness` decimal(10,0) DEFAULT NULL,
  `danceability` decimal(10,0) DEFAULT NULL,
  `energy` decimal(10,0) DEFAULT NULL,
  `instrumentalness` decimal(10,0) DEFAULT NULL,
  `liveness` decimal(10,0) DEFAULT NULL,
  `loudness` decimal(10,0) DEFAULT NULL,
  `speechiness` decimal(10,0) DEFAULT NULL,
  `valence` decimal(10,0) DEFAULT NULL,
  `tempo` decimal(10,0) DEFAULT NULL,
  `album_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_tracks_albums` (`album_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- Dumping data for table spotify_recommender_database.tracks: 0 rows
/*!40000 ALTER TABLE `tracks` DISABLE KEYS */;
/*!40000 ALTER TABLE `tracks` ENABLE KEYS */;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
