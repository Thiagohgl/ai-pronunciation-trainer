import base64
import json
import tempfile
import time
from pathlib import Path

import audioread
import numpy as np
import torch
from torchaudio.transforms import Resample

import WordMatching as wm
import lambdaChangeModel
import utilsFileIO
from constants import app_logger, sample_rate_resample, sample_rate_start, USE_DTW, IS_TESTING, tmp_audio_extension


transform = Resample(orig_freq=sample_rate_start, new_freq=sample_rate_resample)


def lambda_handler(event, context):
    from soundfile import LibsndfileError

    data = json.loads(event['body'])

    real_text = data['title']
    file_bytes = base64.b64decode(
        data['base64Audio'][22:].encode('utf-8'))
    language = data['language']
    try:
        use_dtw = data["useDTW"]
        app_logger.info(f'use_dtw: "{type(use_dtw)}", "{use_dtw}".')
    except KeyError:
        app_logger.info(f"useDTW key not found, use its default value '{USE_DTW}' ('{type(USE_DTW)}').")
        use_dtw = USE_DTW

    if len(real_text) == 0:
        return utilsFileIO.return_response_ok("{}")

    delete_tmp = not IS_TESTING
    with tempfile.NamedTemporaryFile(suffix=tmp_audio_extension, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_name = tmp.name
        app_logger.info(f'Loading {tmp_name} file, delete it? {delete_tmp}, IS_TESTING:{IS_TESTING}.')
        try:
            signal, samplerate = soundfile_load(tmp_name)
        except LibsndfileError as sfe:
            # https://github.com/beetbox/audioread/issues/144
            # deprecation warnings => pip install standard-aifc standard-sunau
            app_logger.error(f"Error reading file {tmp_name}: '{sfe}', re-try with audioread...")
            signal, samplerate = audioread_load(tmp_name)

    signal_transformed = transform(torch.Tensor(signal)).unsqueeze(0)
    # Path(tmp_name).unlink(missing_ok=True)

    language_trainer_sst_lambda = lambdaChangeModel.trainer_SST_lambda[language]
    app_logger.info('language_trainer_sst_lambda: preparing...')
    result = language_trainer_sst_lambda.processAudioForGivenText(signal_transformed, real_text)
    app_logger.info(f'language_trainer_sst_lambda: result: {result}...')

    #start = time.time()
    #os.remove(random_file_name)
    #app_logger.info('Time for deleting file: {time.time()-start}.')

    start = time.time()
    real_transcripts_ipa = ' '.join(
        [word[0] for word in result['real_and_transcribed_words_ipa']])
    matched_transcripts_ipa = ' '.join(
        [word[1] for word in result['real_and_transcribed_words_ipa']])

    real_transcripts = ' '.join(
        [word[0] for word in result['real_and_transcribed_words']])
    matched_transcripts = ' '.join(
        [word[1] for word in result['real_and_transcribed_words']])

    words_real = real_transcripts.lower().split()
    mapped_words = matched_transcripts.split()

    is_letter_correct_all_words = ''
    for idx, word_real in enumerate(words_real):

        mapped_letters, mapped_letters_indices = wm.get_best_mapped_words(
            mapped_words[idx], word_real, use_dtw=use_dtw)

        is_letter_correct = wm.getWhichLettersWereTranscribedCorrectly(
            word_real, mapped_letters)  # , mapped_letters_indices)

        is_letter_correct_all_words += ''.join([str(is_correct)
                                                for is_correct in is_letter_correct]) + ' '

    pair_accuracy_category = ' '.join(
        [str(category) for category in result['pronunciation_categories']])
    time_post_process = time.time() - start
    app_logger.info(f'Time to post-process results: {time_post_process:.3f}.')

    res = {'real_transcript': result['recording_transcript'],
           'ipa_transcript': result['recording_ipa'],
           'pronunciation_accuracy': str(int(result['pronunciation_accuracy'])),
           'real_transcripts': real_transcripts, 'matched_transcripts': matched_transcripts,
           'real_transcripts_ipa': real_transcripts_ipa, 'matched_transcripts_ipa': matched_transcripts_ipa,
           'pair_accuracy_category': pair_accuracy_category,
           'start_time': result['start_time'],
           'end_time': result['end_time'],
           'is_letter_correct_all_words': is_letter_correct_all_words}

    return json.dumps(res)


def soundfile_load(path: str | Path, offset: float = 0.0, duration: float = None, dtype=np.float32) -> tuple[np.ndarray, int]:
    """
    Load an audio buffer using soundfile.

    Parameters:
        path (str | Path): The path to the audio file.
        offset (float): The offset in seconds to start reading the file.
        duration (float): The duration in seconds to read from the file.
        dtype (np.float32): The data type of the audio buffer.

    Returns:
        tuple: A tuple containing the audio buffer and the sample rate.
    """
    import soundfile as sf

    if isinstance(path, sf.SoundFile):
        # If the user passed an existing soundfile object,
        # we can use it directly
        context = path
    else:
        # Otherwise, create the soundfile object
        context = sf.SoundFile(path)

    with context as sf_desc:
        sr_native = sf_desc.samplerate
        if offset:
            # Seek to the start of the target read
            sf_desc.seek(int(offset * sr_native))
        if duration is not None:
            frame_duration = int(duration * sr_native)
        else:
            frame_duration = -1

        # Load the target number of frames, and transpose to match librosa form
        y = sf_desc.read(frames=frame_duration, dtype=dtype, always_2d=False).T

    return y, sr_native


def audioread_load(path, offset=0.0, duration=None, dtype=np.float32):
    """Load an audio buffer using audioread.

    This loads one block at a time, and then concatenates the results.
    """

    y = []
    with audioread.audio_open(path) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels

        s_start = int(np.round(sr_native * offset)) * n_channels

        if duration is None:
            s_end = np.inf
        else:
            s_end = s_start + \
                (int(np.round(sr_native * duration)) * n_channels)

        n = 0

        for frame in input_file:
            frame = buf_to_float(frame, dtype=dtype)
            n_prev = n
            n = n + len(frame)

            if n < s_start:
                # offset is after the current frame
                # keep reading
                continue

            if s_end < n_prev:
                # we're off the end.  stop reading
                break

            if s_end < n:
                # the end is in this frame.  crop.
                frame = frame[: s_end - n_prev]

            if n_prev <= s_start <= n:
                # beginning is in this frame
                frame = frame[(s_start - n_prev):]

            # tack on the current frame
            y.append(frame)

    if y:
        y = np.concatenate(y)
        if n_channels > 1:
            y = y.reshape((-1, n_channels)).T
    else:
        y = np.empty(0, dtype=dtype)

    return y, sr_native

# From Librosa


def buf_to_float(x, n_bytes=2, dtype=np.float32):
    """Convert an integer buffer to floating point values.
    This is primarily useful when loading integer-valued wav data
    into numpy arrays.

    Parameters
    ----------
    x : np.ndarray [dtype=int]
        The integer-valued data buffer

    n_bytes : int [1, 2, 4]
        The number of bytes per sample in ``x``

    dtype : numeric type
        The target output type (default: 32-bit float)

    Returns
    -------
    x_float : np.ndarray [dtype=float]
        The input data buffer cast to floating point
    """

    # Invert the scale of the data
    scale = 1.0 / float(1 << ((8 * n_bytes) - 1))

    # Construct the format string
    fmt = "<i{:d}".format(n_bytes)

    # Rescale and format the data buffer
    return scale * np.frombuffer(x, fmt).astype(dtype)
