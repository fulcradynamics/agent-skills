import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);
        const CHAT_FILE = path.join(process.cwd(), 'src/lib/data/chat.json');

// Initialize if not exists
if (!fs.existsSync(CHAT_FILE)) {
    fs.writeFileSync(CHAT_FILE, JSON.stringify([], null, 2));
}

export async function GET() {
    try {
        if (!fs.existsSync(CHAT_FILE)) {
            return json([]);
        }
        const data = fs.readFileSync(CHAT_FILE, 'utf8');
        return json(JSON.parse(data));
    } catch (err) {
        return json({ error: err.message }, { status: 500 });
    }
}

export async function POST({ request }) {
    try {
        const body = await request.json();
        
        let data = [];
        if (fs.existsSync(CHAT_FILE)) {
            data = JSON.parse(fs.readFileSync(CHAT_FILE, 'utf8'));
        }
        
        data.push({
            role: 'user',
            text: body.message,
            timestamp: new Date().toISOString()
        });
        
        fs.writeFileSync(CHAT_FILE, JSON.stringify(data, null, 2));
        
        // Trigger OpenClaw immediately (fire and forget, but detached so it survives the request ending)
        console.log('New user message detected, calling OpenClaw immediately...');
        const prompt = `A new user message was posted in the Fulcra dashboard chat. Read the local chat.json file in this directory. Respond to the user's latest message, and append your response to the chat.json file as role 'assistant' with a timestamp. Do not modify the history. Reply with a short summary when done.`;
        
        // Using exec in the background cleanly. We pass --to main to route it to the main session.
        exec(`openclaw agent --to main --message "${prompt}" > /dev/null 2>&1 &`, (error) => {
            if (error) {
                console.error('Error initiating openclaw background process:', error);
            }
        });

        return json({ success: true });
    } catch (err) {
        return json({ error: err.message }, { status: 500 });
    }
}
