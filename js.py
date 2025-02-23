js_update_ipa_output = """
function updateCssText(text, letters, idxSelectedWord) {
    let wordsArr = text.split(" ")
    let lettersWordsArr = letters.split(" ")
    let speechOutputContainer = document.querySelector('#speech-output');
    speechOutputContainer.textContent = ""

    for (let idx in wordsArr) {
        let word = wordsArr[idx]
        let letterIsCorrect = lettersWordsArr[idx]
        for (let idx1 in word) {
            let letterCorrect = letterIsCorrect[idx1] == "1"
            let containerLetter = document.createElement("span")
            let color = letterCorrect ? 'green' : "red"
            containerLetter.style.cssText = idx == idxSelectedWord ? `color: ${color}; text-decoration-line: underline;` : `color: ${color};`
            containerLetter.innerText = word[idx1];
            speechOutputContainer.appendChild(containerLetter)
        }
        let containerSpace = document.createElement("span")
        containerSpace.textContent = " "
        speechOutputContainer.appendChild(containerSpace)
    }
}
"""

js_play_audio = """
function playAudio(text, language, sleepTime = 0) {
    let voice_idx = 0;
    let voice_synth = null;
    let synth = window.speechSynthesis;
    let voice_lang;
    let sleepTimeAdditional = 500; // for some reason using this with a default input argument give an object instead of the correct number

    function sleep (time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }

    function setSpeech() {
        return new Promise(
            function (resolve, reject) {
                let id;
                id = setInterval(() => {
                    if (synth.getVoices().length !== 0) {
                        resolve(synth.getVoices());
                        clearInterval(id);
                    }
                }, 10);
            }
        )
    }

    switch (language) {
        case 'de':
            voice_lang = 'de-DE';
            break;
        case 'en':
            voice_lang = 'en-US';
            break;
        default:
            const msg = `Error: language ${language} not valid!`
            console.error(msg);
            alert(msg)
            throw new Error(msg)
    }
    
    let s = setSpeech();
    s.then((voices) => {
        let voicesSynth = voices.filter(voice => voice.lang === voice_lang);
        if (voicesSynth.length === 0) {
            console.error(`No voice found for language ${voice_lang}, retry for less restrictive check (startsWith)...`)
            voicesSynth = voices.filter(voice => voice.lang.startsWith(language));
        }
        if (voicesSynth.length === 0) {
            const msg = `Error: no voice found for language ${voice_lang} / ${language}, you should use the Text-To-Speech backend feature...`
            console.error(msg);
            alert(msg)
            throw new Error(msg)
        }
        var utterThis = new SpeechSynthesisUtterance(text);
        utterThis.voice = voicesSynth[0];
        utterThis.rate = 0.7;

        if (sleepTime > 0) {
            sleepTime *= 1000;
            sleepTime += sleepTimeAdditional;
        }
        console.log("start js_play_audio:: sleepTime:", sleepTime, "#")
        sleep(sleepTime).then(() => {
            synth.speak(utterThis);
        })
        // todo: capture audio from speech synthesis to reuse on the frontend
        // https://stackoverflow.com/questions/45003548/how-to-capture-generated-audio-from-window-speechsynthesis-speak-call
    });
}
"""

head_driver_tour = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/driver.js/1.3.1/driver.js.iife.js" integrity="sha512-8EdV4D5VlQLX0dJFcdx6h/oJ/NanAIMlaViz57NDkhzwbQsxabgpFua0gzM4f5vdk60CfRAydhlbfbDThMfh3w==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/driver.js/1.3.1/driver.css" integrity="sha512-jRsM62XMRl33ewZ0Si7yX6ANq+ZiWwUcvPk4H2DKr417W80rPMXzbD/towhs2YEoux/dfOuVRkLB+5Tfzmfolg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<script type="module">
const driver = window.driver.js.driver;

const driverSteps = [
    { element: "id-ai-pronunciation-trainer-gradio-app-container", popover: { title: "AI Pronunciation Trainer Gradio App", description: "A quick tour of the features of the Gradio app 'AI Pronunciation Trainer'." } },
    { element: "#id-choose-random-phrase-by-language-and-difficulty", popover: { title: "Choose a Random Phrase", description: "Choose a random sentence to be used as input for speech recognition, defining your own language and difficulty..." } },
    { element: "#accordion-examples-id-element", popover: { title: "Text Examples", description: "...Or start with these text examples, increasing in difficulty." } },
    { element: "#text-student-transcription-id-element", popover: { title: "Phrase to Read for Speech Recognition", description: "You can also write your own sentence." } },
    { element: "#btn-run-tts-id-element", popover: { title: "In-Browser Text-to-Speech", description: "Execute the text-to-speech functionality in the browser by reading the student's transcription." } },
    { element: "#btn-run-tts-backend-id-element", popover: { title: "Backend Text-to-Speech", description: "Execute the text-to-speech functionality in the backend by reading the student's transcription." } },
    { element: "#btn-clear-tts-backend-id-element", popover: { title: "Clear Text-to-Speech", description: "Clear the synthetic audio output of the text-to-speech synthesis." } },
    { element: ".speech-output-group", popover: { title: "Detailed Speech Accuracy Output", description: "Detailed output of speech accuracy, word by word." } },
    { element: "#id-replay-splitted-audio-by-words", popover: { title: "Replay Split Audio by Words", description: "Replay your recorded audio split into single words followed by the 'ideal' pronunciation spelled by the text-to-speech audio output for the same word." } },
];
const driverObj = driver({
  showProgress: true,
  steps: driverSteps
});
driverObj.drive();
</script>
"""
