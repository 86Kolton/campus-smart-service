const { test, expect, request } = require("@playwright/test");

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173/index.html";
const API_BASE = process.env.PLAYWRIGHT_API_BASE || "http://127.0.0.1:8000";

test("comment action uses filled style without outline border", async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  const style = await page.locator('#feedList button[data-action="comment"]').first().evaluate((node) => {
    const computed = window.getComputedStyle(node);
    return {
      borderStyle: computed.borderStyle,
      borderTopColor: computed.borderTopColor,
      backgroundImage: computed.backgroundImage,
      backgroundColor: computed.backgroundColor
    };
  });

  expect(style.borderStyle).toBe("none");
  expect(style.borderTopColor).not.toBe("rgb(86, 149, 225)");
  expect(style.backgroundImage).not.toBe("none");
});

test("profile view refreshes after same-account remote update", async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await page.click('button.tab[data-target="profile"]');
  await expect(page.locator("#profilePublicName")).toBeVisible();

  const session = await page.evaluate(() => window.CampusClientAuth.getSession());
  expect(session.token).toBeTruthy();

  const originalName = (await page.locator("#profilePublicName").textContent()).trim();
  const nextName = `联动${Date.now().toString().slice(-4)}`;
  const api = await request.newContext({ baseURL: API_BASE });

  try {
    const updateResp = await api.post("/api/client/profile/public-name", {
      headers: {
        Authorization: `Bearer ${session.token}`,
        "Content-Type": "application/json"
      },
      data: { public_name: nextName }
    });
    expect(updateResp.ok()).toBeTruthy();

    await page.click('button.tab[data-target="home"]');
    await page.click('button.tab[data-target="profile"]');
    await expect(page.locator("#profilePublicName")).toHaveText(nextName, { timeout: 15000 });
  } finally {
    await api.post("/api/client/profile/public-name", {
      headers: {
        Authorization: `Bearer ${session.token}`,
        "Content-Type": "application/json"
      },
      data: { public_name: originalName }
    });
    await api.dispose();
  }
});
