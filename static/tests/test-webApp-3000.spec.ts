import { test, expect, chromium } from "@playwright/test";

test("test: get a custom sample writing within the input field.", async () => {
  const browser = await chromium.launch({
    args: [
      "--use-fake-device-for-media-stream",
      "--use-fake-ui-for-media-stream",
    ],
  });
  const context = await browser.newContext();
  context.grantPermissions(["microphone"]);
  const page = await browser.newPage({});
  await page.goto("http://localhost:3000");
  await expect(page).toHaveTitle("AI pronunciation trainer");

  const textDescription = page.getByText("Click on the bar on the");
  await expect(textDescription).toBeVisible();

  const inputField = page.getByPlaceholder(
    "Write and press enter to filter"
  );
  const text = "Hi Tom, how are you?"
  await expect(page.getByText(text)).toBeHidden();
  await inputField.fill(text);
  await inputField.press("Enter");
  await expect(page.getByText(text)).toBeVisible();
  await page.waitForTimeout(500);
  
  await expect(
    page.getByText("/ hiː toːm, hoː aːrɛː yːuː? /")
  ).toBeVisible();
  await expect(textDescription).toBeHidden();
  await expect(page).toHaveScreenshot({threshold: 0.1});

  console.log("end");
  await page.close();
});
