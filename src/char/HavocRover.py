import time
from ok import Logger
from src.char.BaseChar import BaseChar, Elements
from src.combat.team_rotations import (
    advance_lhv_phase,
    advance_zpr_phase,
    get_lhv_phase,
    get_zpr_phase,
    get_rotation_switch_priority,
    perform_rotation_phase,
)

_ROVER_FORM_NAMES = {
    Elements.SPECTRO: 'Rover: Spectro',
    Elements.WIND: 'Rover: Aero',
    Elements.HAVOC: 'Rover: Havoc',
}


class HavocRover(BaseChar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger(__name__)

    def do_perform(self):
        self.init()
        if not self.has_intro:
            self.sleep(0.01)
        if self.linnai_havoc_rover_verina_rotation():
            return
        if self.zani_phoebe_rover_rotation():
            return
        if self.ring_index == Elements.HAVOC:
            self.intro_motion_freeze_duration = 0.64
            self.perform_havoc_routine()
        elif self.ring_index == Elements.SPECTRO:
            self.perform_spectro_routine()
        else:
            self.perform_basic_routine()
        self.switch_next_char()

    def init(self):
        if self.ring_index == -1:
            self.task._ensure_ring_index()

    def perform_havoc_routine(self):
        self.continues_normal_attack(1.8)
        self._try_resonance_with_liberation_if_available()
        self.continues_normal_attack(0.8)
        self._try_resonance_with_liberation_if_available()
        self.continues_normal_attack(0.5)
        self._try_resonance_with_liberation_if_available()

    def perform_spectro_routine(self):
        self.continues_normal_attack(0.9)
        self.spectro_routine_aftertune_combo()
        self._try_resonance_with_liberation_if_available()
        self.continues_normal_attack(0.8)
        self.spectro_routine_aftertune_combo()
        self._try_resonance_with_liberation_if_available()

    def perform_basic_routine(self):
        self.continues_normal_attack(2.0)
        self._try_resonance_with_liberation_if_available()

    def spectro_routine_aftertune_combo(self):
        if self.is_forte_full():
            self.send_heavy_attack(duration=0.35)
        else:
            self.continues_normal_attack(0.5)

    def _try_resonance_with_liberation_if_available(self):
        if self.resonance_available() and self.liberation_available():
            self.send_liberation_key()
        if self.resonance_available():
            self.click_resonance()


    def zani_phoebe_rover_rotation(self):
        return perform_rotation_phase(self, get_zpr_phase, advance_zpr_phase, wait_down=True)

    def rover_r(self):
        self.click_echo(time_out=0)

    def rover_e(self):
        self.click_resonance(send_click=False, time_out=0.4)

    def rover_e_q(self):
        self.click_resonance(send_click=False, time_out=0.4)
        self.click_liberation(send_click=True)

    def rover_a(self):
        self.continues_normal_attack(0.25)

    def rover_a_z_a(self):
        self.continues_normal_attack(0.2)
        self.spectro_routine_aftertune_combo()

    def rover_a_z_a_r(self):
        self.rover_a_z_a()
        self.click_echo(time_out=0)

    def rover_a_z_a_e_q(self):
        self.rover_a_z_a()
        self.click_resonance(send_click=False, time_out=0.4)
        self.click_liberation(send_click=True)

    def linnai_havoc_rover_verina_rotation(self):
        return perform_rotation_phase(self, get_lhv_phase, advance_lhv_phase)

    def lhv_rover_open_e(self):
        self.init()
        self.click_resonance(send_click=False, time_out=0.4)

    def lhv_rover_burst_after_linnai(self):
        self.init()
        self.click_resonance(send_click=False, time_out=0.4)
        if not self.heavy_click_forte(check_fun=self.is_mouse_forte_full):
            self.heavy_attack(0.35)
        self.click_echo(time_out=0)
        self.click_liberation(send_click=True)
        self.click_resonance(send_click=False, time_out=0.4)
        self.lhv_rover_empty_forte()

    def lhv_rover_empty_forte(self):
        start = time.time()
        empty_start = 0
        while time.time() - start < 3.2:
            if self.is_mouse_forte_full():
                empty_start = 0
                self.heavy_click_forte(check_fun=self.is_mouse_forte_full)
            else:
                if empty_start == 0:
                    empty_start = time.time()
                if time.time() - empty_start > 0.5:
                    break
                self.click(interval=0.1)
            self.check_combat()
            self.task.next_frame()
    def get_switch_priority(self, current_char=None, has_intro=False, target_low_con=False):
        priority = get_rotation_switch_priority(self, get_lhv_phase)
        if priority is not None:
            return priority
        priority = get_rotation_switch_priority(self, get_zpr_phase)
        if priority is not None:
            return priority
        return super().get_switch_priority(current_char, has_intro, target_low_con)
