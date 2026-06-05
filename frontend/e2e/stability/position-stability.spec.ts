import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

/**
 * Position Stability Tests
 * Đo tọa độ các element quan trọng tại nhiều thời điểm.
 * Nếu position thay đổi → UI bị trượt → rối mắt player.
 */

interface ElementPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

async function getPosition(page: any, selector: string): Promise<ElementPosition | null> {
  const box = await page.locator(selector).first().boundingBox();
  return box ? { x: box.x, y: box.y, width: box.width, height: box.height } : null;
}

function assertStable(before: ElementPosition | null, after: ElementPosition | null, name: string, tolerance = 1) {
  if (!before || !after) return;
  expect(Math.abs(before.x - after.x), `${name} X shifted`).toBeLessThanOrEqual(tolerance);
  expect(Math.abs(before.y - after.y), `${name} Y shifted`).toBeLessThanOrEqual(tolerance);
  expect(Math.abs(before.width - after.width), `${name} width changed`).toBeLessThanOrEqual(tolerance);
  expect(Math.abs(before.height - after.height), `${name} height changed`).toBeLessThanOrEqual(tolerance);
}

test.describe("Position Stability — Game Board", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto("/play/ai");
    await page.click("text=Bắt đầu");
    await page.waitForTimeout(1500); // wait for board + AI first response
  });

  test("board position stable during AI thinking", async ({ page }) => {
    // Snapshot positions
    const boardBefore = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');
    const clockTopBefore = await getPosition(page, 'main > div > div > div:nth-child(1)'); // top player bar
    const clockBottomBefore = await getPosition(page, 'main > div > div > div:last-child'); // bottom player bar

    // Wait 3 seconds (AI thinking, clock ticking)
    await page.waitForTimeout(3000);

    // Measure again
    const boardAfter = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');
    const clockTopAfter = await getPosition(page, 'main > div > div > div:nth-child(1)');
    const clockBottomAfter = await getPosition(page, 'main > div > div > div:last-child');

    assertStable(boardBefore, boardAfter, "Board");
    assertStable(clockTopBefore, clockTopAfter, "Top clock");
    assertStable(clockBottomBefore, clockBottomAfter, "Bottom clock");
  });

  test("side panel position stable during gameplay", async ({ page }) => {
    const panelBefore = await getPosition(page, '[class*="MuiCard-root"]');

    await page.waitForTimeout(3000);

    const panelAfter = await getPosition(page, '[class*="MuiCard-root"]');
    assertStable(panelBefore, panelAfter, "Side panel");
  });

  test("board does not shift when move list grows", async ({ page }) => {
    const boardBefore = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');

    // Wait for several moves (AI responds, move list grows)
    await page.waitForTimeout(5000);

    const boardAfter = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');
    assertStable(boardBefore, boardAfter, "Board after moves");
  });
});

test.describe("Position Stability — Page Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("sidebar position stable across navigation", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(500);
    const sidebarBefore = await getPosition(page, '[class*="MuiDrawer-paper"]');

    // Navigate to different pages
    await page.click("text=Giải đấu");
    await page.waitForTimeout(500);
    const sidebarAfterTournaments = await getPosition(page, '[class*="MuiDrawer-paper"]');

    await page.click("text=Chơi cờ");
    await page.waitForTimeout(500);
    const sidebarAfterPlay = await getPosition(page, '[class*="MuiDrawer-paper"]');

    assertStable(sidebarBefore, sidebarAfterTournaments, "Sidebar after nav to tournaments");
    assertStable(sidebarBefore, sidebarAfterPlay, "Sidebar after nav to play");
  });

  test("header position stable across navigation", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(500);
    const headerBefore = await getPosition(page, '[class*="MuiAppBar-root"]');

    await page.click("text=Thành viên");
    await page.waitForTimeout(500);
    const headerAfter = await getPosition(page, '[class*="MuiAppBar-root"]');

    assertStable(headerBefore, headerAfter, "Header");
  });

  test("content area does not jump on lazy load", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(500);

    // Get content area position
    const contentBefore = await getPosition(page, 'main');

    // Navigate (triggers lazy load)
    await page.click("text=Tài chính");
    await page.waitForTimeout(1000);

    const contentAfter = await getPosition(page, 'main');
    assertStable(contentBefore, contentAfter, "Content area");
  });
});

test.describe("Position Stability — Game Replay", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("board stable when stepping through moves", async ({ page }) => {
    await page.goto("/play/history");
    await page.waitForTimeout(1000);

    // Click first game in history
    const firstRow = page.locator('[class*="MuiDataGrid-row"]').first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
      await page.waitForTimeout(1500);

      const boardBefore = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');

      // Click next move button multiple times
      const nextBtn = page.locator('button').filter({ has: page.locator('[data-testid="SkipNextIcon"]') }).first();
      if (await nextBtn.isVisible()) {
        await nextBtn.click();
        await page.waitForTimeout(200);
        await nextBtn.click();
        await page.waitForTimeout(200);
        await nextBtn.click();
        await page.waitForTimeout(200);
      }

      const boardAfter = await getPosition(page, '[class*="cbs-board"], [data-testid="chessboard"], main svg');
      assertStable(boardBefore, boardAfter, "Board during replay navigation");
    }
  });
});
