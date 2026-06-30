from src.combat.team_rotations.base import TeamRotation, find_char


ZPR_PHASES = [
    ("Phoebe", "phoebe_long_e_r_e_q"),
    ("Zani", "zani_e_a"),
    ("HavocRover", "rover_r"),
    ("Zani", "zani_a"),
    ("Phoebe", "phoebe_aaa_dodge_aaa_dodge_aaa_z"),
    ("Zani", "zani_e"),
    ("Phoebe", "phoebe_aaa"),
    ("Zani", "zani_q_r_aaa"),
    ("HavocRover", "rover_a_z_a_e_q"),
    ("Zani", "zani_aaa"),
    ("Phoebe", "phoebe_z"),
    ("HavocRover", "rover_a_z_a"),
    ("Zani", "zani_aaa"),
    ("HavocRover", "rover_e"),
    ("Phoebe", "phoebe_intro"),
    ("HavocRover", "rover_r"),
    ("Zani", "zani_aa"),
    ("Phoebe", "phoebe_long_e_r_e_q"),
    ("Zani", "zani_a"),
    ("HavocRover", "rover_a_z_a"),
    ("Zani", "zani_r_e_a"),
    ("HavocRover", "rover_e"),
    ("Phoebe", "phoebe_aaa_dodge_z_dodge_aaa_f"),
    ("Zani", "zani_e_q_r_aaa"),
    ("HavocRover", "rover_e_q"),
    ("Phoebe", "phoebe_z"),
    ("HavocRover", "rover_a"),
    ("Zani", "zani_aaa"),
    ("HavocRover", "rover_a_z_a_r"),
    ("Phoebe", "phoebe_intro"),
    ("Zani", "zani_aaa"),
    ("HavocRover", "rover_e"),
    ("Phoebe", "phoebe_e_dodge_long_e_r_q"),
    ("Zani", "zani_aaa"),
    ("HavocRover", "rover_a_z_a"),
    ("Zani", "zani_r_e_a"),
]

ZPR_LOOP_START = 21


class ZaniPhoebeRoverRotation(TeamRotation):
    name = "赞妮菲比漂泊者固定轴"
    rotation_attr = "_zani_phoebe_rover_rotation"
    phases = ZPR_PHASES
    loop_start = ZPR_LOOP_START

    def match(self, task):
        from src.char.BaseChar import Elements
        from src.char.HavocRover import HavocRover
        from src.char.Phoebe import Phoebe
        from src.char.Zani import Zani

        rover = find_char(task, HavocRover)
        return bool(
            find_char(task, Zani)
            and find_char(task, Phoebe)
            and rover
            and rover.ring_index in (-1, Elements.SPECTRO)
        )


ZANI_PHOEBE_ROVER_ROTATION = ZaniPhoebeRoverRotation()


def is_zani_phoebe_rover_team(task):
    return ZANI_PHOEBE_ROVER_ROTATION.match(task)


def ensure_zani_phoebe_rover_rotation(task):
    return ZANI_PHOEBE_ROVER_ROTATION.ensure(task)


def get_zpr_phase(task):
    return ZANI_PHOEBE_ROVER_ROTATION.get_phase(task)


def advance_zpr_phase(task):
    ZANI_PHOEBE_ROVER_ROTATION.advance_phase(task)
