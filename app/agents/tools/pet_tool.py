from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import crud


@tool
def get_my_pets(user_id: int) -> str:
    """
    查询当前用户的所有宠物档案。适用于：
    - "我家有什么宠物"
    - "我家狗叫什么名字"
    - "我养了几只猫"

    参数:
        user_id: 用户 ID（系统自动传入）

    返回:
        用户的宠物列表（名字、品种、年龄等）
    """
    db: Session = SessionLocal()
    try:
        pets = crud.get_pets_by_user(db, user_id)
        if not pets:
            return "您还没有添加宠物档案。"

        lines = []
        for pet in pets:
            info = f"- {pet.name}（{pet.species}"
            if pet.breed:
                info += f"，{pet.breed}"
            if pet.age:
                info += f"，{pet.age}岁"
            if pet.weight:
                info += f"，{pet.weight}"
            info += "）"
            lines.append(info)
        return "您的宠物：\n" + "\n".join(lines)
    finally:
        db.close()


@tool
def get_pet_info(user_id: int, pet_name: str) -> str:
    """
    查询指定宠物的详细信息。适用于：
    - "小白的疫苗记录"
    - "我家金毛几岁了"
    - "小白的体重"

    参数:
        user_id: 用户 ID（系统自动传入）
        pet_name: 宠物名字

    返回:
        该宠物的详细信息
    """
    db: Session = SessionLocal()
    try:
        pet = crud.get_pet_by_name(db, user_id, pet_name)
        if not pet:
            return f"没有找到叫「{pet_name}」的宠物。"

        info = f"【{pet.name} 的档案】\n"
        info += f"- 种类：{pet.species}\n"
        if pet.breed:
            info += f"- 品种：{pet.breed}\n"
        if pet.age:
            info += f"- 年龄：{pet.age} 岁\n"
        if pet.weight:
            info += f"- 体重：{pet.weight}\n"
        if pet.gender:
            info += f"- 性别：{pet.gender}\n"
        if pet.last_vaccine_date:
            info += f"- 上次疫苗：{pet.last_vaccine_date.strftime('%Y-%m-%d')}\n"
        if pet.notes:
            info += f"- 备注：{pet.notes}\n"
        return info
    finally:
        db.close()