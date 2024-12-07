import { test, expect, chromium } from "@playwright/test";

test("test: get a phonetic accuracy evaluation from an uploaded audio file.", async () => {
  const testAudioEnvPath = `${import.meta.dirname}/../../tests/events/test_de_easy.wav`
  console.log(`testAudioEnvPath: ${testAudioEnvPath}...`);
  
  const browser = await chromium.launch({
    args: [
        "--use-fake-device-for-media-stream",
      ],
      ignoreDefaultArgs: ['--mute-audio']
    })

  const context = await browser.newContext();
  context.grantPermissions(["microphone"]);
  const page = await browser.newPage({});

  await page.goto('http://localhost:7860/');

  const radioLanguageSelectedDE = page.getByRole('radio', { name: 'de' })
  await radioLanguageSelectedDE.check();

  const textboxStudentTranscriptionInput = page.getByLabel('Phrase to read for speech recognition')
  await textboxStudentTranscriptionInput.fill('Ich bin Alex, wer bist du?');

  await page.getByRole('button', { name: 'TTS backend', exact: true }).click();
  const buttonPlay = page.getByLabel('Play', { exact: true })
  await buttonPlay.click();
  const waveFormTTS = page.locator('.scroll > .wrapper').first();
  await waveFormTTS.waitFor({ state: 'attached' });
  await waveFormTTS.waitFor({ state: 'visible' });
  await expect(waveFormTTS).toBeVisible();

  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByLabel('Upload file').click();
  await page.getByRole('button', { name: 'Drop Audio Here - or - Click' }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles(testAudioEnvPath);
  
  await page.getByRole('button', { name: 'Get speech accuracy score (%)' }).click();

  await page.waitForTimeout(300);
  const errorsElements = page.getByText(/Error/);
  const ErrorText = errorsElements.all()
  console.log("ErrorText:", (await ErrorText).length, "#");
  await expect(errorsElements).toHaveCount(0);

  const currentWordIndex = page.getByLabel(/Current word index/);
  currentWordIndex.fill('1');
  const audioSlittedStudentSpeechOutput = page.getByTestId('waveform-Splitted student speech output');
  await expect(audioSlittedStudentSpeechOutput).toBeVisible();
  const buttonPlayStudentSpeechOutput = audioSlittedStudentSpeechOutput.getByLabel('Play', { exact: true })
  // before playing the audio, the color of the button should be gray
  await expect(buttonPlayStudentSpeechOutput).toHaveCSS('color', 'rgb(187, 187, 194)');
  await buttonPlayStudentSpeechOutput.click();
  await page.waitForTimeout(10);
  // after playing the audio, the color of the button should be orange, but only for few milliseconds: don't wait too long!
  await expect(buttonPlayStudentSpeechOutput).toHaveCSS('color', 'rgb(249, 115, 22)');
  
  console.log("end");
  await page.close();
});
