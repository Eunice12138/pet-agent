"""
临时用的内存数据库，模拟用户的存取。
第二步接 MySQL 时，这个文件会被 models.py + crud.py 替代。
"""
from datetime import datetime
from typing import Optional

# 内存里的"用户表"
_users = {}
_next_id = 1


def find_user_by_account(account: str) -> Optional[dict]:
    for user in _users.values():
        if user["account"] == account:
            return user
    return None


def create_user(nickname: str, account: str, password: str) -> dict:
    global _next_id
    user = {
        "id": _next_id,
        "nickname": nickname,
        "account": account,
        "password": password,  # ⚠️ 假数据阶段先明文，第二步一定换哈希
        "created_at": datetime.now(),
    }
    _users[_next_id] = user
    _next_id += 1
    return user


def verify_user(account: str, password: str) -> Optional[dict]:
    user = find_user_by_account(account)
    if user and user["password"] == password:
        return user
    return None