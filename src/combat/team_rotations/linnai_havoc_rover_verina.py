from src.combat.team_rotations.base import TeamRotation, find_char


LHV_PHASES = [
    ("HavocRover", "lhv_rover_open_e"),
    ("Linnai", "lhv_linnai_quick_e"),
    ("Verina", "lhv_verina_full_support"),
    ("Linnai", "lhv_linnai_burst_to_rover"),
    ("HavocRover", "lhv_rover_burst_after_linnai"),
    ("Linnai", "lhv_linnai_quick_e"),
    ("Verina", "lhv_verina_bridge_support"),
    ("HavocRover", "lhv_rover_open_e"),
    ("Verina", "lhv_verina_full_support"),
]

LHV_LOOP_START = 3


class LinnaiHavocRoverVerinaRotation(TeamRotation):
    name = "琳奈湮灭漂泊者维里奈固定轴"
    rotation_attr = "_linnai_havoc_rover_verina_rotation"
    phases = LHV_PHASES
    loop_start = LHV_LOOP_START

    def match(self, task):
        from src.char.BaseChar import Elements
        from src.char.HavocRover import HavocRover
        from src.char.Linnai import Linnai
        from src.char.Verina import Verina

        rover = find_char(task, HavocRover)
        return bool(
            find_char(task, Linnai)
            and find_char(task, Verina)
            and rover
            and rover.ring_index in (-1, Elements.HAVOC)
        )


LINNAI_HAVOC_ROVER_VERINA_ROTATION = LinnaiHavocRoverVerinaRotation()


def is_linnai_havoc_rover_verina_team(task):
    return LINNAI_HAVOC_ROVER_VERINA_ROTATION.match(task)


def ensure_linnai_havoc_rover_verina_rotation(task):
    return LINNAI_HAVOC_ROVER_VERINA_ROTATION.ensure(task)


def get_lhv_phase(task):
    return LINNAI_HAVOC_ROVER_VERINA_ROTATION.get_phase(task)


def advance_lhv_phase(task):
    LINNAI_HAVOC_ROVER_VERINA_ROTATION.advance_phase(task)
