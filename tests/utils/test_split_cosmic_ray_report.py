import unittest
from pathlib import Path
from aip_trainer.utils.split_cosmic_ray_report import get_cosmic_ray_report_filtered
from aip_trainer.utils import utilities
from tests import EVENTS_FOLDER


class TestSplitCosmicRayReport(unittest.TestCase):
    def test_get_cosmic_ray_report_filtered_only_string_killed(self):
        input_filename = EVENTS_FOLDER / "cosmic-ray-lambdagetsample.txt"
        output_filename = EVENTS_FOLDER / f"{input_filename.stem}_filtered{input_filename.suffix}"
        self.assertFalse(output_filename.exists())
        get_cosmic_ray_report_filtered(input_filename, separator="============", filter_string_list=["test outcome: TestOutcome.KILLED", ])

        # Check if the filtered file is created
        self.assertTrue(output_filename.exists() and output_filename.is_file())

        # Verify the filtered content
        hash_output = utilities.hash_calculate(output_filename, True)
        try:
            self.assertEqual(hash_output, b'HqzO5Hq50Z1CIz/8rGE8Hpt4wSRM5Xm86pv+9FOYbUg=')
        except AssertionError:
            self.assertEqual(hash_output, b'KAEGrZdO8cY9sXoKYQFtsc4FF/tLavzDJbqO5+pyCSw=')

        output_filename.unlink(missing_ok=False)


    def test_get_cosmic_ray_report_filtered_list_strings(self):
        input_filename = EVENTS_FOLDER / "cosmic-ray-pronunciationtrainer.txt"
        output_filename = EVENTS_FOLDER / f"{input_filename.stem}_filtered{input_filename.suffix}"
        self.assertFalse(output_filename.exists())
        get_cosmic_ray_report_filtered(input_filename, separator="============", filter_string_list=["test outcome: TestOutcome.KILLED", "-        duration = time.time()"])

        # Check if the filtered file is created
        self.assertTrue(output_filename.exists() and output_filename.is_file())

        # Verify the filtered content
        hash_output = utilities.hash_calculate(output_filename, True)
        try:
            self.assertEqual(hash_output, b'Fk0KDWCbc8mPoZllQ7HfgMjuWQVvUdNl+eR56eJeSxg=')
        except AssertionError:
            self.assertEqual(hash_output, b'1s0Gvw4Y972Gkw/oojf69rXK3CVlPfKjATGJ14WzFw8=')

        output_filename.unlink(missing_ok=False)


if __name__ == "__main__":
    unittest.main()
