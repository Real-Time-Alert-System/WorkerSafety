const axios = require("axios");
const fs = require("fs");
const path = require("path");
const FormData = require("form-data");
const db = require("./database");

const lastNotificationTimes = new Map(); // Key: location_area_violation, Value: timestamp

// Helper to strip accidental outer quotes or whitespace
const clean = (val) => (val || "").replace(/^["']|["']$/g, "").trim();

/**
 * Sends an alert message to a single Telegram chatId
 */
async function sendSingleTelegram(token, chatId, message, imagePath = null) {
  const url = `https://api.telegram.org/bot${token}/`;
  try {
    if (imagePath && fs.existsSync(imagePath)) {
      const form = new FormData();
      form.append("chat_id", chatId);
      form.append("photo", fs.createReadStream(imagePath));
      form.append("caption", message);
      form.append("parse_mode", "Markdown");

      const response = await axios.post(`${url}sendPhoto`, form, {
        headers: form.getHeaders(),
        timeout: 20000
      });
      return response.data.ok;
    } else {
      const response = await axios.post(`${url}sendMessage`, {
        chat_id: chatId,
        text: message,
        parse_mode: "Markdown"
      }, { timeout: 10000 });
      return response.data.ok;
    }
  } catch (error) {
    console.error(`❌ Telegram send failed for Chat ID ${chatId}:`, error?.response?.data || error.message);
    return false;
  }
}

/**
 * Sends an alert message to ALL configured Telegram target chats:
 * 1) process.env.TELEGRAM_CHAT_ID (Channel/Group)
 * 2) All user personal telegram_chat_ids from PostgreSQL
 */
async function sendTelegramNotification(message, imagePath = null, overrideChatId = null) {
  const enabled = process.env.TELEGRAM_ENABLED === "true";
  const token = clean(process.env.TELEGRAM_BOT_TOKEN);

  if (!enabled || !token || token.includes("YOUR_")) {
    console.log("⚠️ Telegram notifications disabled or token misconfigured.");
    return false;
  }

  const targetChatIds = new Set();

  if (overrideChatId) {
    targetChatIds.add(clean(overrideChatId));
  } else {
    const envChatId = clean(process.env.TELEGRAM_CHAT_ID);
    if (envChatId && !envChatId.includes("YOUR_")) {
      targetChatIds.add(envChatId);
    }

    try {
      const userRes = await db.query(
        "SELECT telegram_chat_id FROM users WHERE telegram_chat_id IS NOT NULL AND telegram_chat_id != '';"
      );
      userRes.rows.forEach(r => {
        const cId = clean(r.telegram_chat_id);
        if (cId) targetChatIds.add(cId);
      });
    } catch (err) {
      console.error("Failed to query user Telegram chat IDs:", err.message);
    }
  }

  if (targetChatIds.size === 0) {
    console.log("⚠️ No Telegram target chat IDs found to send alerts.");
    return false;
  }

  console.log(`📱 Dispatching Telegram alert to ${targetChatIds.size} chat target(s):`, Array.from(targetChatIds));

  let anySuccess = false;
  for (const chatId of targetChatIds) {
    const success = await sendSingleTelegram(token, chatId, message, imagePath);
    if (success) anySuccess = true;
  }
  return anySuccess;
}

/**
 * Processes a detected violation, checks cooldowns, and dispatches alerts to Telegram ONLY.
 */
async function notifyViolation({ violationType, location, areaType, severity, imagePath, imageUrl }) {
  const cooldownPeriod = parseInt(clean(process.env.NOTIFICATION_COOLDOWN) || "60") * 1000;
  const now = Date.now();

  const cooldownKey = `${location}_${areaType}_${violationType}`;
  const lastSent = lastNotificationTimes.get(cooldownKey);

  if (lastSent && (now - lastSent) < cooldownPeriod) {
    const remainingSec = Math.ceil((cooldownPeriod - (now - lastSent)) / 1000);
    console.log(`⏳ Cooldown active for ${cooldownKey} (${remainingSec}s remaining). Skipping duplicate alert.`);
    return false;
  }

  const timestampStr = new Date().toLocaleString();
  const severityEmojis = { high: "🚨", medium: "⚠️", low: "ℹ️" };
  const emoji = severityEmojis[(severity || "").toLowerCase()] || "⚠️";

  const alertMessage = 
`${emoji} *WORKERSHIELD SAFETY ALERT* ${emoji}

*Violation Detected:* ${violationType}
*Severity:* ${severity ? severity.toUpperCase() : "HIGH"}
*Location:* ${location} (${areaType})
*Time:* ${timestampStr}

Please inspect the hazard area immediately.`;

  console.log(`\n📢 Dispatched Telegram Safety Alert for ${violationType} @ ${location}`);

  const tgSuccess = await sendTelegramNotification(alertMessage, imagePath);

  if (tgSuccess) {
    lastNotificationTimes.set(cooldownKey, now);
    return true;
  }
  return false;
}

module.exports = {
  notifyViolation,
  sendTelegramNotification
};
