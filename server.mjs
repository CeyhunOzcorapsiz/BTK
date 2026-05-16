import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const PORT = Number(process.env.PORT || 5173);
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-2.5-flash";
const ROOT = process.cwd();

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
};

function sendJson(res, status, payload) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(payload));
}

async function readJson(req) {
  let body = "";
  for await (const chunk of req) {
    body += chunk;
  }
  return JSON.parse(body || "{}");
}

function buildPrompt(message, erpData) {
  return `
Sen ERPilot AI adli bir ERP asistanisin.
Kullanici Turkce konusuyor. Cevabin kisa, net ve is aksiyonuna donuk olsun.
Varsayim uydurma; sadece verilen ERP verisini yorumla.
Para birimini TL olarak ifade et.

ERP verisi:
${JSON.stringify(erpData, null, 2)}

Kullanici sorusu:
${message}
`;
}

async function askGemini(message, erpData) {
  if (!GEMINI_API_KEY) {
    return null;
  }

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
      },
      body: JSON.stringify({
        contents: [
          {
            role: "user",
            parts: [{ text: buildPrompt(message, erpData) }],
          },
        ],
        generationConfig: {
          temperature: 0.25,
          maxOutputTokens: 260,
        },
      }),
    }
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Gemini API error ${response.status}: ${detail}`);
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("").trim() || null;
}

async function serveStatic(req, res) {
  const requestedPath = new URL(req.url, `http://${req.headers.host}`).pathname;
  const safePath = normalize(decodeURIComponent(requestedPath)).replace(/^(\.\.[/\\])+/, "");
  const filePath = join(ROOT, safePath === "/" ? "index.html" : safePath);

  try {
    const content = await readFile(filePath);
    res.writeHead(200, {
      "Content-Type": mimeTypes[extname(filePath)] || "application/octet-stream",
    });
    res.end(content);
  } catch (error) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Dosya bulunamadi");
  }
}

const server = createServer(async (req, res) => {
  try {
    if (req.method === "POST" && req.url === "/api/chat") {
      const { message, erpData } = await readJson(req);
      if (!message || !erpData) {
        return sendJson(res, 400, { error: "message ve erpData zorunlu" });
      }

      const answer = await askGemini(message, erpData);
      return sendJson(res, 200, {
        answer,
        provider: answer ? "gemini" : "fallback",
      });
    }

    if (req.method === "GET") {
      return serveStatic(req, res);
    }

    sendJson(res, 405, { error: "Method not allowed" });
  } catch (error) {
    sendJson(res, 500, {
      error: "Gemini yaniti alinamadi",
      detail: error.message,
    });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`ERPilot AI http://127.0.0.1:${PORT} adresinde calisiyor`);
});
