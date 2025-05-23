import re
import json
import os
from pathlib import Path
import hashlib
import logging
from typing import Optional, Dict, Tuple

class AccountManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data/accounts")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.accounts_file = self.data_dir / "accounts.json"
        self.accounts: Dict[str, str] = self._load_accounts()

    def _load_accounts(self) -> Dict[str, str]:
        """加载已存在的账号信息"""
        if not self.accounts_file.exists():
            return {}
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载账号文件失败: {e}")
            return {}

    def _save_accounts(self) -> bool:
        """保存账号信息到文件"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存账号文件失败: {e}")
            return False

    def _hash_password(self, password: str) -> str:
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _validate_username(self, username: str) -> bool:
        """验证用户名格式"""
        pattern = r'^[a-zA-Z0-9_]{3,16}$'
        return bool(re.match(pattern, username))

    def register(self, username: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        注册新账号
        
        Args:
            username: 用户名
            password: 密码
            confirm_password: 确认密码
            
        Returns:
            (成功标志, 消息)
        """
        # 验证用户名格式
        if not self._validate_username(username):
            return False, "用户名只能包含英文、数字和下划线，长度3-16位"

        # 检查用户名是否已存在
        if username in self.accounts:
            return False, "用户名已存在"

        # 验证密码匹配
        if password != confirm_password:
            return False, "两次输入的密码不匹配"

        # 密码长度检查
        if len(password) < 6:
            return False, "密码长度不能小于6位"

        # 保存账号信息
        self.accounts[username] = self._hash_password(password)
        if self._save_accounts():
            return True, "注册成功"
        return False, "注册失败，请稍后重试"