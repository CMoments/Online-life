-- 创建新的Reputation表
CREATE TABLE `Reputation_New` (
    `ReputationID` BIGINT NOT NULL AUTO_INCREMENT,
    `Score` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
    `Review` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
    `RUserID` decimal(20,0) NOT NULL,
    `UserID` decimal(20,0) NOT NULL,
    `OrderID` decimal(20,0),
    `ReviewTime` varchar(30) COLLATE utf8mb4_general_ci DEFAULT '',
    PRIMARY KEY (`ReputationID`),
    UNIQUE KEY `idx_user_order` (`RUserID`, `OrderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 迁移现有数据到新表
INSERT INTO `Reputation_New` (`Score`, `Review`, `RUserID`, `UserID`, `OrderID`, `ReviewTime`)
SELECT `Score`, `Review`, `RUserID`, `UserID`, `OrderID`, `ReviewTime`
FROM `Reputation`;

-- 备份原表（以防万一）
RENAME TABLE `Reputation` TO `Reputation_Backup`;

-- 将新表重命名为正式表
RENAME TABLE `Reputation_New` TO `Reputation`; 