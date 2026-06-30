from src.combat.team_rotations.base import TeamRotation, find_char


CQC_PHASES = [
    ("Chisa", "cqc_chisa_e"),
    ("Cartethyia", "cqc_cart_e_r_e_e"),
    ("Chisa", "cqc_chisa_a"),
    ("Qiuyuan", "cqc_qiuyuan_aae_jump_a"),
    ("Chisa", "cqc_chisa_a3"),
    ("Cartethyia", "cqc_cart_a3_a4"),
    ("Chisa", "cqc_chisa_a4"),
    ("Qiuyuan", "cqc_qiuyuan_aae_jump_z"),
    ("Cartethyia", "cqc_cart_a5_r1"),
    ("Chisa", "cqc_chisa_r_e"),
    ("Cartethyia", "cqc_cart_a3"),
    ("Qiuyuan", "cqc_qiuyuan_r"),
    ("Chisa", "cqc_chisa_z2_dodge_a3"),
    ("Cartethyia", "cqc_cart_a4_z_q"),
    ("Chisa", "cqc_chisa_a4"),
    ("Cartethyia", "cqc_cart_drop_a_z_e3_a_e_e_r"),
]

CQC_LOOP_START = 0


class CartethyiaQiuyuanChisaRotation(TeamRotation):
    name = "卡提希娅秋水炽霞固定轴"
    rotation_attr = "_cartethyia_qiuyuan_chisa_rotation"
    phases = CQC_PHASES
    loop_start = CQC_LOOP_START

    def match(self, task):
        from src.char.Cartethyia import Cartethyia
        from src.char.Chisa import Chisa
        from src.char.Qiuyuan import Qiuyuan

        return bool(
            find_char(task, Cartethyia)
            and find_char(task, Qiuyuan)
            and find_char(task, Chisa)
        )


CARTETHYIA_QIUYUAN_CHISA_ROTATION = CartethyiaQiuyuanChisaRotation()


def is_cartethyia_qiuyuan_chisa_team(task):
    return CARTETHYIA_QIUYUAN_CHISA_ROTATION.match(task)


def ensure_cartethyia_qiuyuan_chisa_rotation(task):
    return CARTETHYIA_QIUYUAN_CHISA_ROTATION.ensure(task)


def get_cqc_phase(task):
    return CARTETHYIA_QIUYUAN_CHISA_ROTATION.get_phase(task)


def advance_cqc_phase(task):
    CARTETHYIA_QIUYUAN_CHISA_ROTATION.advance_phase(task)
