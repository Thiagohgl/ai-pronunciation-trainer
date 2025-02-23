import { test, expect, chromium } from "@playwright/test";
import { assertPlaySingleWordAudio, assertResponseOK, awaitAndExpectForSpinner } from "./helpers_tests";

test("test: English language, get a phonetic accuracy evaluation from an uploaded audio file.", async () => {
  const testAudioEnvPath = `${import.meta.dirname}/../../tests/events/test_en_easy.wav`
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
  
  await page.goto('http://localhost:7860/', { waitUntil: 'commit' });

  const radioLanguageSelectedDE = page.getByRole('radio', { name: 'en' })
  await radioLanguageSelectedDE.check();

  let textboxStudentTranscription = page.getByRole('textbox', { name: 'Phrase to read for speech' })
  await textboxStudentTranscription.fill('Hi there, how are you?');

  const waitTime = 250
  await assertResponseOK(page, testAudioEnvPath, waitTime)
  await assertPlaySingleWordAudio(page, '2', waitTime)

  console.log("end");
  await page.close();
});
