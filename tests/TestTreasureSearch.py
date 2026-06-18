import unittest

from ok import CannotFindException
from src.task.BaseWWTask import BaseWWTask


class TestTreasureSearch(unittest.TestCase):

    def test_treasure_search_includes_screen_edges(self):
        task = BaseWWTask.__new__(BaseWWTask)
        search_boxes = []
        find_calls = []

        def box_of_screen(*args, **kwargs):
            search_boxes.append((args, kwargs))
            return 'treasure_search_box'

        task.box_of_screen = box_of_screen
        task.find_one = lambda *args, **kwargs: find_calls.append((args, kwargs)) or 'treasure'

        self.assertEqual('treasure', task.find_treasure_icon())
        self.assertEqual([((0.03, 0.1, 0.97, 0.81), {})], search_boxes)
        self.assertEqual('treasure_search_box', find_calls[0][1]['box'])

    def test_walk_to_treasure_fails_after_short_search(self):
        task = BaseWWTask.__new__(BaseWWTask)
        wait_calls = []

        task.log_info = lambda *args, **kwargs: None
        task.find_f_with_text = lambda: None
        task.find_treasure_icon = lambda: None
        task.wait_until = lambda *args, **kwargs: wait_calls.append(kwargs) or None

        with self.assertRaisesRegex(CannotFindException, 'can not find treasure'):
            task.walk_to_treasure()

        self.assertEqual(3, wait_calls[0]['time_out'])
        self.assertFalse(wait_calls[0]['raise_if_not_found'])


if __name__ == '__main__':
    unittest.main()
