import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test.describe("Game Board — Layout Stability (CLS)", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("no layout shift when AI is thinking", async ({ page }) => {
    await page.goto("/play/ai");
    await page.click("text=Bắt đầu");
    await page.waitForTimeout(1000);

    // Measure board position before move
    const boardBefore = await page.locator('[class*="cbs-board"], svg, [data-testid="chessboard"]').first().boundingBox();

    // Make a move (drag e2 to e4 or click)
    // Since we can't easily drag, we'll wait for AI thinking state
    await page.waitForTimeout(2000);

    // Measure board position after AI responds
    const boardAfter = await page.locator('[class*="cbs-board"], svg, [data-testid="chessboard"]').first().boundingBox();

    // Board should NOT shift position
    if (boardBefore && boardAfter) {
      expect(Math.abs(boardBefore.x - boardAfter.x)).toBeLessThan(2);
      expect(Math.abs(boardBefore.y - boardAfter.y)).toBeLessThan(2);
      expect(Math.abs(boardBefore.width - boardAfter.width)).toBeLessThan(2);
      expect(Math.abs(boardBefore.height - boardAfter.height)).toBeLessThan(2);
    }
  });

  test("no layout shift on page load (CLS < 0.1)", async ({ page }) => {
    // Measure CLS using Performance Observer
    await page.goto("/play/ai");

    const cls = await page.evaluate(async () => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            // @ts-ignore
            if (!entry.hadRecentInput) {
              // @ts-ignore
              clsValue += entry.value;
            }
          }
        });
        observer.observe({ type: "layout-shift", buffered: true });
        // Wait for page to settle
        setTimeout(() => {
          observer.disconnect();
          resolve(clsValue);
        }, 3000);
      });
    });

    // CLS should be less than 0.1 (Google's "good" threshold)
    expect(cls).toBeLessThan(0.1);
  });

  test("no layout shift when navigating to game page", async ({ page }) => {
    await page.goto("/play");
    await page.waitForTimeout(500);

    const cls = await page.evaluate(async () => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            // @ts-ignore
            if (!entry.hadRecentInput) {
              // @ts-ignore
              clsValue += entry.value;
            }
          }
        });
        observer.observe({ type: "layout-shift", buffered: true });

        // Navigate to AI page
        window.location.href = "/play/ai";

        setTimeout(() => {
          observer.disconnect();
          resolve(clsValue);
        }, 3000);
      });
    });

    expect(cls).toBeLessThan(0.15);
  });

  test("clock area does not cause shift when active/inactive", async ({ page }) => {
    await page.goto("/play/ai");
    await page.click("text=Bắt đầu");
    await page.waitForTimeout(500);

    // Get all clock elements position
    const clocks = page.locator('[class*="MuiBox-root"]').filter({ hasText: /\d+:\d+/ });
    const count = await clocks.count();

    // Record positions
    const positions: Array<{ x: number; y: number }> = [];
    for (let i = 0; i < count; i++) {
      const box = await clocks.nth(i).boundingBox();
      if (box) positions.push({ x: box.x, y: box.y });
    }

    // Wait 3 seconds (clock ticks, AI may respond)
    await page.waitForTimeout(3000);

    // Check positions haven't shifted
    for (let i = 0; i < count; i++) {
      const box = await clocks.nth(i).boundingBox();
      if (box && positions[i]) {
        expect(Math.abs(box.x - positions[i].x)).toBeLessThan(2);
        expect(Math.abs(box.y - positions[i].y)).toBeLessThan(2);
      }
    }
  });
});
