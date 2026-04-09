const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const FASTAPI_URL = 'http://127.0.0.1:8000/ingest/group';

const client = new Client();

client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ WhatsApp client ready');
});

client.on('message', async (msg) => {
    try {
        const chat = await msg.getChat();

        if (chat.isGroup) {
            const payload = {
                source: 'group',
                group_name: chat.name,
                sender: msg.author || msg.from,
                message: msg.body,
                timestamp: Date.now() / 1000,
            };

            const res = await fetch(FASTAPI_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            console.log(`[GROUP] Queued → ${chat.name}: ${msg.body.slice(0, 60)}`);
        }
    } catch (err) {
        console.error('[GROUP] Skipped message:', err.message);
    }
});

client.initialize();
