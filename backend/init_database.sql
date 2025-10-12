-- 医院综合管理系统 - MySQL数据库初始化脚本
-- Hospital Management System - MySQL Database Initialization Script

-- 创建数据库
CREATE DATABASE IF NOT EXISTS hospital_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE hospital_db;

-- 创建用户（可选，生产环境使用）
-- CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 注意：表结构将通过Flask的db.create_all()自动创建
-- 如果需要手动创建表，请运行以下命令：
-- python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

-- 插入测试数据（可选）
-- INSERT INTO patients (patient_no, name, gender, age, phone) VALUES
-- ('P20240001', '张三', '男', 35, '13800138000'),
-- ('P20240002', '李四', '女', 28, '13900139000');

-- INSERT INTO doctors (doctor_no, name, gender, department, title) VALUES
-- ('D20240001', '王医生', '男', '内科', '主任医师'),
-- ('D20240002', '刘医生', '女', '外科', '副主任医师');

-- 查看数据库信息
SELECT 'Database initialized successfully!' AS status;
SHOW TABLES;

