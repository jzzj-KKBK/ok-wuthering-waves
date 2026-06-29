import time
from decimal import Decimal, ROUND_UP, ROUND_HALF_UP
from enum import Enum
from typing import Callable
import cv2
import numpy as np
import math

from src.char.BaseChar import BaseChar, SwitchPriority, forte_white_color
from ok import color_range_to_bound

class State(Enum):
    FORTE_FULL = 1
    CON_FULL = 2
    DONE = 3
    FAILED = 4
    INTERRUPTED = 5


class Zani(BaseChar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intro_motion_freeze_duration = 1.42
        self.liberation_time = 0
        self.in_liberation = False
        self.blazes = -1
        self.blazes_threshold = -1
        self.char_phoebe = None
        self.crisis_time = -1
        self.nightfall_time = -1
        self.state = 0
        self.chair_time = -1
        self.last_liber2 = -1
        self.dodge_time = -1
        self.attack_breakthrough_time = -1
        self.check_f_on_switch = False

    def reset_state(self):
        self.char_phoebe = None
        self.blazes_threshold = -1
        self.chair_time = -1
        super().reset_state()

    def do_perform(self):
        if self.blazes_threshold == -1:
            self.decide_teammate()

        self.wait_down()
        self.check_liber()

        if self.in_liberation:
            self.logger.info('in liberation')
            self.state = 1
            if self.should_end_liberation():
                self.click_liber2()
            else:
                self.nightfall_combo()
            return self.switch_next_char()

        self.state = 0
        self.f_break()
        self.crisis_time = -1

        self.update_blazes()
        forte_full = self.is_e_forte_full()
        e_available = self.current_resonance() > 0.05
        liber_avail = self.liberation_available()
        if self.has_intro and self.blazes >= 1 and not liber_avail:
            self.sleep(0.2, check_combat=False)
            liber_avail = self.liberation_available()
            e_available = self.current_resonance() > 0.05
        predicted = float(self.blazes) + 0.1

        self.logger.info(
            f'Zani entry: blazes={self.blazes} threshold={self.blazes_threshold} '
            f'forte_full={forte_full} e_avail={e_available} predicted={predicted:.2f} '
            f'liber_avail={liber_avail} has_intro={self.has_intro}'
        )

        if self.blazes >= 1 and liber_avail:
            self.logger.info('scene3: blazes full, liberation available, direct liberation')
            if not self._try_liberation():
                self.sleep(0.1)
                self._try_liberation()
            return self.switch_next_char()

        if forte_full:
            self.logger.info(f'scene4: enhanced E ready, predicted={predicted:.2f}')
            should_liberate = predicted >= self.blazes_threshold
            success = self.crisis_response_protocol_combo()
            if success and should_liberate and self.liberation_available():
                self.logger.info('scene4: enhanced E -> liberate')
                self._try_liberation(wait_crisis=True)
            else:
                self.logger.info('scene4: enhanced E -> switch')
            return self.switch_next_char()

        if e_available:
            self.logger.info(f'scene1: normal E available, predicted={predicted:.2f}')
            success = self.crisis_response_protocol_combo()
            if success and self.blazes >= self.blazes_threshold:
                if self.liberation_available():
                    self.logger.info('scene1: liberate after enhanced E')
                    self._try_liberation(wait_crisis=True)
            return self.switch_next_char()

        self.logger.info('scene2: E on CD, normal attack until can switch')
        self.normal_attack_until_can_switch()
        return self.switch_next_char()

    def _try_liberation(self, wait_crisis=False):
        if wait_crisis:
            self.wait_crisis_protocol_end()
            self.update_blazes()
        if self.echo_available():
            self.click_echo(time_out=0)
        if self.click_liberation(send_click=True):
            self._liberation_followup()
            return True
        return False

    def _liberation_followup(self):
        self.crisis_time = -1
        self.state = 1
        self.in_liberation = True
        self.liberation_time = time.time()
        self.check_liber()
        self.continues_right_click(0.05)
        self.continues_normal_attack(0.15)
        self.nightfall_combo(cancel_last_smash=True)
        self.sleep(0.1)
        if self.is_mouse_forte_full():
            self.nightfall_combo()

    def basic_attack_breakthrough_combo(self):
        if self.is_e_forte_full():
            return State.FORTE_FULL
        self.logger.info('basic attack - breakthrough')
        if (result := self.basic_attack_breakthrough()) != State.DONE:
            return result
        self.attack_breakthrough_time = time.time()
        return State.DONE

    def click_liber2(self):
        start = time.time()
        self.task.in_liberation = True
        send_key = True
        not_liber_box = self.task.box_of_screen_scaled(2560, 1440, 1909, 1274, 1957, 1322, name='zani_not_liber_box', hcenter=True)
        while not self.task.find_one('box_target_enemy_inner', box=not_liber_box, threshold=0.75):
            if time.time() - start > 6:
                self.task.in_liberation = False
                if not self.check_liber():
                    self.update_blazes()
                return
            if self.current_resonance() == 0:
                start = time.time()
            elif time.time() - start > 1.5:
                send_key = False
            if send_key:
                self.send_liberation_key()
            self.task.next_frame()
        self.task.in_liberation = False
        current = time.time()
        duration = 2.25
        if current - start >= duration:
            self.last_liber2 = current
            self.add_freeze_duration(current - duration, duration, 0)
            self.logger.info('clicked liber2')
        self.in_liberation = False
        self.blazes = -1
        self.liberation_time = -1
        self.state = 0

    def should_end_liberation(self, time_only=False):
        if self.liberation_time_left() < 1.7:
            self.logger.info('Liberation is about to end, perform liberation2')
            return True
        if time_only or self.is_nightfall_ready():
            return False
        if self.wait_resonance_not_gray(send_click=True, liber_time_check=True) == State.INTERRUPTED:
            self.logger.info('Nightfall interrupted, perform liberation2')
            return True
        if not self.is_mouse_forte_full():
            self.logger.info('Cannot perform another nightfall, perform liberation2')
            return True
        return False

    def liberation_time_left(self):
        if not self.in_liberation or self.liberation_time <= 0:
            return 0
        result = 20 - self.time_elapsed_accounting_for_freeze(self.liberation_time)
        self.logger.debug(f'liberation_lasted: {result}')
        return result

    def nightfall_combo(self, cancel_last_smash=False):
        self.logger.info('perform nightfall_combo')
        start = time.time()
        if not self.is_nightfall_ready():
            self.wait_nightfall_ready()
        self.perform_nightfall(cancel_last_smash=cancel_last_smash)

    def update_blazes(self):
        self.blazes = self.calculate_blazes()

    def decide_teammate(self):
        from src.char.Phoebe import Phoebe
        if char := self.task.has_char(Phoebe):
            self.char_phoebe = char
            self.blazes_threshold = 0.9
        else:
            self.blazes_threshold = 0.8

    def calculate_blazes(self):
        box = self.task.box_of_screen_scaled(2560, 1440, 600, 1300, 700, 1400, name='blazes', hcenter=False)
        cropped = box.crop_frame(self.task.frame)
        lower, upper = color_range_to_bound(forte_white_color)
        mask = cv2.inRange(cropped, lower, upper)
        white_pixels = cv2.countNonZero(mask)
        total_pixels = mask.size
        percent = white_pixels / total_pixels
        if percent > 0.5:
            return 1.0
        elif percent > 0.2:
            return 0.9
        else:
            return 0.0

    def check_liber(self):
        if self.liberation_available():
            self.in_liberation = True

    def get_state(self):
        if self.in_liberation:
            return 1
        return 0

    def is_e_forte_full(self):
        return self.is_forte_full()

    def crisis_response_protocol_combo(self):
        self.logger.info('crisis_response_protocol_combo')
        return State.DONE

    def wait_crisis_protocol_end(self):
        self.sleep(0.5)

    def normal_attack_until_can_switch(self):
        self.continues_normal_attack(1.0)

    def f_break(self, check_f_on_switch=False):
        pass

    def is_nightfall_ready(self):
        return True

    def wait_nightfall_ready(self):
        self.sleep(0.5)

    def perform_nightfall(self, cancel_last_smash=False):
        self.sleep(1.0)
