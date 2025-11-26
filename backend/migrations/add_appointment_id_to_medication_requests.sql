-- 为 medication_requests 表添加 appointment_id 字段
-- 用于关联用药申请和预约

ALTER TABLE medication_requests 
ADD COLUMN appointment_id INT NULL COMMENT '关联的预约ID' AFTER medicine_id;

-- 添加外键约束
ALTER TABLE medication_requests 
ADD CONSTRAINT fk_medication_requests_appointment 
FOREIGN KEY (appointment_id) REFERENCES appointments(id) 
ON DELETE SET NULL;

-- 添加索引以提高查询性能
CREATE INDEX idx_medication_requests_appointment_id ON medication_requests(appointment_id);
