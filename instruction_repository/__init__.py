"""
Instruction Repository - Agent指示管理模块

提供用户自定义指示的增删改查功能，指示会影响Agent的行为和回答风格。
"""

from .db import (
    create_instruction,
    get_active_instructions,
    get_all_instructions,
    get_instruction_by_id,
    update_instruction,
    delete_instruction
)

__all__ = [
    'create_instruction',
    'get_active_instructions',
    'get_all_instructions',
    'get_instruction_by_id',
    'update_instruction',
    'delete_instruction'
]
