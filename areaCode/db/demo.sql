/*
 Navicat Premium Data Transfer

 Source Server         : 本地
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : demo

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 06/01/2021 17:08:23
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for area_code
-- ----------------------------
DROP TABLE IF EXISTS `area_code`;
CREATE TABLE `area_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `province_code` varchar(16) DEFAULT NULL COMMENT '省份code',
  `province_name` varchar(255) DEFAULT NULL COMMENT '省份名称',
  `city_code` varchar(16) DEFAULT NULL COMMENT '城市code',
  `city_name` varchar(255) DEFAULT NULL COMMENT '城市名称',
  `county_code` varchar(16) DEFAULT NULL COMMENT '区县code',
  `county_name` varchar(255) DEFAULT NULL COMMENT '区县名称',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `unx_county_code` (`county_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4552 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for area_code_child
-- ----------------------------
DROP TABLE IF EXISTS `area_code_child`;
CREATE TABLE `area_code_child` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` varchar(16) DEFAULT NULL COMMENT '省份code',
  `name` varchar(128) DEFAULT NULL COMMENT '省份名称',
  `p_code` varchar(16) DEFAULT NULL COMMENT '父级code',
  `level` tinyint(2) DEFAULT NULL COMMENT '区域级别',
  `catagory` varchar(8) DEFAULT NULL COMMENT '类别',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `unx_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=362 DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
