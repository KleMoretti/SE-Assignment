#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""医生数据初始化脚本
Doctor Data Seeding Script

用于在任意分支中导入/更新一批示例医生数据，按医生编号幂等执行。
运行方式（在 backend 目录下）：
    python migrations/seed_doctors.py
"""

import os
import sys
from datetime import date

# 添加项目根目录到路径，保证可以导入 app、extensions 和 models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Doctor  # noqa: E402


DOCTOR_SEED_DATA = [
    {
        "doctor_no": "D20240001",
        "name": "王医生",
        "gender": "男",
        "age": 45,
        "phone": "13800138000",
        "email": "wangyisheng@hospital.com",
        "department": "内科",
        "title": "主任医师",
        "specialty": "心血管内科、冠心病诊治",
        "education": "博士",
        "hire_date": date(2012, 3, 1),
        "status": "active",
    },
    {
        "doctor_no": "D20240002",
        "name": "刘医生",
        "gender": "女",
        "age": 40,
        "phone": "13900139000",
        "email": "liuyisheng@hospital.com",
        "department": "外科",
        "title": "副主任医师",
        "specialty": "普外科、腹腔镜微创手术",
        "education": "硕士",
        "hire_date": date(2014, 6, 15),
        "status": "active",
    },
    {
        "doctor_no": "D20240003",
        "name": "张医生",
        "gender": "男",
        "age": 38,
        "phone": "13600136000",
        "email": "zhangyisheng@hospital.com",
        "department": "儿科",
        "title": "主治医师",
        "specialty": "小儿呼吸道感染与过敏性疾病",
        "education": "硕士",
        "hire_date": date(2016, 9, 1),
        "status": "active",
    },
]


def seed_doctors() -> None:
    """按 doctor_no 幂等导入/更新医生数据。"""
    app = create_app()

    with app.app_context():
        print("开始导入/更新医生数据...")

        for item in DOCTOR_SEED_DATA:
            doctor_no = item["doctor_no"]
            existing = Doctor.query.filter_by(doctor_no=doctor_no).first()

            if existing:
                print(f"[UPDATE] 更新医生 {doctor_no} - {existing.name} → {item['name']}")
                for field, value in item.items():
                    setattr(existing, field, value)
            else:
                print(f"[CREATE] 新增医生 {doctor_no} - {item.get('name')}")
                doctor = Doctor(**item)
                db.session.add(doctor)

        try:
            db.session.commit()
            print("\n✓ 医生数据导入/更新完成")
        except Exception as exc:  # pragma: no cover - 仅用于命令行提示
            db.session.rollback()
            print(f"\n✗ 医生数据导入失败: {exc}")
            sys.exit(1)


def main() -> None:
    """脚本入口。"""
    seed_doctors()


if __name__ == "__main__":
    main()
