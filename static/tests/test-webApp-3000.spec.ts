import {test, expect, chromium, Page} from "@playwright/test";
import path from "node:path";
import {customDataWithTestAudioNoUseDTW, dataGetSample, CustomDataWithTestAudio, objectUseDTW} from "./constants";

let pageArray: Page[] = [];

const helperGetNextSentenceOutput = async (args: {page: Page, expectedText: string, expectedIPA: string}) => {
    const {page, expectedText, expectedIPA} = args;
    await expect(page.getByLabel('original_script')).toContainText(expectedText);
    await expect(page.getByLabel('ipa_script', { exact: true })).toContainText(expectedIPA);
    await expect(page.getByLabel('playSampleAudio')).not.toHaveClass(/disabled/);
    await expect(page.getByLabel('input-uploader-audio-file')).toBeEnabled();
    await expect(page.getByRole('link', { name: 'recordAudio' })).not.toHaveClass(/disabled/);
    await expect(page.getByLabel('playRecordedWord')).toContainText('Reference');
    await expect(page.getByLabel('playCurrentWord')).toContainText('Spoken');
    // check for not having an error message
    await expect(page.getByLabel('ipa-pair-error')).not.toBeVisible();
}

const helperGetNextSentence = async (args: {page: Page, expectedText: string, expectedIPA: string, language: string, languagePredefined: string, category: string}) => {
    let {page, expectedText, expectedIPA, language, languagePredefined, category} = args;
    let currentSelectedLanguage = page.getByLabel('languageBoxDropdown');
    let currentSelectedLanguageText = await currentSelectedLanguage.textContent();
    if (language !== languagePredefined && currentSelectedLanguageText !== language) {
        console.log(`changing language because => currentSelectedLanguageText:'${currentSelectedLanguageText}', need language:'${language}'`);
        await page.getByRole('button', { name: 'languageBoxDropdown' }).click();
        await page.getByRole('link', { name: language }).click();
    }
    await page.getByRole('radio', { name: category }).click();
    await helperGetNextSentenceOutput({page, expectedText, expectedIPA});
}

