-- MySQL dump 10.13  Distrib 5.7.21, for Linux (x86_64)
--
-- Host: localhost    Database: sfo
-- ------------------------------------------------------
-- Server version	5.7.21-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apscheduler_jobs`
--

DROP TABLE IF EXISTS `apscheduler_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gevent_apscheduler_jobs`
--

DROP TABLE IF EXISTS `gevent_apscheduler_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gevent_apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_gevent_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_account_manager`
--

DROP TABLE IF EXISTS `sfo_account_manager`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_account_manager` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `domain` varchar(128) DEFAULT NULL,
  `project_name` varchar(128) NOT NULL,
  `description` varchar(128) NOT NULL,
  `system_user` varchar(128) NOT NULL,
  `system_passwd` varchar(128) NOT NULL,
  `keystone_user_id` varchar(128) DEFAULT NULL,
  `expire_time` varchar(128) NOT NULL,
  `system_capacity` varchar(128) NOT NULL,
  `system_used` text COMMENT '已使用容量',
  `account_id` varchar(128) NOT NULL,
  `account_stat` varchar(128) NOT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_account_statsd_data`
--

DROP TABLE IF EXISTS `sfo_account_statsd_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_account_statsd_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `reaper_errors` varchar(128) DEFAULT NULL,
  `reaper_timing` text,
  `reaper_return_codes` varchar(128) DEFAULT NULL,
  `reaper_ctn_failures` varchar(128) DEFAULT NULL,
  `reaper_ctn_deleted` varchar(128) DEFAULT NULL,
  `reaper_ctn_remaining` varchar(128) DEFAULT NULL,
  `reaper_ctn_psb_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_failures` varchar(128) DEFAULT NULL,
  `reaper_obj_deleted` varchar(128) DEFAULT NULL,
  `reaper_obj_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_psb_remaining` varchar(128) DEFAULT NULL,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_account_statsd_data_5min`
--

DROP TABLE IF EXISTS `sfo_account_statsd_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_account_statsd_data_5min` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `reaper_errors` varchar(128) DEFAULT NULL,
  `reaper_timing` text,
  `reaper_return_codes` varchar(128) DEFAULT NULL,
  `reaper_ctn_failures` varchar(128) DEFAULT NULL,
  `reaper_ctn_deleted` varchar(128) DEFAULT NULL,
  `reaper_ctn_remaining` varchar(128) DEFAULT NULL,
  `reaper_ctn_psb_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_failures` varchar(128) DEFAULT NULL,
  `reaper_obj_deleted` varchar(128) DEFAULT NULL,
  `reaper_obj_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_psb_remaining` varchar(128) DEFAULT NULL,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_account_statsd_data_day`
--

DROP TABLE IF EXISTS `sfo_account_statsd_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_account_statsd_data_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `reaper_errors` varchar(128) DEFAULT NULL,
  `reaper_timing` text,
  `reaper_return_codes` varchar(128) DEFAULT NULL,
  `reaper_ctn_failures` varchar(128) DEFAULT NULL,
  `reaper_ctn_deleted` varchar(128) DEFAULT NULL,
  `reaper_ctn_remaining` varchar(128) DEFAULT NULL,
  `reaper_ctn_psb_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_failures` varchar(128) DEFAULT NULL,
  `reaper_obj_deleted` varchar(128) DEFAULT NULL,
  `reaper_obj_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_psb_remaining` varchar(128) DEFAULT NULL,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_account_statsd_data_hour`
--

DROP TABLE IF EXISTS `sfo_account_statsd_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_account_statsd_data_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `reaper_errors` varchar(128) DEFAULT NULL,
  `reaper_timing` text,
  `reaper_return_codes` varchar(128) DEFAULT NULL,
  `reaper_ctn_failures` varchar(128) DEFAULT NULL,
  `reaper_ctn_deleted` varchar(128) DEFAULT NULL,
  `reaper_ctn_remaining` varchar(128) DEFAULT NULL,
  `reaper_ctn_psb_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_failures` varchar(128) DEFAULT NULL,
  `reaper_obj_deleted` varchar(128) DEFAULT NULL,
  `reaper_obj_remaining` varchar(128) DEFAULT NULL,
  `reaper_obj_psb_remaining` varchar(128) DEFAULT NULL,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_alarm_log`
--

