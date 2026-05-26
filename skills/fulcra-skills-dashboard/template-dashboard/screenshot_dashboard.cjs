const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/home/leif/.cache/puppeteer/chrome/linux-148.0.7778.97/chrome-linux64/chrome',
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1000 });
  await page.goto('http://localhost:5175', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'dashboard.png', fullPage: true });
  await browser.close();
})();