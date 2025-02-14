

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
let SingleWordIpaPairBackup;

// API related variables
let AILanguage = "de"; // Standard is German

// Read the Public Key from an env variable (it's managed within the python/flask code - STScoreAPIKey).
// If, for some reason, you would like a private one, send-me a message and we can discuss some possibilities
try {
    const  cookieList = document.cookie.split("=")
    const  STScoreAPIKey = cookieList[1]
} catch (error) {
    console.log("STScoreAPIKey::error:", error, "#")
}

let apiMainPathSample = '';// 'http://127.0.0.1:3001';// 'https://a3hj0l2j2m.execute-api.eu-central-1.amazonaws.com/Prod';
let apiMainPathSTS = '';// 'https://wrg7ayuv7i.execute-api.eu-central-1.amazonaws.com/Prod';
const defaultOriginalScript = "Click on the bar on the right to generate a new sentence (please use chrome web browser)."
const defaultErrorScript = "Server error. Either the daily quota of the server is over or there was some internal error. You can try to generate a new sample in a few seconds. If the error persist, try comming back tomorrow or download the local version from Github :)";
const editErrorScript = "Please edit this text before generating the IPA for a custom sentence!";
const browserUnsupported = "Browser unsupported";
const recordingError = "Recording error, please try again or restart page.";

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
const unblockUI = (unlockIPACustomText = false) => {
    document.getElementById("recordAudio").classList.remove('disabled');
    document.getElementById("playSampleAudio").classList.remove('disabled');
    document.getElementById("buttonNext").onclick = () => getNextSample();
    document.getElementById("nextButtonDiv").classList.remove('disabled');
    document.getElementById("original_script").classList.remove('disabled');
    document.getElementById("buttonNext").style["background-color"] = '#58636d';

    if (currentSoundRecorded)
        document.getElementById("playRecordedAudio").classList.remove('disabled');

    enableElementWithClass("input-uploader-audio-file")
    if (unlockIPACustomText) {
        enableElementWithClass("buttonCustomText")
    }
};

const blockUI = () => {

    document.getElementById("recordAudio").classList.add('disabled');
    document.getElementById("playSampleAudio").classList.add('disabled');
    document.getElementById("buttonNext").onclick = null;
    document.getElementById("original_script").classList.add('disabled');
    document.getElementById("playRecordedAudio").classList.add('disabled');

    document.getElementById("buttonNext").classList.add('disabled');
    disableElementWithClass("input-uploader-audio-file")

};

const UIError = (errorMsg = defaultErrorScript) => {
    blockUI();
    document.getElementById("buttonNext").onclick = () => getNextSample(); //If error, user can only try to get a new sample
    document.getElementById("buttonNext").style["background-color"] = '#58636d';

    document.getElementById("recorded_ipa_script").innerHTML = "";
    document.getElementById("single_word_ipa_pair_error").style["display"] = "inline";
    document.getElementById("single_word_ipa_pair_separator").style["display"] = "none";
    document.getElementById("single_word_ipa_reference_recorded").style["display"] = "none";
    document.getElementById("single_word_ipa_current").style["display"] = "none";
    document.getElementById("ipa_script").innerText = "Error"

    document.getElementById("main_title").innerText = 'Server Error';
    document.getElementById("original_script").innerHTML = errorMsg;
};

const disableElementWithClass = (id) => {
    let el = document.getElementById(id)
    el.disabled = true;
    el.classList.remove('darkgreen');
}

const enableElementWithClass = (id) => {
    let el = document.getElementById(id)
    el.removeAttribute("disabled");
    el.classList.add('darkgreen');
}

const UINotSupported = () => {
    unblockUI();

    document.getElementById("main_title").innerText = browserUnsupported;

}

const UIRecordingError = () => {
    unblockUI();
    document.getElementById("main_title").innerText = recordingError;
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
    await fetch(soundsPath + '/ASR_good.wav').then(data => data.arrayBuffer()).
    then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
    then(decodeAudioData => {
        soundFileGood = decodeAudioData;
    });

    await fetch(soundsPath + '/ASR_okay.wav').then(data => data.arrayBuffer()).
    then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
    then(decodeAudioData => {
        soundFileOkay = decodeAudioData;
    });

    await fetch(soundsPath + '/ASR_bad.wav').then(data => data.arrayBuffer()).
    then(arrayBuffer => ctx.decodeAudioData(arrayBuffer)).
    then(decodeAudioData => {
        soundFileBad = decodeAudioData;
    });
}

const getCustomTextIsDisabled = () => {
    const checkText = document.getElementById("original_script").innerText.trim();
    let cleanedText = checkText.toString().replace(/[^\w\s]/gi, ' ').trim();
    return checkText === defaultOriginalScript || checkText === defaultErrorScript || checkText === editErrorScript || cleanedText === "";
}

