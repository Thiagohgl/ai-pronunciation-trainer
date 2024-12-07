// Audio context initialization
let mediaRecorder, audioChunks, audioBlob, stream, audioRecorded;
const ctx = new AudioContext();
let currentAudioForPlaying;
let lettersOfWordAreCorrect = [];

// UI-related variables
const page_title = "AI Pronunciation Trainer";
const accuracy_colors = ["green", "orange", "red"];
let badScoreThreshold = 30;
let mediumScoreThreshold = 70;
let currentSample = 0;
let currentScore = 0.;
let sample_difficult = 0;
let scoreMultiplier = 1;
let playAnswerSounds = true;
let isNativeSelectedForPlayback = true;
let isRecording = false;
let serverIsInitialized = false;
let serverWorking = true;
let languageFound = true;
let currentSoundRecorded = false;
let currentText, currentIpa, real_transcripts_ipa, matched_transcripts_ipa;
let wordCategories;
let startTime, endTime;

// API related variables 
let AILanguage = "de"; // Standard is German

let STScoreAPIKey = '';
let apiMainPathSample = '';// 'http://127.0.0.1:3001';// 'https://a3hj0l2j2m.execute-api.eu-central-1.amazonaws.com/Prod';
let apiMainPathSTS = '';// 'https://wrg7ayuv7i.execute-api.eu-central-1.amazonaws.com/Prod';


// Variables to playback accuracy sounds
let soundsPath = '../static';//'https://stscore-sounds-bucket.s3.eu-central-1.amazonaws.com';
let soundFileGood = null;
let soundFileOkay = null;
let soundFileBad = null;

// Speech generation
var synth = window.speechSynthesis;
let voice_idx = 0;
let voice_synth = null;

//############################ UI general control functions ###################
const unblockUI = () => {
    document.getElementById("recordAudio").classList.remove('disabled');
    document.getElementById("playSampleAudio").classList.remove('disabled');
    document.getElementById("buttonNext").onclick = () => getNextSample();
    document.getElementById("nextButtonDiv").classList.remove('disabled');
    document.getElementById("original_script").classList.remove('disabled');
    document.getElementById("buttonNext").style["background-color"] = '#58636d';

    if (currentSoundRecorded)
        document.getElementById("playRecordedAudio").classList.remove('disabled');
};

const blockUI = () => {

    document.getElementById("recordAudio").classList.add('disabled');
    document.getElementById("playSampleAudio").classList.add('disabled');
    document.getElementById("buttonNext").onclick = null;
    document.getElementById("original_script").classList.add('disabled');
    document.getElementById("playRecordedAudio").classList.add('disabled');

    document.getElementById("buttonNext").style["background-color"] = '#adadad';


};

const UIError = () => {
    blockUI();
    document.getElementById("buttonNext").onclick = () => getNextSample(); //If error, user can only try to get a new sample
    document.getElementById("buttonNext").style["background-color"] = '#58636d';

    document.getElementById("recorded_ipa_script").innerText = "";
    document.getElementById("single_word_ipa_pair").innerText = "Error";
    document.getElementById("ipa_script").innerText = "Error"

    document.getElementById("main_title").innerText = 'Server Error';
    document.getElementById("original_script").innerText = 'Server error. Either the daily quota of the server is over or there was some internal error. You can try to generate a new sample in a few seconds. If the error persist, try comming back tomorrow or download the local version from Github :)';
};

const UINotSupported = () => {
    unblockUI();

    document.getElementById("main_title").innerText = "Browser unsupported";

}

const UIRecordingError = () => {
    unblockUI();
    document.getElementById("main_title").innerText = "Recording error, please try again or restart page.";
    startMediaDevice();
}



//################### Application state functions #######################
function updateScore(currentPronunciationScore) {

    if (Number.isNaN(currentPronunciationScore))
        return;
    currentScore += currentPronunciationScore * scoreMultiplier;
    currentScore = Math.round(currentScore);
}

const cacheSoundFiles = async () => {
    await fetch(soundsPath + '/ASR_good.wav').then(dataSound1 => dataSound1.arrayBuffer()).
        then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
        then(decodeAudioData => {
            soundFileGood = decodeAudioData;
        });

    await fetch(soundsPath + '/ASR_okay.wav').then(dataSound2 => dataSound2.arrayBuffer()).
        then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
        then(decodeAudioData => {
            soundFileOkay = decodeAudioData;
        });

    await fetch(soundsPath + '/ASR_bad.wav').then(dataSound3 => dataSound3.arrayBuffer()).
        then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
        then(decodeAudioData => {
            soundFileBad = decodeAudioData;
        });
}

