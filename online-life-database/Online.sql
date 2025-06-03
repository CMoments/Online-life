/*
 Navicat Premium Data Transfer

 Source Server         : RemoteDatabase
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42-0ubuntu0.24.04.1)
 Source Host           : 39.104.19.8:3306
 Source Schema         : Online

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42-0ubuntu0.24.04.1)
 File Encoding         : 65001

 Date: 03/06/2025 10:55:27
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for Admin
-- ----------------------------
DROP TABLE IF EXISTS `Admin`;
CREATE TABLE `Admin`  (
  `UserID` decimal(20, 0) NOT NULL,
  `Username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `JoinDate` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Adlevel` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`) USING BTREE,
  CONSTRAINT `fk_admin_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Admin
-- ----------------------------
INSERT INTO `Admin` VALUES (1748396885664874, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', '2319317481@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'admin', '2025-05-28 09:48:05', '1');

-- ----------------------------
-- Table structure for BidRecord
-- ----------------------------
DROP TABLE IF EXISTS `BidRecord`;
CREATE TABLE `BidRecord`  (
  `UserID` decimal(20, 0) NOT NULL,
  `TaskID` decimal(20, 0) NOT NULL,
  `BidID` decimal(20, 0) NULL DEFAULT NULL,
  `BidTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `BidStatus` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`, `TaskID`) USING BTREE,
  INDEX `fk_bidrecord_task`(`TaskID` ASC) USING BTREE,
  CONSTRAINT `fk_bidrecord_task` FOREIGN KEY (`TaskID`) REFERENCES `Task` (`TaskID`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_bidrecord_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of BidRecord
-- ----------------------------
INSERT INTO `BidRecord` VALUES (1748396903672505, 1001, 4, '2025-06-02 16:52:48', 'rejected');
INSERT INTO `BidRecord` VALUES (1748498150567521, 1001, 2, '2025-06-02 16:52:11', 'accepted');
INSERT INTO `BidRecord` VALUES (1748500567870200, 1001, 3, '2025-06-02 16:52:23', 'rejected');
INSERT INTO `BidRecord` VALUES (1748500568191351, 1001, 1, '2025-06-02 16:51:51', 'rejected');
INSERT INTO `BidRecord` VALUES (1748500568513115, 1001, 5, '2025-06-02 16:53:03', 'rejected');

-- ----------------------------
-- Table structure for Client
-- ----------------------------
DROP TABLE IF EXISTS `Client`;
CREATE TABLE `Client`  (
  `UserID` decimal(20, 0) NOT NULL,
  `Username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ClientID` decimal(20, 0) NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`) USING BTREE,
  CONSTRAINT `fk_client_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Client
-- ----------------------------
INSERT INTO `Client` VALUES (1748395817847071, 'client', '948fe603f61dc036b5c596dc09fe3ce3f3d30dc90f024c85f3c82db2ccab679d', '2319317070@qq.com', '18935139706', '四川省成都市四川大学江安区7舍', 'client', 1748395817847071);
INSERT INTO `Client` VALUES (1748397795518788, 'client1', '1917e33407c28366c8e3b975b17e7374589312676b90229adb4ce6e58552e223', '2319317581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client', 1748397795518788);
INSERT INTO `Client` VALUES (1748398096150898, 'client2', '3f455143e75d1e7fd659dea57023496da3bd9f2f8908d1e2ac32641cd819d3e3', '2319357581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client', 1748398096150898);
INSERT INTO `Client` VALUES (1748398135816773, 'client3', 'e8648df64a518b6eda18c1c77a7ed76326308dc41cbbd79fc7827d4be46b1a39', '2319367581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client', 1748398135816773);
INSERT INTO `Client` VALUES (1748398456508245, 'client4', '9b4335c9f0711919a2224879b3672f479483ce5828d88331271533136a6bcfa0', '2319365581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client', 1748398456508245);
INSERT INTO `Client` VALUES (1748434864506324, 'testclient', '846488f1dc5c07b4cebe5c14e0814b7b14f958f962c39ee7e5e5282c4b1e9474', 'client@example.com', '9876543210', '四川大学江安校区小西南门', 'client', 1748434864506324);

-- ----------------------------
-- Table structure for GroupTask
-- ----------------------------
DROP TABLE IF EXISTS `GroupTask`;
CREATE TABLE `GroupTask`  (
  `GroupTaskID` decimal(20, 0) NOT NULL,
  `TaskID` decimal(20, 0) NULL DEFAULT NULL,
  `ParticipatingUserID` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `JoinTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `endTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`GroupTaskID`) USING BTREE,
  INDEX `fk_grouptask_task`(`TaskID` ASC) USING BTREE,
  CONSTRAINT `fk_grouptask_task` FOREIGN KEY (`TaskID`) REFERENCES `Task` (`TaskID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of GroupTask
-- ----------------------------
INSERT INTO `GroupTask` VALUES (1001, NULL, NULL, '2025-06-02 16:06:33', '');
INSERT INTO `GroupTask` VALUES (1002, NULL, NULL, '2025-06-02 21:36:25', '');

-- ----------------------------
-- Table structure for GroupTaskUser
-- ----------------------------
DROP TABLE IF EXISTS `GroupTaskUser`;
CREATE TABLE `GroupTaskUser`  (
  `UserID` decimal(20, 0) NOT NULL,
  `TaskID` decimal(20, 0) NOT NULL,
  `GroupTaskID` decimal(20, 0) NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`, `TaskID`) USING BTREE,
  INDEX `fk_groupuser_taskid`(`TaskID` ASC) USING BTREE,
  CONSTRAINT `fk_groupuser_taskid` FOREIGN KEY (`TaskID`) REFERENCES `Task` (`TaskID`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_groupuser_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '团队任务用户关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of GroupTaskUser
-- ----------------------------
INSERT INTO `GroupTaskUser` VALUES (1748434864506324, 1002, 1002);

-- ----------------------------
-- Table structure for Orders
-- ----------------------------
DROP TABLE IF EXISTS `Orders`;
CREATE TABLE `Orders`  (
  `OrderType` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `OrderStatus` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `CreationTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `CompletionTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `EstimatedTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `AssignmentType` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `AssignmentStatus` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `OrderID` decimal(20, 0) NOT NULL,
  `ClientID` decimal(20, 0) NULL DEFAULT NULL,
  `StaffID` decimal(20, 0) NULL DEFAULT NULL,
  `OrderLocation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Amount` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ShopAddress` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '商家地址',
  PRIMARY KEY (`OrderID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Orders
-- ----------------------------
INSERT INTO `Orders` VALUES ('immediate', 'paid', '2025-06-02 19:15:48', '2025-06-02 22:04:08', '4378', 'direct', 'closed', 1748862948838502, 1748434864506324, 1748396903672505, '四川大学望江校区', '10.8', '四川大学江安校区');
INSERT INTO `Orders` VALUES ('immediate', 'paid', '2025-06-02 19:16:31', '2025-06-02 21:48:45', '84346', 'direct', 'closed', 1748862991590957, 1748434864506324, 1748396903672505, '四川省人民政府', '210.75', '重庆市人民政府');
INSERT INTO `Orders` VALUES ('immediate', 'paid', '2025-06-02 22:00:15', '2025-06-02 22:01:08', '4319', 'direct', 'closed', 1748872815344639, 1748434864506324, 1748396903672505, '四川大学华西校区', '10.65', '四川大学江安校区');
INSERT INTO `Orders` VALUES ('immediate', 'completed', '2025-06-02 23:37:16', '2025-06-02 23:37:54', '3544', 'direct', 'closed', 1748878636508104, 1748434864506324, 1748396903672505, '山西省太原市知达常青藤中学', '8.85', '山西大学附属中学');
INSERT INTO `Orders` VALUES ('immediate', 'pending', '2025-06-02 23:50:57', '', '3739', 'direct', 'open', 1748879457063497, 1748434864506324, NULL, '山西省太原市东龙壹湾', '9.3', '山西省太原市开元南小区');
INSERT INTO `Orders` VALUES ('immediate', 'pending', '2025-06-02 23:53:25', '', '1911', 'direct', 'open', 1748879605528238, 1748434864506324, NULL, '山西大学附属中学', '4.65', '山西大学');

-- ----------------------------
-- Table structure for Points
-- ----------------------------
DROP TABLE IF EXISTS `Points`;
CREATE TABLE `Points`  (
  `UserID` decimal(20, 0) NOT NULL,
  `Points` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`) USING BTREE,
  CONSTRAINT `fk_points_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Points
-- ----------------------------
INSERT INTO `Points` VALUES (1748395817847071, '666666');
INSERT INTO `Points` VALUES (1748398096150898, '601');
INSERT INTO `Points` VALUES (1748434864506324, '1647');
INSERT INTO `Points` VALUES (1748498150567521, '2');

-- ----------------------------
-- Table structure for Reputation
-- ----------------------------
DROP TABLE IF EXISTS `Reputation`;
CREATE TABLE `Reputation`  (
  `ReputationID` bigint NOT NULL AUTO_INCREMENT,
  `Score` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Review` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `RUserID` decimal(20, 0) NOT NULL,
  `UserID` decimal(20, 0) NOT NULL,
  `OrderID` decimal(20, 0) NULL DEFAULT NULL,
  `ReviewTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '',
  PRIMARY KEY (`ReputationID`) USING BTREE,
  UNIQUE INDEX `idx_user_order`(`RUserID` ASC, `OrderID` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Reputation
-- ----------------------------
INSERT INTO `Reputation` VALUES (1, '90', NULL, 1748398456508245, 1748498150567521, NULL, NULL);
INSERT INTO `Reputation` VALUES (2, '80', 'a', 1748434864506324, 1748396903672505, 1748862948838502, '2025-06-02 22:41:39');
INSERT INTO `Reputation` VALUES (3, '100', NULL, 1748498150567521, 1748398456508245, NULL, NULL);
INSERT INTO `Reputation` VALUES (4, '80', 'a', 1748434864506324, 1748396903672505, 1748872815344639, '2025-06-02 23:27:32.298184');

-- ----------------------------
-- Table structure for Reputation_Backup
-- ----------------------------
DROP TABLE IF EXISTS `Reputation_Backup`;
CREATE TABLE `Reputation_Backup`  (
  `Score` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Review` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `RUserID` decimal(20, 0) NOT NULL,
  `UserID` decimal(20, 0) NULL DEFAULT NULL,
  `OrderID` decimal(20, 0) NULL DEFAULT NULL,
  `ReviewTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`RUserID`) USING BTREE,
  CONSTRAINT `fk_reputation_user` FOREIGN KEY (`RUserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Reputation_Backup
-- ----------------------------
INSERT INTO `Reputation_Backup` VALUES ('90', NULL, 1748398456508245, 1748498150567521, NULL, NULL);
INSERT INTO `Reputation_Backup` VALUES ('80', 'a', 1748434864506324, 1748396903672505, 1748862948838502, '2025-06-02 22:41:39');
INSERT INTO `Reputation_Backup` VALUES ('100', NULL, 1748498150567521, 1748398456508245, NULL, NULL);

-- ----------------------------
-- Table structure for Staff
-- ----------------------------
DROP TABLE IF EXISTS `Staff`;
CREATE TABLE `Staff`  (
  `UserID` decimal(20, 0) NOT NULL,
  `Username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `StaffID` decimal(20, 0) NULL DEFAULT NULL,
  `Salary` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`) USING BTREE,
  CONSTRAINT `fk_staff_user` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Staff
-- ----------------------------
INSERT INTO `Staff` VALUES (1748396903672505, 'staff', '1562206543da764123c21bd524674f0a8aaf49c8a89744c97352fe677f7e4006', '2319317581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'staff', 1748396903672505, '0');
INSERT INTO `Staff` VALUES (1748498150567521, 'staff1', '010f4928749bd109657b1b4ef213359ac420678c72932b0d5bc110076afc52f7', 'sfaff1@exapmle.com', '6666666', '四川省成都市双流区川大路一段1号', 'staff', 1748498150567521, '0');
INSERT INTO `Staff` VALUES (1748500567543179, 'staff2', '00bbfdc27068d300bab70e46dc683a9d81355634eff13b1a491b498925b89a57', 'staff2@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff', 1748500567543179, '0');
INSERT INTO `Staff` VALUES (1748500567870200, 'staff3', 'e46d3aad1f8afa436d163dea2a99ee063bd080d62d50042ecd3d36dd75bc5e78', 'staff3@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff', 1748500567870200, '0');
INSERT INTO `Staff` VALUES (1748500568191351, 'staff4', 'ea5be547940bed070ae095bba85ddd3ea191cdf7640bc1c2da2f87a5e247eba3', 'staff4@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff', 1748500568191351, '0');
INSERT INTO `Staff` VALUES (1748500568513115, 'staff5', '7cd8ce71859fec548cfd58d2748316e63a8ea25b4c104c5a66d22a1ad0531e5c', 'staff5@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff', 1748500568513115, '0');

-- ----------------------------
-- Table structure for Task
-- ----------------------------
DROP TABLE IF EXISTS `Task`;
CREATE TABLE `Task`  (
  `TaskID` decimal(20, 0) NOT NULL,
  `TaskType` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `EstimatedTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ActualTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `CurrentBidder` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `BidDeadline` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `GroupTaskID` decimal(20, 0) NULL DEFAULT NULL,
  `TaskLocation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `MaxParticipants` int NULL DEFAULT NULL,
  `Status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`TaskID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Task
-- ----------------------------
INSERT INTO `Task` VALUES (1001, 'group', '造数测试团办任务', '', '', '1748498150567521', '2025-06-09 16:37:12', 1001, '测试地点', 5, 'assigned');
INSERT INTO `Task` VALUES (1002, 'group', '送外卖', '', '', '', '', 1002, '四川大学江安校区', 5, 'recruiting');

-- ----------------------------
-- Table structure for TaskParticipant
-- ----------------------------
DROP TABLE IF EXISTS `TaskParticipant`;
CREATE TABLE `TaskParticipant`  (
  `UserID` decimal(20, 0) NOT NULL,
  `TaskID` decimal(20, 0) NOT NULL,
  `JoinTime` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `Status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`, `TaskID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of TaskParticipant
-- ----------------------------
INSERT INTO `TaskParticipant` VALUES (1748397795518788, 1001, '2025-06-02 16:37:12', 'active');
INSERT INTO `TaskParticipant` VALUES (1748398096150898, 1001, '2025-06-02 16:37:12', 'active');
INSERT INTO `TaskParticipant` VALUES (1748398135816773, 1001, '2025-06-02 16:37:12', 'active');
INSERT INTO `TaskParticipant` VALUES (1748398456508245, 1001, '2025-06-02 16:37:12', 'active');
INSERT INTO `TaskParticipant` VALUES (1748434864506324, 1001, '2025-06-02 16:37:12', 'active');
INSERT INTO `TaskParticipant` VALUES (1748434864506324, 1002, '2025-06-02 21:36:25', 'active');

-- ----------------------------
-- Table structure for User
-- ----------------------------
DROP TABLE IF EXISTS `User`;
CREATE TABLE `User`  (
  `UserID` decimal(20, 0) NOT NULL,
  `Username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `Role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`UserID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of User
-- ----------------------------
INSERT INTO `User` VALUES (1748395817847071, 'client', '948fe603f61dc036b5c596dc09fe3ce3f3d30dc90f024c85f3c82db2ccab679d', '2319317070@qq.com', '18935139706', '四川省成都市四川大学江安区7舍', 'client');
INSERT INTO `User` VALUES (1748396885664874, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', '2319317481@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'admin');
INSERT INTO `User` VALUES (1748396903672505, 'staff', '1562206543da764123c21bd524674f0a8aaf49c8a89744c97352fe677f7e4006', '2319317080@qq.com', 'fd23432', '23432', 'staff');
INSERT INTO `User` VALUES (1748397795518788, 'client1', '1917e33407c28366c8e3b975b17e7374589312676b90229adb4ce6e58552e223', '123@example.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client');
INSERT INTO `User` VALUES (1748398096150898, 'client2', '3f455143e75d1e7fd659dea57023496da3bd9f2f8908d1e2ac32641cd819d3e3', '2319357581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client');
INSERT INTO `User` VALUES (1748398135816773, 'client3', 'e8648df64a518b6eda18c1c77a7ed76326308dc41cbbd79fc7827d4be46b1a39', '2319367581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client');
INSERT INTO `User` VALUES (1748398456508245, 'client4', '9b4335c9f0711919a2224879b3672f479483ce5828d88331271533136a6bcfa0', '2319365581@qq.com', '18935139705', '四川省成都市四川大学江安校区7舍', 'client');
INSERT INTO `User` VALUES (1748434864506324, 'testclient', '846488f1dc5c07b4cebe5c14e0814b7b14f958f962c39ee7e5e5282c4b1e9474', '2319317080@qq.com', 'fd23432', '23432', 'client');
INSERT INTO `User` VALUES (1748498150567521, 'staff1', '010f4928749bd109657b1b4ef213359ac420678c72932b0d5bc110076afc52f7', 'sfaff1@exapmle.com', '6666666', '四川省成都市双流区川大路一段1号', 'staff');
INSERT INTO `User` VALUES (1748500567543179, 'staff2', '00bbfdc27068d300bab70e46dc683a9d81355634eff13b1a491b498925b89a57', 'staff2@example.com', '242424242', '四川省成都市电子科技大学（沙河校区）', 'staff');
INSERT INTO `User` VALUES (1748500567870200, 'staff3', 'e46d3aad1f8afa436d163dea2a99ee063bd080d62d50042ecd3d36dd75bc5e78', 'staff3@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff');
INSERT INTO `User` VALUES (1748500568191351, 'staff4', 'ea5be547940bed070ae095bba85ddd3ea191cdf7640bc1c2da2f87a5e247eba3', 'staff4@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff');
INSERT INTO `User` VALUES (1748500568513115, 'staff5', '7cd8ce71859fec548cfd58d2748316e63a8ea25b4c104c5a66d22a1ad0531e5c', 'staff5@example.com', '242424242', '四川省成都市电子科技大学（清水河校区）', 'staff');

SET FOREIGN_KEY_CHECKS = 1;