const getCustomText = async () => {
    blockUI();

    if (!serverIsInitialized)
        await initializeServer();

    if (!serverWorking) {
        UIError();
        return;
    }

    if (soundFileBad == null)
        cacheSoundFiles();

    if (getCustomTextIsDisabled()) {
        UIError(editErrorScript);
        return;
    }
    updateScore(parseFloat(document.getElementById("pronunciation_accuracy").innerHTML));

    document.getElementById("main_title").innerText = "Get IPA transcription for custom text...";

    try {
        const original_script_element = document.getElementById("original_script")
        const original_script = original_script_element.innerText;
        await fetch(apiMainPathSample + '/getSample', {
            method: "post",
            body: JSON.stringify({
                "language": AILanguage,
                "transcript": original_script
            }),
            headers: { "X-Api-Key": STScoreAPIKey }
        }).then(res => res.json()).
        then(data => {
            formatTranscriptData(data);
            audioRecorded = undefined;
        })
    }
    catch (err)
    {
        console.log("getCustomText::err:", err)
        UIError();
    }
}

const getNextSample = async () => {
    blockUI();

    if (!serverIsInitialized)
        await initializeServer();

    if (!serverWorking) {
        UIError();
        return;
    }

    if (soundFileBad == null)
        cacheSoundFiles();



    updateScore(parseFloat(document.getElementById("pronunciation_accuracy").innerHTML));

    document.getElementById("main_title").innerText = "Processing new sample...";


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
            headers: { "X-Api-Key": STScoreAPIKey }
        }).then(res => res.json()).
        then(data => {
            formatTranscriptData(data);
        })
    }
    catch (err)
    {
        console.log("getNextSample::err:", err)
        UIError();
    }
};

const formatTranscriptData = (data) => {
    let doc = document.getElementById("original_script");
    currentText = data.real_transcript;
    doc.innerText = currentText;

    currentIpa = data.ipa_transcript

    let doc_ipa = document.getElementById("ipa_script");
    doc_ipa.ariaLabel = "ipa_script"
    doc_ipa.innerText = `/ ${currentIpa} /`;

    let recorded_ipa_script = document.getElementById("recorded_ipa_script")
    recorded_ipa_script.ariaLabel = "recorded_ipa_script"
    recorded_ipa_script.innerText = ""

    let pronunciation_accuracy = document.getElementById("pronunciation_accuracy")
    pronunciation_accuracy.ariaLabel = "pronunciation_accuracy"
    pronunciation_accuracy.innerHTML = "";

    // restore a clean state for document.getElementById("single_word_ipa_pair") to avoid errors when playing the word audio
    $(document).ready(function() {
        $("#single_word_ipa_pair").replaceWith(SingleWordIpaPairBackup.clone())
    })

    document.getElementById("section_accuracy").innerText = `| Score: ${currentScore.toString()} - (${currentSample.toString()})`;
    currentSample += 1;

    document.getElementById("main_title").innerText = page_title;

    document.getElementById("translated_script").innerText = data.transcript_translation;

    currentSoundRecorded = false;
    unblockUI(true);
    document.getElementById("playRecordedAudio").classList.add('disabled');
}

const updateRecordingState = async () => {
    return isRecording ? stopRecording() : recordSample();
}

const generateWordModal = (word_idx) => {
    wrapWordForPlayingLink(real_transcripts_ipa[word_idx], word_idx, false, "black")
    wrapWordForPlayingLink(matched_transcripts_ipa[word_idx], word_idx, true, accuracy_colors[parseInt(wordCategories[word_idx])])
}

