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
  await page.waitForSelector("textarea")

  const textboxStudentTranscriptionInput = page.getByLabel("Phrase to read for speech recognition");
  let studentTranscriptionScreenshot0 = await textboxStudentTranscriptionInput.screenshot()

  const buttonRandom = page.getByRole('button', { name: 'Choose a random phrase' });
  await buttonRandom.click();
  await page.waitForTimeout(300);
  let studentTranscriptionScreenshot1 = await textboxStudentTranscriptionInput.screenshot();

  // find a way to measure how much the screenshots differ
  // assert that the Phrase to read for speech recognition screenshots (converted both to base64 strings) changed
  expect(
    studentTranscriptionScreenshot0.toString('base64')
  ).not.toEqual(
    studentTranscriptionScreenshot1.toString('base64')
  )

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
  console.log(`ErrorText: ${(await ErrorText).length}...`)
  await expect(errorsElements).toHaveCount(0);
  console.log("end");
  await page.close();
});
