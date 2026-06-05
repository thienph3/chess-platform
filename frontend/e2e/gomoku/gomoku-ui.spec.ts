import { expect, test } from "@playwright/test";

async function loginAndDismiss(page: import("@playwright/test").Page) {
  await page.goto("/login");
  await page.fill('input[name="email"]', "phthien@vinamilk.com.vn");
  await page.fill('input[name="password"]', "123456");
  await page.click('button[type="submit"]');
  await page.waitForURL("/", { timeout: 10000 });
  try { await page.locator("text=Bắt đầu khám phá").click({ timeout: 2000 }); } catch {}
}

test.describe.serial("Gomoku (Cờ caro) — UI Tests", () => {
  test.setTimeout(15000);

  test("login and gomoku in Play AI selector", async ({ page }) => {
    await loginAndDismiss(page);
    await page.goto("/play/ai");
    await expect(page.locator("button:has-text('Cờ caro')")).toBeVisible();
  });

  test("gomoku board renders after start", async ({ page }) => {
    await loginAndDismiss(page);
    await page.goto("/play/ai");
    await page.click("button:has-text('Cờ caro')");
    await page.locator("button:has-text('Bắt đầu')").last().click();
    await page.waitForTimeout(1500);
    const board = page.locator('svg[aria-label="Bàn cờ caro"]');
    await expect(board).toBeVisible();
    // Check 30 grid lines (15x2)
    expect(await board.locator("line").count()).toBe(30);
    // Board is square
    const box = await board.boundingBox();
    expect(box).not.toBeNull();
    if (box) expect(Math.abs(box.width - box.height)).toBeLessThan(2);
  });

  test("gomoku in lobby page", async ({ page }) => {
    await loginAndDismiss(page);
    await page.goto("/play");
    await expect(page.locator("text=Chơi cờ trực tuyến")).toBeVisible();
  });

  test("gomoku in leaderboard tabs", async ({ page }) => {
    await loginAndDismiss(page);
    await page.goto("/ratings");
    await expect(page.locator('[role="tab"]', { hasText: "Cờ caro" })).toBeVisible();
  });
});
