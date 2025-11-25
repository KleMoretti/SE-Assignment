-- Active: 1763447403549@@127.0.0.1@3306@hospital_db
-- 数据库结构更新脚本
-- 说明：
-- 1. 为 medicines 表新增 category 列（如果不存在）
-- 2. 为 medicine_purchases 表新增 priority 列（如果不存在）
-- 3. 为 appointments 表新增 appointment_no 列并填充数据（如果不存在）

-- 请选择正确的数据库
USE hospital_db;

-- 1. medicines 表：新增药品分类字段 category
SET @db_name := DATABASE();

-- 1.1 如果 medicines.category 不存在，则添加
SET @exists_medicines_category := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @db_name
    AND TABLE_NAME = 'medicines'
    AND COLUMN_NAME = 'category'
);

SET @sql := IF(
  @exists_medicines_category = 0,
  'ALTER TABLE medicines ADD COLUMN category VARCHAR(50) NULL COMMENT ''药品分类'' AFTER generic_name;',
  'SELECT ''medicines.category already exists'';'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. medicine_purchases 表：新增采购优先级字段 priority
SET @exists_purchases_priority := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @db_name
    AND TABLE_NAME = 'medicine_purchases'
    AND COLUMN_NAME = 'priority'
);

SET @sql := IF(
  @exists_purchases_priority = 0,
  'ALTER TABLE medicine_purchases ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT ''medium'' COMMENT ''优先级：low/medium/high'' AFTER status;',
  'SELECT ''medicine_purchases.priority already exists'';'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. appointments 表：新增预约编号字段 appointment_no，并保证与后端模型一致
-- 3.1 如果没有 appointment_no 列，则新增（允许先为 NULL）
SET @exists_appointments_no := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @db_name
    AND TABLE_NAME = 'appointments'
    AND COLUMN_NAME = 'appointment_no'
);

SET @sql := IF(
  @exists_appointments_no = 0,
  'ALTER TABLE appointments ADD COLUMN appointment_no VARCHAR(20) NULL COMMENT ''预约编号'' AFTER id;',
  'SELECT ''appointments.appointment_no already exists'';'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3.2 为已有记录填充唯一的预约编号（仅针对当前为 NULL 的记录）
UPDATE appointments
SET appointment_no = CONCAT('AP_INIT_', LPAD(id, 6, '0'))
WHERE appointment_no IS NULL;

-- 3.3 将 appointment_no 改为 NOT NULL（与 models.Appointment 定义保持一致）
ALTER TABLE appointments
  MODIFY COLUMN appointment_no VARCHAR(20) NOT NULL COMMENT '预约编号';

-- 3.4 确保唯一索引存在
SET @exists_appointments_no_idx := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.STATISTICS
  WHERE TABLE_SCHEMA = @db_name
    AND TABLE_NAME = 'appointments'
    AND INDEX_NAME = 'uk_appointments_appointment_no'
);

SET @sql := IF(
  @exists_appointments_no_idx = 0,
  'ALTER TABLE appointments ADD UNIQUE INDEX uk_appointments_appointment_no (appointment_no);',
  'SELECT ''uk_appointments_appointment_no already exists'';'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
