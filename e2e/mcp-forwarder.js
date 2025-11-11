// mcp-forwarder.js — reads e2e-events.log and POSTs to MCP ingestion endpoint
const fs = require('fs');
const https = require('https');
const http = require('http');

const MCP_INGEST_URL = process.env.MCP_INGEST_URL || 'http://localhost:8000/ingest';
const EVENTS_LOG = process.env.EVENTS_LOG || './e2e-events.log';

console.log('🚀 MCP Forwarder started');
console.log(`📡 Forwarding events to: ${MCP_INGEST_URL}`);
console.log(`📝 Watching log file: ${EVENTS_LOG}\n`);

// Track last position to avoid re-reading
let lastPosition = 0;

// Parse URL for http/https
const url = new URL(MCP_INGEST_URL);
const httpModule = url.protocol === 'https:' ? https : http;

async function forwardEvent(eventLine) {
  return new Promise((resolve, reject) => {
    try {
      const event = JSON.parse(eventLine);
      const data = JSON.stringify(event);
      
      const options = {
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data)
        }
      };

      // Add API key if provided
      if (process.env.MCP_API_KEY) {
        options.headers['Authorization'] = `Bearer ${process.env.MCP_API_KEY}`;
      }

      const req = httpModule.request(options, (res) => {
        let responseData = '';
        res.on('data', (chunk) => { responseData += chunk; });
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(`✅ Forwarded: ${event.kind} (${res.statusCode})`);
            resolve();
          } else {
            console.error(`❌ Failed: ${event.kind} (${res.statusCode}) - ${responseData}`);
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        });
      });

      req.on('error', (err) => {
        console.error(`❌ Network error forwarding ${event.kind}:`, err.message);
        reject(err);
      });

      req.write(data);
      req.end();
    } catch (e) {
      console.error('❌ Parse/send error:', e.message);
      reject(e);
    }
  });
}

async function processNewEvents() {
  try {
    // Check if file exists
    if (!fs.existsSync(EVENTS_LOG)) {
      return;
    }

    const stats = fs.statSync(EVENTS_LOG);
    
    // If file is smaller than last position, it was truncated/recreated
    if (stats.size < lastPosition) {
      lastPosition = 0;
    }

    // If no new data, return
    if (stats.size === lastPosition) {
      return;
    }

    // Read only new data
    const stream = fs.createReadStream(EVENTS_LOG, {
      start: lastPosition,
      encoding: 'utf8'
    });

    let buffer = '';
    
    stream.on('data', (chunk) => {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.trim()) {
          forwardEvent(line).catch(() => {}); // Fire and forget
        }
      }
    });

    stream.on('end', () => {
      lastPosition = stats.size;
    });

  } catch (err) {
    console.error('❌ Error processing events:', err.message);
  }
}

// Watch file for changes
fs.watch(EVENTS_LOG, { persistent: true }, (eventType) => {
  if (eventType === 'change') {
    processNewEvents();
  }
});

// Initial read
processNewEvents();

// Also poll every 2 seconds as fallback
setInterval(processNewEvents, 2000);

console.log('👀 Watching for new events...\n');

// Security note: When forwarding artifacts/screenshots to any server, 
// secure the endpoint (API keys, TLS) and avoid sending PII accidentally.
