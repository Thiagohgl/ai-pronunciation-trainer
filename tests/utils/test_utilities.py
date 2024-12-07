import unittest
import numpy as np

from tests import EVENTS_FOLDER
from aip_trainer import app_logger


class TestUtilities(unittest.TestCase):
    def test_hash_calculate_not_file(self):
        from aip_trainer.utils.utilities import hash_calculate

        size = 5
        input_arr = np.arange(size**2).reshape((size, size))
        hash_output = hash_calculate(input_arr, is_file=False)
        self.assertEqual(hash_output, b'KgoWp86FwhH2tuinWOfsCfn9d+Iw6B10wwqFfdUeLeY=')

        hash_output = hash_calculate({"arr": input_arr}, is_file=False)
        self.assertEqual(hash_output, b'M/EYsBPRQLVP9T299xHyOrtT7bdCkIDaMmW2hslMays=')

        hash_output = hash_calculate("a test string...", is_file=False)
        self.assertEqual(hash_output, b'29a8JwujQklQ6MKQhPyix6G1i/7Pp0uUg5wFybKuCC0=')

        hash_output = hash_calculate("123123123", is_file=False)
        self.assertEqual(hash_output, b'ky88G1YlfOhTmsJp16q0JVDaz4gY0HXwvfGZBWKq4+8=')

        hash_output = hash_calculate(b"a byte test string...", is_file=False)
        self.assertEqual(hash_output, b'dgSt/jiqLk0HJ09Xqe/BWzMvnYiOqzWlcSCCfN767zA=')

        with self.assertRaises(ValueError):
            try:
                hash_calculate(1, is_file=False)
            except ValueError as ve:
                self.assertEqual(str(ve), "variable 'arr':1 of type '<class 'int'>' not yet handled.")
                raise ve

    def test_hash_calculate_is_file(self):
        from aip_trainer.utils.utilities import hash_calculate

        output_hash = hash_calculate(EVENTS_FOLDER / "test_en.wav", is_file=True, read_mode="rb")
        app_logger.info(f"output_hash test_en: {output_hash}")
        assert b'Dsvmm+mj/opHnmKLT7wIqyhqMLeIuVP4hTWi+DAXS8Y=' == output_hash

        output_hash = hash_calculate(EVENTS_FOLDER / "example.json", is_file=True)
        app_logger.info(f"output_hash json: {output_hash}")
        assert b'aLGnsOa1Z3QmfilSPybdVcUHcjgd5ntOZh6mbQDEy2w=' == output_hash


if __name__ == '__main__':
    unittest.main()
