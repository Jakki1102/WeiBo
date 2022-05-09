/*
 Navicat MySQL Data Transfer

 Source Server         : Mysql
 Source Server Type    : MySQL
 Source Server Version : 80020
 Source Host           : localhost:3306
 Source Schema         : weibo

 Target Server Type    : MySQL
 Target Server Version : 80020
 File Encoding         : 65001

 Date: 12/06/2020 14:06:41
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tb_avg_sentiment
-- ----------------------------
DROP TABLE IF EXISTS `tb_avg_sentiment`;
CREATE TABLE `tb_avg_sentiment`  (
  `weibo_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sentiment` int(0) NULL DEFAULT NULL,
  `time` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`weibo_id`) USING BTREE,
  UNIQUE INDEX `weibo_id`(`weibo_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tb_comment
-- ----------------------------
DROP TABLE IF EXISTS `tb_comment`;
CREATE TABLE `tb_comment`  (
  `comment_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '评论唯一标识',
  `weibo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '评论的微博id',
  `time` datetime(0) NULL DEFAULT NULL COMMENT '评论时间',
  `content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '评论内容',
  `sentiment` int(0) NULL DEFAULT NULL COMMENT '情感值',
  `like_num` int(0) NULL DEFAULT NULL COMMENT '点赞数',
  PRIMARY KEY (`comment_id`) USING BTREE,
  INDEX `weibo_id`(`weibo_id`) USING BTREE,
  CONSTRAINT `tb_comment_ibfk_1` FOREIGN KEY (`weibo_id`) REFERENCES `tb_weibo` (`weibo_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tb_user
-- ----------------------------
DROP TABLE IF EXISTS `tb_user`;
CREATE TABLE `tb_user`  (
  `user_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户唯一标识',
  `user_home_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户主页地址',
  `nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户昵称',
  `location` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户所在地',
  `gender` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户性别',
  `birthday` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户生日',
  `introduction` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户简介',
  `register_time` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户注册时间',
  `followers_num` int(0) NULL DEFAULT NULL COMMENT '用户关注数',
  `fans_num` int(0) NULL DEFAULT NULL COMMENT '用户粉丝数',
  `weibo_num` int(0) NULL DEFAULT NULL COMMENT '用户微博数',
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tb_weibo
-- ----------------------------
DROP TABLE IF EXISTS `tb_weibo`;
CREATE TABLE `tb_weibo`  (
  `weibo_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '微博唯一标识',
  `user_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '发布该微博的用户id',
  `weibo_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '微博详情页地址',
  `time` datetime(0) NULL DEFAULT NULL COMMENT '微博发布时间',
  `content` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '微博正文',
  `sentiment` int(0) NULL DEFAULT NULL COMMENT '情感值',
  `image` varchar(1500) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '微博图片链接',
  `video` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '微博视频链接',
  `repost_num` int(0) NULL DEFAULT NULL COMMENT '微博转发数',
  `comment_num` int(0) NULL DEFAULT NULL COMMENT '微博评论数',
  `like_num` int(0) NULL DEFAULT NULL COMMENT '微博点赞数',
  PRIMARY KEY (`weibo_id`) USING BTREE,
  UNIQUE INDEX `weibo_id`(`weibo_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `time`(`time`) USING BTREE,
  FULLTEXT INDEX `content`(`content`),
  CONSTRAINT `tb_weibo_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tb_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
