from src.combat.team_rotations.base import get_rotation_switch_priority, perform_rotation_phase
from src.combat.team_rotations.cartethyia_qiuyuan_chisa import (
    CQC_LOOP_START,
    CQC_PHASES,
    advance_cqc_phase,
    ensure_cartethyia_qiuyuan_chisa_rotation,
    get_cqc_phase,
    is_cartethyia_qiuyuan_chisa_team,
)
from src.combat.team_rotations.linnai_havoc_rover_verina import (
    LHV_LOOP_START,
    LHV_PHASES,
    advance_lhv_phase,
    ensure_linnai_havoc_rover_verina_rotation,
    get_lhv_phase,
    is_linnai_havoc_rover_verina_team,
)
from src.combat.team_rotations.registry import ROTATIONS, match_team_rotation
from src.combat.team_rotations.zani_phoebe_rover import (
    ZPR_LOOP_START,
    ZPR_PHASES,
    advance_zpr_phase,
    ensure_zani_phoebe_rover_rotation,
    get_zpr_phase,
    is_zani_phoebe_rover_team,
)
