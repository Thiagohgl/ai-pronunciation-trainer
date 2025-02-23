from tests import EVENTS_FOLDER

text_dict = {"de": "Hallo, wie geht es dir?", "en": "Hi there, how are you?"}
real_transcript = {
    "de": " Ich bin Alex, wer bin ich zu tun?",
    "en": " Hey there, how are you?"
}

real_transcripts_ipa = {
    "de": "haloː, viː ɡeːt ɛːs diːr?",
    "en": "haɪ ðɛr, haʊ ər ju?"
}
expected_GetAccuracyFromRecordedAudio = {
    "cmd": {
        "dtw_false": {
            'de': {
                "real_transcript": " Hallo, wie geht es dir?",
                "ipa_transcript": " halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "pronunciation_accuracy": "100",
                "real_transcripts": "Hallo, wie geht es dir?",
                "matched_transcripts": "Hallo, wie geht es dir?",
                "real_transcripts_ipa": "halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "matched_transcripts_ipa": "halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "pair_accuracy_category": "0 0 0 0 0",
                "start_time": "0.0 0.49 0.59 0.77 0.99",
                "end_time": "0.37 0.69 0.87 1.09 1.31",
                "is_letter_correct_all_words": "111111 111 1111 11 1111 "
            },
            'en': {
                'real_transcript': ' Hi there, how are you?',
                'ipa_transcript': 'haɪ ðɛr, haʊ ər ju?',
                'pronunciation_accuracy': '100',
                'real_transcripts': 'Hi there, how are you?',
                'matched_transcripts': 'Hi there, how are you?',
                'real_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'matched_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'pair_accuracy_category': '0 0 0 0 0',
                'start_time': '0.0 0.09 0.41 0.53 0.65',
                'end_time': '0.19 0.35 0.63 0.75 0.91',
                'is_letter_correct_all_words': '11 111111 111 111 1111 '
            }
        },
        "dtw_true": {
            'de': {
                "real_transcript": " Hallo, wie geht es dir?",
                "ipa_transcript": " halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "pronunciation_accuracy": "100",
                "real_transcripts": "Hallo, wie geht es dir?",
                "matched_transcripts": "Hallo, wie geht es dir?",
                "real_transcripts_ipa": "halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "matched_transcripts_ipa": "halo\u02d0, vi\u02d0 \u0261e\u02d0t \u025b\u02d0s di\u02d0r?",
                "pair_accuracy_category": "0 0 0 0 0",
                "start_time": "0.0 0.49 0.59 0.77 0.99",
                "end_time": "0.37 0.69 0.87 1.09 1.31",
                "is_letter_correct_all_words": "111111 111 1111 11 1111 "
            },
            'en': {
                "real_transcript": " Hi there, how are you?",
                "ipa_transcript": "ha\u026a \u00f0\u025br, ha\u028a \u0259r ju?",
                "pronunciation_accuracy": "100",
                "real_transcripts": "Hi there, how are you?",
                "matched_transcripts": "Hi there, how are you?",
                "real_transcripts_ipa": "ha\u026a \u00f0\u025br, ha\u028a \u0259r ju?",
                "matched_transcripts_ipa": "ha\u026a \u00f0\u025br, ha\u028a \u0259r ju?",
                "pair_accuracy_category": "0 0 0 0 0",
                "start_time": "0.0 0.09 0.41 0.53 0.65",
                "end_time": "0.19 0.35 0.63 0.75 0.91",
                "is_letter_correct_all_words": "11 111111 111 111 1111 "
            }
        }
    },
    "gui": {
        "dtw_false": {
            "de": {
                'real_transcript': ' Hallo, wie geht es dir?',
                'ipa_transcript': ' haloː, viː ɡeːt ɛːs diːr?',
                'pronunciation_accuracy': '100',
                'real_transcripts': 'Hallo, wie geht es dir?',
                'matched_transcripts': 'Hallo, wie geht es dir?',
                'real_transcripts_ipa': 'haloː, viː ɡeːt ɛːs diːr?',
                'matched_transcripts_ipa': 'haloː, viː ɡeːt ɛːs diːr?',
                'pair_accuracy_category': '0 0 0 0 0',
                'start_time': '0.0 0.49 0.59 0.77 0.99',
                'end_time': '0.37 0.69 0.87 1.09 1.31',
                'is_letter_correct_all_words': '111111 111 1111 11 1111 '
            },
            "en": {
                'real_transcript': ' Hi there, how are you?',
                'ipa_transcript': 'haɪ ðɛr, haʊ ər ju?',
                'pronunciation_accuracy': '100',
                'real_transcripts': 'Hi there, how are you?',
                'matched_transcripts': 'Hi there, how are you?',
                'real_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'matched_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'pair_accuracy_category': '0 0 0 0 0',
                'start_time': '0.0 0.09 0.41 0.53 0.65',
                'end_time': '0.19 0.35 0.63 0.75 0.91',
                'is_letter_correct_all_words': '11 111111 111 111 1111 '
            },
        },
        "dtw_true": {
            "de": {
                'real_transcript': ' Hallo, wie geht es dir?',
                'ipa_transcript': ' haloː, viː ɡeːt ɛːs diːr?',
                'pronunciation_accuracy': '100',
                'real_transcripts': 'Hallo, wie geht es dir?',
                'matched_transcripts': 'Hallo, wie geht es dir?',
                'real_transcripts_ipa': 'haloː, viː ɡeːt ɛːs diːr?',
                'matched_transcripts_ipa': 'haloː, viː ɡeːt ɛːs diːr?',
                'pair_accuracy_category': '0 0 0 0 0',
                'start_time': '0.0 0.49 0.59 0.77 0.99',
                'end_time': '0.37 0.69 0.87 1.09 1.31',
                'is_letter_correct_all_words': '111111 111 1111 11 1111 '
            },
            "en": {
                'real_transcript': ' Hi there, how are you?',
                'ipa_transcript': 'haɪ ðɛr, haʊ ər ju?',
                'pronunciation_accuracy': '100',
                'real_transcripts': 'Hi there, how are you?',
                'matched_transcripts': 'Hi there, how are you?',
                'real_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'matched_transcripts_ipa': 'haɪ ðɛr, haʊ ər ju?',
                'pair_accuracy_category': '0 0 0 0 0',
                'start_time': '0.0 0.09 0.41 0.53 0.65',
                'end_time': '0.19 0.35 0.63 0.75 0.91',
                'is_letter_correct_all_words': '11 111111 111 111 1111 '
            }
        }
    }
}