DROP TABLE IF EXISTS `sfo_alarm_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_alarm_log` (
  `guid` varchar(128) NOT NULL,
  `alarm_device` varchar(128) DEFAULT NULL,
  `alarm_type` varchar(128) DEFAULT NULL,
  `hostname` varchar(128) DEFAULT NULL,
  `device_name` varchar(128) DEFAULT NULL,
  `alarm_message` varchar(128) DEFAULT NULL,
  `alarm_level` varchar(128) DEFAULT NULL,
  `alarm_result` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  `update_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `index_guid` (`guid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_beatheart_info`
--

DROP TABLE IF EXISTS `sfo_beatheart_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_beatheart_info` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `hostname` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_check_report_data`
--

DROP TABLE IF EXISTS `sfo_check_report_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_check_report_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `subject_name` varchar(128) NOT NULL,
  `item_name` varchar(128) NOT NULL,
  `check_command` varchar(1024) DEFAULT NULL,
  `check_result` varchar(128) NOT NULL,
  `check_remark` varchar(1024) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster`
--

DROP TABLE IF EXISTS `sfo_cluster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `creater` varchar(128) NOT NULL,
  `cluster_stat` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  `extend` mediumtext,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  UNIQUE KEY `cluster_name` (`cluster_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_accounts`
--

DROP TABLE IF EXISTS `sfo_cluster_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_accounts` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `account_name` varchar(128) DEFAULT NULL,
  `account_passwd` varchar(128) DEFAULT NULL,
  `system_code` varchar(128) DEFAULT NULL,
  `system_name` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_configure_info`
--

DROP TABLE IF EXISTS `sfo_cluster_configure_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_configure_info` (
  `guid` varchar(128) NOT NULL,
  `config_filename` varchar(128) NOT NULL,
  `config_group` varchar(128) DEFAULT NULL,
  `config_key` varchar(128) DEFAULT NULL,
  `config_value` varchar(1024) DEFAULT NULL,
  `remark` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_disks`
--

DROP TABLE IF EXISTS `sfo_cluster_disks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_disks` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) NOT NULL,
  `host_ip` varchar(128) DEFAULT NULL,
  `disk_name` varchar(128) NOT NULL,
  `label` varchar(128) DEFAULT NULL,
  `system_type` varchar(128) DEFAULT NULL,
  `is_abnormal` varchar(128) DEFAULT NULL,
  `is_used` varchar(128) DEFAULT NULL,
  `is_xfs_format` varchar(128) DEFAULT NULL,
  `is_mount` varchar(128) DEFAULT NULL,
  `mount_params` varchar(128) DEFAULT NULL,
  `mount_on` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_info`
--

DROP TABLE IF EXISTS `sfo_cluster_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_info` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `proxy_num` varchar(128) DEFAULT NULL,
  `storage_num` varchar(128) DEFAULT NULL,
  `disk_num` varchar(128) DEFAULT NULL,
  `capacity_total` varchar(128) DEFAULT NULL,
  `band_width` varchar(128) DEFAULT NULL,
  `cluster_iops` varchar(128) DEFAULT NULL,
  `account_num` varchar(128) DEFAULT NULL,
  `container_num` varchar(128) DEFAULT NULL,
  `object_num` varchar(128) DEFAULT NULL,
  `uri_total` varchar(128) DEFAULT NULL,
  `uri_success_num` varchar(128) DEFAULT NULL,
  `uri_fail_num` varchar(128) DEFAULT NULL,
  `uri_response_time` varchar(256) DEFAULT NULL,
  `auditor_queue` varchar(1024) DEFAULT NULL,
  `replicate_num` varchar(1024) DEFAULT NULL,
  `update_num` varchar(1024) DEFAULT NULL,
  `sync_num` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_info_day`
--

DROP TABLE IF EXISTS `sfo_cluster_info_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_info_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `proxy_num` varchar(128) DEFAULT NULL,
  `storage_num` varchar(256) DEFAULT NULL,
  `disk_num` varchar(128) DEFAULT NULL,
  `capacity_total` varchar(128) DEFAULT NULL,
  `band_width` varchar(128) DEFAULT NULL,
  `cluster_iops` varchar(128) DEFAULT NULL,
  `account_num` varchar(128) DEFAULT NULL,
  `container_num` varchar(128) DEFAULT NULL,
  `object_num` varchar(128) DEFAULT NULL,
  `uri_total` varchar(128) DEFAULT NULL,
  `uri_success_num` varchar(128) DEFAULT NULL,
  `uri_fail_num` varchar(128) DEFAULT NULL,
  `uri_response_time` varchar(256) DEFAULT NULL,
  `auditor_queue` varchar(1024) DEFAULT NULL,
  `replicate_num` varchar(1024) DEFAULT NULL,
  `update_num` varchar(1024) DEFAULT NULL,
  `sync_num` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_info_hour`
--

DROP TABLE IF EXISTS `sfo_cluster_info_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_info_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `proxy_num` varchar(128) DEFAULT NULL,
  `storage_num` varchar(256) DEFAULT NULL,
  `disk_num` varchar(128) DEFAULT NULL,
  `capacity_total` varchar(128) DEFAULT NULL,
  `band_width` varchar(128) DEFAULT NULL,
  `cluster_iops` varchar(128) DEFAULT NULL,
  `account_num` varchar(128) DEFAULT NULL,
  `container_num` varchar(128) DEFAULT NULL,
  `object_num` varchar(128) DEFAULT NULL,
  `uri_total` varchar(128) DEFAULT NULL,
  `uri_success_num` varchar(128) DEFAULT NULL,
  `uri_fail_num` varchar(128) DEFAULT NULL,
  `uri_response_time` varchar(256) DEFAULT NULL,
  `auditor_queue` varchar(1024) DEFAULT NULL,
  `replicate_num` varchar(1024) DEFAULT NULL,
  `update_num` varchar(1024) DEFAULT NULL,
  `sync_num` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_lb_info`
--

DROP TABLE IF EXISTS `sfo_cluster_lb_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_lb_info` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `net_area` varchar(128) NOT NULL,
  `service_ip` varchar(1024) NOT NULL,
  `lb_stat` varchar(128) DEFAULT NULL,
  `lb_weight` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_node`
--

DROP TABLE IF EXISTS `sfo_cluster_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_node` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `node_host_name` varchar(128) DEFAULT NULL,
  `node_inet_ip` varchar(128) DEFAULT NULL,
  `node_replicate_ip` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `node_stat` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_policy`
--

DROP TABLE IF EXISTS `sfo_cluster_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_policy` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `policy_num` varchar(128) NOT NULL,
  `policy_name` varchar(128) NOT NULL,
  `policy_alias` varchar(128) DEFAULT NULL,
  `deprecated` varchar(128) DEFAULT NULL,
  `policy_type` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `policy_num` (`policy_num`),
  KEY `ix_sfo_cluster_policy_add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_ring`
--

DROP TABLE IF EXISTS `sfo_cluster_ring`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_ring` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `ring_name` varchar(128) NOT NULL,
  `part_power` varchar(128) NOT NULL,
  `replicas` varchar(128) NOT NULL,
  `min_part_hours` varchar(128) NOT NULL,
  `ring_stat` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_special_resource_map`
--

DROP TABLE IF EXISTS `sfo_cluster_special_resource_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_special_resource_map` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `system_code` varchar(128) NOT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  KEY `ix_sfo_cluster_special_resource_map_system_code` (`system_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_srv`
--

DROP TABLE IF EXISTS `sfo_cluster_srv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_srv` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) NOT NULL,
  `node_host_name` varchar(128) NOT NULL,
  `service_name` varchar(128) NOT NULL,
  `is_rely_software` varchar(128) DEFAULT NULL,
  `srv_stat` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_cluster_tps_info`
--

DROP TABLE IF EXISTS `sfo_cluster_tps_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_cluster_tps_info` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `avg_time` varchar(128) DEFAULT NULL,
  `head_time` varchar(128) DEFAULT NULL,
  `get_time` varchar(128) DEFAULT NULL,
  `put_time` varchar(128) DEFAULT NULL,
  `post_time` varchar(128) DEFAULT NULL,
  `delete_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) NOT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_configure_info`
--

DROP TABLE IF EXISTS `sfo_configure_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_configure_info` (
  `guid` varchar(128) NOT NULL,
  `config_group` varchar(128) DEFAULT NULL,
  `config_key` varchar(128) DEFAULT NULL,
  `config_value` varchar(128) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_container_statsd_data`
--

DROP TABLE IF EXISTS `sfo_container_statsd_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_container_statsd_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `sync_skips` varchar(128) DEFAULT NULL,
  `sync_failures` varchar(128) DEFAULT NULL,
  `sync_syncs` varchar(128) DEFAULT NULL,
  `sync_deletes` varchar(128) DEFAULT NULL,
  `sync_del_timing` text,
  `sync_puts` varchar(128) DEFAULT NULL,
  `sync_puts_timing` text,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_no_changes` varchar(128) DEFAULT NULL,
  `updater_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_container_statsd_data_5min`
--

DROP TABLE IF EXISTS `sfo_container_statsd_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_container_statsd_data_5min` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `sync_skips` varchar(128) DEFAULT NULL,
  `sync_failures` varchar(128) DEFAULT NULL,
  `sync_syncs` varchar(128) DEFAULT NULL,
  `sync_deletes` varchar(128) DEFAULT NULL,
  `sync_del_timing` text,
  `sync_puts` varchar(128) DEFAULT NULL,
  `sync_puts_timing` text,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_no_changes` varchar(128) DEFAULT NULL,
  `updater_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_container_statsd_data_day`
--

DROP TABLE IF EXISTS `sfo_container_statsd_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_container_statsd_data_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `sync_skips` varchar(128) DEFAULT NULL,
  `sync_failures` varchar(128) DEFAULT NULL,
  `sync_syncs` varchar(128) DEFAULT NULL,
  `sync_deletes` varchar(128) DEFAULT NULL,
  `sync_del_timing` text,
  `sync_puts` varchar(128) DEFAULT NULL,
  `sync_puts_timing` text,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_no_changes` varchar(128) DEFAULT NULL,
  `updater_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_container_statsd_data_hour`
--

DROP TABLE IF EXISTS `sfo_container_statsd_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_container_statsd_data_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_passes` varchar(128) DEFAULT NULL,
  `auditor_failures` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `replicator_diffs` varchar(128) DEFAULT NULL,
  `replicator_diff_caps` varchar(128) DEFAULT NULL,
  `replicator_no_changes` varchar(128) DEFAULT NULL,
  `replicator_hashmatches` varchar(128) DEFAULT NULL,
  `replicator_rsyncs` varchar(128) DEFAULT NULL,
  `replicator_remote_merges` varchar(128) DEFAULT NULL,
  `replicator_attempts` varchar(128) DEFAULT NULL,
  `replicator_failures` varchar(128) DEFAULT NULL,
  `replicator_removes` varchar(1024) DEFAULT NULL,
  `replicator_successes` varchar(128) DEFAULT NULL,
  `replicator_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_put_err_timing` text,
  `req_put_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `sync_skips` varchar(128) DEFAULT NULL,
  `sync_failures` varchar(128) DEFAULT NULL,
  `sync_syncs` varchar(128) DEFAULT NULL,
  `sync_deletes` varchar(128) DEFAULT NULL,
  `sync_del_timing` text,
  `sync_puts` varchar(128) DEFAULT NULL,
  `sync_puts_timing` text,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_no_changes` varchar(128) DEFAULT NULL,
  `updater_timing` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_disk_perform_data`
--

DROP TABLE IF EXISTS `sfo_disk_perform_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_disk_perform_data` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `disk_uuid` varchar(1024) NOT NULL,
  `disk_name` varchar(1024) DEFAULT NULL,
  `disk_total` varchar(128) DEFAULT NULL,
  `disk_used` varchar(1024) DEFAULT NULL,
  `disk_free` varchar(1024) DEFAULT NULL,
  `disk_percent` varchar(1024) DEFAULT NULL,
  `read_count` varchar(1024) DEFAULT NULL,
  `write_count` varchar(1024) DEFAULT NULL,
  `read_bytes` varchar(1024) DEFAULT NULL,
  `write_bytes` varchar(1024) DEFAULT NULL,
  `read_time` varchar(1024) DEFAULT NULL,
  `write_time` varchar(1024) DEFAULT NULL,
  `read_merged_count` varchar(1024) DEFAULT NULL,
  `write_merged_count` varchar(1024) DEFAULT NULL,
  `busy_time` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `index_hostname` (`host_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_disk_perform_data_5min`
--

DROP TABLE IF EXISTS `sfo_disk_perform_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_disk_perform_data_5min` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `disk_uuid` varchar(1024) NOT NULL,
  `disk_name` varchar(1024) DEFAULT NULL,
  `disk_total` varchar(128) DEFAULT NULL,
  `disk_used` varchar(1024) DEFAULT NULL,
  `disk_free` varchar(1024) DEFAULT NULL,
  `disk_percent` varchar(1024) DEFAULT NULL,
  `read_count` varchar(1024) DEFAULT NULL,
  `write_count` varchar(1024) DEFAULT NULL,
  `read_bytes` varchar(1024) DEFAULT NULL,
  `write_bytes` varchar(1024) DEFAULT NULL,
  `read_time` varchar(1024) DEFAULT NULL,
  `write_time` varchar(1024) DEFAULT NULL,
  `read_merged_count` varchar(1024) DEFAULT NULL,
  `write_merged_count` varchar(1024) DEFAULT NULL,
  `busy_time` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `index_hostname` (`host_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_disk_perform_data_day`
--

DROP TABLE IF EXISTS `sfo_disk_perform_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_disk_perform_data_day` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `disk_uuid` varchar(1024) NOT NULL,
  `disk_name` varchar(1024) DEFAULT NULL,
  `disk_total` varchar(128) DEFAULT NULL,
  `disk_used` varchar(1024) DEFAULT NULL,
  `disk_free` varchar(1024) DEFAULT NULL,
  `disk_percent` varchar(1024) DEFAULT NULL,
  `read_count` varchar(1024) DEFAULT NULL,
  `write_count` varchar(1024) DEFAULT NULL,
  `read_bytes` varchar(1024) DEFAULT NULL,
  `write_bytes` varchar(1024) DEFAULT NULL,
  `read_time` varchar(1024) DEFAULT NULL,
  `write_time` varchar(1024) DEFAULT NULL,
  `read_merged_count` varchar(1024) DEFAULT NULL,
  `write_merged_count` varchar(1024) DEFAULT NULL,
  `busy_time` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `index_hostname` (`host_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_disk_perform_data_his`
--

DROP TABLE IF EXISTS `sfo_disk_perform_data_his`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_disk_perform_data_his` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `disk_uuid` varchar(1024) NOT NULL,
  `disk_name` varchar(1024) DEFAULT NULL,
  `disk_total` varchar(128) DEFAULT NULL,
  `disk_used` varchar(1024) DEFAULT NULL,
  `disk_free` varchar(1024) DEFAULT NULL,
  `disk_percent` varchar(1024) DEFAULT NULL,
  `read_count` varchar(1024) DEFAULT NULL,
  `write_count` varchar(1024) DEFAULT NULL,
  `read_bytes` varchar(1024) DEFAULT NULL,
  `write_bytes` varchar(1024) DEFAULT NULL,
  `read_time` varchar(1024) DEFAULT NULL,
  `write_time` varchar(1024) DEFAULT NULL,
  `read_merged_count` varchar(1024) DEFAULT NULL,
  `write_merged_count` varchar(1024) DEFAULT NULL,
  `busy_time` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_disk_perform_data_hour`
--

DROP TABLE IF EXISTS `sfo_disk_perform_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_disk_perform_data_hour` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `disk_uuid` varchar(1024) NOT NULL,
  `disk_name` varchar(1024) DEFAULT NULL,
  `disk_total` varchar(128) DEFAULT NULL,
  `disk_used` varchar(1024) DEFAULT NULL,
  `disk_free` varchar(1024) DEFAULT NULL,
  `disk_percent` varchar(1024) DEFAULT NULL,
  `read_count` varchar(1024) DEFAULT NULL,
  `write_count` varchar(1024) DEFAULT NULL,
  `read_bytes` varchar(1024) DEFAULT NULL,
  `write_bytes` varchar(1024) DEFAULT NULL,
  `read_time` varchar(1024) DEFAULT NULL,
  `write_time` varchar(1024) DEFAULT NULL,
  `read_merged_count` varchar(1024) DEFAULT NULL,
  `write_merged_count` varchar(1024) DEFAULT NULL,
  `busy_time` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `index_hostname` (`host_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_dispersion_report_data`
--

DROP TABLE IF EXISTS `sfo_dispersion_report_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_dispersion_report_data` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `object_retries` varchar(128) DEFAULT NULL,
  `object_missing_two` varchar(128) DEFAULT NULL,
  `object_copies_found` varchar(128) DEFAULT NULL,
  `object_missing_one` varchar(128) DEFAULT NULL,
  `object_copies_expected` varchar(128) DEFAULT NULL,
  `object_pct_found` varchar(128) DEFAULT NULL,
  `object_overlapping` varchar(128) DEFAULT NULL,
  `object_missing_all` varchar(128) DEFAULT NULL,
  `container_retries` varchar(128) DEFAULT NULL,
  `container_missing_two` varchar(128) DEFAULT NULL,
  `container_copies_found` varchar(128) DEFAULT NULL,
  `container_missing_one` varchar(128) DEFAULT NULL,
  `container_copies_expected` varchar(128) DEFAULT NULL,
  `container_pct_found` varchar(128) DEFAULT NULL,
  `container_overlapping` varchar(128) DEFAULT NULL,
  `container_missing_all` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_info`
--

DROP TABLE IF EXISTS `sfo_host_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_info` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) NOT NULL,
  `mf_name` varchar(128) DEFAULT NULL,
  `mf_model` varchar(128) DEFAULT NULL,
  `mf_bios_version` varchar(128) DEFAULT NULL,
  `mf_bios_date` varchar(128) DEFAULT NULL,
  `mf_serial_number` varchar(128) DEFAULT NULL,
  `os_version` varchar(128) DEFAULT NULL,
  `os_kernel_version` varchar(128) DEFAULT NULL,
  `cpu_model` varchar(1024) DEFAULT NULL,
  `cpu_sockets` varchar(128) DEFAULT NULL,
  `cpu_cores` varchar(128) DEFAULT NULL,
  `cpu_processors` varchar(1024) DEFAULT NULL,
  `cpu_frequency` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_number` varchar(128) DEFAULT NULL,
  `mem_single_size` varchar(128) DEFAULT NULL,
  `mem_frequency` varchar(1024) DEFAULT NULL,
  `net_model` text,
  `net_number` varchar(128) DEFAULT NULL,
  `net_speed` varchar(1024) DEFAULT NULL,
  `net_mac_address` varchar(1024) DEFAULT NULL,
  `net_ip_address` varchar(1024) DEFAULT NULL,
  `disk_type` varchar(1024) DEFAULT NULL,
  `disk_number` varchar(128) DEFAULT NULL,
  `disk_rpm_speed` varchar(1024) DEFAULT NULL,
  `disk_capacity` varchar(1024) DEFAULT NULL,
  `disk_useful_size` varchar(1024) DEFAULT NULL,
  `disk_rw_rate` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_monitor_data`
--

DROP TABLE IF EXISTS `sfo_host_monitor_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_monitor_data` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_cpu_rate` varchar(1024) DEFAULT NULL,
  `host_mem_rate` varchar(1024) DEFAULT NULL,
  `host_net_rate` varchar(1024) DEFAULT NULL,
  `host_net_stat` varchar(1024) DEFAULT NULL,
  `host_disk_stat` varchar(1024) DEFAULT NULL,
  `host_file_rate` text,
  `host_rw_file` varchar(1024) DEFAULT NULL,
  `host_ntp_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_monitor_data_5min`
--

DROP TABLE IF EXISTS `sfo_host_monitor_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_monitor_data_5min` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_cpu_rate` varchar(1024) DEFAULT NULL,
  `host_mem_rate` varchar(1024) DEFAULT NULL,
  `host_net_rate` varchar(1024) DEFAULT NULL,
  `host_net_stat` varchar(1024) DEFAULT NULL,
  `host_disk_stat` varchar(1024) DEFAULT NULL,
  `host_file_rate` text,
  `host_rw_file` varchar(1024) DEFAULT NULL,
  `host_ntp_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_monitor_data_day`
--

DROP TABLE IF EXISTS `sfo_host_monitor_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_monitor_data_day` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_cpu_rate` varchar(1024) DEFAULT NULL,
  `host_mem_rate` varchar(1024) DEFAULT NULL,
  `host_net_rate` varchar(1024) DEFAULT NULL,
  `host_net_stat` varchar(1024) DEFAULT NULL,
  `host_disk_stat` varchar(1024) DEFAULT NULL,
  `host_file_rate` text,
  `host_rw_file` varchar(1024) DEFAULT NULL,
  `host_ntp_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_monitor_data_his`
--

DROP TABLE IF EXISTS `sfo_host_monitor_data_his`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_monitor_data_his` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_cpu_rate` varchar(1024) DEFAULT NULL,
  `host_mem_rate` varchar(1024) DEFAULT NULL,
  `host_net_rate` varchar(1024) DEFAULT NULL,
  `host_net_stat` varchar(1024) DEFAULT NULL,
  `host_disk_stat` varchar(1024) DEFAULT NULL,
  `host_file_rate` text,
  `host_rw_file` varchar(1024) DEFAULT NULL,
  `host_ntp_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_monitor_data_hour`
--

DROP TABLE IF EXISTS `sfo_host_monitor_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_monitor_data_hour` (
  `guid` varchar(128) NOT NULL,
  `data_model` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_cpu_rate` varchar(1024) DEFAULT NULL,
  `host_mem_rate` varchar(1024) DEFAULT NULL,
  `host_net_rate` varchar(1024) DEFAULT NULL,
  `host_net_stat` varchar(1024) DEFAULT NULL,
  `host_disk_stat` varchar(1024) DEFAULT NULL,
  `host_file_rate` text,
  `host_rw_file` varchar(1024) DEFAULT NULL,
  `host_ntp_time` varchar(128) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_host_ring`
--

DROP TABLE IF EXISTS `sfo_host_ring`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_host_ring` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `ip_addr` varchar(128) DEFAULT NULL,
  `rings_md5` text,
  `ring_info` text,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_manager_task_list`
--

DROP TABLE IF EXISTS `sfo_manager_task_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_manager_task_list` (
  `guid` varchar(128) NOT NULL,
  `taskid` varchar(128) NOT NULL,
  `excute_description` text,
  `excute_message` text,
  `add_time` varchar(128) DEFAULT NULL,
  `end_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_perform_data`
--

DROP TABLE IF EXISTS `sfo_node_perform_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_perform_data` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `swift_version` varchar(128) DEFAULT NULL,
  `node_time` varchar(128) DEFAULT NULL,
  `async_pending` varchar(128) DEFAULT NULL,
  `node_sockstat` varchar(1024) DEFAULT NULL,
  `stg_diskusage` text,
  `drive_audit_errors` varchar(1024) DEFAULT NULL,
  `node_ringmd5` varchar(1024) DEFAULT NULL,
  `swiftconfmd5` varchar(128) DEFAULT NULL,
  `quarantined_count` varchar(1024) DEFAULT NULL,
  `account_replication` varchar(1024) DEFAULT NULL,
  `container_replication` varchar(1024) DEFAULT NULL,
  `object_replication` text,
  `account_auditor` varchar(1024) DEFAULT NULL,
  `container_auditor` varchar(1024) DEFAULT NULL,
  `object_auditor` varchar(1024) DEFAULT NULL,
  `account_updater` varchar(1024) DEFAULT NULL,
  `container_updater` varchar(1024) DEFAULT NULL,
  `object_updater` text,
  `object_expirer` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_perform_data_5min`
--

DROP TABLE IF EXISTS `sfo_node_perform_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_perform_data_5min` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `swift_version` varchar(128) DEFAULT NULL,
  `node_time` varchar(128) DEFAULT NULL,
  `async_pending` varchar(128) DEFAULT NULL,
  `node_sockstat` varchar(1024) DEFAULT NULL,
  `stg_diskusage` text,
  `drive_audit_errors` varchar(1024) DEFAULT NULL,
  `node_ringmd5` varchar(1024) DEFAULT NULL,
  `swiftconfmd5` varchar(128) DEFAULT NULL,
  `quarantined_count` varchar(1024) DEFAULT NULL,
  `account_replication` varchar(1024) DEFAULT NULL,
  `container_replication` varchar(1024) DEFAULT NULL,
  `object_replication` text,
  `account_auditor` varchar(1024) DEFAULT NULL,
  `container_auditor` varchar(1024) DEFAULT NULL,
  `object_auditor` varchar(1024) DEFAULT NULL,
  `account_updater` varchar(1024) DEFAULT NULL,
  `container_updater` varchar(1024) DEFAULT NULL,
  `object_updater` text,
  `object_expirer` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_perform_data_day`
--

DROP TABLE IF EXISTS `sfo_node_perform_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_perform_data_day` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `swift_version` varchar(128) DEFAULT NULL,
  `node_time` varchar(128) DEFAULT NULL,
  `async_pending` varchar(128) DEFAULT NULL,
  `node_sockstat` varchar(1024) DEFAULT NULL,
  `stg_diskusage` text,
  `drive_audit_errors` varchar(1024) DEFAULT NULL,
  `node_ringmd5` varchar(1024) DEFAULT NULL,
  `swiftconfmd5` varchar(128) DEFAULT NULL,
  `quarantined_count` varchar(1024) DEFAULT NULL,
  `account_replication` varchar(1024) DEFAULT NULL,
  `container_replication` varchar(1024) DEFAULT NULL,
  `object_replication` text,
  `account_auditor` varchar(1024) DEFAULT NULL,
  `container_auditor` varchar(1024) DEFAULT NULL,
  `object_auditor` varchar(1024) DEFAULT NULL,
  `account_updater` varchar(1024) DEFAULT NULL,
  `container_updater` varchar(1024) DEFAULT NULL,
  `object_updater` text,
  `object_expirer` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_perform_data_his`
--

DROP TABLE IF EXISTS `sfo_node_perform_data_his`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_perform_data_his` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `swift_version` varchar(128) DEFAULT NULL,
  `node_time` varchar(128) DEFAULT NULL,
  `async_pending` varchar(128) DEFAULT NULL,
  `node_sockstat` varchar(1024) DEFAULT NULL,
  `stg_diskusage` text,
  `drive_audit_errors` varchar(1024) DEFAULT NULL,
  `node_ringmd5` varchar(1024) DEFAULT NULL,
  `swiftconfmd5` varchar(128) DEFAULT NULL,
  `quarantined_count` varchar(1024) DEFAULT NULL,
  `account_replication` varchar(1024) DEFAULT NULL,
  `container_replication` varchar(1024) DEFAULT NULL,
  `object_replication` text,
  `account_auditor` varchar(1024) DEFAULT NULL,
  `container_auditor` varchar(1024) DEFAULT NULL,
  `object_auditor` varchar(1024) DEFAULT NULL,
  `account_updater` varchar(1024) DEFAULT NULL,
  `container_updater` varchar(1024) DEFAULT NULL,
  `object_updater` text,
  `object_expirer` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_perform_data_hour`
--

DROP TABLE IF EXISTS `sfo_node_perform_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_perform_data_hour` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `node_role` varchar(128) DEFAULT NULL,
  `swift_version` varchar(128) DEFAULT NULL,
  `node_time` varchar(128) DEFAULT NULL,
  `async_pending` varchar(128) DEFAULT NULL,
  `node_sockstat` varchar(1024) DEFAULT NULL,
  `stg_diskusage` text,
  `drive_audit_errors` varchar(1024) DEFAULT NULL,
  `node_ringmd5` varchar(1024) DEFAULT NULL,
  `swiftconfmd5` varchar(128) DEFAULT NULL,
  `quarantined_count` varchar(1024) DEFAULT NULL,
  `account_replication` varchar(1024) DEFAULT NULL,
  `container_replication` varchar(1024) DEFAULT NULL,
  `object_replication` text,
  `account_auditor` varchar(1024) DEFAULT NULL,
  `container_auditor` varchar(1024) DEFAULT NULL,
  `object_auditor` varchar(1024) DEFAULT NULL,
  `account_updater` varchar(1024) DEFAULT NULL,
  `container_updater` varchar(1024) DEFAULT NULL,
  `object_updater` text,
  `object_expirer` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_srvstat_data`
--

DROP TABLE IF EXISTS `sfo_node_srvstat_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_srvstat_data` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `srv_proxy` varchar(128) DEFAULT NULL,
  `srv_account` varchar(128) DEFAULT NULL,
  `srv_account_auditor` varchar(128) DEFAULT NULL,
  `srv_account_reaper` varchar(128) DEFAULT NULL,
  `srv_account_replicator` varchar(128) DEFAULT NULL,
  `srv_container` varchar(128) DEFAULT NULL,
  `srv_container_auditor` varchar(128) DEFAULT NULL,
  `srv_container_replicator` varchar(128) DEFAULT NULL,
  `srv_container_updater` varchar(128) DEFAULT NULL,
  `srv_container_sync` varchar(128) DEFAULT NULL,
  `srv_container_reconciler` varchar(128) DEFAULT NULL,
  `srv_object` varchar(128) DEFAULT NULL,
  `srv_object_auditor` varchar(128) DEFAULT NULL,
  `srv_object_replicator` varchar(128) DEFAULT NULL,
  `srv_object_updater` varchar(128) DEFAULT NULL,
  `srv_object_expirer` varchar(128) DEFAULT NULL,
  `srv_object_reconstructor` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_srvstat_data_5min`
--

DROP TABLE IF EXISTS `sfo_node_srvstat_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_srvstat_data_5min` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `srv_proxy` varchar(128) DEFAULT NULL,
  `srv_account` varchar(128) DEFAULT NULL,
  `srv_account_auditor` varchar(128) DEFAULT NULL,
  `srv_account_reaper` varchar(128) DEFAULT NULL,
  `srv_account_replicator` varchar(128) DEFAULT NULL,
  `srv_container` varchar(128) DEFAULT NULL,
  `srv_container_auditor` varchar(128) DEFAULT NULL,
  `srv_container_replicator` varchar(128) DEFAULT NULL,
  `srv_container_updater` varchar(128) DEFAULT NULL,
  `srv_container_sync` varchar(128) DEFAULT NULL,
  `srv_container_reconciler` varchar(128) DEFAULT NULL,
  `srv_object` varchar(128) DEFAULT NULL,
  `srv_object_auditor` varchar(128) DEFAULT NULL,
  `srv_object_replicator` varchar(128) DEFAULT NULL,
  `srv_object_updater` varchar(128) DEFAULT NULL,
  `srv_object_expirer` varchar(128) DEFAULT NULL,
  `srv_object_reconstructor` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_srvstat_data_day`
--

DROP TABLE IF EXISTS `sfo_node_srvstat_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_srvstat_data_day` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `srv_proxy` varchar(128) DEFAULT NULL,
  `srv_account` varchar(128) DEFAULT NULL,
  `srv_account_auditor` varchar(128) DEFAULT NULL,
  `srv_account_reaper` varchar(128) DEFAULT NULL,
  `srv_account_replicator` varchar(128) DEFAULT NULL,
  `srv_container` varchar(128) DEFAULT NULL,
  `srv_container_auditor` varchar(128) DEFAULT NULL,
  `srv_container_replicator` varchar(128) DEFAULT NULL,
  `srv_container_updater` varchar(128) DEFAULT NULL,
  `srv_container_sync` varchar(128) DEFAULT NULL,
  `srv_container_reconciler` varchar(128) DEFAULT NULL,
  `srv_object` varchar(128) DEFAULT NULL,
  `srv_object_auditor` varchar(128) DEFAULT NULL,
  `srv_object_replicator` varchar(128) DEFAULT NULL,
  `srv_object_updater` varchar(128) DEFAULT NULL,
  `srv_object_expirer` varchar(128) DEFAULT NULL,
  `srv_object_reconstructor` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_srvstat_data_his`
--

DROP TABLE IF EXISTS `sfo_node_srvstat_data_his`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_srvstat_data_his` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `srv_proxy` varchar(128) DEFAULT NULL,
  `srv_account` varchar(128) DEFAULT NULL,
  `srv_account_auditor` varchar(128) DEFAULT NULL,
  `srv_account_reaper` varchar(128) DEFAULT NULL,
  `srv_account_replicator` varchar(128) DEFAULT NULL,
  `srv_container` varchar(128) DEFAULT NULL,
  `srv_container_auditor` varchar(128) DEFAULT NULL,
  `srv_container_replicator` varchar(128) DEFAULT NULL,
  `srv_container_updater` varchar(128) DEFAULT NULL,
  `srv_container_sync` varchar(128) DEFAULT NULL,
  `srv_container_reconciler` varchar(128) DEFAULT NULL,
  `srv_object` varchar(128) DEFAULT NULL,
  `srv_object_auditor` varchar(128) DEFAULT NULL,
  `srv_object_replicator` varchar(128) DEFAULT NULL,
  `srv_object_updater` varchar(128) DEFAULT NULL,
  `srv_object_expirer` varchar(128) DEFAULT NULL,
  `srv_object_reconstructor` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_srvstat_data_hour`
--

DROP TABLE IF EXISTS `sfo_node_srvstat_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_srvstat_data_hour` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `srv_proxy` varchar(128) DEFAULT NULL,
  `srv_account` varchar(128) DEFAULT NULL,
  `srv_account_auditor` varchar(128) DEFAULT NULL,
  `srv_account_reaper` varchar(128) DEFAULT NULL,
  `srv_account_replicator` varchar(128) DEFAULT NULL,
  `srv_container` varchar(128) DEFAULT NULL,
  `srv_container_auditor` varchar(128) DEFAULT NULL,
  `srv_container_replicator` varchar(128) DEFAULT NULL,
  `srv_container_updater` varchar(128) DEFAULT NULL,
  `srv_container_sync` varchar(128) DEFAULT NULL,
  `srv_container_reconciler` varchar(128) DEFAULT NULL,
  `srv_object` varchar(128) DEFAULT NULL,
  `srv_object_auditor` varchar(128) DEFAULT NULL,
  `srv_object_replicator` varchar(128) DEFAULT NULL,
  `srv_object_updater` varchar(128) DEFAULT NULL,
  `srv_object_expirer` varchar(128) DEFAULT NULL,
  `srv_object_reconstructor` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_stat_data`
--

DROP TABLE IF EXISTS `sfo_node_stat_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_stat_data` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_runtime` varchar(128) DEFAULT NULL,
  `host_average_load` varchar(128) DEFAULT NULL,
  `host_login_users` varchar(128) DEFAULT NULL,
  `host_time` varchar(128) DEFAULT NULL,
  `thread_total` varchar(128) DEFAULT NULL,
  `thread_running` varchar(128) DEFAULT NULL,
  `thread_sleeping` varchar(128) DEFAULT NULL,
  `thread_stoped` varchar(128) DEFAULT NULL,
  `thread_zombie` varchar(128) DEFAULT NULL,
  `cpu_us` varchar(128) DEFAULT NULL,
  `cpu_sy` varchar(128) DEFAULT NULL,
  `cpu_ni` varchar(128) DEFAULT NULL,
  `cpu_id` varchar(128) DEFAULT NULL,
  `cpu_wa` varchar(128) DEFAULT NULL,
  `cpu_hi` varchar(128) DEFAULT NULL,
  `cpu_si` varchar(128) DEFAULT NULL,
  `cpu_st` varchar(128) DEFAULT NULL,
  `cpu_core_used` varchar(1024) DEFAULT NULL,
  `cpu_core_frq` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_used` varchar(128) DEFAULT NULL,
  `mem_free` varchar(128) DEFAULT NULL,
  `mem_buffers` varchar(128) DEFAULT NULL,
  `swap_total` varchar(128) DEFAULT NULL,
  `swap_used` varchar(128) DEFAULT NULL,
  `swap_free` varchar(128) DEFAULT NULL,
  `swap_cached` varchar(128) DEFAULT NULL,
  `net_uesd` varchar(1024) DEFAULT NULL,
  `net_send_packages` varchar(1024) DEFAULT NULL,
  `net_recv_packages` varchar(1024) DEFAULT NULL,
  `net_send_bytes` varchar(1024) DEFAULT NULL,
  `net_recv_bytes` varchar(1024) DEFAULT NULL,
  `net_in_err` varchar(1024) DEFAULT NULL,
  `net_out_err` varchar(1024) DEFAULT NULL,
  `net_in_drop` varchar(1024) DEFAULT NULL,
  `net_out_drop` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `host_name` (`host_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_stat_data_5min`
--

DROP TABLE IF EXISTS `sfo_node_stat_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_stat_data_5min` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_runtime` varchar(128) DEFAULT NULL,
  `host_average_load` varchar(128) DEFAULT NULL,
  `host_login_users` varchar(128) DEFAULT NULL,
  `host_time` varchar(128) DEFAULT NULL,
  `thread_total` varchar(128) DEFAULT NULL,
  `thread_running` varchar(128) DEFAULT NULL,
  `thread_sleeping` varchar(128) DEFAULT NULL,
  `thread_stoped` varchar(128) DEFAULT NULL,
  `thread_zombie` varchar(128) DEFAULT NULL,
  `cpu_us` varchar(128) DEFAULT NULL,
  `cpu_sy` varchar(128) DEFAULT NULL,
  `cpu_ni` varchar(128) DEFAULT NULL,
  `cpu_id` varchar(128) DEFAULT NULL,
  `cpu_wa` varchar(128) DEFAULT NULL,
  `cpu_hi` varchar(128) DEFAULT NULL,
  `cpu_si` varchar(128) DEFAULT NULL,
  `cpu_st` varchar(128) DEFAULT NULL,
  `cpu_core_used` varchar(1024) DEFAULT NULL,
  `cpu_core_frq` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_used` varchar(128) DEFAULT NULL,
  `mem_free` varchar(128) DEFAULT NULL,
  `mem_buffers` varchar(128) DEFAULT NULL,
  `swap_total` varchar(128) DEFAULT NULL,
  `swap_used` varchar(128) DEFAULT NULL,
  `swap_free` varchar(128) DEFAULT NULL,
  `swap_cached` varchar(128) DEFAULT NULL,
  `net_uesd` varchar(1024) DEFAULT NULL,
  `net_send_packages` varchar(1024) DEFAULT NULL,
  `net_recv_packages` varchar(1024) DEFAULT NULL,
  `net_send_bytes` varchar(1024) DEFAULT NULL,
  `net_recv_bytes` varchar(1024) DEFAULT NULL,
  `net_in_err` varchar(1024) DEFAULT NULL,
  `net_out_err` varchar(1024) DEFAULT NULL,
  `net_in_drop` varchar(1024) DEFAULT NULL,
  `net_out_drop` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `host_name` (`host_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_stat_data_day`
--

DROP TABLE IF EXISTS `sfo_node_stat_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_stat_data_day` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_runtime` varchar(128) DEFAULT NULL,
  `host_average_load` varchar(128) DEFAULT NULL,
  `host_login_users` varchar(128) DEFAULT NULL,
  `host_time` varchar(128) DEFAULT NULL,
  `thread_total` varchar(128) DEFAULT NULL,
  `thread_running` varchar(128) DEFAULT NULL,
  `thread_sleeping` varchar(128) DEFAULT NULL,
  `thread_stoped` varchar(128) DEFAULT NULL,
  `thread_zombie` varchar(128) DEFAULT NULL,
  `cpu_us` varchar(128) DEFAULT NULL,
  `cpu_sy` varchar(128) DEFAULT NULL,
  `cpu_ni` varchar(128) DEFAULT NULL,
  `cpu_id` varchar(128) DEFAULT NULL,
  `cpu_wa` varchar(128) DEFAULT NULL,
  `cpu_hi` varchar(128) DEFAULT NULL,
  `cpu_si` varchar(128) DEFAULT NULL,
  `cpu_st` varchar(128) DEFAULT NULL,
  `cpu_core_used` varchar(1024) DEFAULT NULL,
  `cpu_core_frq` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_used` varchar(128) DEFAULT NULL,
  `mem_free` varchar(128) DEFAULT NULL,
  `mem_buffers` varchar(128) DEFAULT NULL,
  `swap_total` varchar(128) DEFAULT NULL,
  `swap_used` varchar(128) DEFAULT NULL,
  `swap_free` varchar(128) DEFAULT NULL,
  `swap_cached` varchar(128) DEFAULT NULL,
  `net_uesd` varchar(1024) DEFAULT NULL,
  `net_send_packages` varchar(1024) DEFAULT NULL,
  `net_recv_packages` varchar(1024) DEFAULT NULL,
  `net_send_bytes` varchar(1024) DEFAULT NULL,
  `net_recv_bytes` varchar(1024) DEFAULT NULL,
  `net_in_err` varchar(1024) DEFAULT NULL,
  `net_out_err` varchar(1024) DEFAULT NULL,
  `net_in_drop` varchar(1024) DEFAULT NULL,
  `net_out_drop` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `host_name` (`host_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_stat_data_his`
--

DROP TABLE IF EXISTS `sfo_node_stat_data_his`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_stat_data_his` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_runtime` varchar(128) DEFAULT NULL,
  `host_average_load` varchar(128) DEFAULT NULL,
  `host_login_users` varchar(128) DEFAULT NULL,
  `host_time` varchar(128) DEFAULT NULL,
  `thread_total` varchar(128) DEFAULT NULL,
  `thread_running` varchar(128) DEFAULT NULL,
  `thread_sleeping` varchar(128) DEFAULT NULL,
  `thread_stoped` varchar(128) DEFAULT NULL,
  `thread_zombie` varchar(128) DEFAULT NULL,
  `cpu_us` varchar(128) DEFAULT NULL,
  `cpu_sy` varchar(128) DEFAULT NULL,
  `cpu_ni` varchar(128) DEFAULT NULL,
  `cpu_id` varchar(128) DEFAULT NULL,
  `cpu_wa` varchar(128) DEFAULT NULL,
  `cpu_hi` varchar(128) DEFAULT NULL,
  `cpu_si` varchar(128) DEFAULT NULL,
  `cpu_st` varchar(128) DEFAULT NULL,
  `cpu_core_used` varchar(1024) DEFAULT NULL,
  `cpu_core_frq` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_used` varchar(128) DEFAULT NULL,
  `mem_free` varchar(128) DEFAULT NULL,
  `mem_buffers` varchar(128) DEFAULT NULL,
  `swap_total` varchar(128) DEFAULT NULL,
  `swap_used` varchar(128) DEFAULT NULL,
  `swap_free` varchar(128) DEFAULT NULL,
  `swap_cached` varchar(128) DEFAULT NULL,
  `net_uesd` varchar(1024) DEFAULT NULL,
  `net_send_packages` varchar(1024) DEFAULT NULL,
  `net_recv_packages` varchar(1024) DEFAULT NULL,
  `net_send_bytes` varchar(1024) DEFAULT NULL,
  `net_recv_bytes` varchar(1024) DEFAULT NULL,
  `net_in_err` varchar(1024) DEFAULT NULL,
  `net_out_err` varchar(1024) DEFAULT NULL,
  `net_in_drop` varchar(1024) DEFAULT NULL,
  `net_out_drop` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `Index 3` (`add_time`) USING BTREE,
  KEY `Index 4` (`host_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_node_stat_data_hour`
--

DROP TABLE IF EXISTS `sfo_node_stat_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_node_stat_data_hour` (
  `guid` varchar(128) NOT NULL,
  `host_name` varchar(128) DEFAULT NULL,
  `host_runtime` varchar(128) DEFAULT NULL,
  `host_average_load` varchar(128) DEFAULT NULL,
  `host_login_users` varchar(128) DEFAULT NULL,
  `host_time` varchar(128) DEFAULT NULL,
  `thread_total` varchar(128) DEFAULT NULL,
  `thread_running` varchar(128) DEFAULT NULL,
  `thread_sleeping` varchar(128) DEFAULT NULL,
  `thread_stoped` varchar(128) DEFAULT NULL,
  `thread_zombie` varchar(128) DEFAULT NULL,
  `cpu_us` varchar(128) DEFAULT NULL,
  `cpu_sy` varchar(128) DEFAULT NULL,
  `cpu_ni` varchar(128) DEFAULT NULL,
  `cpu_id` varchar(128) DEFAULT NULL,
  `cpu_wa` varchar(128) DEFAULT NULL,
  `cpu_hi` varchar(128) DEFAULT NULL,
  `cpu_si` varchar(128) DEFAULT NULL,
  `cpu_st` varchar(128) DEFAULT NULL,
  `cpu_core_used` varchar(1024) DEFAULT NULL,
  `cpu_core_frq` varchar(1024) DEFAULT NULL,
  `mem_total` varchar(128) DEFAULT NULL,
  `mem_used` varchar(128) DEFAULT NULL,
  `mem_free` varchar(128) DEFAULT NULL,
  `mem_buffers` varchar(128) DEFAULT NULL,
  `swap_total` varchar(128) DEFAULT NULL,
  `swap_used` varchar(128) DEFAULT NULL,
  `swap_free` varchar(128) DEFAULT NULL,
  `swap_cached` varchar(128) DEFAULT NULL,
  `net_uesd` varchar(1024) DEFAULT NULL,
  `net_send_packages` varchar(1024) DEFAULT NULL,
  `net_recv_packages` varchar(1024) DEFAULT NULL,
  `net_send_bytes` varchar(1024) DEFAULT NULL,
  `net_recv_bytes` varchar(1024) DEFAULT NULL,
  `net_in_err` varchar(1024) DEFAULT NULL,
  `net_out_err` varchar(1024) DEFAULT NULL,
  `net_in_drop` varchar(1024) DEFAULT NULL,
  `net_out_drop` varchar(1024) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `index_time` (`add_time`) USING BTREE,
  KEY `host_name` (`host_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_object_statsd_data`
--

DROP TABLE IF EXISTS `sfo_object_statsd_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_object_statsd_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_quarantines` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `expirer_objects` varchar(128) DEFAULT NULL,
  `expirer_errors` varchar(128) DEFAULT NULL,
  `expirer_timing` text,
  `reconstructor_part_del_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_del_timing` text,
  `reconstructor_part_update_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_update_timing` text,
  `reconstructor_suffix_hashes` varchar(128) DEFAULT NULL,
  `reconstructor_suffix_syncs` varchar(128) DEFAULT NULL,
  `replicator_part_del_count` varchar(128) DEFAULT NULL,
  `replicator_part_del_timing` text,
  `replicator_part_update_count` varchar(128) DEFAULT NULL,
  `replicator_part_update_timing` text,
  `replicator_suffix_hashes` varchar(128) DEFAULT NULL,
  `replicator_suffix_syncs` varchar(128) DEFAULT NULL,
  `req_quarantines` varchar(128) DEFAULT NULL,
  `req_async_pendings` varchar(128) DEFAULT NULL,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `req_put_err_timing` text,
  `req_put_timeouts` varchar(128) DEFAULT NULL,
  `req_put_timing` text,
  `req_put_dev_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `updater_errors` varchar(128) DEFAULT NULL,
  `updater_timing` varchar(128) DEFAULT NULL,
  `updater_quarantines` varchar(128) DEFAULT NULL,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_unlinks` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_object_statsd_data_5min`
--

DROP TABLE IF EXISTS `sfo_object_statsd_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_object_statsd_data_5min` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_quarantines` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `expirer_objects` varchar(128) DEFAULT NULL,
  `expirer_errors` varchar(128) DEFAULT NULL,
  `expirer_timing` text,
  `reconstructor_part_del_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_del_timing` text,
  `reconstructor_part_update_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_update_timing` text,
  `reconstructor_suffix_hashes` varchar(128) DEFAULT NULL,
  `reconstructor_suffix_syncs` varchar(128) DEFAULT NULL,
  `replicator_part_del_count` varchar(128) DEFAULT NULL,
  `replicator_part_del_timing` text,
  `replicator_part_update_count` varchar(128) DEFAULT NULL,
  `replicator_part_update_timing` text,
  `replicator_suffix_hashes` varchar(128) DEFAULT NULL,
  `replicator_suffix_syncs` varchar(128) DEFAULT NULL,
  `req_quarantines` varchar(128) DEFAULT NULL,
  `req_async_pendings` varchar(128) DEFAULT NULL,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `req_put_err_timing` text,
  `req_put_timeouts` varchar(128) DEFAULT NULL,
  `req_put_timing` text,
  `req_put_dev_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `updater_errors` varchar(128) DEFAULT NULL,
  `updater_timing` varchar(128) DEFAULT NULL,
  `updater_quarantines` varchar(128) DEFAULT NULL,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_unlinks` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_object_statsd_data_day`
--

DROP TABLE IF EXISTS `sfo_object_statsd_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_object_statsd_data_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_quarantines` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `expirer_objects` varchar(128) DEFAULT NULL,
  `expirer_errors` varchar(128) DEFAULT NULL,
  `expirer_timing` text,
  `reconstructor_part_del_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_del_timing` text,
  `reconstructor_part_update_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_update_timing` text,
  `reconstructor_suffix_hashes` varchar(128) DEFAULT NULL,
  `reconstructor_suffix_syncs` varchar(128) DEFAULT NULL,
  `replicator_part_del_count` varchar(128) DEFAULT NULL,
  `replicator_part_del_timing` text,
  `replicator_part_update_count` varchar(128) DEFAULT NULL,
  `replicator_part_update_timing` text,
  `replicator_suffix_hashes` varchar(128) DEFAULT NULL,
  `replicator_suffix_syncs` varchar(128) DEFAULT NULL,
  `req_quarantines` varchar(128) DEFAULT NULL,
  `req_async_pendings` varchar(128) DEFAULT NULL,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `req_put_err_timing` text,
  `req_put_timeouts` varchar(128) DEFAULT NULL,
  `req_put_timing` text,
  `req_put_dev_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `updater_errors` varchar(128) DEFAULT NULL,
  `updater_timing` varchar(128) DEFAULT NULL,
  `updater_quarantines` varchar(128) DEFAULT NULL,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_unlinks` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_object_statsd_data_hour`
--

DROP TABLE IF EXISTS `sfo_object_statsd_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_object_statsd_data_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `auditor_quarantines` varchar(128) DEFAULT NULL,
  `auditor_errors` varchar(128) DEFAULT NULL,
  `auditor_timing` text,
  `expirer_objects` varchar(128) DEFAULT NULL,
  `expirer_errors` varchar(128) DEFAULT NULL,
  `expirer_timing` text,
  `reconstructor_part_del_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_del_timing` text,
  `reconstructor_part_update_count` varchar(128) DEFAULT NULL,
  `reconstructor_part_update_timing` text,
  `reconstructor_suffix_hashes` varchar(128) DEFAULT NULL,
  `reconstructor_suffix_syncs` varchar(128) DEFAULT NULL,
  `replicator_part_del_count` varchar(128) DEFAULT NULL,
  `replicator_part_del_timing` text,
  `replicator_part_update_count` varchar(128) DEFAULT NULL,
  `replicator_part_update_timing` text,
  `replicator_suffix_hashes` varchar(128) DEFAULT NULL,
  `replicator_suffix_syncs` varchar(128) DEFAULT NULL,
  `req_quarantines` varchar(128) DEFAULT NULL,
  `req_async_pendings` varchar(128) DEFAULT NULL,
  `req_post_err_timing` text,
  `req_post_timing` text,
  `req_put_err_timing` text,
  `req_put_timeouts` varchar(128) DEFAULT NULL,
  `req_put_timing` text,
  `req_put_dev_timing` text,
  `req_get_err_timing` text,
  `req_get_timing` text,
  `req_head_err_timing` text,
  `req_head_timing` text,
  `req_del_err_timing` text,
  `req_del_timing` text,
  `req_rep_err_timing` text,
  `req_rep_timing` text,
  `updater_errors` varchar(128) DEFAULT NULL,
  `updater_timing` varchar(128) DEFAULT NULL,
  `updater_quarantines` varchar(128) DEFAULT NULL,
  `updater_successes` varchar(128) DEFAULT NULL,
  `updater_failures` varchar(128) DEFAULT NULL,
  `updater_unlinks` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_partitions_info`
--

DROP TABLE IF EXISTS `sfo_partitions_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_partitions_info` (
  `guid` char(128) NOT NULL,
  `cluster_name` text,
  `update_time` char(20) DEFAULT NULL,
  `use_handoff_partitions` text,
  `health_partitions` text,
  `error_partitions` text,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_proxy_statsd_data`
--

DROP TABLE IF EXISTS `sfo_proxy_statsd_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_proxy_statsd_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `req_errors` varchar(128) DEFAULT NULL,
  `req_handoff_count` varchar(128) DEFAULT NULL,
  `req_handoff_all_count` varchar(128) DEFAULT NULL,
  `req_client_timeouts` varchar(128) DEFAULT NULL,
  `req_client_disconnects` varchar(128) DEFAULT NULL,
  `req_timing` text,
  `req_get_timing` text,
  `req_xfer` varchar(128) DEFAULT NULL,
  `req_obj_policy_timing` text,
  `req_obj_policy_get_timing` text,
  `req_obj_policy_xfer` varchar(128) DEFAULT NULL,
  `req_auth_unauthorized` varchar(128) DEFAULT NULL,
  `req_auth_forbidden` varchar(128) DEFAULT NULL,
  `req_auth_token_denied` varchar(128) DEFAULT NULL,
  `req_auth_errors` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_proxy_statsd_data_5min`
--

DROP TABLE IF EXISTS `sfo_proxy_statsd_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_proxy_statsd_data_5min` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `req_errors` varchar(128) DEFAULT NULL,
  `req_handoff_count` varchar(128) DEFAULT NULL,
  `req_handoff_all_count` varchar(128) DEFAULT NULL,
  `req_client_timeouts` varchar(128) DEFAULT NULL,
  `req_client_disconnects` varchar(128) DEFAULT NULL,
  `req_timing` text,
  `req_get_timing` text,
  `req_xfer` varchar(128) DEFAULT NULL,
  `req_obj_policy_timing` text,
  `req_obj_policy_get_timing` text,
  `req_obj_policy_xfer` varchar(128) DEFAULT NULL,
  `req_auth_unauthorized` varchar(128) DEFAULT NULL,
  `req_auth_forbidden` varchar(128) DEFAULT NULL,
  `req_auth_token_denied` varchar(128) DEFAULT NULL,
  `req_auth_errors` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_proxy_statsd_data_day`
--

DROP TABLE IF EXISTS `sfo_proxy_statsd_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_proxy_statsd_data_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `req_errors` varchar(128) DEFAULT NULL,
  `req_handoff_count` varchar(128) DEFAULT NULL,
  `req_handoff_all_count` varchar(128) DEFAULT NULL,
  `req_client_timeouts` varchar(128) DEFAULT NULL,
  `req_client_disconnects` varchar(128) DEFAULT NULL,
  `req_timing` text,
  `req_get_timing` text,
  `req_xfer` varchar(128) DEFAULT NULL,
  `req_obj_policy_timing` text,
  `req_obj_policy_get_timing` text,
  `req_obj_policy_xfer` varchar(128) DEFAULT NULL,
  `req_auth_unauthorized` varchar(128) DEFAULT NULL,
  `req_auth_forbidden` varchar(128) DEFAULT NULL,
  `req_auth_token_denied` varchar(128) DEFAULT NULL,
  `req_auth_errors` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_proxy_statsd_data_hour`
--

DROP TABLE IF EXISTS `sfo_proxy_statsd_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_proxy_statsd_data_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `req_errors` varchar(128) DEFAULT NULL,
  `req_handoff_count` varchar(128) DEFAULT NULL,
  `req_handoff_all_count` varchar(128) DEFAULT NULL,
  `req_client_timeouts` varchar(128) DEFAULT NULL,
  `req_client_disconnects` varchar(128) DEFAULT NULL,
  `req_timing` text,
  `req_get_timing` text,
  `req_xfer` varchar(128) DEFAULT NULL,
  `req_obj_policy_timing` text,
  `req_obj_policy_get_timing` text,
  `req_obj_policy_xfer` varchar(128) DEFAULT NULL,
  `req_auth_unauthorized` varchar(128) DEFAULT NULL,
  `req_auth_forbidden` varchar(128) DEFAULT NULL,
  `req_auth_token_denied` varchar(128) DEFAULT NULL,
  `req_auth_errors` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `add_time` (`add_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_access_log`
--

DROP TABLE IF EXISTS `sfo_server_access_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_access_log` (
  `guid` varchar(128) NOT NULL,
  `access_user` varchar(128) NOT NULL,
  `access_time` varchar(128) NOT NULL,
  `access_method` varchar(128) NOT NULL,
  `access_path` varchar(128) NOT NULL,
  `access_result` varchar(128) DEFAULT NULL,
  `access_result_message` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_permission`
--

DROP TABLE IF EXISTS `sfo_server_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_permission` (
  `guid` varchar(128) NOT NULL,
  `resource_name` varchar(128) DEFAULT NULL,
  `permission_name` varchar(128) NOT NULL,
  `permission_desc` varchar(256) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `permission_name` (`permission_name`),
  KEY `resource_name` (`resource_name`),
  CONSTRAINT `sfo_server_permission_ibfk_1` FOREIGN KEY (`resource_name`) REFERENCES `sfo_server_resource` (`table_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_permissions_to_roles`
--

DROP TABLE IF EXISTS `sfo_server_permissions_to_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_permissions_to_roles` (
  `role_name` varchar(128) DEFAULT NULL,
  `permission_name` varchar(128) DEFAULT NULL,
  KEY `role_name` (`role_name`),
  KEY `permission_name` (`permission_name`),
  CONSTRAINT `sfo_server_permissions_to_roles_ibfk_1` FOREIGN KEY (`role_name`) REFERENCES `sfo_server_role` (`role_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sfo_server_permissions_to_roles_ibfk_2` FOREIGN KEY (`permission_name`) REFERENCES `sfo_server_permission` (`permission_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_resource`
--

DROP TABLE IF EXISTS `sfo_server_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_resource` (
  `guid` int(11) NOT NULL AUTO_INCREMENT,
  `table_name` varchar(128) NOT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `table_name` (`table_name`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_role`
--

DROP TABLE IF EXISTS `sfo_server_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_role` (
  `guid` varchar(128) NOT NULL,
  `role_name` varchar(128) NOT NULL,
  `role_desc` varchar(256) DEFAULT NULL,
  `last_modify_time` varchar(128) NOT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_roles_to_users`
--

DROP TABLE IF EXISTS `sfo_server_roles_to_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_roles_to_users` (
  `user_account` varchar(128) DEFAULT NULL,
  `role_name` varchar(128) DEFAULT NULL,
  KEY `user_account` (`user_account`),
  KEY `role_name` (`role_name`),
  CONSTRAINT `sfo_server_roles_to_users_ibfk_1` FOREIGN KEY (`user_account`) REFERENCES `sfo_server_user` (`user_account`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sfo_server_roles_to_users_ibfk_2` FOREIGN KEY (`role_name`) REFERENCES `sfo_server_role` (`role_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_server_user`
--

DROP TABLE IF EXISTS `sfo_server_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_server_user` (
  `guid` varchar(128) NOT NULL,
  `user_account` varchar(128) NOT NULL,
  `cluster_account` varchar(128) DEFAULT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `display_name` varchar(128) DEFAULT NULL,
  `active_status` tinyint(1) DEFAULT NULL,
  `is_clusteradmin` tinyint(1) DEFAULT NULL,
  `last_login_time` varchar(128) DEFAULT NULL,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `user_account` (`user_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_statsd_data`
--

DROP TABLE IF EXISTS `sfo_statsd_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_statsd_data` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `counters` text,
  `timers` longtext,
  `gauges` text,
  `timer_data` text,
  `counter_rates` text,
  `sets` text,
  `pctThreshold` text,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_statsd_data_5min`
--

DROP TABLE IF EXISTS `sfo_statsd_data_5min`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_statsd_data_5min` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `counters` text,
  `timers` longtext,
  `gauges` text,
  `timer_data` text,
  `counter_rates` text,
  `sets` text,
  `pctThreshold` text,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_statsd_data_day`
--

DROP TABLE IF EXISTS `sfo_statsd_data_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_statsd_data_day` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `counters` text,
  `timers` longtext,
  `gauges` text,
  `timer_data` text,
  `counter_rates` text,
  `sets` text,
  `pctThreshold` text,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_statsd_data_hour`
--

DROP TABLE IF EXISTS `sfo_statsd_data_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_statsd_data_hour` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `counters` text,
  `timers` longtext,
  `gauges` text,
  `timer_data` text,
  `counter_rates` text,
  `sets` text,
  `pctThreshold` text,
  `add_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  KEY `time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_swift_role`
--

DROP TABLE IF EXISTS `sfo_swift_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_swift_role` (
  `guid` varchar(128) NOT NULL,
  `role_name` varchar(128) NOT NULL,
  `role_desc` varchar(128) DEFAULT NULL,
  `role_meta` varchar(128) NOT NULL,
  `extend` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `guid` (`guid`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_swift_user`
--

DROP TABLE IF EXISTS `sfo_swift_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_swift_user` (
  `guid` varchar(128) NOT NULL,
  `cluster_name` varchar(128) DEFAULT NULL,
  `account_id` varchar(128) DEFAULT NULL,
  `role_name` varchar(128) DEFAULT NULL,
  `system_user` varchar(128) NOT NULL,
  `extend` text,
  `add_time` varchar(128) NOT NULL,
  PRIMARY KEY (`guid`),
  UNIQUE KEY `uix_user_account_role_systemuser_accountid_rolename` (`system_user`,`account_id`,`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_system_input_info`
--

DROP TABLE IF EXISTS `sfo_system_input_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_system_input_info` (
  `guid` varchar(128) NOT NULL,
  `sys_code` varchar(128) NOT NULL,
  `sys_id` varchar(128) NOT NULL,
  `sys_key` varchar(128) NOT NULL,
  `sys_token` varchar(128) DEFAULT NULL,
  `sys_stat` varchar(128) DEFAULT NULL,
  `sys_url` varchar(1024) DEFAULT NULL,
  `extend` text,
  `add_time` varchar(128) DEFAULT NULL,
  UNIQUE KEY `index_guid` (`guid`) USING BTREE,
  KEY `index_sys` (`sys_id`) USING BTREE,
  KEY `index_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sfo_tasks_list`
--

DROP TABLE IF EXISTS `sfo_tasks_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sfo_tasks_list` (
  `guid` varchar(128) NOT NULL,
  `create_user` varchar(128) DEFAULT NULL,
  `node_host_name` varchar(128) DEFAULT NULL,
  `service_type` varchar(128) DEFAULT NULL,
  `service_name` text,
  `operation` varchar(128) DEFAULT NULL,
  `service_task_ending_flag` varchar(128) DEFAULT NULL,
  `task_start_time` datetime DEFAULT NULL,
  `task_end_time` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-09-28 20:38:07
