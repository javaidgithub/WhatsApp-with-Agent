const puppeteer = require('puppeteer');

const FASTAPI_URL = 'http://127.0.0.1:8000/ingest/channel';
const POLL_INTERVAL_MS = 5000; // scrape every 5 seconds

async function postMessage(message, channelName = 'WhatsApp Channel') {
    try {
        await fetch(FASTAPI_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: 'channel',
                channel_name: channelName,
                message,
                timestamp: Date.now() / 1000,
            }),
        });
    } catch (err) {
        console.error('[CHANNEL] Failed to send to FastAPI:', err.message);
    }
}

(async () => {
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        protocolTimeout: 0
    });

    const page = await browser.newPage();

    await page.goto('https://web.whatsapp.com');

    console.log("👉 Scan QR Code...");

    // await page.waitForSelector('div[contenteditable="true"]', { timeout: 0 });
    await page.waitForSelector('#pane-side', { timeout: 0 });

    console.log("✅ Logged in!");

    console.log("👉 Open your channel manually...");
    await new Promise(resolve => setTimeout(resolve, 15000));

    const seen = new Set(); // avoid duplicates

    async function scrapeAndQueue() {
        try {
            const messages = await page.evaluate(() => {
                const msgs = [];

                const elements = document.querySelectorAll('div.copyable-text');

                elements.forEach(el => {
                    const text = el.innerText;
                    if (text) {
                        msgs.push(text);
                    }
                });

                return msgs;
            });

            for (const msg of messages) {
                if (!seen.has(msg)) {
                    seen.add(msg);

                    await postMessage(msg);

                    console.log("📢 QUEUED MESSAGE:");
                    console.log(msg);
                }
            }

        } catch (err) {
            console.error('[CHANNEL] Scrape error:', err.message);
        }
    }

    // initial run
    await scrapeAndQueue();

    // polling loop
    setInterval(scrapeAndQueue, POLL_INTERVAL_MS);
})();