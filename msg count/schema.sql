DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` bigint(18) NOT NULL,
  `xp` int(11) NOT NULL,
  `lvl` int(11) NOT NULL,
  `msg` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
