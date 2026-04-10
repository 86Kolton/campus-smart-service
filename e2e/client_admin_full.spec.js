const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");

const SHOT_DIR = path.join(process.cwd(), "test-results", "visible-shots");
const BACKEND_ENV_PATH = path.join(process.cwd(), "backend", ".env");

function readBackendEnvValue(key) {
  if (!fs.existsSync(BACKEND_ENV_PATH)) {
    return "";
  }
  const raw = fs.readFileSync(BACKEND_ENV_PATH, "utf8");
  const line = raw.split(/\r?\n/).find((entry) => entry.startsWith(`${key}=`));
  return line ? String(line.slice(key.length + 1)).trim() : "";
}

const ADMIN_USERNAME = String(process.env.ADMIN_USERNAME || readBackendEnvValue("ADMIN_USERNAME") || "").trim();
const ADMIN_PASSWORD = String(process.env.ADMIN_PASSWORD || readBackendEnvValue("ADMIN_PASSWORD") || "").trim();

function ensureShotDir() {
  if (!fs.existsSync(SHOT_DIR)) {
    fs.mkdirSync(SHOT_DIR, { recursive: true });
  }
}

async function shot(page, name) {
  ensureShotDir();
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const out = path.join(SHOT_DIR, `${stamp}_${name}.png`);
  await page.screenshot({ path: out, fullPage: true });
}

test("client + admin full visible regression", async ({ page }) => {
  page.on("dialog", async (dialog) => {
    await dialog.accept();
  });

  await page.goto("http://127.0.0.1:5173/index.html", { waitUntil: "domcontentloaded" });
  await expect(page.locator("h1")).toContainText("校园助手");
  await shot(page, "01_client_home");

  await page.click('button.tab[data-target="search"]');
  await expect(page.locator('section[data-view="search"]')).toBeVisible();
  await expect(page.locator('button.category-item[data-category="课程评价"]')).toBeVisible();
  await shot(page, "02_client_search");

  await page.fill("#marketQuery", "A1");
  await page.click("#marketSearchBtn");
  await expect(page.locator("#searchResultSheet")).toBeVisible();
  await expect(page.locator("#searchPagePrevBtn")).toBeVisible();
  await expect(page.locator("#searchPageNextBtn")).toBeVisible();
  await expect(page.locator("#searchPageJumpBtn")).toBeVisible();
  await shot(page, "03_search_result_page");

  const firstResult = page.locator("#searchResultList .result-item.is-clickable").first();
  await expect(firstResult).toBeVisible();
  await firstResult.click();
  await expect(page.locator("#postDetailSheet")).toBeVisible();
  await shot(page, "04_post_detail");

  if (await page.locator("#backPostDetailBtn").isVisible()) {
    await page.click("#backPostDetailBtn");
  }
  if (await page.locator("#backSearchResultBtn").isVisible()) {
    await page.click("#backSearchResultBtn");
  }

  await page.click('button.tab[data-target="home"]');
  await expect(page.locator("#feedList .post-card").first()).toBeVisible();
  await page.locator("#feedList .post-card").first().click();
  await expect(page.locator("#postDetailSheet")).toBeVisible();
  await expect(page.locator("#postDetailCommentBtn")).toBeVisible();
  await page.click("#postDetailCommentBtn");
  await expect(page.locator("#commentSheet")).toBeVisible();
  await page.fill("#commentInput", "playwright full regression comment");
  await page.click("#commentSendBtn");
  await expect(page.locator("#commentList")).toContainText("playwright full regression comment");
  await shot(page, "05_comment_after_send");

  const ownComment = page.locator(".comment-item", { hasText: "playwright full regression comment" }).first();
  await expect(ownComment).toBeVisible();
  const deleteBtn = ownComment.locator(".comment-delete-btn");
  await expect(deleteBtn).toBeVisible();
  await deleteBtn.click();
  await expect(page.locator("#commentList")).not.toContainText("playwright full regression comment");
  await shot(page, "06_comment_after_delete");

  await page.click("#backCommentSheetBtn");
  await expect(page.locator("#commentSheet")).toBeHidden();

  await page.click('button.tab[data-target="profile"]');
  await expect(page.locator(".edu-card")).toBeVisible();
  await shot(page, "07_profile_home");

  await page.click('button.edu-item[data-edu-action="grades"]');
  await expect(page.locator("#eduSheet")).toBeVisible();
  await shot(page, "08_edu_grades");
  await page.click("#backEduSheetBtn");
  await expect(page.locator("#eduSheet")).toBeHidden();

  await page.goto("http://127.0.0.1:8000/studio/login.html", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#adminUsername")).toBeVisible();
  await expect(page.locator("#adminPassword")).toBeVisible();
  await expect(page.locator("#togglePassword")).toBeVisible();
  await expect(page.locator("#guardSummary")).toContainText("连续失败");
  await shot(page, "09_admin_login");

  expect(ADMIN_USERNAME).not.toBe("");
  expect(ADMIN_PASSWORD).not.toBe("");
  await page.locator("#adminUsername").fill(ADMIN_USERNAME);
  await page.locator("#adminPassword").fill(ADMIN_PASSWORD);
  await page.locator("#togglePassword").click();
  await expect(page.locator("#adminPassword")).toHaveAttribute("type", "text");
  await page.locator("#togglePassword").click();
  await expect(page.locator("#adminPassword")).toHaveAttribute("type", "password");
  await page.click("#btnLogin");

  await expect(page.locator("#workspaceNav")).toBeVisible();
  await expect(page.locator("#statusCards")).toBeVisible();
  await shot(page, "10_admin_workspace");

  await page.click("#btnSelfCheck");
  await expect(page.locator("#selfCheckResult")).toContainText("database");
  await shot(page, "11_admin_overview");

  await page.locator('#workspaceNav [data-screen="kb"]').click();
  await expect(page.locator("#screen-kb")).toBeVisible();
  await expect(page.locator("#kbTable")).toContainText("校园通用知识库");
  await shot(page, "12_admin_kb");

  await page.locator('#workspaceNav [data-screen="ingest"]').click();
  await expect(page.locator("#screen-ingest")).toBeVisible();
  await expect(page.locator("#docTable")).toBeVisible();
  await expect(page.locator("#taskTable")).toBeVisible();
  await shot(page, "13_admin_ingest");

  await page.locator('#workspaceNav [data-screen="qa"]').click();
  await expect(page.locator("#screen-qa")).toBeVisible();
  await page.fill("#qaQuestion", "河北大学软件工程ISEC是什么？");
  await page.click("#btnAsk");
  await expect(page.locator("#qaResult")).toContainText("ISEC");
  await expect(page.locator("#logSummary")).toContainText("日志");
  await shot(page, "14_admin_qa");

  await page.locator('#workspaceNav [data-screen="ops"]').click();
  await expect(page.locator("#screen-ops")).toBeVisible();
  await expect(page.locator("#opsSummary")).toBeVisible();
  await expect(page.locator("#evolutionReviewTable")).toBeVisible();
  await expect(page.locator("#adoptionTable")).toBeVisible();
  await shot(page, "15_admin_ops");
});
