import base64
import json
from pathlib import Path
import tempfile
import time
from typing import Dict, Any
try:
    from typing import LiteralString
except ImportError:
    from typing_extensions import LiteralString

import audioread
import numpy as np
import torch
from torchaudio.transforms import Resample

import WordMatching as wm
import pronunciationTrainer
import utilsFileIO
from constants import app_logger, sample_rate_resample, sample_rate_start, USE_DTW, IS_TESTING, tmp_audio_extension


trainer_SST_lambda = {'de': pronunciationTrainer.getTrainer("de"), 'en': pronunciationTrainer.getTrainer("en")}
transform = Resample(orig_freq=sample_rate_start, new_freq=sample_rate_resample)


def lambda_handler(event: dict[str], context: Any) -> str:
    """
    Lambda handler for speech-to-score.

    Args:
        event (Dict[str, Any]): The event data containing the request body.
        context (Any): The context in which the lambda function is executed.

    Returns:
        str: The json response containing the speech-to-score results.
    """
    body = event['body']
    data = json.loads(body)

    real_text = data['title']
    base64_audio = data["base64Audio"]
    app_logger.debug(f"base64Audio:{base64_audio} ...")
    file_bytes_or_audiotmpfile = base64.b64decode(base64_audio[22:].encode('utf-8'))
    language = data['language']
    try:
        use_dtw = data["useDTW"]
        app_logger.info(f'use_dtw: "{type(use_dtw)}", "{use_dtw}".')
    except KeyError:
        use_dtw = USE_DTW

    if len(real_text) == 0:
        return utilsFileIO.return_response_ok('{}')
    output = get_speech_to_score_dict(
        real_text=real_text, file_bytes_or_audiotmpfile=file_bytes_or_audiotmpfile, language=language, use_dtw=use_dtw
    )
    pronunciation_accuracy = int(output["pronunciation_accuracy"])
    output["pronunciation_accuracy"] = f"{pronunciation_accuracy}"
    output = json.dumps(output)
    app_logger.debug(f"output: {output} ...")
    return output


def get_speech_to_score_dict(
        real_text: str, file_bytes_or_audiotmpfile: str | bytes | dict, language: str = "en", extension: str = tmp_audio_extension, use_dtw: bool = False
) -> Dict[str | Any, float | LiteralString | str | Any]:
    """
    Process the audio file and return a dictionary with speech-to-score results.

    Args:
        use_dtw:
        real_text (str): The text to be matched with the audio.
        file_bytes_or_audiotmpfile (str | bytes | dict): The audio file in bytes or a temporary file.
        language (str): The language of the audio.
        extension (str): The file extension of the audio file.

    Returns:
        Dict[str | Any, float | LiteralString | str | Any]: The speech-to-score results.
    """
    from soundfile import LibsndfileError
    app_logger.info(f"real_text:{real_text} ...")
    app_logger.debug(f"file_bytes:{file_bytes_or_audiotmpfile} ...")
    app_logger.info(f"language:{language} ...")

    if real_text is None or len(real_text) == 0:
        raise ValueError(f"cannot read an empty/None text: '{real_text}'...")
    if language is None or len(language) == 0:
        raise NotImplementedError(f"Not tested/supported with '{language}' language...")
    if file_bytes_or_audiotmpfile is None or len(file_bytes_or_audiotmpfile) == 0:
        raise OSError(f"cannot read an empty/None file: '{file_bytes_or_audiotmpfile}'...")
    if not isinstance(file_bytes_or_audiotmpfile, (bytes, bytearray)) and Path(file_bytes_or_audiotmpfile).exists() and Path(file_bytes_or_audiotmpfile).stat().st_size == 0:
        raise OSError(f"cannot read an empty file: '{file_bytes_or_audiotmpfile}'...")

    start0 = time.time()

    random_file_name = file_bytes_or_audiotmpfile
    app_logger.debug(f"random_file_name:{random_file_name} ...")
    if isinstance(file_bytes_or_audiotmpfile, (bytes, bytearray)):
        app_logger.debug("writing streaming data to file on disk...")
        with tempfile.NamedTemporaryFile(prefix="temp_sound_speech_score_", suffix=extension, delete=False) as f1:
            f1.write(file_bytes_or_audiotmpfile)
            random_file_name = f1.name
            duration = time.time() - start0
            app_logger.info(f'Saved binary data in file in {duration}s.')

    start = time.time()
    app_logger.info(f"Loading temp '{random_file_name}' file...")
    try:
        signal, samplerate = soundfile_load(random_file_name)
    except LibsndfileError as sfe:
        # https://github.com/beetbox/audioread/issues/144
        # deprecation warnings => pip install standard-aifc standard-sunau
        app_logger.error(f"Error reading file {random_file_name}: {sfe}, re-try with audioread...")
        signal, samplerate = audioread_load(random_file_name)

    duration = time.time() - start
    app_logger.info(f'Read {extension} file {random_file_name} in {duration}s.')

    signal_transformed = transform(torch.Tensor(signal)).unsqueeze(0)

    duration = time.time() - start
    app_logger.info(f'Loaded {extension} file {random_file_name} in {duration}s.')

    language_trainer_sst_lambda = trainer_SST_lambda[language]
    app_logger.info('language_trainer_sst_lambda: preparing...')
    result = language_trainer_sst_lambda.processAudioForGivenText(signal_transformed, real_text)
    app_logger.info(f'language_trainer_sst_lambda: result: {result}...')

    # start = time.time()
    # if remove_random_file:
    #     os.remove(random_file_name)
    # duration = time.time() - start
    # app_logger.info(f'Deleted file {random_file_name} in {duration}s.')

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
    duration = time.time() - start
    duration_tot = time.time() - start0
    app_logger.info(f'Time to post-process results: {duration}, tot_duration:{duration_tot}.')
    pronunciation_accuracy = float(result['pronunciation_accuracy'])
    ipa_transcript = result['recording_ipa']

    return {
        'real_transcript': result['recording_transcript'],
        'ipa_transcript': ipa_transcript,
        'pronunciation_accuracy': pronunciation_accuracy,
        'real_transcripts': real_transcripts, 'matched_transcripts': matched_transcripts,
        'real_transcripts_ipa': real_transcripts_ipa, 'matched_transcripts_ipa': matched_transcripts_ipa,
        'pair_accuracy_category': pair_accuracy_category,
        'start_time': result['start_time'],
        'end_time': result['end_time'],
        'is_letter_correct_all_words': is_letter_correct_all_words,
        "random_file_name": random_file_name
    }