const getNextSample = async () => {
    await prepareUiForNextSample()

    if (document.getElementById('lengthCat1').checked) {
        sample_difficult = 0;
        scoreMultiplier = 1.3;
    }
    else if (document.getElementById('lengthCat2').checked) {
        sample_difficult = 1;
        scoreMultiplier = 1;
    }
    else if (document.getElementById('lengthCat3').checked) {
        sample_difficult = 2;
        scoreMultiplier = 1.3;
    }
    else if (document.getElementById('lengthCat4').checked) {
        sample_difficult = 3;
        scoreMultiplier = 1.6;
    }

    try {
        await fetch(apiMainPathSample + '/getSample', {
            method: "post",
            body: JSON.stringify({
                "category": sample_difficult.toString(), "language": AILanguage
            }),
        }).then(res => res.json()).then(dataFromNextSample => {
            // console.debug(`getNextSample:: dataFromNextSample: `, typeof dataFromNextSample, "=>", dataFromNextSample, "#");
            populateSampleById(dataFromNextSample)
        })
    }
    catch {
        UIError();
    }

};

const prepareUiForNextSample = async () => {
    blockUI();

    if (!serverIsInitialized)
        await initializeServer();

    if (!serverWorking) {
        UIError();
        return;
    }

    if (soundFileBad == null)
        cacheSoundFiles();

    updateScore(parseFloat(document.getElementById("pronunciation_accuracy").innerText));

    document.getElementById("main_title").innerText = "Processing new sample...";
}

const populateSampleById = (dataById) => {
    // console.debug(`populateSampleById:: dataById: `, typeof dataById, "=>", dataById, "#");
    let doc = document.getElementById("original_script");
    currentText = dataById.real_transcript;
    doc.innerText = currentText;
    currentIpa = dataById.ipa_transcript

    let doc_ipa = document.getElementById("ipa_script");
    doc_ipa.innerText = `/ ${String(currentIpa)} /`

    document.getElementById("recorded_ipa_script").innerText = ""
    document.getElementById("pronunciation_accuracy").innerText = "";
    document.getElementById("single_word_ipa_pair").innerText = "Reference | Spoken"
    document.getElementById("section_accuracy").innerText = `| Score: ${currentScore.toString()} - sample n: ${currentSample.toString()}`;
    currentSample += 1;

    document.getElementById("main_title").innerText = page_title;
    document.getElementById("translated_script").innerText = dataById.transcript_translation;

    currentSoundRecorded = false;
    unblockUI();
    document.getElementById("playRecordedAudio").classList.add('disabled');
}

const updateRecordingState = async () => {
    if (isRecording) {
        stopRecording();
        return
    }
    else {
        recordSample()
        return;
    }
}

const generateWordModal = (word_idx) => {
    innerText0 = wrapWordForPlayingLink(real_transcripts_ipa[word_idx], word_idx, false, "black")
    innerText1 = wrapWordForPlayingLink(matched_transcripts_ipa[word_idx], word_idx, true, accuracy_colors[parseInt(wordCategories[word_idx])])
    document.getElementById("single_word_ipa_pair").innerText = `${innerText0} | ${innerText1}`
}

const recordSample = async () => {

    document.getElementById("main_title").innerText = "Recording... click again when done speaking";
    document.getElementById("recordIcon").innerText = 'pause_presentation';
    blockUI();
    document.getElementById("recordAudio").classList.remove('disabled');
    audioChunks = [];
    isRecording = true;
    mediaRecorder.start();

}

const changeLanguage = (language, generateNewSample = false) => {
    voices = synth.getVoices();
    AILanguage = language;
    languageFound = false;
    let languageIdentifier, languageName;
    document.getElementById("field-filter-samples").value = "";
    switch (language) {
        case 'de':
            document.getElementById("languageBox").innerText = "German";
            languageIdentifier = 'de';
            languageName = 'Anna';
            break;

        case 'en':
            document.getElementById("languageBox").innerText = "English";
            languageIdentifier = 'en';
            languageName = 'Daniel';
            break;
    };

    for (idx = 0; idx < voices.length; idx++) {
        if (voices[idx].lang.slice(0, 2) == languageIdentifier && voices[idx].name == languageName) {
            voice_synth = voices[idx];
            languageFound = true;
            break;
        }

    }
    // If specific voice not found, search anything with the same language 
    if (!languageFound) {
        for (idx = 0; idx < voices.length; idx++) {
            if (voices[idx].lang.slice(0, 2) == languageIdentifier) {
                voice_synth = voices[idx];
                languageFound = true;
                break;
            }
        }
    }
    if (generateNewSample)
        getNextSample();
}

//################### Speech-To-Score function ########################
const mediaStreamConstraints = {
    audio: {
        channelCount: 1,
        sampleRate: 48000
    }
}


