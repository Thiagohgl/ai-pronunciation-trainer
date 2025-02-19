import unittest
from unittest.mock import patch

import numpy as np

## permit to import from parent directory also in
import sys
from pathlib import Path

parent = Path(__file__).parent.parent.parent
sys.path.append(str(parent))
print(f"## sys.path:{sys.path}.")

from constants import app_logger
import lambdaSpeechToScore
from tests import EVENTS_FOLDER
from tests.utilities import hash_calculate


input_file_test_de = EVENTS_FOLDER / "test_de.wav"
hash_input = hash_calculate(input_file_test_de, is_file=True)
assert hash_input == b'tGNDknDQRwCAx4LJ88Ft3y2+YAxcqXW7GAqasxxZoBw='


class TestAudioReadLoad(unittest.TestCase):

    def test_audioread_load_full_file(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(
            signal.shape, (129653,)
        )  # Assuming the audio file is ~2,93 seconds long (107603 / 44100)
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'3bfNuuMk0ov5+E77cUZmzjijfBUaMxuy1mrPmyjFyeo=')
        
    def test_audioread_load_with_offset(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=0.5)
        self.assertEqual(sr_native, 44100)
        self.assertAlmostEqual(signal.shape, (107603,))  # audio file is ~2.44 seconds long (107603 / 44100), offset is 0.5 seconds
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'QiDTDSZ4xAUniANNz4M43oa2FwpTSjvzW3IsKyqCVeE=')

    def test_audioread_load_with_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, duration=129653 / 44100)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (129653,))  # Assuming the duration is ~2,93 seconds long (129653 / 44100)
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'3bfNuuMk0ov5+E77cUZmzjijfBUaMxuy1mrPmyjFyeo=')

    def test_audioread_load_with_offset_and_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=0.5, duration=129653 / 44100)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (107603,))
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'QiDTDSZ4xAUniANNz4M43oa2FwpTSjvzW3IsKyqCVeE=')
    
    def test_audioread_load_with_big_offset_and_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=10, duration=129653 / 44100)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (0,))
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')

    def test_audioread_load_with_big_offset_no_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=10)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (0,))
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')
    
    def test_audioread_load_with_small_very_small_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, duration=0.000001)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (0,))
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')

    def test_audioread_load_with_small_offset_and_no_duration(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=0.02)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (128771,))
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'twAqaV+NNszPT6DwMOC2zL0mCx+BZ51CcoESmULfWRQ=')

    def test_audioread_load_empty_file(self):
        """
        To create an empty file, set an offset greater than the duration of the file:
        ```
        import soundfile as sf
        import numpy as np
        duration = 129653 / 44100  # ~2.93 seconds
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_file_test_de, offset=5, duration=duration)
        sf.write(EVENTS_FOLDER / "test_empty.wav", data=signal, samplerate=44100)
        ```
        """
        input_empty = EVENTS_FOLDER / "test_empty.wav"
        hash_input_empty = hash_calculate(input_empty, is_file=True)
        self.assertEqual(hash_input_empty, b'i4+6/oZ5B2RUQpdW+nLxHV9ELIc4HMakKFRR2Cap5ik=')
        signal, sr_native = lambdaSpeechToScore.audioread_load(input_empty)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (0, ))  # Assuming the file is empty
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')

    def test_audioread_load_full_stereo_file_long(self):
        signal, sr_native = lambdaSpeechToScore.audioread_load(EVENTS_FOLDER / "test_stereo.wav", duration=6)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(
            signal.shape, (2, 264600)
        )  # Assuming the audio file is ~6 seconds long (264600 / 44100)
        signal_contiguous = np.ascontiguousarray(signal)
        hash_output = hash_calculate(signal_contiguous, is_file=False)
        self.assertEqual(hash_output, b'NBLPhDBmZSTv844S3oDf4lMbQt1x+JbRckub/3rSEJI=')


