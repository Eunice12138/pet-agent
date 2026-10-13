from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import Conversation, Message
from app.db.models import User
from app.core.security import hash_password, verify_password
from app.db.models import Pet, Appointment

def get_user_by_account(db: Session, account: str) -> Optional[User]:
    return db.query(User).filter(User.account == account).first()


def create_user(db: Session, nickname: str, account: str, password: str) -> User:
    user = User(
        nickname=nickname,
        account=account,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, account: str, password: str) -> Optional[User]:
    user = get_user_by_account(db, account)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()




def get_or_create_conversation(db: Session, user_id: int) -> Conversation:
    """获取或创建用户的最新会话"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if conversation is None:
        conversation = Conversation(user_id=user_id, title="新会话")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    """添加一条消息"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(db: Session, conversation_id: int, limit: int = 20) -> list:
    """获取会话最近 N 条消息（按时间正序）"""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(messages))




# ========== Pet CRUD ==========

def get_pets_by_user(db: Session, user_id: int) -> list:
    """查用户的所有宠物"""
    return db.query(Pet).filter(Pet.user_id == user_id).all()


def get_pet_by_name(db: Session, user_id: int, name: str) -> Pet:
    """按名字查用户的宠物"""
    return (
        db.query(Pet)
        .filter(Pet.user_id == user_id, Pet.name == name)
        .first()
    )


def create_pet(
    db: Session,
    user_id: int,
    name: str,
    species: str,
    breed: str = None,
    age: int = None,
    weight: str = None,
    gender: str = None,
) -> Pet:
    """创建宠物档案"""
    pet = Pet(
        user_id=user_id,
        name=name,
        species=species,
        breed=breed,
        age=age,
        weight=weight,
        gender=gender,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


# ========== Appointment CRUD ==========

def get_appointments_by_user(db: Session, user_id: int) -> list:
    """查用户的所有预约"""
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == user_id)
        .order_by(Appointment.appointment_time.desc())
        .all()
    )


def get_upcoming_appointments(db: Session, user_id: int) -> list:
    """查用户未来的预约（未完成）"""
    from datetime import datetime
    return (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user_id,
            Appointment.appointment_time >= datetime.now(),
            Appointment.status.in_(["pending", "confirmed"]),
        )
        .order_by(Appointment.appointment_time.asc())
        .all()
    )


def create_appointment(
    db: Session,
    user_id: int,
    service_type: str,
    appointment_time,
    pet_id: int = None,
    notes: str = None,
) -> Appointment:
    """创建预约"""
    appointment = Appointment(
        user_id=user_id,
        pet_id=pet_id,
        service_type=service_type,
        appointment_time=appointment_time,
        notes=notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment