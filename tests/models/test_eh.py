import unittest

from smb3_eh_manip.models import eh


class TestEh(unittest.TestCase):
    def test_world_load(self):
        self.assertEqual(2, eh.EH().world.number)
