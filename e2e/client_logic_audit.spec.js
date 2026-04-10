const { test, expect } = require("@playwright/test");

async function closeSearchSheetIfOpen(page) {
  const searchSheet = page.locator("#searchResultSheet");
  if (!(await searchSheet.isVisible())) return;

  const backBtn = page.locator("#backSearchResultBtn");
  if (await backBtn.isVisible()) {
    await backBtn.click();
    await expect(searchSheet).toBeHidden();
    return;
  }

  await page.keyboard.press("Escape");
  await expect(searchSheet).toBeHidden();
}

test("client logic audit: search/likes/comments", async ({ page }) => {
  page.on("dialog", async (dialog) => {
    await dialog.accept();
  });

  await page.goto("http://127.0.0.1:5173/index.html", { waitUntil: "domcontentloaded" });

  await page.click('button.tab[data-target="search"]');
  const keywords = ["食堂", "图书馆", "校车", "成绩单", "宿舍", "教务", "空教室"];
  for (const kw of keywords) {
    await closeSearchSheetIfOpen(page);
    await page.fill("#marketQuery", kw);
    await page.locator("#marketQuery").press("Enter");
    await expect(page.locator("#searchResultSheet")).toBeVisible();
    await expect(page.locator("#recentSearchList")).toContainText(kw);
    await closeSearchSheetIfOpen(page);
  }
  await expect(page.locator("#recentSearchList .recent-chip")).toHaveCount(6);

  await closeSearchSheetIfOpen(page);
  await page.click('button.tab[data-target="home"]');
  const firstPost = page.locator("#feedList .post-card[data-feed-post-id]").first();
  await expect(firstPost).toBeVisible();
  const targetPostId = String((await firstPost.getAttribute("data-feed-post-id")) || "").trim();
  expect(targetPostId).not.toBe("");

  const targetLikeButton = () => page.locator(`#feedList .post-card[data-feed-post-id="${targetPostId}"] button[data-action="like"]`);
  const targetCard = () => page.locator(`#feedList .post-card[data-feed-post-id="${targetPostId}"]`);

  let likeBtn = targetLikeButton();
  await expect(likeBtn).toBeVisible();
  const currentText = (await likeBtn.textContent()) || "";
  if (currentText.includes("已点赞")) {
    await likeBtn.click();
    await page.waitForTimeout(300);
  }

  await page.reload({ waitUntil: "domcontentloaded" });
  await page.click('button.tab[data-target="home"]');
  likeBtn = targetLikeButton();
  await likeBtn.click();
  await page.waitForTimeout(300);

  await page.reload({ waitUntil: "domcontentloaded" });
  await page.click('button.tab[data-target="home"]');
  likeBtn = targetLikeButton();
  await expect(likeBtn).toContainText("已点赞");
  await likeBtn.click();

  await targetCard().click();
  await expect(page.locator("#postDetailSheet")).toBeVisible();
  await page.click("#postDetailCommentBtn");
  await expect(page.locator("#commentSheet")).toBeVisible();

  const marker = Date.now();
  const rootText = `ui-root-${marker}`;
  const replyText = `ui-reply-${marker}`;

  await page.fill("#commentInput", rootText);
  await page.click("#commentSendBtn");
  await expect(page.locator("#commentList")).toContainText(rootText);

  let rootItem = page.locator(".comment-item", { hasText: rootText }).first();
  await rootItem.locator('button[data-reply-comment-id]').click();
  await page.fill("#commentInput", replyText);
  await page.click("#commentSendBtn");
  await expect(page.locator("#commentList")).toContainText(replyText);

  rootItem = page.locator(".comment-item", { hasText: rootText }).first();
  await rootItem.locator('button[data-delete-comment-id]').click();
  await expect(page.locator("#commentList")).not.toContainText(rootText);
  await expect(page.locator("#commentList")).not.toContainText(replyText);

  const refreshDeleteText = `ui-refresh-del-${marker}`;
  await page.fill("#commentInput", refreshDeleteText);
  await page.click("#commentSendBtn");
  await expect(page.locator("#commentList")).toContainText(refreshDeleteText);

  await page.reload({ waitUntil: "domcontentloaded" });
  await page.click('button.tab[data-target="home"]');
  await targetCard().click();
  await page.click("#postDetailCommentBtn");
  await expect(page.locator("#commentList")).toContainText(refreshDeleteText);
  const persistedItem = page.locator(".comment-item", { hasText: refreshDeleteText }).first();
  await expect(persistedItem.locator('button[data-delete-comment-id]')).toBeVisible();
  await persistedItem.locator('button[data-delete-comment-id]').click();
  await expect(page.locator("#commentList")).not.toContainText(refreshDeleteText);
});
