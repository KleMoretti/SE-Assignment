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
from datetime import date, datetime, timedelta

# 添加项目根目录到路径，保证可以导入 app、extensions 和 models
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app  # noqa: E402
from backend.extensions import db  # noqa: E402
from backend.models import (  # noqa: E402
    Appointment,
    Doctor,
    DoctorPerformance,
    DoctorSchedule,
    DoctorUserLink,
    MedicalRecord,
    MedicationRequest,
    Medicine,
    MedicineInventory,
    MedicinePurchase,
    Patient,
    PatientUserLink,
    User,
)
from backend.modules.doctor.models_extended import (  # noqa: E402
    DoctorLeave,
    DoctorQualification,
    DoctorScheduleTemplate,
    DoctorScheduleTemplateDetail,
)


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


def _upsert_doctors():
    """按 doctor_no 幂等导入/更新医生数据，返回 doctor_no -> Doctor 映射。"""
    doctor_map = {}

    for item in DOCTOR_SEED_DATA:
        doctor_no = item["doctor_no"]
        existing = Doctor.query.filter_by(doctor_no=doctor_no).first()

        if existing:
            print(f"[UPDATE] 更新医生 {doctor_no} - {existing.name} → {item['name']}")
            for field, value in item.items():
                setattr(existing, field, value)
            doctor = existing
        else:
            print(f"[CREATE] 新增医生 {doctor_no} - {item.get('name')}")
            doctor = Doctor(**item)
            db.session.add(doctor)

        doctor_map[doctor_no] = doctor

    return doctor_map


def _seed_schedules(doctor_map):
    """为示例医生生成基础排班数据（按 doctor_id + date + shift 幂等）。"""
    print("\n开始导入/更新医生排班数据...")

    today = date.today()
    schedule_seed_data = [
        {
            "doctor_no": "D20240001",
            "days_offset": 0,
            "shift": "morning",
            "start_time": "08:00",
            "end_time": "12:00",
            "max_patients": 30,
            "status": "available",
            "notes": "心内科普通门诊",
        },
        {
            "doctor_no": "D20240001",
            "days_offset": 1,
            "shift": "afternoon",
            "start_time": "14:00",
            "end_time": "17:30",
            "max_patients": 25,
            "status": "available",
            "notes": "心内科复查门诊",
        },
        {
            "doctor_no": "D20240002",
            "days_offset": 0,
            "shift": "morning",
            "start_time": "08:30",
            "end_time": "12:00",
            "max_patients": 20,
            "status": "available",
            "notes": "普通外科门诊",
        },
        {
            "doctor_no": "D20240002",
            "days_offset": 2,
            "shift": "morning",
            "start_time": "08:00",
            "end_time": "11:30",
            "max_patients": 10,
            "status": "available",
            "notes": "择期手术排班",
        },
        {
            "doctor_no": "D20240003",
            "days_offset": 0,
            "shift": "morning",
            "start_time": "09:00",
            "end_time": "12:00",
            "max_patients": 25,
            "status": "available",
            "notes": "儿科呼吸道门诊",
        },
        {
            "doctor_no": "D20240003",
            "days_offset": 1,
            "shift": "afternoon",
            "start_time": "14:00",
            "end_time": "17:00",
            "max_patients": 20,
            "status": "available",
            "notes": "儿科过敏门诊",
        },
    ]

    for item in schedule_seed_data:
        doctor = doctor_map.get(item["doctor_no"])
        if not doctor:
            continue

        schedule_date = today + timedelta(days=item["days_offset"])
        existing = DoctorSchedule.query.filter_by(
            doctor_id=doctor.id,
            date=schedule_date,
            shift=item["shift"],
        ).first()

        if existing:
            existing.start_time = item.get("start_time")
            existing.end_time = item.get("end_time")
            existing.max_patients = item.get("max_patients", existing.max_patients)
            existing.status = item.get("status", existing.status)
            existing.notes = item.get("notes", existing.notes)
        else:
            schedule = DoctorSchedule(
                doctor_id=doctor.id,
                date=schedule_date,
                shift=item["shift"],
                start_time=item.get("start_time"),
                end_time=item.get("end_time"),
                max_patients=item.get("max_patients", 20),
                status=item.get("status", "available"),
                notes=item.get("notes"),
            )
            db.session.add(schedule)

    print("✓ 医生排班数据导入/更新完成")


