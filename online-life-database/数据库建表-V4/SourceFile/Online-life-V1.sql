/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2025-05-22 20:10:34                          */
/*==============================================================*/


drop table if exists BidRecord;

drop table if exists Client;

drop table if exists GroupTask;

drop table if exists "Order";

drop table if exists Reputation;

drop table if exists Staff;

drop table if exists Task;

drop table if exists User;

drop table if exists 团办事宜与用户;

/*==============================================================*/
/* Table: BidRecord                                             */
/*==============================================================*/
create table BidRecord
(
   UserID               numeric(20,0) not null,
   TaskID               numeric(20,0) not null,
   BidID                numeric(20,0) not null,
   BidTime              varchar(30) not null,
   BidStatus            varchar(30) not null,
   primary key (UserID, TaskID)
);

/*==============================================================*/
/* Table: Client                                                */
/*==============================================================*/
create table Client
(
   UserID               numeric(20,0) not null,
   Username             varchar(30) not null,
   Password             varchar(30) not null,
   Email                varchar(30) not null,
   Phone                varchar(30) not null,
   Address              varchar(30) not null,
   Role                 varchar(30) not null,
   Points               varchar(30) not null,
   ClientID             numeric(20,0) not null,
   primary key (UserID)
);

/*==============================================================*/
/* Table: GroupTask                                             */
/*==============================================================*/
create table GroupTask
(
   GroupTaskID          numeric(20,0) not null,
   TaskID               numeric(20,0) not null,
   ParticipatingUserID  varchar(30) not null,
   JoinTime             varchar(30) not null,
   endTime              varchar(30) not null,
   primary key (GroupTaskID)
);

/*==============================================================*/
/* Table: "Order"                                               */
/*==============================================================*/
create table "Order"
(
   OrderType            varchar(30) not null,
   OrderStatus          varchar(30) not null,
   CreationTime         varchar(30) not null,
   CompletionTime       varchar(30) not null,
   AssignmentType       varchar(30) not null,
   AssignmentStatus     varchar(30) not null,
   OUserID              numeric(20,0) not null,
   UserID               numeric(20,0) not null,
   primary key (OUserID)
);

/*==============================================================*/
/* Table: Reputation                                            */
/*==============================================================*/
create table Reputation
(
   Score                varchar(30) not null,
   Review               varchar(30) not null,
   RUserID              numeric(20,0) not null,
   UserID               numeric(20,0) not null,
   primary key (RUserID)
);

/*==============================================================*/
/* Table: Staff                                                 */
/*==============================================================*/
create table Staff
(
   UserID               numeric(20,0) not null,
   Username             varchar(30) not null,
   Password             varchar(30) not null,
   Email                varchar(30) not null,
   Phone                varchar(30) not null,
   Address              varchar(30) not null,
   Role                 varchar(30) not null,
   Points               varchar(30) not null,
   StaffID              numeric(20,0) not null,
   Salary               varchar(30) not null,
   primary key (UserID)
);

/*==============================================================*/
/* Table: Task                                                  */
/*==============================================================*/
create table Task
(
   TaskID               numeric(20,0) not null,
   TaskType             varchar(30) not null,
   Description          varchar(30) not null,
   EstimatedTime        varchar(30) not null,
   ActualTime           varchar(30) not null,
   CurrentBidder        varchar(30) not null,
   BidDeadline          varchar(30) not null,
   primary key (TaskID)
);

/*==============================================================*/
/* Table: User                                                  */
/*==============================================================*/
create table User
(
   UserID               numeric(20,0) not null,
   Username             varchar(30) not null,
   Password             varchar(30) not null,
   Email                varchar(30) not null,
   Phone                varchar(30) not null,
   Address              varchar(30) not null,
   Role                 varchar(30) not null,
   Points               varchar(30) not null,
   primary key (UserID)
);

/*==============================================================*/
/* Table: 团办事宜与用户                                               */
/*==============================================================*/
create table 团办事宜与用户
(
   UserID               numeric(20,0) not null,
   GroupTaskID          numeric(20,0) not null,
   primary key (UserID, GroupTaskID)
);

alter table 团办事宜与用户 comment '一个团办事宜可以由多个用户参与
一个用户可以参与多个团办事宜';

alter table BidRecord add constraint FK_BidRecord foreign key (TaskID)
      references Task (TaskID) on delete restrict on update restrict;

alter table BidRecord add constraint FK_BidRecord2 foreign key (UserID)
      references Staff (UserID) on delete restrict on update restrict;

alter table Client add constraint FK_客户继承 foreign key (UserID)
      references User (UserID) on delete restrict on update restrict;

alter table GroupTask add constraint FK_团办事宜与事务 foreign key (TaskID)
      references Task (TaskID) on delete restrict on update restrict;

alter table "Order" add constraint FK_用户与订单 foreign key (UserID)
      references Client (UserID) on delete restrict on update restrict;

alter table Reputation add constraint FK_用户与信誉 foreign key (UserID)
      references User (UserID) on delete restrict on update restrict;

alter table Staff add constraint FK_职工继承 foreign key (UserID)
      references User (UserID) on delete restrict on update restrict;

alter table 团办事宜与用户 add constraint FK_团办事宜与用户 foreign key (UserID)
      references Client (UserID) on delete restrict on update restrict;

alter table 团办事宜与用户 add constraint FK_团办事宜与用户2 foreign key (GroupTaskID)
      references GroupTask (GroupTaskID) on delete restrict on update restrict;

