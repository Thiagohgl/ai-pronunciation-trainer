import { test, expect, chromium } from "@playwright/test";
import { assertResponseOK, awaitAndExpectForSpinner } from "./helpers_tests";

test("test: English language, get a phonetic accuracy evaluation from an uploaded audio file.", async () => {
  const testAudioEnvPath = `${import.meta.dirname}/../../tests/events/test_en_medium.wav`
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

  const accordionExamples = page.getByText('Click here to expand the table examples');
  accordionExamples.click();
  const exampleMediumFirst = page.getByRole('gridcell', { name: 'medium' }).nth(1);
  await exampleMediumFirst.click();

  await assertResponseOK(page, testAudioEnvPath, 250)
  
  console.log("end");
  await page.close();
});
