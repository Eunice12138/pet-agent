from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(50), nullable=False)
    account = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, account={self.account})>"

class Conversation(Base):
    """会话表：一次聊天 = 一个会话"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class Message(Base):
    """消息表：每条消息"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "human" / "ai"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"

class Pet(Base):
    """宠物档案表"""
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    species = Column(String(20), nullable=False)   # 狗 / 猫
    breed = Column(String(50), nullable=True)      # 金毛 / 布偶
    age = Column(Integer, nullable=True)           # 年龄（岁）
    weight = Column(String(20), nullable=True)     # 体重（如 "25kg"）
    gender = Column(String(10), nullable=True)     # 公 / 母
    last_vaccine_date = Column(DateTime, nullable=True)  # 上次疫苗日期
    notes = Column(Text, nullable=True)            # 备注
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Pet(id={self.id}, name={self.name}, species={self.species})>"


class Appointment(Base):
    """预约记录表"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    pet_id = Column(Integer, nullable=True)
    service_type = Column(String(50), nullable=False)   # 洗澡 / 美容 / 寄养
    appointment_time = Column(DateTime, nullable=False) # 预约时间
    status = Column(String(20), default="pending")      # pending / confirmed / done / canceled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Appointment(id={self.id}, service={self.service_type})>"