class TestSoundFileLoad(unittest.TestCase):

    def test_soundfile_load_full_file(self):
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_file_test_de)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(
            signal.shape, (129653,)
        )  # Assuming the audio file is ~2,93 seconds long (107603 / 44100)
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'3bfNuuMk0ov5+E77cUZmzjijfBUaMxuy1mrPmyjFyeo=')
        
    def test_soundfile_load_with_offset(self):
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_file_test_de, offset=0.5)
        self.assertEqual(sr_native, 44100)
        self.assertAlmostEqual(signal.shape, (107603,))  # audio file is ~2.44 seconds long (107603 / 44100), offset is 0.5 seconds
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'QiDTDSZ4xAUniANNz4M43oa2FwpTSjvzW3IsKyqCVeE=')

    def test_soundfile_load_with_duration(self):
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_file_test_de, duration=129653 / 44100)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (129653,))  # Assuming the duration is ~2,93 seconds long (129653 / 44100)
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'3bfNuuMk0ov5+E77cUZmzjijfBUaMxuy1mrPmyjFyeo=')

    def test_soundfile_load_with_offset_and_duration(self):
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_file_test_de, offset=0.5, duration=129653 / 44100)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (107603,))  # Assuming the duration is 5 seconds starting from 2 seconds offset
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'QiDTDSZ4xAUniANNz4M43oa2FwpTSjvzW3IsKyqCVeE=')

    def test_soundfile_load_empty_file(self):
        """
        To create an empty file, set an offset greater than the duration of the file:
        ```
        import soundfile as sf
        import numpy as np
        duration = 129653 / 44100  # ~2.93 seconds
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_file_test_de, offset=5, duration=duration)
        sf.write(EVENTS_FOLDER / "test_empty.wav", data=signal, samplerate=44100)
        ```
        """
        input_empty = EVENTS_FOLDER / "test_empty.wav"
        hash_input_empty = hash_calculate(input_empty, is_file=True)
        self.assertEqual(hash_input_empty, b'i4+6/oZ5B2RUQpdW+nLxHV9ELIc4HMakKFRR2Cap5ik=')
        signal, sr_native = lambdaSpeechToScore.soundfile_load(input_empty)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(signal.shape, (0, ))  # Assuming the file is empty
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=')

    def test_soundfile_load_full_stereo_file_long(self):
        signal, sr_native = lambdaSpeechToScore.soundfile_load(EVENTS_FOLDER / "test_stereo.wav", duration=6)
        self.assertEqual(sr_native, 44100)
        self.assertEqual(
            signal.shape, (2, 264600)
        )  # Assuming the audio file is ~6 seconds long (264600 / 44100)
        signal_contiguous = np.ascontiguousarray(signal)
        hash_output = hash_calculate(signal_contiguous, is_file=False)
        self.assertEqual(hash_output, b'NBLPhDBmZSTv844S3oDf4lMbQt1x+JbRckub/3rSEJI=')

    def test_soundfile_load_soundfile_object(self):
        import soundfile as sf
        signal, sr_native = lambdaSpeechToScore.soundfile_load(sf.SoundFile(input_file_test_de))
        self.assertEqual(sr_native, 44100)
        self.assertEqual(
            signal.shape, (129653,)
        )  # Assuming the audio file is ~2,93 seconds long (107603 / 44100)
        hash_output = hash_calculate(signal, is_file=False)
        self.assertEqual(hash_output, b'3bfNuuMk0ov5+E77cUZmzjijfBUaMxuy1mrPmyjFyeo=')

    @patch.object(lambdaSpeechToScore, "soundfile_load")
    def test_soundfile_load_LibsndfileError1(self, soundfile_load_mock):
        from soundfile import LibsndfileError
        from tests.lambdas.test_lambdaSpeechToScore import helper_get_accuracy_from_recorded_audio
        from tests.lambdas.constants_test_lambdaSpeechToScore import expected_GetAccuracyFromRecordedAudio

        soundfile_load_mock.side_effect = LibsndfileError(3, prefix="Exc:")
        try:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "cmd", False)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "gui", False)

    @patch.object(lambdaSpeechToScore, "soundfile_load")
    @patch.object(lambdaSpeechToScore, "audioread_load")
    def test_soundfile_load_LibsndfileError1_ModuleNotFoundError2(self, soundfile_load_mock, audioread_load_mock):
        from soundfile import LibsndfileError
        from tests.lambdas.test_lambdaSpeechToScore import helper_get_accuracy_from_recorded_audio
        from tests.lambdas.constants_test_lambdaSpeechToScore import expected_GetAccuracyFromRecordedAudio

        soundfile_load_mock.side_effect = LibsndfileError(3, prefix="error:")
        audioread_load_mock.side_effect = ModuleNotFoundError("ModuleNotFoundError error2")
        with self.assertRaises(ModuleNotFoundError):
            try:
                try:
                    helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "cmd", False)
                except AssertionError:
                    helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "gui", False)
            except ModuleNotFoundError as mnfe:
                app_logger.error("## ModuleNotFoundError raised.")
                assert str(mnfe) == "ModuleNotFoundError error2"
                raise mnfe