def _seed_performances(doctor_map):
    """为示例医生生成绩效数据（按 doctor_id + year + month 幂等）。"""
    print("\n开始导入/更新医生绩效数据...")

    today = date.today()
    year, month = today.year, today.month
    last_month_year = year if month > 1 else year - 1
    last_month = month - 1 if month > 1 else 12

    performance_seed_data = [
        {
            "doctor_no": "D20240001",
            "year": last_month_year,
            "month": last_month,
            "patient_count": 120,
            "satisfaction_score": 95.0,
            "punctuality_score": 98.0,
            "quality_score": 92.0,
            "notes": "上月门诊量较高，患者满意度优秀",
        },
        {
            "doctor_no": "D20240002",
            "year": year,
            "month": month,
            "patient_count": 80,
            "satisfaction_score": 90.0,
            "punctuality_score": 96.0,
            "quality_score": 88.0,
            "notes": "外科手术排期稳定，患者反馈良好",
        },
        {
            "doctor_no": "D20240003",
            "year": year,
            "month": month,
            "patient_count": 100,
            "satisfaction_score": 93.0,
            "punctuality_score": 97.0,
            "quality_score": 90.0,
            "notes": "儿科呼吸道疾病就诊量较大，诊疗质量稳定",
        },
    ]

    for item in performance_seed_data:
        doctor = doctor_map.get(item["doctor_no"])
        if not doctor:
            continue

        existing = DoctorPerformance.query.filter_by(
            doctor_id=doctor.id,
            year=item["year"],
            month=item["month"],
        ).first()

        patient_count = item["patient_count"]
        satisfaction = item["satisfaction_score"]
        punctuality = item["punctuality_score"]
        quality = item["quality_score"]
        total_score = satisfaction * 0.4 + punctuality * 0.2 + quality * 0.4
        bonus = patient_count * 10 + total_score * 100

        if existing:
            existing.patient_count = patient_count
            existing.satisfaction_score = satisfaction
            existing.punctuality_score = punctuality
            existing.quality_score = quality
            existing.total_score = total_score
            existing.bonus = bonus
            existing.notes = item.get("notes", existing.notes)
        else:
            performance = DoctorPerformance(
                doctor_id=doctor.id,
                year=item["year"],
                month=item["month"],
                patient_count=patient_count,
                satisfaction_score=satisfaction,
                punctuality_score=punctuality,
                quality_score=quality,
                total_score=total_score,
                bonus=bonus,
                notes=item.get("notes"),
            )
            db.session.add(performance)

    print("✓ 医生绩效数据导入/更新完成")


