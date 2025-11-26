"""
数据库迁移脚本：为 medication_requests 表添加 appointment_id 字段
Migration: Add appointment_id to medication_requests table
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.extensions import db
from backend.app import create_app
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            result = db.session.execute(text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'medication_requests' "
                "AND COLUMN_NAME = 'appointment_id'"
            ))
            
            if result.fetchone():
                print("✓ 字段 appointment_id 已存在，无需迁移")
                return
            
            print("开始迁移：添加 appointment_id 字段...")
            
            # 添加字段
            db.session.execute(text(
                "ALTER TABLE medication_requests "
                "ADD COLUMN appointment_id INT NULL COMMENT '关联的预约ID' AFTER medicine_id"
            ))
            print("✓ 已添加 appointment_id 字段")
            
            # 添加外键约束
            db.session.execute(text(
                "ALTER TABLE medication_requests "
                "ADD CONSTRAINT fk_medication_requests_appointment "
                "FOREIGN KEY (appointment_id) REFERENCES appointments(id) "
                "ON DELETE SET NULL"
            ))
            print("✓ 已添加外键约束")
            
            # 添加索引
            db.session.execute(text(
                "CREATE INDEX idx_medication_requests_appointment_id "
                "ON medication_requests(appointment_id)"
            ))
            print("✓ 已添加索引")
            
            db.session.commit()
            print("\n✓ 迁移成功完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
