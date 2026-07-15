import time

import cv2
import numpy as np

from src.char.BaseChar import BaseChar, SwitchPriority, forte_white_color
from src.combat.team_rotations import advance_lhv_phase, get_lhv_phase, get_rotation_switch_priority, perform_rotation_phase

class Linnai(BaseChar):
    CON_READY_TO_SWITCH = 0.99
    RES_CHECK_THRESHOLD = 0.6
    INTRO_RES_WAIT = 1.0
    AEMEATH_INTRO_RES_WAIT = 1.6
    MORNYE_NAMES = {'char_moning', 'char_moning_new'}
    SECOND_GAUGE_THRESHOLD = 0.12
    JUMP_MARKER_PROGRESS_THRESHOLD = 0.42
    SECOND_GAUGE_JUMP_COUNT = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_heavy = 0

    def do_perform(self):
        if self.linnai_havoc_rover_verina_rotation():
            return
        if self.has_intro:
            if self.is_con_ready_to_switch():
                return self.switch_after_liberation()
            if self.check_res():
                self.continues_normal_attack(1.33, until_con_full=True)
            else:
                self.continues_normal_attack(1, until_con_full=True)
                if self.is_con_ready_to_switch():
                    return self.switch_after_liberation()
                self.click_echo(time_out=0)
                if not self.is_con_ready_to_switch():
                    self.click_liberation()
                if self.is_con_ready_to_switch():
                    return self.switch_after_liberation()
                if not self.is_mouse_forte_full():
                    self.click_resonance()
                if self.is_con_ready_to_switch():
                    return self.switch_after_liberation()
                self.task.wait_until(lambda: self.is_mouse_forte_full() or self.is_con_ready_to_switch(),
                                     post_action=self.click, time_out=2)
                if self.is_con_ready_to_switch():
                    return self.switch_after_liberation()
                self.task.mouse_down() 
                if self.task.wait_until(lambda: not self.is_mouse_forte_full(), time_out=5):
                    self.task.mouse_up()
                    self.sleep(0.4)                 
                    self.perform_under_intro()
                else:
                    self.task.mouse_up()
                
        else: 
            self.click_echo(time_out=0)
            if self.is_con_ready_to_switch():
                pass
            elif self.perform_under_intro():
                return self.switch_after_liberation()
            elif self.flying():
                self.continues_normal_attack(0.1)
            elif not self.is_con_ready_to_switch() and self.click_liberation():
                self.continues_normal_attack(0.5, until_con_full=True)
            if not self.is_con_ready_to_switch():
                self.click_resonance()

        return self.switch_after_liberation()

    def linnai_havoc_rover_verina_rotation(self):
        return perform_rotation_phase(self, get_lhv_phase, advance_lhv_phase)

    def lhv_linnai_quick_e(self):
        if self.flying():
            self.continues_normal_attack(0.1)
        self.click_resonance(time_out=0.5)

    def lhv_linnai_burst_to_rover(self):
        if self.wait_for_accelerate_ready():
            self.click_liberation()
            self.lhv_linnai_fill_concerto()
        else:
            self.charge_heavy()
        self.click_echo(time_out=0)

    def lhv_linnai_fill_concerto(self):
        start = time.time()
        while not self.is_con_ready_to_switch() and time.time() - start < 5.5:
            if self.is_mouse_forte_full():
                self.task.mouse_down()
                self.task.wait_until(lambda: not self.is_mouse_forte_full() or self.is_con_ready_to_switch(),
                                     time_out=1.8)
                self.task.mouse_up()
                self.sleep(0.1)
            elif self.resonance_available():
                if self.click_resonance()[0]:
                    self.wait_after_resonance_kick()
        else:
            self.click(interval=0.1)
        self.check_combat()
        self.task.next_frame()

    def switch_after_liberation(self):
        """琳奈离场优先交棒主 C，不在离场前继续贪大招。"""
        return self.switch_next_char()

    def charge_heavy(self):
        """攒满回路后蓄力重击，放完后接 perform_under_intro。

        无论是否协奏入场都执行；Mornye 不满协奏切来时也要蓄力。
        """
        self.continues_normal_attack(1)
        self.click_echo(time_out=0)
        if not self.is_con_full():
            self.click_liberation()
        if not self.is_mouse_forte_full():
            self.click_resonance()
        self.task.wait_until(self.is_mouse_forte_full, post_action=self.click, time_out=2)
        self.task.mouse_down()
        if self.task.wait_until(lambda: not self.is_mouse_forte_full(), time_out=5):
            self.task.mouse_up()
            self.sleep(0.4)
            self.perform_under_intro()
        else:
            self.task.mouse_up()
            
    def perform_under_intro(self):
        if not self.wait_for_accelerate_ready():
            self.logger.debug(f'Linnai fails entering accelerate mode!')
            return False
        self.task.wait_until(lambda: self.is_color_full() or self.is_con_ready_to_switch(), post_action=self.click,
                                     time_out=1)
        if self.is_con_ready_to_switch():
            return True
        if not self.task.wait_until(lambda: self.is_linnai_second_forte_gauge() or self.is_con_ready_to_switch(),
                                    post_action=self.click, time_out=1):
            if self.is_mouse_forte_full():
                self.charge_heavy()
            return True
        if self.is_con_ready_to_switch():
            return True
        if not self.task.wait_until(lambda: self.is_linnai_jump_energy_ready() or self.is_con_ready_to_switch(),
                                    post_action=self.click, time_out=1.5):
            return True
        self.perform_second_gauge_jumps()
        if self.is_con_ready_to_switch():
            return True
        if self.task.wait_until(lambda: self.is_con_ready_to_switch() or self.click_resonance()[0],
         post_action=self.click, time_out=1):
            if not self.is_con_ready_to_switch():
                self.wait_after_resonance_kick()
        return True

    def is_con_ready_to_switch(self):
        return self.get_current_con() >= self.CON_READY_TO_SWITCH

    def wait_after_resonance_kick(self):
        self.sleep(0.3)
        self.wait_down()

    def perform_second_gauge_jumps(self):
        """琳奈第二管固定执行三跳，保证 Buff 叠满后再交后续动作。"""
        for _ in range(self.SECOND_GAUGE_JUMP_COUNT):
            if not self.is_linnai_second_forte_gauge():
                break
            self.task.wait_until(self.is_linnai_jump_energy_ready, post_action=self.click, time_out=1.5)
            self.task.jump()
            self.task.wait_until(lambda: not self.is_linnai_jump_energy_ready() or not self.is_linnai_second_forte_gauge(),
                                 time_out=0.8)

    def wait_for_accelerate_ready(self):
        """等待琳奈入场后的目标状态稳定，避免特效遮挡导致误判。"""
        if self.check_res():
            return True
        time_out = self.INTRO_RES_WAIT
        if self.has_intro and self.check_outro() in {'char_aemeath'}:
            time_out = self.AEMEATH_INTRO_RES_WAIT
        return self.task.wait_until(self.check_res, post_action=self.click_with_interval, time_out=time_out)

    def get_target_names(self):
        if hasattr(self.task, 'get_target_names'):
            return self.task.get_target_names()
        return 'has_target', 'no_target'

    def find_target_status_in_box(self, box_name):
        try:
            box = self.task.get_box_by_name(box_name)
            return self.task.find_best_match_in_box(box, list(self.get_target_names()),
                                                    threshold=self.RES_CHECK_THRESHOLD)
        except Exception as e:
            self.logger.debug(f'Linnai check res skipped {box_name}: {e}')
            return None

    def check_res(self):
        if not self.task.in_team_and_world():
            return False

        best = self.find_target_status_in_box('target_box_long2')
        if not best:
            best = self.find_target_status_in_box('box_target_enemy_long')
        if not best:
            try:
                best = self.task.find_one('target_box_short', threshold=self.RES_CHECK_THRESHOLD)
            except Exception as e:
                self.logger.debug(f'Linnai check res skipped target_box_short: {e}')
                best = None
        self.logger.debug(f'check res {best}')
        return best

    def is_color_full(self):
        box = self.task.box_of_screen_scaled(5120, 2880, 2846, 2602, 2889, 2690, name='color_full', hcenter=True)
        white_percent = self.task.calculate_color_percentage(forte_white_color, box)
        self.logger.debug(f'forte_color_percent {white_percent}')
        return white_percent > 0.06

    def hsv_color_percentage(self, box, lower, upper, name):
        cropped = box.crop_frame(self.task.frame)
        if cropped.size == 0:
            return 0
        hsv = cv2.cvtColor(cropped[:, :, :3], cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        percent = cv2.countNonZero(mask) / mask.size
        box.confidence = percent
        self.task.draw_boxes(name, box)
        return percent

    def is_linnai_second_forte_gauge(self):
        """识别琳奈第二管 UI，未确认第二管时禁止进入跳跃连段。"""
        box = self.task.box_of_screen_scaled(2560, 1440, 1200, 1280, 1358, 1345,
                                             name='linnai_second_gauge', hcenter=True)
        cyan_percent = self.hsv_color_percentage(box, (80, 50, 80), (105, 255, 255),
                                                 'linnai_second_gauge')
        self.logger.debug(f'Linnai second gauge cyan {cyan_percent}')
        return cyan_percent > self.SECOND_GAUGE_THRESHOLD

    def linnai_jump_marker_progress(self):
        box = self.task.box_of_screen_scaled(2560, 1440, 1040, 1295, 1505, 1330,
                                             name='linnai_jump_marker', hcenter=True)
        cropped = box.crop_frame(self.task.frame)
        if cropped.size == 0:
            return 0
        hsv = cv2.cvtColor(cropped[:, :, :3], cv2.COLOR_BGR2HSV)
        marker = cv2.inRange(hsv, np.array([130, 50, 100]), np.array([170, 255, 255]))
        ys, xs = np.where(marker > 0)
        if len(xs) < 8:
            box.confidence = 0
            self.task.draw_boxes('linnai_jump_marker', box)
            return 0
        progress = float(np.median(xs)) / max(box.width, 1)
        box.confidence = progress
        self.task.draw_boxes('linnai_jump_marker', box)
        self.logger.debug(f'Linnai jump marker progress {progress}')
        return progress

    def is_linnai_jump_energy_ready(self):
        if not self.is_linnai_second_forte_gauge():
            return False
        return self.linnai_jump_marker_progress() >= self.JUMP_MARKER_PROGRESS_THRESHOLD

    def on_combat_end(self, chars):
        self.switch_other_char()

    def get_switch_priority(self, current_char=None, has_intro=False, target_low_con=False):
        priority = get_rotation_switch_priority(self, get_lhv_phase)
        if priority is not None:
            return priority
        # Mornye 离场就强制切 Linnai
        if current_char and current_char.char_name in self.MORNYE_NAMES:
            return SwitchPriority.MUST
        return super().get_switch_priority(current_char, has_intro, target_low_con)