def _seed_qualifications(doctor_map):
    """为示例医生生成资质证书数据（按 doctor_id + qualification_type + certificate_no 幂等）。"""
    print("\n开始导入/更新医生资质证书数据...")

    qualification_seed_data = [
        {
            "doctor_no": "D20240001",
            "qualification_type": "medical_license",
            "certificate_no": "ML-2024-0001",
            "certificate_name": "执业医师资格证书",
            "issue_date": date(2010, 1, 1),
            "expiry_date": date(2030, 12, 31),
            "issuing_authority": "国家卫生健康委员会",
            "scope_of_practice": "内科",
        },
        {
            "doctor_no": "D20240002",
            "qualification_type": "medical_license",
            "certificate_no": "ML-2024-0002",
            "certificate_name": "执业医师资格证书",
            "issue_date": date(2012, 6, 1),
            "expiry_date": date(2032, 5, 31),
            "issuing_authority": "国家卫生健康委员会",
            "scope_of_practice": "外科",
        },
        {
            "doctor_no": "D20240003",
            "qualification_type": "medical_license",
            "certificate_no": "ML-2024-0003",
            "certificate_name": "执业医师资格证书",
            "issue_date": date(2015, 9, 1),
            "expiry_date": date(2035, 8, 31),
            "issuing_authority": "国家卫生健康委员会",
            "scope_of_practice": "儿科",
        },
    ]

    for item in qualification_seed_data:
        doctor = doctor_map.get(item["doctor_no"])
        if not doctor:
            continue

        existing = DoctorQualification.query.filter_by(
            doctor_id=doctor.id,
            qualification_type=item["qualification_type"],
            certificate_no=item["certificate_no"],
        ).first()

        if existing:
            existing.certificate_name = item.get("certificate_name", existing.certificate_name)
            existing.issue_date = item.get("issue_date", existing.issue_date)
            existing.expiry_date = item.get("expiry_date", existing.expiry_date)
            existing.issuing_authority = item.get("issuing_authority", existing.issuing_authority)
            existing.scope_of_practice = item.get("scope_of_practice", existing.scope_of_practice)
        else:
            qualification = DoctorQualification(
                doctor_id=doctor.id,
                qualification_type=item["qualification_type"],
                certificate_no=item.get("certificate_no"),
                certificate_name=item.get("certificate_name"),
                issue_date=item.get("issue_date"),
                expiry_date=item.get("expiry_date"),
                issuing_authority=item.get("issuing_authority"),
                scope_of_practice=item.get("scope_of_practice"),
                status="valid",
            )
            db.session.add(qualification)

    print("✓ 医生资质证书数据导入/更新完成")


def _seed_leaves(doctor_map):
    """为示例医生生成请假数据（按 doctor_id + start_date + end_date + leave_type 幂等）。"""
    print("\n开始导入/更新医生请假数据...")

    today = date.today()
    leave_seed_data = [
        {
            "doctor_no": "D20240001",
            "leave_type": "annual",
            "start_offset": -10,
            "days": 3,
            "status": "approved",
            "reason": "年度休假",
            "substitute_doctor_no": "D20240002",
            "approval_notes": "已安排外科值班医生替班",
        },
        {
            "doctor_no": "D20240003",
            "leave_type": "sick",
            "start_offset": 5,
            "days": 1,
            "status": "pending",
            "reason": "上呼吸道感染",
            "substitute_doctor_no": "D20240001",
            "approval_notes": None,
        },
    ]

    for item in leave_seed_data:
        doctor = doctor_map.get(item["doctor_no"])
        if not doctor:
            continue

        start_date = today + timedelta(days=item["start_offset"])
        end_date = start_date + timedelta(days=item["days"] - 1)
        days = (end_date - start_date).days + 1

        substitute_doctor = None
        substitute_no = item.get("substitute_doctor_no")
        if substitute_no:
            substitute_doctor = doctor_map.get(substitute_no)

        existing = DoctorLeave.query.filter_by(
            doctor_id=doctor.id,
            start_date=start_date,
            end_date=end_date,
            leave_type=item["leave_type"],
        ).first()

        status = item.get("status", "pending")
        approved = status == "approved"
        approval_date = datetime.utcnow() if approved else None
        approval_notes = item.get("approval_notes") if approved else None

        if existing:
            existing.days = days
            existing.reason = item.get("reason", existing.reason)
            existing.status = status
            existing.substitute_doctor_id = substitute_doctor.id if substitute_doctor else None
            existing.approver_id = 1 if approved else existing.approver_id
            existing.approval_date = approval_date
            existing.approval_notes = approval_notes or existing.approval_notes
        else:
            leave = DoctorLeave(
                doctor_id=doctor.id,
                leave_type=item["leave_type"],
                start_date=start_date,
                end_date=end_date,
                days=days,
                reason=item.get("reason"),
                status=status,
                approver_id=1 if approved else None,
                approval_date=approval_date,
                approval_notes=approval_notes,
                substitute_doctor_id=substitute_doctor.id if substitute_doctor else None,
            )
            db.session.add(leave)

    print("✓ 医生请假数据导入/更新完成")