const recordSample = async () => {

    document.getElementById("main_title").innerText = "Recording... click again when done speaking";
    document.getElementById("recordIcon").innerHTML = 'pause_presentation';
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
        if (voices[idx].lang.slice(0, 2) === languageIdentifier && voices[idx].name === languageName) {
            voice_synth = voices[idx];
            languageFound = true;
            break;
        }

    }
    // If specific voice not found, search anything with the same language
    if (!languageFound) {
        for (idx = 0; idx < voices.length; idx++) {
            if (voices[idx].lang.slice(0, 2) === languageIdentifier) {
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


async function sendAudioToGetAccuracyFromRecordedAudio(audioBase64) {
    try {
        // Get currentText from "original_script" div, in case user has change it
        let text = document.getElementById("original_script").innerHTML;
        // Remove html tags
        text = text.replace(/<[^>]*>?/gm, '');
        //Remove spaces on the beginning and end
        text = text.trim();
        // Remove double spaces
        text = text.replace(/\s\s+/g, ' ');
        currentText = [text];
        let useDTWValue = document.getElementById("checkbox-dtw").checked

        await fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
            method: "post",
            body: JSON.stringify({
                "title": currentText[0], "base64Audio": audioBase64, "language": AILanguage, "useDTW": useDTWValue
            }),
            headers: {"X-Api-Key": STScoreAPIKey}

        }).then(res => res.json()).then(data => {

            if (playAnswerSounds)
                playSoundForAnswerAccuracy(parseFloat(data.pronunciation_accuracy))

            document.getElementById("recorded_ipa_script").innerText = `/ ${data.ipa_transcript} /`;
            document.getElementById("recordAudio").classList.add('disabled');
            document.getElementById("main_title").innerText = page_title;
            document.getElementById("pronunciation_accuracy").innerText = `${data.pronunciation_accuracy}%`;
            document.getElementById("ipa_script").innerText = data.real_transcripts_ipa

            lettersOfWordAreCorrect = data.is_letter_correct_all_words.split(" ")

            startTime = data.start_time;
            endTime = data.end_time;

            real_transcripts_ipa = data.real_transcripts_ipa.split(" ")
            matched_transcripts_ipa = data.matched_transcripts_ipa.split(" ")
            wordCategories = data.pair_accuracy_category.split(" ")
            let arrayOriginalText = currentText[0].split(" ")

            let arrayColoredWords = document.getElementById("original_script")
            arrayColoredWords.textContent = ""

            for (let wordIdx in arrayOriginalText) {
                let currentWordText = arrayOriginalText[wordIdx]

                let letterIsCorrect = lettersOfWordAreCorrect[wordIdx]

                let coloredWordTemp = document.createElement("a")
                for (let letterIdx in currentWordText) {
                    let letterCorrect = letterIsCorrect[letterIdx] === "1"
                    let containerLetter = document.createElement("span")
                    containerLetter.style.color = letterCorrect ? 'green' : "red"
                    containerLetter.innerText = currentWordText[letterIdx];
                    coloredWordTemp.appendChild(containerLetter)

                    coloredWordTemp.ariaLabel = `word${wordIdx}${currentWordText}`.replace(/[^a-zA-Z0-9]/g, "")
                    console.log(`coloredWordTemp.ariaLabel:${coloredWordTemp.ariaLabel}!`)
                    coloredWordTemp.style.whiteSpace = "nowrap"
                    coloredWordTemp.style.textDecoration = "underline"
                    coloredWordTemp.onclick = function () {
                        generateWordModal(wordIdx.toString())
                    }
                    arrayColoredWords.appendChild(coloredWordTemp)
                }
                let containerSpace = document.createElement("span")
                containerSpace.textContent = " "
                arrayColoredWords.appendChild(containerSpace)
            }

            currentSoundRecorded = true;
            unblockUI();
            document.getElementById("playRecordedAudio").classList.remove('disabled');

        });
    } catch {
        UIError();
    }
}

const startMediaDevice = () => {
    navigator.mediaDevices.getUserMedia(mediaStreamConstraints).then(_stream => {
        stream = _stream
        mediaRecorder = new MediaRecorder(stream);

        let currentSamples = 0
        mediaRecorder.ondataavailable = event => {

            currentSamples += event.data.length
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
            await sendAudioToGetAccuracyFromRecordedAudio(audioBase64);
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
    playWithMozillaApi(currentText[0]);
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
                document.getElementById("main_title").innerHTML = "Recorded Sound was played";
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
    playWithMozillaApi(currentText[0].split(' ')[word_idx]);
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

const wrapWordForPlayingLink = (word, word_idx, isSpokenWord, word_color) => {
    // for some reason here the function is swapped
    const fn = isSpokenWord ? "playRecordedWord" : "playCurrentWord";
    const id = isSpokenWord ? "single_word_ipa_current" : "single_word_ipa_reference_recorded";
    const element = document.getElementById(id)
    element.innerText = word
    element.href = `javascript:${fn}(${word_idx.toString()})`
    element.removeAttribute("disabled")
    element.style["color"] = word_color
    element.style["whiteSpace"] = "nowrap"
}

// ########## Function to initialize server ###############
// This is to try to avoid aws lambda cold start
try {
    fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
        method: "post",
        body: JSON.stringify({ "title": '', "base64Audio": '', "language": AILanguage }),
        headers: { "X-Api-Key": STScoreAPIKey }

    });
}
catch { }

const audioToBase64 = async (audioFile) => {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.onerror = reject;
        reader.onload = (e) => resolve(e.target.result);

        // custom: set the global variable 'audioRecorded' to play later the uploaded audio
        let audioUrl = URL.createObjectURL(audioFile);
        audioRecorded = new Audio(audioUrl);

        reader.readAsDataURL(audioFile);
    });
}

const audioUpload = async (audioFile) => {
    console.log("starting uploading the file...")
    let audioBase64 = await audioToBase64(audioFile);
    console.log("file uploaded, starting making the request...")
    await sendAudioToGetAccuracyFromRecordedAudio(audioBase64);
    console.log("request done!")
}

const initializeServer = async () => {

    let valid_response = false;
    document.getElementById("main_title").innerText = 'Initializing server, this may take up to 2 minutes...';
    $(document).ready(function() {
        // required to properly reset the #single_word_ipa_pair element
        SingleWordIpaPairBackup = $("#single_word_ipa_pair").clone();
    })
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
                headers: { "X-Api-Key": STScoreAPIKey }

            }).then(
                valid_response = true);
            serverIsInitialized = true;
        }
        catch (e)
        {
            number_of_tries += 1;
            console.log(`initializeServer::error: ${e}, retry n=${number_of_tries}.`)
        }
    }
}

