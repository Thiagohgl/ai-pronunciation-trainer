import { expect, Frame, Page } from "@playwright/test";

// await page.locator('#text-student-recording-ipa-id-element').getByRole('img').click();
let locatorTextSpinner = '#number-pronunciation-accuracy-id-element > .wrap > div:nth-child(3) > svg'

export const awaitAndExpectForSpinner = async (page: Page | Frame, name = "#number-pronunciation-accuracy-id-element", selector = ".wrap > div:nth-child(3) > svg", throwError1 = false, throwError2 = true, timeout = 1000, timeout2 = 12000) => {
    try {
        await page.waitForTimeout(400)
        let locatorTextSpinner = `${name} > ${selector}`
        console.log(`${name}: locatorTextSpinner: ${locatorTextSpinner}...`);
        let waitingSpinner = page.locator(locatorTextSpinner)
        try {
            await waitingSpinner.waitFor({state: "attached", timeout: timeout})
            await waitingSpinner.waitFor({state: "visible", timeout: timeout})
            expect.soft(waitingSpinner).toBeVisible();
            console.log(`awaitAndExpectForSpinner: ${name} visible ...`);
        } catch (errWaitingSpinnerVisible) {
            console.error(formatError(errWaitingSpinnerVisible as Error, `awaitAndExpectForSpinner: ${name}, timeout: ${timeout}, timeout2: ${timeout2}, throwError1: ${throwError1}.`))
            if (throwError1) {
                throw errWaitingSpinnerVisible
            }
        }
        await waitingSpinner.waitFor({state: "hidden", timeout: timeout2})
        expect(waitingSpinner).toBeHidden();
        console.log(`processingArray: ${waitingSpinner} hidden ...`);
    } catch (err) { 
        console.error(formatError(err as Error, `awaitAndExpectForSpinner: ${name}, timeout: ${timeout}, timeout2: ${timeout2}, throwError2: ${throwError2}.`))
        if (throwError2) {
            throw err
        }
    }
}

const formatError = (error: Error, customMessage: String) => {
    try {
        return `error '${customMessage}' => name: ${error.name}, message: ${error.message}.`;
    } catch (error) {
        return `error: ${error}\n## 'name' in error: ${"name" in Object(error)}, 'message' in error: ${"message" in Object(error)}.`
    }
}

export const assertResponseOK = async (page: Page | Frame, testAudioEnvPath: string, waitTime = 300) => {
    await page.getByRole('button', { name: 'TTS backend', exact: true }).click();
    const buttonPlay = page.getByLabel('Play', { exact: true })
    await buttonPlay.click();
    const waveFormTTS = page.locator('.scroll > .wrapper').first();
    await waveFormTTS.waitFor({ state: 'attached' });
    await waveFormTTS.waitFor({ state: 'visible' });
    await page.waitForTimeout(waitTime)
    await expect(waveFormTTS).toBeVisible();
    console.log("waveFormTTS is visible");

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByLabel('Upload file').click();
    await page.waitForTimeout(waitTime);
    console.log("clicked on 'Upload file'");

    await page.getByRole('button', { name: 'Drop an audio file here to' }).click();
    await page.waitForTimeout(waitTime);
    console.log("clicked on 'Drop Audio Here'");

    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(testAudioEnvPath);
    console.log("prepared file to upload");

    let currentScorePerc = page.getByRole('spinbutton', { name: 'Current score %' })
    expect(await page.getByRole('spinbutton', { name: 'Current score %' })).toHaveValue('0');

    console.log("Before clicking on 'Get speech accuracy score (%)'");
    await page.getByRole('button', { name: 'Get speech accuracy score (%)' }).click();
    await page.waitForTimeout(waitTime);
    console.log("clicked on 'Get speech accuracy score (%)'");
    // workaround to wait for the spinner to appear and disappear
    await awaitAndExpectForSpinner(page)

    expect(await page.getByRole('spinbutton', { name: 'Current score %' })).not.toHaveValue('0');
    let currentScorePercValue1 = await currentScorePerc.inputValue()
    console.log(`currentScorePercValue1 inputValue UPDATED!: ${currentScorePercValue1}...`);

    const errorsElements = page.getByText(/Error/);
    const ErrorText = errorsElements.all()
    console.log(`ErrorText: ${(await ErrorText).length}...`)
    await expect(errorsElements).toHaveCount(0);
}

export const assertPlaySingleWordAudio = async (page: Page | Frame, nthString: string, waitTime = 300) => {
    const currentWordIndex = page.getByLabel(/Current word index/);
    currentWordIndex.fill(nthString);
    await page.waitForTimeout(waitTime);
    const audioSlittedStudentSpeechOutput = page.getByTestId('waveform-Sliced student speech output');
    await expect(audioSlittedStudentSpeechOutput).toBeVisible();
    const buttonPlayStudentSpeechOutput = audioSlittedStudentSpeechOutput.getByLabel('Play', { exact: true })
    // before playing the audio, the color of the button should be gray
    await expect(buttonPlayStudentSpeechOutput).toHaveCSS('color', 'rgb(187, 187, 194)');
    await buttonPlayStudentSpeechOutput.click();
    await page.waitForTimeout(10);
    // after playing the audio, the color of the button should be orange, but only for few milliseconds: don't wait too long!
    await expect(buttonPlayStudentSpeechOutput).toHaveCSS('color', 'rgb(249, 115, 22)');
}