const startMediaDevice = () => {
    navigator.mediaDevices.getUserMedia(mediaStreamConstraints).then(_stream => {
        stream = _stream
        mediaRecorder = new MediaRecorder(stream);

        let currentSamplesN = 0
        mediaRecorder.ondataavailable = event => {

            currentSamplesN += event.data.length
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {


            document.getElementById("recordIcon").innerHTML = 'mic';
            blockUI();


            audioBlob = new Blob(audioChunks, { type: 'audio/ogg;' });

            let audioUrl = URL.createObjectURL(audioBlob);
            audioRecorded = new Audio(audioUrl);

            let audioBase64 = await convertBlobToBase64(audioBlob);

            let minimumAllowedLength = 6;
            if (audioBase64.length < minimumAllowedLength) {
                setTimeout(UIRecordingError, 50); // Make sure this function finished after get called again
                return;
            }

            try {
                await fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
                    method: "post",
                    body: JSON.stringify({ "title": currentText, "base64Audio": audioBase64, "language": AILanguage }),

                }).then(res => res.json()).
                    then(mediaData => {

                        if (playAnswerSounds)
                            playSoundForAnswerAccuracy(parseFloat(mediaData.pronunciation_accuracy))

                        document.getElementById("recorded_ipa_script").innerText = `/ ${mediaData.ipa_transcript} /`
                        document.getElementById("recordAudio").classList.add('disabled');
                        document.getElementById("main_title").innerText = page_title;
                        document.getElementById("pronunciation_accuracy").innerText = `${mediaData.pronunciation_accuracy}%`;

                        lettersOfWordAreCorrect = mediaData.is_letter_correct_all_words.split(" ")


                        startTime = mediaData.start_time;
                        endTime = mediaData.end_time;


                        real_transcripts_ipa = mediaData.real_transcripts_ipa.split(" ")
                        matched_transcripts_ipa = mediaData.matched_transcripts_ipa.split(" ")
                        wordCategories = mediaData.pair_accuracy_category.split(" ")
                        let currentTextWords = currentText.split(" ")

                        coloredWords = "";
                        for (let word_idx = 0; word_idx < currentTextWords.length; word_idx++) {

                            wordTemp = '';
                            for (let letter_idx = 0; letter_idx < currentTextWords[word_idx].length; letter_idx++) {
                                letter_is_correct = lettersOfWordAreCorrect[word_idx][letter_idx] == '1'
                                if (letter_is_correct)
                                    color_letter = 'green'
                                else
                                    color_letter = 'red'

                                wordTemp += '<font color=' + color_letter + '>' + currentTextWords[word_idx][letter_idx] + "</font>"
                            }
                            currentTextWords[word_idx]
                            coloredWords += " " + wrapWordForIndividualPlayback(wordTemp, word_idx)
                        }



                        document.getElementById("original_script").innerHTML = coloredWords

                        currentSoundRecorded = true;
                        unblockUI();
                        document.getElementById("playRecordedAudio").classList.remove('disabled');

                    });
            }
            catch {
                UIError();
            }
        };

    });
};
startMediaDevice();

// ################### Audio playback ##################
const playSoundForAnswerAccuracy = async (accuracy) => {

    currentAudioForPlaying = soundFileGood;
    if (accuracy < mediumScoreThreshold) {
        if (accuracy < badScoreThreshold) {
            currentAudioForPlaying = soundFileBad;
        }
        else {
            currentAudioForPlaying = soundFileOkay;
        }
    }
    playback();

}

const playAudio = async () => {

    document.getElementById("main_title").innerText = "Generating sound...";
    // console.debug(`playAudio:: currentText: `, typeof currentText, "=>", currentText, "#");
    playWithMozillaApi(currentText);
    document.getElementById("main_title").innerText = "Current Sound was played";

};

function playback() {
    const playSound = ctx.createBufferSource();
    playSound.buffer = currentAudioForPlaying;
    playSound.connect(ctx.destination);
    playSound.start(ctx.currentTime)
}


const playRecording = async (start = null, end = null) => {
    blockUI();

    try {
        if (start == null || end == null) {
            endTimeInMs = Math.round(audioRecorded.duration * 1000)
            audioRecorded.addEventListener("ended", function () {
                audioRecorded.currentTime = 0;
                unblockUI();
                document.getElementById("main_title").innerText = "Recorded Sound was played";
            });
            await audioRecorded.play();

        }
        else {
            audioRecorded.currentTime = start;
            audioRecorded.play();
            durationInSeconds = end - start;
            endTimeInMs = Math.round(durationInSeconds * 1000);
            setTimeout(function () {
                unblockUI();
                audioRecorded.pause();
                audioRecorded.currentTime = 0;
                document.getElementById("main_title").innerText = "Recorded Sound was played";
            }, endTimeInMs);

        }
    }
    catch {
        UINotSupported();
    }
};

