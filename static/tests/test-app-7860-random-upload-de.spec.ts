import { test, expect, chromium,  } from "@playwright/test";
import {assertResponseOK, awaitAndExpectForSpinner} from "./helpers_tests";

test("test: German language, get a phonetic accuracy evaluation from an uploaded audio file.", async () => {
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

  await page.goto('http://localhost:7860/', { waitUntil: 'commit' });
  await page.waitForSelector("textarea")

  // check for the sentence content
  let textboxStudentTranscription = page.getByRole('textbox', { name: 'Phrase to read for speech' })
  let textboxStudentTranscriptionInputText0 = textboxStudentTranscription.inputValue()
  console.log(`textboxStudentTranscriptionInputText inputValue: ${textboxStudentTranscriptionInputText0}...`);
  
  const textboxStudentTranscriptionInputContainer = page.getByLabel("Phrase to read for speech recognition");
  let studentTranscriptionScreenshot0 = await textboxStudentTranscriptionInputContainer.screenshot()

  const buttonRandom = page.getByRole('button', { name: 'Choose a random phrase' });
  await buttonRandom.click();
  await page.waitForTimeout(300);
  let textboxStudentTranscriptionInputText1 = await page.getByRole('textbox', { name: 'Phrase to read for speech' }).inputValue()
  console.log(`textboxStudentTranscriptionInputText1 inputValue: ${textboxStudentTranscriptionInputText1}...`);
  expect(textboxStudentTranscriptionInputText0).not.toEqual(textboxStudentTranscriptionInputText1);

  let studentTranscriptionScreenshot1 = await textboxStudentTranscriptionInputContainer.screenshot();
  console.log(`studentTranscriptionScreenshot0 vs studentTranscriptionScreenshot1...`);
  // assert that the Phrase to read for speech recognition screenshots (converted both to base64 strings) changed
  expect(
    studentTranscriptionScreenshot0.toString()
  ).not.toEqual(
    studentTranscriptionScreenshot1.toString()
  )

  await assertResponseOK(page, testAudioEnvPath, 250)

  console.log("end");
  await page.close();
});