test.describe("test: get a custom sample writing within the input field.", async () => {
    test.beforeAll(async ({}) => {
        const browser = await chromium.launch({
            args: [
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream",
            ],
        });
        const context = await browser.newContext();
        await context.grantPermissions(["microphone"]);
        let page = await browser.newPage({});
        pageArray.push(page);
        await page.goto("/");
        await expect(page).toHaveTitle("AI pronunciation trainer");
        await expect(page.getByRole('button', { name: 'languageBoxDropdown' })).toBeVisible();
        await expect(page.getByLabel('languageBoxDropdown')).toContainText('German');
        await expect(page.getByLabel('section_accuracy_score')).toContainText('| Score: 0');
        const textPlaceholder = page.getByText("Click on the bar on the");
        await expect(textPlaceholder).toBeVisible();

        await expect(page.getByLabel('playRecordedWord')).toContainText('Reference');
        await expect(page.getByLabel('playCurrentWord')).toContainText('Spoken');
        await expect(page.getByLabel('pronunciation_accuracy')).toContainText('%');

        const inputUploaderAudioFile = page.getByLabel('input-uploader-audio-file');
        await expect(inputUploaderAudioFile).toBeDisabled();
        await expect(inputUploaderAudioFile).toContainText('Custom audio file');
        await expect(page.getByLabel('playRecordedAudio')).toHaveClass(/disabled/);
        await expect(page.getByLabel('playSampleAudio')).toHaveClass(/disabled/);
        const buttonCustomText = page.getByRole('button', { name: 'buttonCustomText' });
        await expect(buttonCustomText).toBeEnabled()
        await expect(buttonCustomText).toContainText('IPA for custom text');
        await expect(page.getByLabel('recordAudio')).toHaveClass(/disabled/);
        await expect(page.getByLabel('ipa-pair-error')).not.toBeVisible();
        console.log("end of beforeAll");
    });

    test.afterAll(async ({browser}) => {
        await browser.close();
    });

    test("Get a custom sample writing within the input field using the predefined 'easy' sentence category,", async ({}) => {
        let page = pageArray[0];
        await page.getByRole('button', { name: 'buttonNext' }).click({timeout: 10000});
        console.log("clicked buttonNext");
        /** immediately after clicking on 'buttonNext' the elements
         - playSampleAudio
         - recordAudio
         - input-uploader-audio-file
         should NOT be disabled or to have the class 'disabled'.
         **/
        let {expectedText, expectedIPA} = dataGetSample[1];
        await helperGetNextSentenceOutput({
            page,
            expectedText,
            expectedIPA,
        });
        await expect(page.getByLabel('section_accuracy_score')).toContainText('| Score: 0 - (0)');
    });

    let languagePredefined = "German"
    for (let {expectedText, category, expectedIPA, language} of dataGetSample) {
        test(`Get a custom sample using a custom sentence ('${category}' category, '${language}' language)`, async ({}) => {
            await helperGetNextSentence({
                page: pageArray[0],
                expectedText,
                expectedIPA,
                language,
                languagePredefined,
                category
            });
        });
    }

    test("Test an error message, then remove it (switch back to English)", async ({}) => {
        let page = pageArray[0];
        let language = "German";
        await page.getByRole('button', { name: 'languageBoxDropdown' }).click();
        await page.getByRole('link', { name: language }).click();
        await page.waitForTimeout(200)

        // test an error message when clicking on 'IPA for custom text' without editing the input field OR when the input field is empty
        await page.getByLabel('original_script').fill('');
        await page.getByRole('button', { name: 'buttonCustomText' }).click();
        await page.waitForTimeout(200)
        await expect(page.getByLabel('original_script')).toContainText('Please edit this text before generating the IPA for a custom sentence!');
        await expect(page.getByLabel('ipa_script', { exact: true })).toContainText('Error');
        await expect(page.getByLabel('ipa-pair-error')).toBeVisible();

        // click again on a different sentence category to remove the error message
        let {expectedText, expectedIPA, category} = dataGetSample[1];
        await page.getByRole('radio', { name: category }).click();
        let originalScript = page.getByLabel('original_script')
        await expect(originalScript).toContainText(expectedText);
        let ipaScript = page.getByLabel('ipa_script', { exact: true });
        await expect(ipaScript).toContainText(expectedIPA);
    })

    for (let useDTW of [false, true]) {
        let customDataWithAudio = objectUseDTW[useDTW]
        for (let {
            expectedText, category, expectedIPA, language, expectedRecordedIPAScript,
            expectedSectionAccuracyScore, expectedPronunciationAccuracy, testAudioFile
        } of customDataWithAudio) {
            test(`Test the /GetAccuracyFromRecordedAudio endpoint with a custom sentence ('${category}' category, '${language}' language, useDTW='${useDTW}')`, async ({}) => {
                let page = pageArray[0];

                if (language !== languagePredefined) {
                    await page.getByRole('button', { name: 'languageBoxDropdown' }).click();
                    await page.getByRole('link', { name: language }).click();
                    await page.waitForTimeout(200)
                }
                await page.getByLabel('original_script').fill(expectedText);
                await page.getByRole('button', { name: 'buttonCustomText' }).click();
                await page.waitForTimeout(200)
                await helperGetNextSentenceOutput({page, expectedText, expectedIPA});

                let checkboxDTW = page.getByText('DTW')
                let dtwCheckbox = await checkboxDTW.isChecked();
                console.log(`useDTW: ${useDTW}, verify checkboxDTW: is checked? ${dtwCheckbox}!`);
                if (useDTW) {
                    await page.waitForTimeout(200)
                    if (!dtwCheckbox) {
                        await checkboxDTW.click();
                        await page.waitForTimeout(200)
                        console.log(`useDTW: ${useDTW}, AFTER checkboxDTW: is checked?`, await checkboxDTW.isChecked());
                    }
                } else console.log("useDTW is false, so no need to click on the checkboxDTW");

                // test the /GetAccuracyFromRecordedAudio endpoint
                const audioFilePath = path.join( import.meta.dirname, '..', '..', 'tests', 'events', testAudioFile);
                try {
                    await expect(page.getByLabel('original_script')).toContainText(expectedText);
                    // workaround to upload the audio file that will trigger the /GetAccuracyFromRecordedAudio endpoint
                    await page.getByLabel("input-uploader-audio-hidden").setInputFiles(audioFilePath);
                } catch (err1) {
                    console.log(`import.meta.dirname: '${import.meta.dirname}', audioFilePath: '${audioFilePath}'`);
                    console.error(`input-uploader-audio-hidden::err1: `, err1, "#");
                }
                await expect(page.getByLabel('original_script')).toHaveScreenshot();

                const expectedText2 = expectedIPA.replace(/^\/ /g, "").replace(/ \/$/g, "")
                try {
                    await expect(page.getByLabel('ipa_script', {exact: true})).toContainText(expectedText2);
                } catch (err2) {
                    console.log(`expectedText2: '${expectedText2}'`);
                    throw err2;
                }
                await expect(page.getByLabel('recorded_ipa_script')).toContainText(expectedRecordedIPAScript);
                await expect(page.getByLabel('pronunciation_accuracy')).toContainText(expectedPronunciationAccuracy);

                /** todo: find a way to record the played audio sounds:
                 * - playSampleAudio
                 * - playRecordedAudio
                 * - playRecordedWord
                 * - playCurrentWord
                 * and compare them with the expected audio sounds
                 */
                await page.getByRole('link', { name: 'playSampleAudio' }).click();
                await page.getByRole('link', { name: 'playRecordedAudio' }).click();

                let idx = expectedText.split(" ").length - 1;
                let wordForPlayAudio = expectedText.split(" ")[idx]
                let wordForPlayAudioAriaLabel = `word${idx}${wordForPlayAudio}`.replace(/[^a-zA-Z0-9]/g, "")
                await expect(page.getByLabel(wordForPlayAudioAriaLabel)).toHaveScreenshot();
                await page.getByLabel(wordForPlayAudioAriaLabel).click();
                let playRecordedWord = page.getByRole('link', { name: 'playRecordedWord' });
                await expect(playRecordedWord).toHaveScreenshot();
                await playRecordedWord.click();

                await expect(page.getByLabel('pronunciation_accuracy')).toContainText(expectedPronunciationAccuracy);
                await expect(page.getByLabel('section_accuracy_score')).toContainText(expectedSectionAccuracyScore);
            });
        }
    }

});