expected_get_speech_to_score = {
    "de": {
        "real_transcript": real_transcript["de"],
        'ipa_transcript': ' ɪç biːn aːlɛks, vɛːr biːn ɪç t͡suː tuːn?',
        'pronunciation_accuracy': 24.0,
        "real_transcripts": text_dict["de"],
        'matched_transcripts': 'Alex, wer ich - tun?',
        "real_transcripts_ipa": real_transcripts_ipa["de"],
        'matched_transcripts_ipa': 'aːlɛks, vɐ ɪç - tuːn?',
        'pair_accuracy_category': '2 2 2 2 2',
        'start_time': '0.51 1.15 1.75 2.03 2.03',
        'end_time': '0.97 1.41 2.03 2.33 2.33',
        'is_letter_correct_all_words': '000101 101 0010 00 0001 '
    },
    "en": {
        "real_transcript": real_transcript["en"],
        'ipa_transcript': 'heɪ ðɛr, haʊ ər ju?',
        'pronunciation_accuracy': 88.0,
        "real_transcripts": text_dict["en"],
        'matched_transcripts': 'Hey there, how are you?',
        "real_transcripts_ipa": real_transcripts_ipa["en"],
        'matched_transcripts_ipa': 'heɪ ðɛr, haʊ ər ju?',
        'pair_accuracy_category': '2 0 0 0 0',
        'start_time': '0.0 0.57 0.97 1.07 1.19',
        'end_time': '0.67 0.85 1.17 1.29 1.47',
        'is_letter_correct_all_words': '10 111111 111 111 1111 '
    },
}
expected_with_audio_files_splitted_list = {
    "de": {
        'audio_files': [
            f'{EVENTS_FOLDER / "test_de__part0_start0.51_end0.97..wav"}',
            f'{EVENTS_FOLDER / "test_de__part1_start1.15_end1.41..wav"}',
            f'{EVENTS_FOLDER / "test_de__part2_start1.75_end2.03..wav"}',
            f'{EVENTS_FOLDER / "test_de__part3_start2.03_end2.33..wav"}',
            f'{EVENTS_FOLDER / "test_de__part4_start2.03_end2.33..wav"}'
        ],
        "real_transcript": real_transcript["de"],
        'ipa_transcript': ' ɪç biːn aːlɛks, vɛːr biːn ɪç t͡suː tuːn?',
        'pronunciation_accuracy': '24.00',
        "real_transcripts": text_dict["de"],
        'matched_transcripts': 'Alex, wer ich - tun?',
        "real_transcripts_ipa": real_transcripts_ipa["de"],
        'matched_transcripts_ipa': 'aːlɛks, vɐ ɪç - tuːn?',
        'pair_accuracy_category': '2 2 2 2 2',
        'start_time': '0.51 1.15 1.75 2.03 2.03',
        'end_time': '0.97 1.41 2.03 2.33 2.33',
        'is_letter_correct_all_words': '000101 101 0010 00 0001 '
    },
    "en": {
        'audio_files': [
            f'{EVENTS_FOLDER / "test_en__part0_start0.0_end0.67..wav"}',
            f'{EVENTS_FOLDER / "test_en__part1_start0.57_end0.85..wav"}',
            f'{EVENTS_FOLDER / "test_en__part2_start0.97_end1.17..wav"}',
            f'{EVENTS_FOLDER / "test_en__part3_start1.07_end1.29..wav"}',
            f'{EVENTS_FOLDER / "test_en__part4_start1.19_end1.47..wav"}'
        ],
        # "audio_durations": [], # checking only if the audio durations are floats and > 0
        "real_transcript": real_transcript["en"],
        "ipa_transcript": "heɪ ðɛr, haʊ ər ju?",
        "pronunciation_accuracy": "88.00",
        "real_transcripts": text_dict["en"],
        "matched_transcripts": "Hey there, how are you?",
        "real_transcripts_ipa": real_transcripts_ipa["en"],
        "matched_transcripts_ipa": "heɪ ðɛr, haʊ ər ju?",
        "pair_accuracy_category": "2 0 0 0 0",
        "start_time": "0.0 0.57 0.97 1.07 1.19",
        "end_time": "0.67 0.85 1.17 1.29 1.47",
        "is_letter_correct_all_words": "10 111111 111 111 1111 "
    },
}
expected_with_selected_word_valid_index = {
    "de": {
        "audio_files": [
            f'{EVENTS_FOLDER / "test_de_easy__part0_start0.0_end0.4733125..wav"}',
            f'{EVENTS_FOLDER / "test_de_easy__part1_start0.3733125_end0.70425..wav"}',
            f'{EVENTS_FOLDER / "test_de_easy__part2_start0.60425_end0.8966875..wav"}',
            f'{EVENTS_FOLDER / "test_de_easy__part3_start0.7966875_end1.089125..wav"}',
            f'{EVENTS_FOLDER / "test_de_easy__part4_start0.989125_end1.3200625..wav"}',
        ],
        # "audio_durations": [], # checking only if the audio durations are floats and > 0
        "real_transcript": "hallo wie geht es dir",
        "ipa_transcript": "haloː viː ɡeːt ɛːs diːɐ̯",
        "pronunciation_accuracy": 100.0,
        "real_transcripts": text_dict["de"],
        "matched_transcripts": "hallo wie geht es dir",
        "real_transcripts_ipa": real_transcripts_ipa["de"],
        "matched_transcripts_ipa": "haloː viː ɡeːt ɛːs diːɐ̯",
        "pair_accuracy_category": "0 0 0 0 0",
        "start_time": "0.0 0.3733125 0.60425 0.7966875 0.989125",
        "end_time": "0.4733125 0.70425 0.8966875 1.089125 1.3200625",
        "is_letter_correct_all_words": "111111 111 1111 11 1111 ",
    },
    "en": {
        "audio_files": [
            f'{EVENTS_FOLDER / "test_en_easy__part0_start0.0_end0.1625..wav"}',
            f'{EVENTS_FOLDER / "test_en_easy__part1_start0.0625_end0.3875..wav"}',
            f'{EVENTS_FOLDER / "test_en_easy__part2_start0.2875_end0.575..wav"}',
            f'{EVENTS_FOLDER / "test_en_easy__part3_start0.475_end0.8..wav"}',
            f'{EVENTS_FOLDER / "test_en_easy__part4_start0.7_end0.9875..wav"}',
        ],
        "audio_durations": [
            0.1625,
            0.325,
            0.22000000000000003,
            0.32500000000000007,
            0.2875000000000001,
        ],
        "real_transcript": "i there how are you",
        "ipa_transcript": "aɪ ðɛr haʊ ər ju",
        "pronunciation_accuracy": 94.0,
        "real_transcripts": text_dict["en"],
        "matched_transcripts": "i there how are you",
        "real_transcripts_ipa": real_transcripts_ipa["en"],
        "matched_transcripts_ipa": "aɪ ðɛr haʊ ər ju",
        "pair_accuracy_category": "2 0 0 0 0",
        "start_time": "0.0 0.0625 0.2875 0.475 0.7",
        "end_time": "0.1625 0.3875 0.575 0.8 0.9875",
        "is_letter_correct_all_words": "01 111111 111 111 1111 ",
    },
}
