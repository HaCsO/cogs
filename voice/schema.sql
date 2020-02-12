DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` bigint(20) DEFAULT NULL,
  `voiceTime` bigint(20) DEFAULT NULL,
  `startTime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
