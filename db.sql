/*
 Navicat Premium Data Transfer

 Source Server         : backend_db
 Source Server Type    : MariaDB
 Source Server Version : 100237
 Source Host           : 192.180.0.61:3306
 Source Schema         : base

 Target Server Type    : MariaDB
 Target Server Version : 100237
 File Encoding         : 65001

 Date: 16/07/2022 22:08:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id`            int(11) NOT NULL AUTO_INCREMENT,
  `create_time`   datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Created at',
  `update_time`   datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Updated at',
  `username`      varchar(25) DEFAULT NULL,
  `user_type`     tinyint(1) NOT NULL DEFAULT '0' COMMENT 'True:SuperAdmin False:Admin',
  `password`      varchar(255) DEFAULT NULL,
  `nickname`      varchar(255) NOT NULL DEFAULT 'dgos',
  `user_phone`    varchar(15) DEFAULT NULL COMMENT 'phone number',
  `user_email`    varchar(255) DEFAULT NULL COMMENT 'Mail',
  `full_name`     varchar(255) DEFAULT NULL COMMENT 'Name',
  `user_status`   int(11) NOT NULL DEFAULT '2' COMMENT '0 No activation 1 Normal 2 Disable',
  `header_img`    varchar(255) DEFAULT NULL COMMENT 'avatar',
  `sex`           int(11) DEFAULT '0' COMMENT '0 Unknown 1 Men and 2 Women',
  `remarks`       varchar(30) DEFAULT NULL COMMENT 'Remark',
  `client_host`   varchar(19) DEFAULT NULL COMMENT 'Access IP',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='user table';
--
-- Dumping data for table `user`
--
BEGIN;
INSERT INTO `user` (`id`, `create_time`, `update_time`, `username`, `user_type`, `password`, `nickname`, `user_phone`, `user_email`, `full_name`, `user_status`, `header_img`, `sex`, `remarks`, `client_host`) VALUES
(1, '2022-05-18 18:25:56.776176', '2022-07-16 09:36:46.742337', 'root', 1, '$pbkdf2-sha256$29000$f88ZgzDGeC8lJGSM0RpjzA$ZEKDz34TzG0b5Qhd1o1IS6rc63xj1rQV2/T1kohGw/0', 'dgosroot', '19391008993', 'dev@dgos.id', NULL, 1, '/upload/photo/favicon.ico', 0, 'string', NULL);
COMMIT;

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) COMMENT 'Creation time',
  `update_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6) COMMENT 'Update time',
  `role_name` varchar(25) NOT NULL COMMENT 'Role Name',
  `role_status` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'True: Enable False: Disable',
  `role_desc` varchar(255) DEFAULT NULL COMMENT 'Character description',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Character table';

-- ----------------------------
-- Records of role
-- ----------------------------


-- ----------------------------
-- Table structure for access
-- ----------------------------
DROP TABLE IF EXISTS `access`;
CREATE TABLE `access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) COMMENT 'Creation time',
  `update_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6) COMMENT 'Update time',
  `access_name` varchar(25) NOT NULL COMMENT 'Permission name',
  `parent_id` int(11) NOT NULL DEFAULT 0 COMMENT 'Parent ID',
  `scopes` varchar(255) NOT NULL COMMENT 'Permanent scope identification',
  `access_desc` varchar(255) DEFAULT NULL COMMENT 'Permissions description',
  `menu_icon` varchar(255) DEFAULT NULL COMMENT 'Menu icon',
  `is_check` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Whether to verify the permissions TRUE to verify that FALSE does not verify',
  `is_menu` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Whether it is the menu TRUE menu FALSE is not the menu',
  PRIMARY KEY (`id`),
  UNIQUE KEY `scopes` (`scopes`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COMMENT='Permissions table';

-- ----------------------------
-- Records of access
-- ----------------------------
BEGIN;
INSERT INTO `access` VALUES (1, '2022-05-18 18:28:15.699736', '2022-05-18 18:28:15.699771', 'All Access', 0, 'all', NULL, NULL, 1, 0);
INSERT INTO `access` VALUES (2, '2022-05-18 18:28:55.162023', '2022-05-18 18:28:55.162070', 'User Management', 1, 'user_m', NULL, NULL, 0, 1);
INSERT INTO `access` VALUES (3, '2022-05-18 18:32:45.768538', '2022-05-19 07:27:43.328990', 'User query', 2, 'user_query', NULL, NULL, 1, 0);
INSERT INTO `access` VALUES (4, '2022-05-18 18:33:05.634450', '2022-05-18 18:33:05.634498', 'User add', 2, 'user_add', NULL, NULL, 1, 0);
INSERT INTO `access` VALUES (5, '2022-05-18 18:33:35.677990', '2022-05-18 18:33:35.678038', 'User editor', 2, 'user_update', NULL, NULL, 1, 0);
INSERT INTO `access` VALUES (6, '2022-05-18 18:33:53.455916', '2022-05-18 18:33:53.455964', 'User delete', 2, 'user_delete', NULL, NULL, 1, 0);
COMMIT;
-- ----------------------------
-- Table structure for access_log
-- ----------------------------
DROP TABLE IF EXISTS `access_log`;
CREATE TABLE `access_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) COMMENT 'Creation time',
  `update_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6) COMMENT 'Update time',
  `user_id` int(11) NOT NULL COMMENT 'User ID',
  `target_url` varchar(255) DEFAULT NULL COMMENT 'Access URL',
  `user_agent` varchar(255) DEFAULT NULL COMMENT 'Visit UA',
  `request_params` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Request parameter get|post',
  `ip` varchar(32) DEFAULT NULL COMMENT 'Access IP',
  `note` varchar(255) DEFAULT NULL COMMENT 'Remark',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User operation record table';

-- ----------------------------
-- Records of access_log
-- ----------------------------

-- ----------------------------
-- Table structure for system_params
-- ----------------------------
DROP TABLE IF EXISTS `system_params`;
CREATE TABLE `system_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) COMMENT 'Creation time',
  `update_time` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6) COMMENT 'Update time',
  `params_name` varchar(255) NOT NULL COMMENT 'parameter name',
  `params` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'parameter',
  PRIMARY KEY (`id`),
  UNIQUE KEY `params_name` (`params_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='System parameter table';

-- ----------------------------
-- Records of system_params
-- ----------------------------
BEGIN;
INSERT INTO `system_params` VALUES (1, '2022-06-04 18:03:00.648479', '2022-07-16 14:07:37.491553', 'wechat_auth', '{\"appid\":\"1\",\"secret\":\"1\",\"redirect_uri\":\"http://fastapi.binkuolo.com/api/v1/wechat/auth/call\",\"expire\":1}');
INSERT INTO `system_params` VALUES (2, '2022-06-07 21:42:48.946171', '2022-07-16 14:07:45.691333', 'tencent_sms', '{\"secret_id\":\"1\",\"secret_key\":\"1\",\"region\":\"ap-guangzhou\",\"app_id\":\"1400440642\",\"sign\":\"贵州红帽网络\",\"template_id\":\"757896\",\"expire\":10}');
INSERT INTO `system_params` VALUES (3, '2022-07-08 17:56:05.098642', '2022-07-16 14:07:54.795525', 'tencent_cos', '{\"duration_seconds\":1800,\"secret_id\":\"1\",\"secret_key\":\"1\",\"region\":\"ap-chongqing\"}');
COMMIT;
-- ==========================================================================


--
-- Table structure for table `tugas`
--
DROP TABLE IF EXISTS `tugas`;
CREATE TABLE `tugas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Created at',
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Updated at',
  `name` varchar(255) DEFAULT NULL,
  `start` datetime,
  `end` datetime,
  `progress` int(11),
  `tipe` varchar(255) DEFAULT NULL,
  `project` varchar(255) DEFAULT NULL,
  `dependencies` varchar(255) DEFAULT NULL,
  `hidechildren` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='tugas table';


--
-- Table structure for table `tugas`
--
DROP TABLE IF EXISTS `heat_map`;
CREATE TABLE `heat_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `d` varchar(500) DEFAULT NULL,
  `floor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='heat_map table';


--
-- Table structure for table `tugas`
--
DROP TABLE IF EXISTS `rack_server`;
CREATE TABLE `rack_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Created at',
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Updated at',
  `name` varchar(255) DEFAULT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `depth` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `z` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='rack_server table';

--
-- Table structure for table `tugas`
--
DROP TABLE IF EXISTS `workfloweditor`;
CREATE TABLE `workfloweditor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Created at',
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Updated at',
  `name` varchar(255) DEFAULT NULL,
  `nodesjson` json DEFAULT NULL,
  `edgesjson` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='workfloweditor table';


--
-- Table structure for table `tugas`
--
DROP TABLE IF EXISTS `homeassistant`;
CREATE TABLE `homeassistant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Created at',
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Updated at',
  `datachart` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='homeassistant table';