def _seed_schedule_templates():
    """为示例科室生成排班模板及明细数据。"""
    print("\n开始导入/更新排班模板数据...")

    template_seed_data = [
        {
            "template_name": "内科平日门诊模板",
            "department": "内科",
            "description": "周一至周五上午/下午内科门诊排班模板",
            "is_active": True,
        },
        {
            "template_name": "儿科周末门诊模板",
            "department": "儿科",
            "description": "周六上午儿科门诊排班模板",
            "is_active": True,
        },
    ]

    template_map = {}

    for item in template_seed_data:
        existing = DoctorScheduleTemplate.query.filter_by(
            template_name=item["template_name"]
        ).first()

        if existing:
            existing.department = item.get("department", existing.department)
            existing.description = item.get("description", existing.description)
            existing.is_active = item.get("is_active", existing.is_active)
            template = existing
        else:
            template = DoctorScheduleTemplate(
                template_name=item["template_name"],
                department=item.get("department"),
                description=item.get("description"),
                is_active=item.get("is_active", True),
            )
            db.session.add(template)

        template_map[item["template_name"]] = template

    # 确保新建模板拥有 ID
    db.session.flush()

    detail_seed_data = []

    # 内科：周一至周五上午/下午门诊
    for day in range(1, 6):  # 周一到周五
        detail_seed_data.append(
            {
                "template_name": "内科平日门诊模板",
                "day_of_week": day,
                "shift": "morning",
                "start_time": "08:00",
                "end_time": "12:00",
                "max_patients": 30,
            }
        )
        detail_seed_data.append(
            {
                "template_name": "内科平日门诊模板",
                "day_of_week": day,
                "shift": "afternoon",
                "start_time": "14:00",
                "end_time": "17:30",
                "max_patients": 25,
            }
        )

    # 儿科：周六上午门诊
    detail_seed_data.append(
        {
            "template_name": "儿科周末门诊模板",
            "day_of_week": 6,
            "shift": "morning",
            "start_time": "08:30",
            "end_time": "12:00",
            "max_patients": 35,
        }
    )

    for item in detail_seed_data:
        template = template_map.get(item["template_name"])
        if not template or not template.id:
            continue

        existing = DoctorScheduleTemplateDetail.query.filter_by(
            template_id=template.id,
            day_of_week=item["day_of_week"],
            shift=item["shift"],
        ).first()

        if existing:
            existing.start_time = item["start_time"]
            existing.end_time = item["end_time"]
            existing.max_patients = item["max_patients"]
        else:
            detail = DoctorScheduleTemplateDetail(
                template_id=template.id,
                day_of_week=item["day_of_week"],
                shift=item["shift"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                max_patients=item["max_patients"],
            )
            db.session.add(detail)

    print("✓ 排班模板数据导入/更新完成")


PATIENT_SEED_DATA = [
    {
        "patient_no": "P20240001",
        "name": "张三",
        "gender": "男",
        "age": 32,
        "phone": "13500000001",
        "id_card": "110101199001010011",
        "address": "北京市朝阳区幸福路1号",
        "emergency_contact": "李四",
        "emergency_phone": "13500000002",
    },
    {
        "patient_no": "P20240002",
        "name": "李梅",
        "gender": "女",
        "age": 28,
        "phone": "13600000003",
        "id_card": "110101199501020022",
        "address": "北京市海淀区学院路2号",
        "emergency_contact": "王五",
        "emergency_phone": "13600000004",
    },
    {
        "patient_no": "P20240003",
        "name": "小明",
        "gender": "男",
        "age": 6,
        "phone": "13700000005",
        "id_card": "110101201901030033",
        "address": "北京市东城区东大街3号",
        "emergency_contact": "小明妈妈",
        "emergency_phone": "13700000006",
    },
]


APPOINTMENT_SEED_DATA = [
    {
        "appointment_no": "A20240001",
        "patient_no": "P20240001",
        "doctor_no": "D20240001",
        "days_offset": -3,
        "appointment_time": "上午",
        "department": "内科",
        "status": "completed",
        "notes": "首次心内科门诊",
        "diagnosis": "冠心病",
        "symptoms": "胸闷、胸痛，活动后加重",
        "treatment": "建议药物治疗与生活方式干预",
        "prescription": "阿司匹林肠溶片 100mg qd po",
        "record_notes": "需定期复查心电图与血脂",
    },
    {
        "appointment_no": "A20240002",
        "patient_no": "P20240002",
        "doctor_no": "D20240002",
        "days_offset": -1,
        "appointment_time": "下午",
        "department": "外科",
        "status": "completed",
        "notes": "术前评估门诊",
        "diagnosis": "胆囊结石",
        "symptoms": "反复右上腹痛",
        "treatment": "计划择期腹腔镜胆囊切除术",
        "prescription": "头孢克洛胶囊 0.25g bid po",
        "record_notes": "已完成手术风险告知",
    },
    {
        "appointment_no": "A20240003",
        "patient_no": "P20240003",
        "doctor_no": "D20240003",
        "days_offset": 0,
        "appointment_time": "上午",
        "department": "儿科",
        "status": "confirmed",
        "notes": "小儿咳嗽门诊",
        "diagnosis": "上呼吸道感染",
        "symptoms": "咳嗽、流涕3天",
        "treatment": "以对症治疗为主，注意休息和补液",
        "prescription": None,
        "record_notes": "建议一周后复查或症状加重及时就诊",
    },
]


MEDICINE_SEED_DATA = [
    {
        "medicine_no": "M20240001",
        "name": "阿司匹林肠溶片",
        "generic_name": "阿司匹林",
        "category": "心血管用药",
        "specification": "100mg*30片",
        "unit": "盒",
        "manufacturer": "某某制药股份有限公司",
        "price": 18.5,
        "prescription_required": True,
        "usage": "口服，一次1片，一日1次，餐后服用",
        "indications": "用于心肌梗死、脑梗死的二级预防",
        "contraindications": "消化道溃疡、出血倾向者慎用",
        "side_effects": "可能出现胃部不适、出血等",
        "storage_conditions": "密封，在阴凉干燥处保存",
        "status": "active",
    },
    {
        "medicine_no": "M20240002",
        "name": "头孢克洛胶囊",
        "generic_name": "头孢克洛",
        "category": "抗感染药",
        "specification": "0.25g*24粒",
        "unit": "盒",
        "manufacturer": "某某制药集团有限公司",
        "price": 32.0,
        "prescription_required": True,
        "usage": "口服，一次1粒，一日2次，饭前或饭后服用",
        "indications": "适用于敏感菌所致的呼吸道、泌尿道等感染",
        "contraindications": "对头孢类药物过敏者禁用",
        "side_effects": "少数患者可出现恶心、腹泻等",
        "storage_conditions": "密封，在阴凉干燥处保存",
        "status": "active",
    },
]


MEDICATION_REQUEST_SEED_DATA = [
    {
        "patient_no": "P20240001",
        "doctor_no": "D20240001",
        "medicine_no": "M20240001",
        "dose": "100mg",
        "usage": "qd po",
        "quantity": 30,
        "status": "APPROVED",
        "reason": "冠心病二级预防",
    },
    {
        "patient_no": "P20240002",
        "doctor_no": "D20240002",
        "medicine_no": "M20240002",
        "dose": "0.25g",
        "usage": "bid po",
        "quantity": 20,
        "status": "PENDING",
        "reason": "术前预防感染",
    },
]


def _upsert_patients():
    """按 patient_no 幂等导入/更新病人数据，返回 patient_no -> Patient 映射。"""
    print("\n开始导入/更新病人基础数据...")

    patient_map = {}

    for item in PATIENT_SEED_DATA:
        patient_no = item["patient_no"]
        existing = Patient.query.filter_by(patient_no=patient_no).first()

        if existing:
            print(f"[UPDATE] 更新病人 {patient_no} - {existing.name} → {item['name']}")
            for field, value in item.items():
                setattr(existing, field, value)
            patient = existing
        else:
            print(f"[CREATE] 新增病人 {patient_no} - {item.get('name')}")
            patient = Patient(**item)
            db.session.add(patient)

        patient_map[patient_no] = patient

    print("✓ 病人基础数据导入/更新完成")
    return patient_map


def _seed_users_and_links(doctor_map, patient_map):
    """为示例医生和病人创建对应的用户账户及关联关系。"""
    print("\n开始导入/更新用户及账号关联数据...")

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            real_name="系统管理员",
            role="admin",
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        print("[CREATE] 新增管理员账户 admin / admin123")
    else:
        admin.role = "admin"
        admin.is_active = True
        print("[SKIP] 已存在管理员账户 admin，保持原有密码")

    for doctor_no, doctor in doctor_map.items():
        username = f"doctor_{doctor_no.lower()}"
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(
                username=username,
                real_name=doctor.name,
                role="doctor",
                department=doctor.department,
                is_active=True,
            )
            user.set_password("123456")
            db.session.add(user)
            print(f"[CREATE] 新增医生账户 {username} / 123456")
        else:
            user.real_name = doctor.name
            user.role = "doctor"
            user.department = doctor.department
            user.is_active = True
            print(f"[UPDATE] 更新医生账户 {username}")

        link = DoctorUserLink.query.filter_by(user_id=user.id).first()
        if not link:
            link = DoctorUserLink(user=user, doctor=doctor)
            db.session.add(link)

    for patient_no, patient in patient_map.items():
        username = f"patient_{patient_no.lower()}"
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(
                username=username,
                real_name=patient.name,
                role="user",
                department=None,
                is_active=True,
            )
            user.set_password("123456")
            db.session.add(user)
            print(f"[CREATE] 新增病人账户 {username} / 123456")
        else:
            user.real_name = patient.name
            user.role = "user"
            user.is_active = True
            print(f"[UPDATE] 更新病人账户 {username}")

        link = PatientUserLink.query.filter_by(user_id=user.id).first()
        if not link:
            link = PatientUserLink(user=user, patient=patient)
            db.session.add(link)


def _seed_appointments_and_medical_records(doctor_map, patient_map):
    """为示例医生和病人生成挂号预约及病历记录数据。"""
    print("\n开始导入/更新挂号预约及病历数据...")

    today = datetime.utcnow().date()

    for item in APPOINTMENT_SEED_DATA:
        patient = patient_map.get(item["patient_no"])
        doctor = doctor_map.get(item["doctor_no"])
        if not patient or not doctor:
            continue

        appointment_date = datetime(
            year=today.year,
            month=today.month,
            day=today.day,
        ) + timedelta(days=item.get("days_offset", 0))

        existing = Appointment.query.filter_by(
            appointment_no=item["appointment_no"],
        ).first()

        if existing:
            appointment = existing
            appointment.patient_id = patient.id
            appointment.doctor_id = doctor.id
            appointment.appointment_date = appointment_date
            appointment.appointment_time = item.get("appointment_time")
            appointment.department = item.get("department", doctor.department)
            appointment.status = item.get("status", appointment.status)
            appointment.notes = item.get("notes", appointment.notes)
        else:
            appointment = Appointment(
                appointment_no=item["appointment_no"],
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=appointment_date,
                appointment_time=item.get("appointment_time"),
                department=item.get("department", doctor.department),
                status=item.get("status", "completed"),
                notes=item.get("notes"),
            )
            db.session.add(appointment)

        if item.get("diagnosis"):
            record = (
                MedicalRecord.query.filter_by(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    diagnosis=item["diagnosis"],
                )
                .first()
            )

            if record:
                record.symptoms = item.get("symptoms", record.symptoms)
                record.treatment = item.get("treatment", record.treatment)
                record.prescription = item.get("prescription", record.prescription)
                record.notes = item.get("record_notes", record.notes)
            else:
                record = MedicalRecord(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    visit_date=appointment_date,
                    diagnosis=item.get("diagnosis"),
                    symptoms=item.get("symptoms"),
                    treatment=item.get("treatment"),
                    prescription=item.get("prescription"),
                    notes=item.get("record_notes"),
                )
                db.session.add(record)

    print("✓ 挂号预约及病历数据导入/更新完成")


def _seed_medicines_and_inventory():
    """导入/更新药品基础数据及库存数据，返回 medicine_no -> Medicine 映射。"""
    print("\n开始导入/更新药品及库存数据...")

    medicine_map = {}

    for item in MEDICINE_SEED_DATA:
        medicine_no = item["medicine_no"]
        existing = Medicine.query.filter_by(medicine_no=medicine_no).first()

        if existing:
            for field, value in item.items():
                setattr(existing, field, value)
            medicine = existing
        else:
            medicine = Medicine(**item)
            db.session.add(medicine)

        medicine_map[medicine_no] = medicine

    db.session.flush()

    for medicine_no, medicine in medicine_map.items():
        inventory = MedicineInventory.query.filter_by(medicine_id=medicine.id).first()
        if not inventory:
            inventory = MedicineInventory(
                medicine_id=medicine.id,
                quantity=200,
                min_stock=20,
                location="主库房",
            )
            db.session.add(inventory)

    print("✓ 药品及库存数据导入/更新完成")
    return medicine_map


def _seed_medication_requests(doctor_map, patient_map, medicine_map):
    """为示例医生和病人生成用药申请数据。"""
    print("\n开始导入/更新用药申请数据...")

    for item in MEDICATION_REQUEST_SEED_DATA:
        patient = patient_map.get(item["patient_no"])
        doctor = doctor_map.get(item["doctor_no"])
        medicine = medicine_map.get(item["medicine_no"])
        if not patient or not doctor or not medicine:
            continue

        existing = MedicationRequest.query.filter_by(
            patient_id=patient.id,
            doctor_id=doctor.id,
            medicine_id=medicine.id,
        ).first()

        if existing:
            existing.dose = item.get("dose", existing.dose)
            existing.usage = item.get("usage", existing.usage)
            existing.quantity = item.get("quantity", existing.quantity)
            existing.status = item.get("status", existing.status)
            existing.reason = item.get("reason", existing.reason)
        else:
            request = MedicationRequest(
                patient_id=patient.id,
                doctor_id=doctor.id,
                medicine_id=medicine.id,
                dose=item.get("dose"),
                usage=item.get("usage"),
                quantity=item.get("quantity", 0),
                status=item.get("status", "PENDING"),
                reason=item.get("reason"),
            )
            db.session.add(request)

    print("✓ 用药申请数据导入/更新完成")


def seed_doctors() -> None:
    """按 doctor_no 幂等导入/更新医生及其关联示例数据，以及全系统示例数据。"""
    app = create_app()

    with app.app_context():
        print("开始导入/更新示例数据...")

        # 1. 医生与病人基础信息
        doctor_map = _upsert_doctors()
        print("\n✓ 医生基础信息导入/更新完成")
        patient_map = _upsert_patients()

        # 2. 医生子系统关联业务数据
        _seed_schedules(doctor_map)
        _seed_performances(doctor_map)
        _seed_qualifications(doctor_map)
        _seed_leaves(doctor_map)
        _seed_schedule_templates()

        # 3. 用户账户及账号与档案关联
        _seed_users_and_links(doctor_map, patient_map)

        # 4. 挂号预约与病历记录（支撑医生-病人关联、病历页面示例）
        _seed_appointments_and_medical_records(doctor_map, patient_map)

        # 5. 药品、库存及用药申请（支撑药房模块及医生用药申请示例）
        medicine_map = _seed_medicines_and_inventory()
        _seed_medication_requests(doctor_map, patient_map, medicine_map)

        try:
            db.session.commit()
            print("\n✓ 全系统示例数据全部导入/更新完成")
        except Exception as exc:  # pragma: no cover - 仅用于命令行提示
            db.session.rollback()
            print(f"\n✗ 医生数据导入失败: {exc}")
            sys.exit(1)


def main() -> None:
    """脚本入口。"""
    seed_doctors()


if __name__ == "__main__":
    main()
