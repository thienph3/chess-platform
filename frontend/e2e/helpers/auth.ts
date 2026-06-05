import { Page } from "@playwright/test";

export async function login(page: Page, email = "phthien@vinamilk.com.vn", password = "123456") {
  await page.goto("/login");
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL("/", { timeout: 10000 });
}
