from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import crud


@tool
def get_my_appointments(user_id: int) -> str:
    """
    查询当前用户的所有预约记录。适用于：
    - "我有哪些预约"
    - "我的预约历史"

    参数:
        user_id: 用户 ID（系统自动传入）

    返回:
        用户的预约列表
    """
    db: Session = SessionLocal()
    try:
        appointments = crud.get_appointments_by_user(db, user_id)
        if not appointments:
            return "您还没有任何预约记录。"

        lines = []
        for appt in appointments:
            lines.append(
                f"- {appt.service_type} | "
                f"{appt.appointment_time.strftime('%Y-%m-%d %H:%M')} | "
                f"状态：{appt.status}"
            )
        return "您的预约：\n" + "\n".join(lines)
    finally:
        db.close()


@tool
def get_upcoming_appointments(user_id: int) -> str:
    """
    查询当前用户未来的预约。适用于：
    - "我下次预约是什么时候"
    - "我最近要做什么"

    参数:
        user_id: 用户 ID（系统自动传入）

    返回:
        未来的预约列表
    """
    db: Session = SessionLocal()
    try:
        appointments = crud.get_upcoming_appointments(db, user_id)
        if not appointments:
            return "您没有未来的预约。"

        lines = []
        for appt in appointments:
            lines.append(
                f"- {appt.service_type} | "
                f"{appt.appointment_time.strftime('%Y-%m-%d %H:%M')} | "
                f"状态：{appt.status}"
            )
        return "您未来的预约：\n" + "\n".join(lines)
    finally:
        db.close()