class TestBufToFloat(unittest.TestCase):
    def test_buf_to_float_2_bytes(self):
        int_buffer = np.array([0, 32767, -32768], dtype=np.int16).tobytes()
        expected_output = np.array([0.0, 1.0, -1.0], dtype=np.float32)
        output = lambdaSpeechToScore.buf_to_float(int_buffer, n_bytes=2, dtype=np.float32)
        np.testing.assert_array_almost_equal(output, expected_output, decimal=3)

    def test_buf_to_float_1_byte(self):
        int_buffer = np.array([0, 127, -128], dtype=np.int8).tobytes()
        expected_output = np.array([0.0, 0.9921875, -1.0], dtype=np.float32)
        output = lambdaSpeechToScore.buf_to_float(int_buffer, n_bytes=1, dtype=np.float32)
        np.testing.assert_array_almost_equal(output, expected_output, decimal=3)

    def test_buf_to_float_4_bytes(self):
        int_buffer = np.array([0, 2147483647, -2147483648], dtype=np.int32).tobytes()
        expected_output = np.array([0.0, 1.0, -1.0], dtype=np.float32)
        output = lambdaSpeechToScore.buf_to_float(int_buffer, n_bytes=4, dtype=np.float32)
        np.testing.assert_array_almost_equal(output, expected_output, decimal=3)

    def test_buf_to_float_custom_dtype(self):
        int_buffer = np.array([0, 32767, -32768], dtype=np.int16).tobytes()
        expected_output = np.array([0.0, 0.999969482421875, -1.0], dtype=np.float64)
        output = lambdaSpeechToScore.buf_to_float(int_buffer, n_bytes=2, dtype=np.float64)
        np.testing.assert_array_almost_equal(output, expected_output, decimal=3)

    def test_buf_to_float_empty_buffer(self):
        int_buffer = np.array([], dtype=np.int16).tobytes()
        expected_output = np.array([], dtype=np.float32)
        output = lambdaSpeechToScore.buf_to_float(int_buffer, n_bytes=2, dtype=np.float32)
        np.testing.assert_array_almost_equal(output, expected_output, decimal=3)

    def test_buf_to_float_512_bytes(self):
        import json

        float_arr = np.arange(-256, 256, dtype=np.float32)
        float_buffer = float_arr.tobytes()
        output = lambdaSpeechToScore.buf_to_float(float_buffer, dtype=np.float32)  # default n_bytes=2
        hash_output = hash_calculate(output, is_file=False)
        # serialized = serialize.serialize(output)
        # with open(EVENTS_FOLDER / "test_float_buffer.json", "w") as f:
        #     json.dump(serialized, f)
        with open(EVENTS_FOLDER / "test_float_buffer.json", "r") as f:
            expected = f.read()
            expected_output = np.asarray(json.loads(expected), dtype=np.float32)
            hash_expected_output = hash_calculate(expected_output, is_file=False)
        assert hash_output == hash_expected_output
        np.testing.assert_array_almost_equal(output, expected_output)


if __name__ == "__main__":
    unittest.main()