def get_speech_to_score_tuple(real_text: str, file_bytes_or_audiotmpfile: str | dict, language: str = "en", remove_random_file: bool = True) -> tuple:
    """
    Process the audio file and return a tuple with speech-to-score results.

    Args:
        real_text (str): The text to be matched with the audio.
        file_bytes_or_audiotmpfile (str | dict): The audio file in bytes or a temporary file.
        language (str): The language of the audio.
        remove_random_file (bool): Whether to remove the temporary file after processing.

    Returns:
        tuple: A tuple containing real transcripts, letter correctness, pronunciation accuracy, IPA transcript, real transcripts in IPA, number of words, first audio file, and JSON output.
    """
    output = get_speech_to_score_dict(
        real_text=real_text, file_bytes_or_audiotmpfile=file_bytes_or_audiotmpfile,
        language=language
    )
    random_file_name = output["random_file_name"]
    del output["random_file_name"]
    real_transcripts = output['real_transcripts']
    is_letter_correct_all_words = output['is_letter_correct_all_words']
    pronunciation_accuracy = output['pronunciation_accuracy']
    output["pronunciation_accuracy"] = f"{pronunciation_accuracy:.2f}"
    ipa_transcript = output['ipa_transcript']
    real_transcripts_ipa = output['real_transcripts_ipa']
    end_time = [float(x) for x in output['end_time'].split(" ")]
    start_time = [float(x) for x in output['start_time'].split(" ")]
    num_words = len(end_time)
    app_logger.debug(f"start splitting recorded audio into {num_words} words...")

    audio_files, audio_durations = get_splitted_audio_file(audiotmpfile=file_bytes_or_audiotmpfile, start_time=start_time, end_time=end_time)

    remove_random_file = not IS_TESTING and remove_random_file
    if remove_random_file:
        app_logger.info(f"{IS_TESTING} => remove_random_file:{remove_random_file}, removing:{random_file_name} ...")
        Path(random_file_name).unlink(missing_ok=True)
        app_logger.info(f"removed:{random_file_name} ...")

    output = {'audio_files': audio_files, "audio_durations": audio_durations, **output}
    first_audio_file = audio_files[0]
    return real_transcripts, is_letter_correct_all_words, pronunciation_accuracy, ipa_transcript, real_transcripts_ipa, num_words, first_audio_file, json.dumps(output), random_file_name


def soundfile_write(audiofile: str | Path, data: np.ndarray, samplerate: int) -> None:
    """
    Write audio data to a file using soundfile.

    Args:
        audiofile (str | Path): The path to the audio file.
        data (np.ndarray): The audio data to write.
        samplerate (int): The sample rate of the audio data.

    Returns:
        None
    """
    import soundfile as sf
    sf.write(audiofile, data, samplerate)


