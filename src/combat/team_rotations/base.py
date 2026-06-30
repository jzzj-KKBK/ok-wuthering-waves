class TeamRotation:
    """特定配队固定轴基类，负责阶段状态的保存和推进。"""

    name = ""
    rotation_attr = ""
    phases = []
    loop_start = 0

    def match(self, task):
        return False

    def ensure(self, task):
        if not self.match(task):
            return None
        rotation = getattr(task, self.rotation_attr, None)
        if rotation is None:
            rotation = {"phase": 0}
            setattr(task, self.rotation_attr, rotation)
        return rotation

    def get_phase(self, task):
        rotation = self.ensure(task)
        if rotation is None:
            return None
        phase = rotation.get("phase", 0)
        if phase < 0 or phase >= len(self.phases):
            phase = self.loop_start
            rotation["phase"] = phase
        return self.phases[phase]

    def advance_phase(self, task):
        rotation = self.ensure(task)
        if rotation is None:
            return
        phase = rotation.get("phase", 0) + 1
        if phase >= len(self.phases):
            phase = self.loop_start
        rotation["phase"] = phase


def find_char(task, char_cls):
    if hasattr(task, "has_char"):
        return task.has_char(char_cls)
    return next((char for char in getattr(task, "chars", []) if isinstance(char, char_cls)), None)


def is_rotation_target(char, expected_char):
    return any(cls.__name__ == expected_char for cls in char.__class__.mro())


def perform_rotation_phase(char, phase_getter, phase_advancer, wait_down=False, wait_down_if_flying=False):
    phase = phase_getter(char.task)
    if phase is None:
        return False
    expected_char, action = phase
    if not is_rotation_target(char, expected_char):
        char.switch_next_char()
        return True
    if wait_down or (wait_down_if_flying and char.flying()):
        char.wait_down()
    getattr(char, action)()
    phase_advancer(char.task)
    char.switch_next_char()
    return True


def get_rotation_switch_priority(char, phase_getter):
    phase = phase_getter(char.task)
    if phase is None:
        return None
    expected_char, _ = phase
    from src.char.BaseChar import SwitchPriority
    if is_rotation_target(char, expected_char):
        return SwitchPriority.MUST
    return SwitchPriority.NO
