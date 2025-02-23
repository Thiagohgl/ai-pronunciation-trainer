import os
from pathlib import Path
import gradio as gr

import js
from constants import PROJECT_ROOT_FOLDER, app_logger, sample_rate_start, MODEL_NAME_DEFAULT, model_urls
import lambdaGetSample
import lambdaSpeechToScore
import lambdaTTS


css = """
.speech-output-label p {color: grey; margin-bottom: white;}
.background-white {background-color: white !important; }
.speech-output-group {padding: 12px;}
.speech-output-container {min-height: 60px;}
.speech-output-html {text-align: left; }
"""
word_idx_text = "Current word index"


def get_textbox_hidden(text = None):
    if text:
        return gr.Number(value=text, visible=False)
    return gr.Textbox(visible=False)

def get_number_hidden(x: int = None):
    if x:
        return gr.Number(value=x, visible=False)
    return gr.Number(visible=False)

def clear():
    return None


def clear2():
    return None, None


with gr.Blocks(css=css, head=js.head_driver_tour) as gradio_app:
    local_storage = gr.BrowserState([0.0, 0.0])
    app_logger.info("start gradio app building...")

    project_root_folder = Path(PROJECT_ROOT_FOLDER)
    with open(project_root_folder / "app_description.md", "r", encoding="utf-8") as app_description_src:
        md_app_description = app_description_src.read()
        model_url = model_urls[MODEL_NAME_DEFAULT]
        gr.Markdown(md_app_description.format(
            sample_rate_start=sample_rate_start,
            model_name=MODEL_NAME_DEFAULT,
            model_url=model_url
        ))
    with gr.Row():
        with gr.Column(scale=4, min_width=300):
            with gr.Row(elem_id="id-choose-random-phrase-by-language-and-difficulty"):
                with gr.Column(scale=2, min_width=80):
                    radio_language = gr.Radio(["de", "en"], label="Language", value="en", elem_id="radio-language-id-element")
                with gr.Column(scale=5, min_width=160):
                    radio_difficulty = gr.Radio(
                        label="Difficulty",
                        value=0,
                        choices=[
                            ("random", 0),
                            ("easy", 1),
                            ("medium", 2),
                            ("hard", 3),
                        ],
                        elem_id="radio-difficulty-id-element",
                    )
                with gr.Column(scale=1, min_width=100):
                    btn_random_phrase = gr.Button(value="Choose a random phrase", elem_id="btn-random-phrase-id-element")
            with gr.Row():
                with gr.Column(scale=7, min_width=300):
                    text_student_transcription = gr.Textbox(
                        lines=3,
                        label="Phrase to read for speech recognition",
                        value="Hi there, how are you?",
                        elem_id="text-student-transcription-id-element",
                    )
            with gr.Row():
                audio_tts = gr.Audio(label="Audio TTS", elem_id="audio-tts-id-element")
            with gr.Row():
                btn_run_tts = gr.Button(value="TTS in browser", elem_id="btn-run-tts-id-element")
                btn_run_tts_backend = gr.Button(value="TTS backend", elem_id="btn-run-tts-backend-id-element")
                btn_clear_tts = gr.Button(value="Clear TTS backend", elem_id="btn-clear-tts-backend-id-element")
                btn_clear_tts.click(clear, inputs=[], outputs=[audio_tts])
            with gr.Row():
                audio_student_recording_stt = gr.Audio(
                    label="Record a speech to evaluate",
                    sources=["microphone", "upload"],
                    type="filepath",
                    show_download_button=True,
                    elem_id="audio-student-recording-stt-id-element",
                )
            with gr.Row():
                num_audio_duration_hidden = gr.Number(label="num_first_audio_duration", value=0, interactive=False, visible=False)
                with gr.Accordion("Click here to expand the table examples", open=False, elem_id="accordion-examples-id-element"):
                    examples_text = gr.Examples(
                        examples=[
                            ["Hallo, wie geht es dir?", "de", 1],
                            ["Hi there, how are you?", "en", 1],
                            ["Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau.", "de", 2,],
                            ["Rome is home to some of the most beautiful monuments in the world.", "en", 2],
                            ["Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau, einem Ortsteil des drei Kilometer nordöstlich gelegenen Bad Brückenau im Landkreis Bad Kissingen in Bayern.", "de", 3],
                            ["Some machine learning models are designed to understand and generate human-like text based on the input they receive.", "en", 3],
                        ],
                        inputs=[text_student_transcription, radio_language, radio_difficulty],
                        elem_id="examples-text-id-element",
                    )
        with gr.Column(scale=4, min_width=320):
            text_transcribed_hidden = gr.Textbox(
                placeholder=None, label="Transcribed text", visible=False
            )
            text_letter_correctness = gr.Textbox(
                placeholder=None,
                label="Letters correctness",
                visible=False,
            )
            text_recording_ipa = gr.Textbox(
                placeholder="-", label="Student phonetic transcription", elem_id="text-student-recording-ipa-id-element", interactive=False
            )
            text_ideal_ipa = gr.Textbox(
                placeholder="-", label="Ideal phonetic transcription", elem_id="text-ideal-ipa-id-element", interactive=False
            )
            text_raw_json_output_hidden = gr.Textbox(placeholder=None, label="text_raw_json_output_hidden", visible=False)
            with gr.Group(elem_classes="speech-output-group background-white"):
                gr.Markdown("Speech accuracy output", elem_classes="speech-output-label background-white")
                with gr.Group(elem_classes="speech-output-container background-white"):
                    html_output = gr.HTML(
                        label="Speech accuracy output",
                        elem_id="speech-output",
                        show_label=False,
                        visible=True,
                        render=True,
                        value=" - ",
                        elem_classes="speech-output-html background-white",
                    )
            with gr.Row():
                with gr.Column(min_width=100, elem_classes="speech-accuracy-score-container row2 col1", elem_id="id-current-speech-accuracy-score-container"):
                    num_pronunciation_accuracy = gr.Number(label="Current score %", elem_id="number-pronunciation-accuracy-id-element", interactive=False, value=0)
                with gr.Column(min_width=100, elem_classes="speech-accuracy-score-container row2 col2", elem_id="id-global-speech-accuracy-score-de-container"):
                    num_score_de = gr.Number(label="Global score DE %", value=0, interactive=False, elem_id="number-score-de-id-element")
                with gr.Column(min_width=100, elem_classes="speech-accuracy-score-container row2 col3", elem_id="id-global-speech-accuracy-score-en-container"):
                    num_score_en = gr.Number(label="Global score EN %", value=0, interactive=False, elem_id="number-score-en-id-element")
            btn_recognize_speech_accuracy = gr.Button(value="Get speech accuracy score (%)", elem_id="btn-recognize-speech-accuracy-id-element")
            with gr.Row(elem_id="id-replay-splitted-audio-by-words"):
                num_tot_recognized_words = gr.Number(label="Total recognized words", visible=False, minimum=0, interactive=False)
                with gr.Column(scale=1, min_width=50):
                    num_selected_recognized_word = gr.Number(label=word_idx_text, visible=True, minimum=0, value=0, interactive=False)
                with gr.Column(scale=4, min_width=100):
                    audio_sliced_student_recording_stt = gr.Audio(
                        label="Sliced student speech output",
                        type="filepath",
                        show_download_button=True,
                        elem_id="audio-sliced-student-recording-stt-id-element",
                    )
            text_selected_recognized_word_hidden = gr.Textbox(label="text_selected_recognized_word", value="placeholder", interactive=False, visible=False)

    def get_updated_score_by_language(text: str, audio_rec: str | Path, lang: str, score_de: float, score_en: float):
        import json
        _transcribed_text, _letter_correctness, _pronunciation_accuracy, _recording_ipa, _ideal_ipa, _num_tot_recognized_word, first_audio_file, _res, _ = lambdaSpeechToScore.get_speech_to_score_tuple(text, audio_rec, lang, remove_random_file=False)
        new_num_selected_recognized_word = gr.Number(label=word_idx_text, visible=True, value=0)
        words_list = _transcribed_text.split()
        first_word = words_list[0]
        json_res_loaded = json.loads(_res)
        audio_durations = json_res_loaded["audio_durations"]
        first_audio_duration = audio_durations[0]
        output = {
            text_transcribed_hidden: _transcribed_text,
            text_letter_correctness: _letter_correctness,
            num_pronunciation_accuracy: _pronunciation_accuracy,
            text_recording_ipa: _recording_ipa,
            text_ideal_ipa: _ideal_ipa,
            text_raw_json_output_hidden: _res,
            num_tot_recognized_words: _num_tot_recognized_word,
            num_selected_recognized_word: new_num_selected_recognized_word,
            audio_sliced_student_recording_stt: first_audio_file,
            text_selected_recognized_word_hidden: first_word,
            num_audio_duration_hidden: first_audio_duration
        }
        match lang:
            case "de":
                return {
                    num_score_de: float(score_de) + float(_pronunciation_accuracy),
                    num_score_en: float(score_en),
                    **output
                }
            case "en":
                return {
                    num_score_en: float(score_en) + float(_pronunciation_accuracy),
                    num_score_de: float(score_de),
                    **output
                }
            case _:
                raise NotImplementedError(f"Language {lang} not supported")

    btn_recognize_speech_accuracy.click(
        get_updated_score_by_language,
        inputs=[text_student_transcription, audio_student_recording_stt, radio_language, num_score_de, num_score_en],
        outputs=[
            text_transcribed_hidden,
            text_letter_correctness,
            num_pronunciation_accuracy,
            text_recording_ipa,
            text_ideal_ipa,
            text_raw_json_output_hidden,
            num_score_de,
            num_score_en,
            num_tot_recognized_words,
            num_selected_recognized_word,
            audio_sliced_student_recording_stt,
            text_selected_recognized_word_hidden,
            num_audio_duration_hidden
        ],
    )

    def change_max_selected_words(n):
        app_logger.info(f"change_max_selected_words: {n} ...")
        num_max_selected_words = n -1 
        app_logger.info(f"num_selected_recognized_words.maximum, pre: {num_selected_recognized_word.maximum} ...")
        label = word_idx_text if n == 0 else f"{word_idx_text} (from 0 to {num_max_selected_words})"
        interactive = n > 0
        app_logger.info(f"change_max_selected_words: {n}, is interactive? {interactive} ...")
        new_num_selected_recognized_words = gr.Number(label=label, visible=True, value=0, minimum=0, maximum=num_max_selected_words, interactive=interactive)
        app_logger.info(f"num_selected_recognized_words.maximum, post: {num_selected_recognized_word.maximum} ...")
        return new_num_selected_recognized_words

    num_tot_recognized_words.change(
        fn=change_max_selected_words,
        inputs=[num_tot_recognized_words],
        outputs=[num_selected_recognized_word],
    )

    def clear3():
        return None, None, None, None, None, None, 0, 0, 0

    text_student_transcription.change(
        clear3,
        inputs=[],
        outputs=[
            audio_student_recording_stt, audio_tts, audio_sliced_student_recording_stt, text_recording_ipa, text_ideal_ipa, text_transcribed_hidden,
            num_pronunciation_accuracy, num_selected_recognized_word, num_pronunciation_accuracy
        ],
    )

    def reset_max_total_recognized_words(content_text_recording_ipa, content_num_tot_recognized_words):
        if content_text_recording_ipa is None or content_text_recording_ipa == "":
            app_logger.info("reset_max_total_recognized_words...")
            new_num_tot_recognized_words = gr.Number(label="Total recognized words", visible=False, value=0, minimum=0, interactive=False)
            return new_num_tot_recognized_words
        return content_num_tot_recognized_words

    text_recording_ipa.change(
        reset_max_total_recognized_words,
        inputs=[text_recording_ipa, num_tot_recognized_words],
        outputs=[
            num_tot_recognized_words
        ],
    )
    text_recording_ipa.change(
        None,
        inputs=[get_textbox_hidden(), get_textbox_hidden(), get_number_hidden()],
        outputs=[html_output],
        js=js.js_update_ipa_output,
    )

    btn_run_tts.click(fn=None, inputs=[text_student_transcription, radio_language], outputs=audio_tts, js=js.js_play_audio)
    btn_run_tts_backend.click(
        fn=lambdaTTS.get_tts,
        inputs=[text_student_transcription, radio_language],
        outputs=audio_tts,
    )
    btn_random_phrase.click(
        fn=lambdaGetSample.get_random_selection,
        inputs=[radio_language, radio_difficulty],
        outputs=[text_student_transcription],
    )
    btn_random_phrase.click(
        clear2,
        inputs=[],
        outputs=[audio_student_recording_stt, audio_tts]
    )
    html_output.change(
        None,
        inputs=[text_transcribed_hidden, text_letter_correctness, num_selected_recognized_word],
        outputs=[html_output],
        js=js.js_update_ipa_output,
    )
    num_selected_recognized_word.input(
        fn=lambdaSpeechToScore.get_selected_word,
        inputs=[num_selected_recognized_word, text_raw_json_output_hidden],
        outputs=[audio_sliced_student_recording_stt, text_selected_recognized_word_hidden, num_audio_duration_hidden],
    )
    audio_sliced_student_recording_stt.play(
        fn=None,
        inputs=[text_selected_recognized_word_hidden, radio_language, num_audio_duration_hidden],
        outputs=audio_sliced_student_recording_stt,
        js=js.js_play_audio
    )
    
    @gradio_app.load(inputs=[local_storage], outputs=[num_score_de, num_score_en])
    def load_from_local_storage(saved_values):
        app_logger.info(f"loading from local storage: {saved_values} ...")
        return saved_values[0], saved_values[1]

    @gr.on([num_score_de.change, num_score_en.change], inputs=[num_score_de, num_score_en], outputs=[local_storage])
    def save_to_local_storage(score_de, score_en):
        return [score_de, score_en]


if __name__ == "__main__":
    try:
        gradio_app.launch()
    except Exception as ex:
        app_logger.error(f"Error: {ex}")
        raise ex