def get_selected_word(idx_recorded_word: int, raw_json_output: str) -> tuple[str, str, float]:
    """
    Get the selected word, its audio file, and duration from the recognition output.

    Args:
        idx_recorded_word (int): The index of the recorded word.
        raw_json_output (str): The JSON output from the recognition process.

    Returns:
        tuple: A tuple containing the audio file, the current word, and its duration.
    """
    recognition_output = json.loads(raw_json_output)
    list_audio_files = recognition_output["audio_files"]
    real_transcripts = recognition_output["real_transcripts"]
    audio_durations = recognition_output["audio_durations"]
    real_transcripts_list = real_transcripts.split()
    app_logger.info(f"idx_recorded_word:{idx_recorded_word} ...")
    current_word = real_transcripts_list[idx_recorded_word]
    app_logger.info(f"current word:{current_word} ...")
    current_duration = audio_durations[idx_recorded_word]
    app_logger.info(f"current_duration:{current_duration} ...")
    return list_audio_files[idx_recorded_word], current_word, current_duration


def get_splitted_audio_file(audiotmpfile: str | Path, start_time: list[float], end_time: list[float]) -> tuple[list[str], list[float]]:
    """
    Split the audio file into segments based on start and end times.

    Args:
        audiotmpfile (str | Path): The path to the audio file.
        start_time (list[float]): The start times of the segments.
        end_time (list[float]): The end times of the segments.

    Returns:
        tuple: A tuple containing a list of audio files and their durations.
    """
    import soundfile as sf
    audio_files = []
    audio_durations = []
    app_logger.info(f"start_time:{start_time}, end_time:{end_time} ...")
    for n, (start_nth, end_nth) in enumerate(zip(start_time, end_time)):
        # assert start_nth < end_nth, f"start_nth:{start_nth} (index {n}) should be less than end_nth:{end_nth} (start_time:{start_time}, end_time:{end_time})..."
        signal_nth, samplerate = soundfile_load(audiotmpfile, offset=start_nth, duration=end_nth - start_nth)
        audiofile = get_file_with_custom_suffix(audiotmpfile, f"_part{n}_start{start_nth}_end{end_nth}")
        soundfile_write(audiofile=audiofile, data=signal_nth, samplerate=samplerate)
        app_logger.info(f"audio file {audiofile} written...")
        audio_files.append(str(audiofile))
        duration = end_nth - start_nth
        app_logger.info(f"audio file {audiofile} has duration {duration}...")
        audio_durations.append(duration)
    return audio_files, audio_durations


def get_file_with_custom_suffix(basefile: str | Path, custom_suffix: str) -> Path:
    """
    Generate a file path with a custom suffix.

    Args:
        basefile (str | Path): The base file path.
        custom_suffix (str): The custom suffix to add to the file name.

    Returns:
        Path: The new file path with the custom suffix.
    """
    pathname = Path(basefile)
    dirname, filename_no_ext, filename_ext = pathname.parent, pathname.stem, pathname.suffix
    output_file = dirname / f"{filename_no_ext}_{custom_suffix}.{filename_ext}"
    return output_file


# From Librosa

def calc_start_end(sr_native: int, time_position: float, n_channels: int) -> int:
    """
    Calculate the start or end position in samples.

    Args:
        sr_native (int): The native sample rate.
        time_position (float): The time position in seconds.
        n_channels (int): The number of audio channels.

    Returns:
        int: The start or end position in samples.
    """
    return int(np.round(sr_native * time_position)) * n_channels


def soundfile_load(path: str | Path, offset: float = 0.0, duration: float = None, dtype=np.float32) -> tuple[np.ndarray, int]:
    """
    Load an audio buffer using soundfile.

    Args:
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


def audioread_load(path: str | Path, offset: float = 0.0, duration: float = None, dtype=np.float32) -> tuple[np.ndarray, int]:
    """
    This loads one block at a time, and then concatenates the results.

    Args:
        path (str | Path): The path to the audio file.
        offset (float): The offset in seconds to start reading the file.
        duration (float): The duration in seconds to read from the file.
        dtype (np.float32): The data type of the audio buffer.

    Returns:
        tuple: A tuple containing the audio buffer and the sample rate.
    """
    y = []
    app_logger.debug(f"reading audio file at path:{path} ...")
    with audioread.audio_open(path) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels

        s_start = calc_start_end(sr_native, offset, n_channels)

        if duration is None:
            s_end = np.inf
        else:
            duration = calc_start_end(sr_native, duration, n_channels)
            s_end = duration + s_start

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


def buf_to_float(x: np.ndarray, n_bytes: int = 2, dtype: np.float32 = np.float32) -> np.ndarray:
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

