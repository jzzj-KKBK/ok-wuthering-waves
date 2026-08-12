"""TermiteRS 发布前使用的轻量行为回归测试。"""

import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_source_module(name, relative_path, dependencies):
    """在替换平台依赖后，直接加载指定业务模块。"""
    spec = importlib.util.spec_from_file_location(name, PROJECT_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, dependencies):
        spec.loader.exec_module(module)
    return module


class TestMaintenanceGate(unittest.TestCase):
    """覆盖个人补丁最容易在上游 rebase 后失效的行为。"""

    def test_aemeath_enhance_e_uses_recorded_resonance_time(self):
        class BaseChar:
            def __init__(self, task, index):
                self.task = task
                self.index = index
                self.last_res = -1

            def time_elapsed_accounting_for_freeze(self, start, intro_motion_freeze=False):
                return time.time() - start

            def record_resonance_use(self):
                self.last_res = time.time()

            def send_resonance_key(self):
                self.task.keys.append('e')

            def sleep(self, _seconds, check_combat=True):
                return None

        base_char_module = types.ModuleType('src.char.BaseChar')
        base_char_module.BaseChar = BaseChar
        module = load_source_module(
            'maintenance_aemeath',
            'src/char/Aemeath.py',
            {'src.char.BaseChar': base_char_module},
        )

        class Task:
            def __init__(self):
                self.keys = []

            def find_one(self, template, threshold=None):
                return template == 'aemeath_e1'

        aemeath = module.Aemeath(Task(), 0)
        self.assertTrue(aemeath.click_enhance_e_once())
        self.assertFalse(aemeath.click_enhance_e_once())
        self.assertEqual(aemeath.task.keys, ['e'])

    def test_auto_combat_keeps_running_after_team_reload(self):
        class TriggerTask:
            pass

        class Logger:
            @staticmethod
            def get_logger(_name):
                return types.SimpleNamespace(info=lambda *_args, **_kwargs: None)

        class BaseCombatTask:
            pass

        class NotInCombatException(Exception):
            pass

        class CharDeadException(Exception):
            pass

        ok_module = types.ModuleType('ok')
        ok_module.TriggerTask = TriggerTask
        ok_module.Logger = Logger
        ok_module.run_task = lambda *_args, **_kwargs: None
        config_module = types.ModuleType('config')
        config_module.config = {}
        char_factory_module = types.ModuleType('src.char.CharFactory')
        char_factory_module.char_names = []
        scene_module = types.ModuleType('src.scene.WWScene')
        scene_module.WWScene = object
        combat_module = types.ModuleType('src.task.BaseCombatTask')
        combat_module.BaseCombatTask = BaseCombatTask
        combat_module.NotInCombatException = NotInCombatException
        combat_module.CharDeadException = CharDeadException
        module = load_source_module(
            'maintenance_auto_combat',
            'src/task/AutoCombatTask.py',
            {
                'ok': ok_module,
                'config': config_module,
                'src.char.CharFactory': char_factory_module,
                'src.scene.WWScene': scene_module,
                'src.task.BaseCombatTask': combat_module,
            },
        )

        events = []
        combat = module.AutoCombatTask.__new__(module.AutoCombatTask)
        combat.scene = types.SimpleNamespace(in_team=lambda _check: True)
        combat.config = {'Use Liberation': True}
        combat.warm_up_char_features = lambda: None
        combat.in_team_and_world = lambda: True
        combat.in_world = lambda: True
        combat.load_chars = lambda **_kwargs: True
        combat.switch_healer = lambda: events.append('switch_healer')
        combat.combat_end = lambda: events.append('combat_end')
        combat.get_current_char = lambda: types.SimpleNamespace(
            perform=lambda: events.append('perform')
        )
        in_combat = iter((True, True, False))
        combat.in_combat = lambda: next(in_combat)

        self.assertTrue(combat.run())
        self.assertEqual(
            events,
            ['switch_healer', 'perform', 'combat_end', 'switch_healer'],
        )


if __name__ == '__main__':
    unittest.main()
