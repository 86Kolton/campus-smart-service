const { test, expect } = require("@playwright/test");

const BASE_URL = "http://127.0.0.1:5173/index.html";

async function openEduHall(page) {
  const commentStyle = await page.locator('#feedList button[data-action="comment"]').first().evaluate((node) => {
    const style = window.getComputedStyle(node);
    return {
      borderColor: style.borderColor,
      color: style.color
    };
  });
  expect(commentStyle.borderColor).not.toBe("rgb(255, 255, 255)");
  expect(commentStyle.color).not.toBe("rgb(255, 255, 255)");
  expect(commentStyle.backgroundColor).not.toBe("rgba(0, 0, 0, 0)");

  await page.click('button.tab[data-target="profile"]');
  await expect(page.locator(".edu-card")).toBeVisible();
  await page.locator(".edu-card").click();
  await expect(page.locator("#eduSheet")).toBeVisible();
}

test("edu hall supports full selection flow", async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await openEduHall(page);

  await expect(page.locator('#eduSheet .edu-module-btn[data-edu-nav="grades"]')).toBeVisible();
  await expect(page.locator('#eduSheet .edu-module-btn[data-edu-nav="schedule"]')).toBeVisible();
  await expect(page.locator('#eduSheet .edu-module-btn[data-edu-nav="freeClassrooms"]')).toBeVisible();
  await expect(page.locator('#eduSheet .edu-module-btn[data-edu-nav="exams"]')).toBeVisible();

  await page.locator('#eduSheet [data-edu-nav="grades"]').first().click();
  const termSelect = page.locator('#eduSheet select[data-edu-select="term"]');
  await expect(termSelect).toBeVisible();
  const termLabels = await termSelect.locator("option").allTextContents();
  expect(termLabels.length).toBeGreaterThanOrEqual(6);
  for (const label of termLabels.slice(0, 5)) {
    await termSelect.selectOption({ label });
    await expect(page.locator("#eduSheet")).toContainText(label);
    await expect(page.locator("#eduSheet .edu-list-card").first()).toBeVisible();
  }

  await page.locator('#eduSheet [data-edu-nav="hall"]').first().click();
  await page.locator('#eduSheet [data-edu-nav="schedule"]').first().click();
  const weekSelect = page.locator('#eduSheet select[data-edu-select="week"]');
  await expect(weekSelect).toBeVisible();
  const weekChecks = ["1", "2", "8", "12", "18"];
  for (const week of weekChecks) {
    await weekSelect.selectOption(week);
    await expect(page.locator("#eduSheet")).toContainText(`第 ${week} 周`);
    await expect(page.locator("#eduSheet .edu-list-card").first()).toBeVisible();
  }

  await page.locator('#eduSheet [data-edu-nav="hall"]').first().click();
  await page.locator('#eduSheet [data-edu-nav="freeClassrooms"]').first().click();
  const campusSelect = page.locator('#eduSheet select[data-edu-select="campus"]');
  const buildingSelect = page.locator('#eduSheet select[data-edu-select="building"]');
  await expect(campusSelect).toBeVisible();
  const campusLabels = await campusSelect.locator("option").allTextContents();
  expect(campusLabels.length).toBeGreaterThanOrEqual(3);
  for (const campus of campusLabels) {
    await campusSelect.selectOption({ label: campus });
    await expect(page.locator("#eduSheet")).toContainText(campus);
    const buildingLabels = await buildingSelect.locator("option").allTextContents();
    expect(buildingLabels.length).toBeGreaterThanOrEqual(2);
    const pickedBuilding = buildingLabels[1];
    await buildingSelect.selectOption({ label: pickedBuilding });
    await expect(page.locator("#eduSheet")).toContainText(pickedBuilding);
    await expect(page.locator("#eduSheet .edu-list-card").first()).toBeVisible();
  }

  await page.locator('#eduSheet [data-edu-nav="hall"]').first().click();
  await page.locator('#eduSheet [data-edu-nav="exams"]').first().click();
  await expect(page.locator('#eduSheet .edu-list-card').first()).toBeVisible();
  await expect(page.locator("#eduSheet")).toContainText("考试");
});
