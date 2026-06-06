import { expect, test } from "@playwright/test";

const BASE = "http://dev-ml.tech.vinamilklocal.com/chess";

async function login(page: import("@playwright/test").Page) {
  await page.goto(`${BASE}/login`);
  await page.waitForSelector('input[name="email"]', { timeout: 10000 });
  await page.fill('input[name="email"]', "e2e@vinamilk.com.vn");
  await page.fill('input[name="password"]', "123456");
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  try { await page.locator("text=Bắt đầu khám phá").click({ timeout: 2000 }); } catch {}
}

async function dismiss(page: import("@playwright/test").Page) {
  try { await page.locator("text=Bắt đầu khám phá").click({ timeout: 2000 }); } catch {}
}

test.describe.serial("Gomoku (Cờ caro) — E2E on dev-ml", () => {
  test.setTimeout(45000);

  test("login and gomoku in Play AI selector", async ({ page }) => {
    await login(page);
    await page.goto(`${BASE}/play/ai`);
    await dismiss(page);
    await expect(page.locator("button:has-text('Cờ caro')")).toBeVisible({ timeout: 15000 });
  });

  test("gomoku board renders after start", async ({ page }) => {
    await login(page);
    await page.goto(`${BASE}/play/ai`);
    await dismiss(page);
    await page.locator("button:has-text('Cờ caro')").click({ timeout: 15000 });
    await page.locator("button:has-text('Bắt đầu')").last().click({ timeout: 5000 });
    await expect(page.locator('svg[aria-label="Bàn cờ caro"]')).toBeVisible({ timeout: 15000 });
  });

  test("gomoku in lobby", async ({ page }) => {
    await login(page);
    await page.goto(`${BASE}/play`);
    await dismiss(page);
    await expect(page.locator("text=Chơi cờ trực tuyến")).toBeVisible({ timeout: 15000 });
  });

  test("gomoku in leaderboard", async ({ page }) => {
    await login(page);
    await page.goto(`${BASE}/ratings`);
    await dismiss(page);
    await expect(page.locator('[role="tab"]', { hasText: "Cờ caro" })).toBeVisible({ timeout: 15000 });
  });
});
