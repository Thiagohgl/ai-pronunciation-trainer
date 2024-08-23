

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

// Checking if language is saved in local storage
let savedLanguage = localStorage.getItem("ai-language");
if (savedLanguage) {
    AILanguage = savedLanguage;
}

// Displaying initial language name
window.addEventListener('load', () => {
    document.getElementById("languageBox").innerHTML = AILanguage === 'de' ? "German" : "English";
})


let STScoreAPIKey = 'rll5QsTiv83nti99BW6uCmvs9BDVxSB39SVFceYb'; // Public Key. If, for some reason, you would like a private one, send-me a message and we can discuss some possibilities
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

    document.getElementById("recorded_ipa_script").innerHTML = "";
    document.getElementById("single_word_ipa_pair").innerHTML = "Error";
    document.getElementById("ipa_script").innerHTML = "Error"

    document.getElementById("main_title").innerHTML = 'Server Error';
    document.getElementById("original_script").innerHTML = 'Server error. Either the daily quota of the server is over or there was some internal error. You can try to generate a new sample in a few seconds. If the error persist, try comming back tomorrow or download the local version from Github :)';
};

const UINotSupported = () => {
    unblockUI();

    document.getElementById("main_title").innerHTML = "Browser unsupported";

}

const UIRecordingError = () => {
    unblockUI();
    document.getElementById("main_title").innerHTML = "Recording error, please try again or restart page.";
    startMediaDevice();
}



//################### Application state functions #######################
function updateScore(currentPronunciationScore) {

    if (isNaN(currentPronunciationScore))
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

const getNextSample = async () => {

    // Chrome don't allow enabled automaticly
    // the sound context. The user should perfom
    // an interaction to start it.
    ctx.resume().then(() => {
        console.debug("Sound countext resumed");
    })

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

    document.getElementById("main_title").innerHTML = "Processing new sample...";


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



                let doc = document.getElementById("original_script");
                currentText = data.real_transcript;
                doc.innerHTML = currentText;

                currentIpa = data.ipa_transcript

                let doc_ipa = document.getElementById("ipa_script");
                doc_ipa.innerHTML = "/ " + currentIpa + " /";

                document.getElementById("recorded_ipa_script").innerHTML = ""
                document.getElementById("pronunciation_accuracy").innerHTML = "";
                document.getElementById("single_word_ipa_pair").innerHTML = "Reference | Spoken"
                document.getElementById("section_accuracy").innerHTML = "| Score: " + currentScore.toString() + " - (" + currentSample.toString() + ")";
                currentSample += 1;

                document.getElementById("main_title").innerHTML = page_title;

                document.getElementById("translated_script").innerHTML = data.transcript_translation;

                currentSoundRecorded = false;
                unblockUI();
                document.getElementById("playRecordedAudio").classList.add('disabled');

            })
    }
    catch
    {
        UIError();
    }


};

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

    document.getElementById("single_word_ipa_pair").innerHTML = wrapWordForPlayingLink(real_transcripts_ipa[word_idx], word_idx, false, "black")
        + ' | ' + wrapWordForPlayingLink(matched_transcripts_ipa[word_idx], word_idx, true, accuracy_colors[parseInt(wordCategories[word_idx])])
}

const recordSample = async () => {

    document.getElementById("main_title").innerHTML = "Recording... click again when done speaking";
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
    localStorage.setItem("ai-language", AILanguage);  // To be retrieved on the next session
    languageFound = false;
    let languageIdentifier, languageName;
    switch (language) {
        case 'de':

            document.getElementById("languageBox").innerHTML = "German";
            languageIdentifier = 'de';
            languageName = 'Anna';
            break;

        case 'en':

            document.getElementById("languageBox").innerHTML = "English";
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

            try {
                await fetch(apiMainPathSTS + '/GetAccuracyFromRecordedAudio', {
                    method: "post",
                    body: JSON.stringify({ "title": currentText[0], "base64Audio": audioBase64, "language": AILanguage }),
                    headers: { "X-Api-Key": STScoreAPIKey }

                }).then(res => res.json()).
                    then(data => {

                        if (playAnswerSounds)
                            playSoundForAnswerAccuracy(parseFloat(data.pronunciation_accuracy))

                        document.getElementById("recorded_ipa_script").innerHTML = "/ " + data.ipa_transcript + " /";
                        document.getElementById("recordAudio").classList.add('disabled');
                        document.getElementById("main_title").innerHTML = page_title;
                        document.getElementById("pronunciation_accuracy").innerHTML = data.pronunciation_accuracy + "%";

                        lettersOfWordAreCorrect = data.is_letter_correct_all_words.split(" ")


                        startTime = data.start_time;
                        endTime = data.end_time;


                        real_transcripts_ipa = data.real_transcripts_ipa.split(" ")
                        matched_transcripts_ipa = data.matched_transcripts_ipa.split(" ")
                        wordCategories = data.pair_accuracy_category.split(" ")
                        let currentTextWords = currentText[0].split(" ")

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

    document.getElementById("main_title").innerHTML = "Generating sound...";
    playWithMozillaApi(currentText[0]);
    document.getElementById("main_title").innerHTML = "Current Sound was played";

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
                document.getElementById("main_title").innerHTML = "Recorded Sound was played";
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
    document.getElementById("main_title").innerHTML = "Processing audio...";
}


const playCurrentWord = async (word_idx) => {

    document.getElementById("main_title").innerHTML = "Generating word...";
    playWithMozillaApi(currentText[0].split(' ')[word_idx]);
    document.getElementById("main_title").innerHTML = "Word was played";
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
        headers: { "X-Api-Key": STScoreAPIKey }

    });
}
catch { }

const initializeServer = async () => {

    valid_response = false;
    document.getElementById("main_title").innerHTML = 'Initializing server, this may take up to 2 minutes...';
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
        catch
        {
            number_of_tries += 1;
        }
    }
}

