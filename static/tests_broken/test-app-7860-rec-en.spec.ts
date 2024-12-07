import { test, expect, chromium } from "@playwright/test";

test("test: get a phonetic accuracy evaluation from a recorded audio.", async () => {
  const dirname = import.meta.dirname;
  const testAudioEnvPath = `${dirname}/../../tests/events/test_en.wav`
  console.log("testAudioEnvPath", testAudioEnvPath, "#");
  console.log("start");
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
