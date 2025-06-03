-- 确保 Task 状态为 full，CurrentBidder 为空
UPDATE Task SET Status='full', CurrentBidder='' WHERE TaskID=1001;

-- 确保 BidDeadline 在未来
UPDATE Task SET BidDeadline=DATE_ADD(NOW(), INTERVAL 7 DAY) WHERE TaskID=1001;

-- 确保 TaskParticipant 有5条 active 记录
-- （如有必要，先删除原有的 TaskID=1001 记录再插入）
DELETE FROM TaskParticipant WHERE TaskID=1001;
INSERT INTO TaskParticipant (UserID, TaskID, JoinTime, Status) VALUES
(1748397795518788, 1001, NOW(), 'active'),
(1748398096150898, 1001, NOW(), 'active'),
(1748398135816773, 1001, NOW(), 'active'),
(1748398456508245, 1001, NOW(), 'active'),
(1748434864506324, 1001, NOW(), 'active');