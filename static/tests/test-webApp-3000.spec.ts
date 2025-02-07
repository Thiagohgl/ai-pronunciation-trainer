import {test, expect, chromium, Page} from "@playwright/test";
import {dataGetSample} from "./constants";

let pageArray = new Array<Page>();

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
        await expect(page.getByLabel('pronunciation_accuracy')).toContainText('-');
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
        await expect(page.getByRole('link', { name: 'playSampleAudio' })).not.toHaveClass(/disabled/);
        await expect(page.getByRole('link', { name: 'recordAudio' })).not.toHaveClass(/disabled/);
        let originalScript = page.getByLabel('original_script')
        await expect(originalScript).toContainText('Marie leidet an Hashimoto-Thyreoiditis.');
        let ipaScript = page.getByLabel('ipa_script', { exact: true });
        await expect(ipaScript).toContainText('/ maːriː laɪ̯dɛːt aːn haːshiːmoːtoː-tyːrɛːɔɪ̯diːtiːs. /');
        await expect(page.getByLabel('input-uploader-audio-file')).not.toHaveClass(/disabled/);
        await expect(page.getByLabel('input-uploader-audio-file')).toBeEnabled();
        await expect(page.getByLabel('section_accuracy_score')).toContainText('| Score: 0 - (0)');
    });

    let languagePredefined = "German"
    for (let {expectedText, category, expectedIPA, language} of dataGetSample) {
        test(`Get a custom sample writing within the input field using the predefined '${category}' and language '${language}' sentence category.`, async ({}) => {
            let page = pageArray[0];
            if (language !== languagePredefined) {
                await page.getByRole('button', { name: 'languageBoxDropdown' }).click();
                await page.getByRole('link', { name: language }).click();
            }
            await page.getByRole('radio', { name: category }).check();
            await expect(page.getByLabel('original_script')).toContainText(expectedText);
            await expect(page.getByLabel('ipa_script', { exact: true })).toContainText(expectedIPA);
            await expect(page.getByLabel('playSampleAudio')).not.toHaveClass(/disabled/);
            await expect(page.getByLabel('input-uploader-audio-file')).toBeEnabled();
            await expect(page.getByRole('link', { name: 'recordAudio' })).not.toHaveClass(/disabled/);
            await expect(page.getByLabel('playRecordedWord')).toContainText('Reference');
            await expect(page.getByLabel('playCurrentWord')).toContainText('Spoken');
            // check for not having an error message
            await expect(page.getByLabel('ipa-pair-error')).not.toBeVisible();
        });
    }

    test("Get a custom sample writing within the input field using the predefined 'medium' sentence category (switch back to English)", async ({}) => {
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
        await page.getByRole('radio', { name: "Easy" }).check();
        let originalScript = page.getByLabel('original_script')
        await expect(originalScript).toContainText('Marie leidet an Hashimoto-Thyreoiditis.');
        let ipaScript = page.getByLabel('ipa_script', { exact: true });
        await expect(ipaScript).toContainText('/ maːriː laɪ̯dɛːt aːn haːshiːmoːtoː-tyːrɛːɔɪ̯diːtiːs. /');
    })
});
