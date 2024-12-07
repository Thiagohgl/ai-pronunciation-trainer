import { test, expect, chromium } from "@playwright/test";
import { writeFile } from 'node:fs/promises'
import { Readable } from 'node:stream'
import {readFileSync} from "fs"


test("XXX - test: get a phonetic accuracy evaluation from a recorded audio.", async () => {
  /**
   * - DE:
   *      - random choice (random, easy, medium, hard)
   *      - choice from the examples accordion
   *         - record a fake new audio
   *         - upload
   * - EN:
   *      - random choice (random, easy, medium, hard)
   */

  // todo: upload del file test_de.wav dalla cartella corrente senza 
  // todo: download del file audio
  // todo: test online, https://mictests.com/
  const urlAudio = "https://huggingface.co/spaces/aletrn/ai-pronunciation-trainer/resolve/main/tests/events/test_de.wav"
  console.log("import.meta dir", import.meta.dirname, "#");
  const dirname = import.meta.dirname;
  const testAudioEnvPath = `${dirname}/test_de.wav%%noloop`
  console.log("urlAudio", urlAudio, "#");
  console.log("testAudioEnvPath", testAudioEnvPath, "#");
  console.log("testAudioEnvPath", testAudioEnvPath, "#");

  const response = await fetch(urlAudio)
  const stream = Readable.fromWeb(response.body)
  await writeFile(testAudioEnvPath, stream)

  const string_output = readFileSync(testAudioEnvPath, 'utf8')
  if (string_output.length > 0) {
    console.log("testAudioEnvPath", testAudioEnvPath, "#");
    console.log("testAudioEnvPath", testAudioEnvPath, "#");
  } else {
    console.log("empty testAudioEnvPath", testAudioEnvPath, "#");
    throw new Error("File is empty!");
  }

  // const testAudioEnvPath = `${basedirAudioFiles}/test_de.wav`
  console.log("start");
  console.log("testAudioEnvPath", testAudioEnvPath, "#");
  const browser = await chromium.launch({
    args: [
        "--use-fake-device-for-media-stream",
        "--use-fake-ui-for-media-stream",
        `--use-file-for-fake-audio-capture=${testAudioEnvPath}`,
    ],
    ignoreDefaultArgs: ['--mute-audio']
  })

  const context = await browser.newContext();
  context.grantPermissions(["microphone"]);
  const page = await browser.newPage({});

  await page.goto('http://localhost:7860/');
  
  const radioLanguageSelectedDE = page.getByRole('radio', { name: 'de' })
  await radioLanguageSelectedDE.check();

  const textboxInput = page.getByLabel('Learner Transcription')
  await textboxInput.fill('Ich bin Alex, wer bist du?');
  
  const buttonTTS = page.getByRole('button', { name: 'Run TTS' })
  await buttonTTS.click();
  // todo: improve this hardcoded timeout
  await page.waitForTimeout(3000);
  
  const buttonPlay = page.getByLabel('Play', { exact: true })
  await buttonPlay.click();
  const waveFormTTS = page.locator('.scroll > .wrapper').first();
  await waveFormTTS.waitFor({ state: 'attached' });
  await waveFormTTS.waitFor({ state: 'visible' });
  await expect(waveFormTTS).toBeVisible();
  console.log("waveFormTTS??");

  const buttonRecordTTS = page.getByRole('button', { name: 'Record', exact: true })
  await buttonRecordTTS.click();
  console.log("buttonRecordTTS??");
  const buttonStopTTS = page.getByRole('button', { name: 'Stop', exact: true })
  await buttonStopTTS.click();
  console.log("buttonStopTTS??");

  const buttonRecognizeSpeechAccuracy = page.getByRole('button', { name: 'Get speech accuracy score (%)' })
  console.log("buttonRecognizeSpeechAccuracy??");
  console.log("buttonRecognizeSpeechAccuracy??");
  await buttonRecognizeSpeechAccuracy.click();
  console.log("buttonRecognizeSpeechAccuracy=>click!");
  console.log("buttonRecognizeSpeechAccuracy=>click!");
  await page.waitForTimeout(300);
  
  const errorsElements = page.getByText(/Error/);
  const ErrorText = errorsElements.all()
  console.log("ErrorText:", (await ErrorText).length, "#");
  await expect(errorsElements).toHaveCount(0);
  console.log("end");
  await page.close();
});
