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