const playNativeAndRecordedWord = async (word_idx) => {

    if (isNativeSelectedForPlayback)
        playCurrentWord(word_idx)
    else
        playRecordedWord(word_idx);

    isNativeSelectedForPlayback = !isNativeSelectedForPlayback;
}

const stopRecording = () => {
    isRecording = false
    mediaRecorder.stop()
    document.getElementById("main_title").innerText = "Processing audio...";
}


const playCurrentWord = async (word_idx) => {

    document.getElementById("main_title").innerText = "Generating word...";
    // console.debug(`playCurrentWord:: currentText: `, typeof currentText, "=>", currentText, "#");
    playWithMozillaApi(currentText.split(' ')[word_idx]);
    document.getElementById("main_title").innerText = "Word was played";
}

// TODO: Check if fallback is correct
const playWithMozillaApi = (text) => {

    if (languageFound) {
        blockUI();
        if (voice_synth == null)
            changeLanguage(AILanguage);

        var utterThis = new SpeechSynthesisUtterance(text);
        utterThis.voice = voice_synth;
        utterThis.rate = 0.7;
        utterThis.onend = function (event) {
            unblockUI();
        }
        synth.speak(utterThis);
    }
    else {
        UINotSupported();
    }
}

const playRecordedWord = (word_idx) => {

    wordStartTime = parseFloat(startTime.split(' ')[word_idx]);
    wordEndTime = parseFloat(endTime.split(' ')[word_idx]);

    playRecording(wordStartTime, wordEndTime);

}

// ############# Utils #####################
const convertBlobToBase64 = async (blob) => {
    return await blobToBase64(blob);
}

const blobToBase64 = blob => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});

const wrapWordForPlayingLink = (word, word_idx, isFromRecording, word_accuracy_color) => {
    if (isFromRecording)
        return '<a style = " white-space:nowrap; color:' + word_accuracy_color + '; " href="javascript:playRecordedWord(' + word_idx.toString() + ')"  >' + word + '</a> '
    else
        return '<a style = " white-space:nowrap; color:' + word_accuracy_color + '; " href="javascript:playCurrentWord(' + word_idx.toString() + ')" >' + word + '</a> '
}

const wrapWordForIndividualPlayback = (word, word_idx) => {
    return '<a onmouseover="generateWordModal(' + word_idx.toString() + ')" style = " white-space:nowrap; " href="javascript:playNativeAndRecordedWord(' + word_idx.toString() + ')"  >' + word + '</a> '
}

// ########## Function to initialize server ###############
// This is to try to avoid aws lambda cold start 
try {
    fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
        method: "post",
        body: JSON.stringify({ "title": '', "base64Audio": '', "language": AILanguage }),

    });
}
catch { }

const initializeServer = async () => {

    valid_response = false;
    document.getElementById("main_title").innerText = 'Initializing server, this may take up to 2 minutes...';
    let number_of_tries = 0;
    let maximum_number_of_tries = 4;

    while (!valid_response) {
        if (number_of_tries > maximum_number_of_tries) {
            serverWorking = false;
            break;
        }

        try {
            await fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
                method: "post",
                body: JSON.stringify({ "title": '', "base64Audio": '', "language": AILanguage }),

            }).then(valid_response = true);
            serverIsInitialized = true;
        }
        catch {
            number_of_tries += 1;
        }
    }
}

const getSampleFromTextInput = async (AILanguage, textInput) => {
    await fetch(apiMainPathSample + '/getSample', {
        method: "post",
        body: JSON.stringify({
            "language": AILanguage, "transcript": textInput
        }),
    }).then(res => {
        let res2json = res.json()
        // console.debug(`getSampleFromTextInput:: res2json: `, typeof res2json, "=>", res2json, "#");
        return res2json
    }).then(dataOnInput => {
        console.log(`getSampleFromTextInput:: dataOnInput: `, typeof dataOnInput, "=>", dataOnInput, "#");
        populateSampleById(dataOnInput)
    })
}

$(document).ready(function(){
    $("#field-filter-samples").on("keyup", async function(e) {
        e.preventDefault();
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if (keycode === 13 || e.key === 'Enter') {
            var valueFilter = $(this).val()
            // console.debug(`input:: valueFilter: `, typeof valueFilter, "=>", valueFilter, ", AILanguage: ", AILanguage, "#");
            await getSampleFromTextInput(AILanguage, valueFilter);
        }
    });
});
