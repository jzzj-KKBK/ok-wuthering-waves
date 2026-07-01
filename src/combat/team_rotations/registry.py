from src.combat.team_rotations.cartethyia_qiuyuan_chisa import CARTETHYIA_QIUYUAN_CHISA_ROTATION
from src.combat.team_rotations.linnai_havoc_rover_verina import LINNAI_HAVOC_ROVER_VERINA_ROTATION
from src.combat.team_rotations.zani_phoebe_rover import ZANI_PHOEBE_ROVER_ROTATION


ROTATIONS = [
    LINNAI_HAVOC_ROVER_VERINA_ROTATION,
    ZANI_PHOEBE_ROVER_ROTATION,
    CARTETHYIA_QIUYUAN_CHISA_ROTATION,
]


def match_team_rotation(task):
    """返回当前队伍命中的特定配队固定轴；未命中时返回 None。"""
    for rotation in ROTATIONS:
        if rotation.match(task):
            return rotation
    return None


def clear_team_rotations(task):
    """清理所有固定轴状态，避免下一场战斗继承上一场 phase。"""
    for rotation in ROTATIONS:
        rotation.clear(task)


def activate_team_rotation(task):
    """战斗开始时激活一次固定轴，整场战斗不再动态重判。"""
    clear_team_rotations(task)
    rotation = match_team_rotation(task)
    task.team_rotation = rotation
    if rotation is not None:
        rotation.reset(task)
    return rotation
