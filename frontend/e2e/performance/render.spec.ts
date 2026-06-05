import { expect, test } from "@playwright/test";
import { login } from "../helpers/auth";

test.describe("Game — Performance", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("page load time < 3s", async ({ page }) => {
    const start = Date.now();
    await page.goto("/play/ai");
    await page.waitForSelector("text=Chơi với máy");
    const loadTime = Date.now() - start;

    expect(loadTime).toBeLessThan(3000);
  });

  test("game start renders board within 1s", async ({ page }) => {
    await page.goto("/play/ai");
    await page.waitForSelector("text=Bắt đầu");

    const start = Date.now();
    await page.click("text=Bắt đầu");
    await page.waitForSelector('[class*="cbs-board"], svg, [data-testid="chessboard"]', { timeout: 5000 });
    const renderTime = Date.now() - start;

    expect(renderTime).toBeLessThan(1000);
  });

  test("no excessive re-renders during gameplay", async ({ page }) => {
    await page.goto("/play/ai");
    await page.click("text=Bắt đầu");
    await page.waitForTimeout(1000);

    // Inject render counter on board element
    const renderCount = await page.evaluate(() => {
      // Count DOM mutations on the board area
      let mutations = 0;
      const observer = new MutationObserver((list) => {
        mutations += list.length;
      });
      const board = document.querySelector('[class*="cbs-board"], svg, main');
      if (board) {
        observer.observe(board, { childList: true, subtree: true, attributes: true });
      }
      return new Promise<number>((resolve) => {
        setTimeout(() => {
          observer.disconnect();
          resolve(mutations);
        }, 5000);
      });
    });

    // During idle (no moves), should have minimal mutations (clock updates only)
    // Clock updates ~5/sec * 5sec = ~25, plus some React internals
    expect(renderCount).toBeLessThan(100);
  });

  test("move list scroll performance", async ({ page }) => {
    await page.goto("/play/ai");
    await page.click("text=Bắt đầu");
    await page.waitForTimeout(2000);

    // Verify move list container exists and is scrollable
    const moveList = page.locator('[class*="MuiCard-root"]').first();
    const box = await moveList.boundingBox();
    expect(box).not.toBeNull();
    // Panel should have fixed height (not grow infinitely)
    if (box) {
      expect(box.height).toBeLessThan(600);
    }
  });

  test("dashboard loads without jank", async ({ page }) => {
    const start = Date.now();
    await page.goto("/");
    await page.waitForSelector("text=Trang chủ");
    const loadTime = Date.now() - start;

    expect(loadTime).toBeLessThan(3000);

    // Check no layout shift on dashboard
    const cls = await page.evaluate(async () => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            // @ts-ignore
            if (!entry.hadRecentInput) clsValue += entry.value;
          }
        });
        observer.observe({ type: "layout-shift", buffered: true });
        setTimeout(() => { observer.disconnect(); resolve(clsValue); }, 2000);
      });
    });
    expect(cls).toBeLessThan(0.1);
  });
});
