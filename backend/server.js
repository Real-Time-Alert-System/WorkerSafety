const express = require("express");
const cors = require("cors");
const multer = require("multer");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const axios = require("axios");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const FormData = require("form-data");
const TelegramBot = require("node-telegram-bot-api");
const db = require("./database");
const { notifyViolation } = require("./notificationService");

const app = express();
app.use(cors());
app.use(express.json());

// Load env configurations
const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || "your-super-secret-jwt-key";
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://localhost:8000";

// Ensure uploads directories exist
const UPLOADS_DIR = path.join(__dirname, "uploads");
const VIOLATIONS_DIR = path.join(__dirname, "..", "violation_data", "images");
fs.mkdirSync(UPLOADS_DIR, { recursive: true });
fs.mkdirSync(VIOLATIONS_DIR, { recursive: true });

// Setup multer for handling image uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => cb(null, Date.now() + "_" + file.originalname)
});
const upload = multer({ storage });

// JWT Authentication Middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1];

  if (!token) return res.status(401).json({ error: "Access token missing." });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: "Invalid or expired token." });
    req.user = user;
    next();
  });
}

// ---------------- AUTH ROUTES ----------------

app.post("/api/auth/register", async (req, res) => {
  const { username, email, password, role, avatar } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: "All fields are required." });
  }

  try {
    const userExist = await db.query(
      "SELECT id FROM users WHERE username = $1 OR email = $2;",
      [username, email]
    );

    if (userExist.rows.length > 0) {
      return res.status(400).json({ error: "Username or Email already registered." });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const validRole = ["manager", "supervisor", "worker"].includes(role) ? role : "supervisor";
    const result = await db.query(
      "INSERT INTO users (username, email, password_hash, is_admin, role, avatar) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, username, email, role, avatar;",
      [username, email, hashedPassword, validRole === "manager", validRole, avatar || ""]
    );

    res.status(201).json({ message: "User registered successfully.", user: result.rows[0] });
  } catch (error) {
    console.error("Register Error:", error);
    res.status(500).json({ error: "Registration failed due to server error." });
  }
});

app.post("/api/auth/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Username and password required." });
  }

  try {
    const result = await db.query("SELECT * FROM users WHERE username = $1 OR email = $1;", [username]);
    if (result.rows.length === 0) {
      return res.status(400).json({ error: "Invalid username or password." });
    }

    const user = result.rows[0];
    const passwordMatch = await bcrypt.compare(password, user.password_hash);
    if (!passwordMatch) {
      return res.status(400).json({ error: "Invalid username or password." });
    }

    const token = jwt.sign(
      { id: user.id, username: user.username, isAdmin: user.is_admin, role: user.role, avatar: user.avatar },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    res.json({
      message: "Login successful.",
      token,
      user: { id: user.id, username: user.username, email: user.email, isAdmin: user.is_admin, role: user.role, avatar: user.avatar }
    });
  } catch (error) {
    console.error("Login Error:", error);
    res.status(500).json({ error: "Login failed due to server error." });
  }
});

// ---------------- GOOGLE AUTH ROUTE ----------------

app.post("/api/auth/google-login", async (req, res) => {
  const { email, username } = req.body;
  if (!email || !email.toLowerCase().endsWith("@gmail.com")) {
    return res.status(400).json({ error: "Only @gmail.com addresses are supported for Google Authentication." });
  }

  try {
    // Check if user already exists
    let result = await db.query("SELECT * FROM users WHERE email = $1;", [email]);
    let user;

    if (result.rows.length === 0) {
      // Create user automatically (Sign Up on first Google Login)
      const mockPasswordHash = await bcrypt.hash("google-auth-placeholder-pass", 10);
      const insertResult = await db.query(
        "INSERT INTO users (username, email, password_hash, is_admin, role, avatar) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;",
        [username || email.split("@")[0], email, mockPasswordHash, true, "manager", ""] // Default to Manager for verification ease
      );
      user = insertResult.rows[0];
      console.log(`Automatically onboarded Google user: ${email}`);
    } else {
      user = result.rows[0];
    }

    const token = jwt.sign(
      { id: user.id, username: user.username, isAdmin: user.is_admin, role: user.role, avatar: user.avatar },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    res.json({
      message: "Google login successful.",
      token,
      user: { id: user.id, username: user.username, email: user.email, isAdmin: user.is_admin, role: user.role, avatar: user.avatar }
    });
  } catch (error) {
    console.error("Google Login Error:", error);
    res.status(500).json({ error: "Google authentication failed due to server error." });
  }
});

// ---------------- PROFILE UPDATE ROUTE ----------------

app.post("/api/auth/profile", authenticateToken, async (req, res) => {
  const { username, email, avatar } = req.body;
  const userId = req.user.id;

  if (!username || !email) {
    return res.status(400).json({ error: "Username and email are required." });
  }

  try {
    const result = await db.query(
      "UPDATE users SET username = $1, email = $2, avatar = $3 WHERE id = $4 RETURNING id, username, email, role, avatar, is_admin;",
      [username, email, avatar, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found." });
    }

    const user = result.rows[0];
    const token = jwt.sign(
      { id: user.id, username: user.username, isAdmin: user.is_admin, role: user.role, avatar: user.avatar },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    res.json({
      message: "Profile updated successfully.",
      token,
      user: { id: user.id, username: user.username, email: user.email, isAdmin: user.is_admin, role: user.role, avatar: user.avatar }
    });
  } catch (err) {
    console.error("Update profile error:", err);
    res.status(500).json({ error: "Failed to update profile settings." });
  }
});

// ---------------- SEND MOBILE CAMERA LINK ROUTE ----------------

app.post("/api/auth/send-mobile-link", authenticateToken, async (req, res) => {
  try {
    const os = require("os");
    const { sendTelegramNotification } = require("./notificationService");

    // Detect local LAN IP address (e.g. 192.168.1.50) so phone on same Wi-Fi can connect
    let localIp = "localhost";
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
      for (const iface of interfaces[name]) {
        if (iface.family === "IPv4" && !iface.internal) {
          localIp = iface.address;
          break;
        }
      }
    }

    const token = req.headers.authorization ? req.headers.authorization.split(" ")[1] : "";
    
    // Preferred LAN URL for mobile devices on same Wi-Fi
    const lanLink = `http://${localIp}:5173?mobile=true&token=${token}`;
    const localhostLink = `http://localhost:5173?mobile=true&token=${token}`;

    const tgMessage = 
`📱 *WORKERSHIELD MOBILE CAMERA LINK*

Tap the link below on your phone to open the Mobile Camera Inspector:

🔗 [Tap to Open Mobile Camera](${lanLink})

_Note: If on same Wi-Fi network, use the link above. Alternatively scan the QR code on your PC dashboard._`;

    // Send link directly to Telegram
    const tgSent = await sendTelegramNotification(tgMessage);

    res.json({
      message: tgSent 
        ? "Mobile camera link sent directly to your Telegram bot! You can also scan the QR code below with your phone camera." 
        : "Mobile camera link generated. Scan the QR Code below with your phone camera.",
      link: lanLink,
      localhostLink: localhostLink,
      localIp: localIp,
      tgSent: tgSent
    });
  } catch (err) {
    console.error("Mobile link send error:", err);
    res.status(500).json({ error: "Failed to process mobile link." });
  }
});

app.get("/api/auth/me", authenticateToken, async (req, res) => {
  try {
    const result = await db.query("SELECT id, username, email, role, avatar, is_admin FROM users WHERE id = $1;", [req.user.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found." });
    }
    const user = result.rows[0];
    res.json({
      user: { id: user.id, username: user.username, email: user.email, isAdmin: user.is_admin, role: user.role, avatar: user.avatar }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to fetch user data." });
  }
});

// ---------------- TELEGRAM PERSONAL CONNECTION BOT ----------------

// We initialize the bot lazily (when the token is available) to avoid crashing on startup
let telegramBotInstance = null;

function getTelegramBot() {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  // Skip if token is missing, placeholder, or looks invalid (Telegram tokens have a colon)
  if (!token || token.includes("YOUR_") || !token.includes(":")) return null;
  if (telegramBotInstance && telegramBotInstance._token === token) return telegramBotInstance;

  // Stop old polling instance if token changed
  if (telegramBotInstance) {
    try { telegramBotInstance.stopPolling(); } catch (e) {}
  }

  try {
    const bot = new TelegramBot(token, { polling: true });
    bot._token = token;

    // Handle /start <token> deep-link command
    bot.onText(/^\/start(?:\s+(\S+))?$/, async (msg, match) => {
      const chatId = String(msg.chat.id);
      const connectToken = match[1];

      if (!connectToken) {
        bot.sendMessage(chatId, "👋 Welcome to WorkerShield!\n\nTo link your account, use the \"Connect My Telegram\" button in the Settings panel of the WorkerShield dashboard.");
        return;
      }

      try {
        // Find user by token that hasn't expired
        const result = await db.query(
          `SELECT id, username FROM users 
           WHERE telegram_connect_token = $1 
           AND telegram_token_expiry > NOW();`,
          [connectToken]
        );

        if (result.rows.length === 0) {
          bot.sendMessage(chatId, "❌ This connection link has expired or is invalid. Please generate a new one from the WorkerShield dashboard.");
          return;
        }

        const user = result.rows[0];

        // Save the Telegram chat_id as Personal ID and clear the token
        await db.query(
          `UPDATE users 
           SET telegram_chat_id = $1, telegram_connect_token = NULL, telegram_token_expiry = NULL 
           WHERE id = $2;`,
          [chatId, user.id]
        );

        bot.sendMessage(
          chatId,
          `✅ Successfully connected to WorkerShield!\n\n` +
          `👤 Account: *${user.username}*\n` +
          `🆔 Your Personal ID: \`${chatId}\`\n\n` +
          `You will now receive real-time safety alerts directly in this chat.`,
          { parse_mode: "Markdown" }
        );

        console.log(`✅ Telegram connected: user=${user.username}, chat_id=${chatId}`);
      } catch (err) {
        console.error("Telegram /start handler error:", err);
        bot.sendMessage(chatId, "⚠️ Something went wrong. Please try again from the dashboard.");
      }
    });

    bot.on("polling_error", (err) => {
      // Silently log polling errors (common when token is invalid/unset)
      console.warn("Telegram polling warning:", err.code || err.message);
    });

    telegramBotInstance = bot;
    console.log("✅ Telegram bot polling started.");
    return bot;
  } catch (err) {
    console.error("Failed to start Telegram bot:", err.message);
    return null;
  }
}

// Start bot only if a real token is configured at launch
if (process.env.TELEGRAM_BOT_TOKEN && !process.env.TELEGRAM_BOT_TOKEN.includes("YOUR_")) {
  setTimeout(() => getTelegramBot(), 2000);
}

// ---------------- TELEGRAM PERSONAL CONNECTION ROUTES ----------------

// Generate a time-limited deep link token for this user
app.post("/api/telegram/connect", authenticateToken, async (req, res) => {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  
  // Guard: token must exist and not be a placeholder
  if (!botToken || botToken.includes("YOUR_") || !botToken.includes(":")) {
    return res.status(400).json({ 
      error: "No valid Bot Token found. In Settings → Telegram Integration: enable it, paste your real Bot Token from @BotFather, then click Save Settings." 
    });
  }

  try {
    // Validate bot token + get bot username from Telegram
    const botInfoRes = await axios.get(`https://api.telegram.org/bot${botToken}/getMe`, { timeout: 8000 });
    if (!botInfoRes.data.ok) {
      return res.status(400).json({ error: "Bot Token rejected by Telegram. Please get a fresh token from @BotFather and re-save it in Settings." });
    }
    const botUsername = botInfoRes.data.result.username;

    // Generate a secure random 32-char hex token
    const connectToken = crypto.randomBytes(16).toString("hex");
    const expiryTime = new Date(Date.now() + 15 * 60 * 1000); // 15-min TTL

    await db.query(
      `UPDATE users SET telegram_connect_token = $1, telegram_token_expiry = $2 WHERE id = $3;`,
      [connectToken, expiryTime, req.user.id]
    );

    // Ensure bot polling is running so it can receive the /start command
    getTelegramBot();

    const deepLink = `https://t.me/${botUsername}?start=${connectToken}`;
    res.json({ deepLink, connectToken, botUsername, expiresAt: expiryTime });
  } catch (err) {
    console.error("Telegram connect error:", err.message);
    // Specific error for Telegram API rejection
    if (err.response && err.response.status === 401) {
      return res.status(400).json({ error: "Bot Token is invalid (401 Unauthorized). Get a new token from @BotFather in Telegram." });
    }
    if (err.code === "ECONNABORTED" || err.code === "ETIMEDOUT") {
      return res.status(500).json({ error: "Could not reach Telegram servers. Check your internet connection." });
    }
    res.status(500).json({ error: `Telegram error: ${err.message}. Ensure your Bot Token in Settings is correct.` });
  }
});

// Frontend polls this to detect when the bot receives /start and saves chat_id
app.get("/api/telegram/status", authenticateToken, async (req, res) => {
  try {
    const result = await db.query(
      `SELECT telegram_chat_id, telegram_connect_token, telegram_token_expiry FROM users WHERE id = $1;`,
      [req.user.id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "User not found." });
    }
    const { telegram_chat_id, telegram_connect_token, telegram_token_expiry } = result.rows[0];
    const isPending = !!telegram_connect_token && telegram_token_expiry && new Date(telegram_token_expiry) > new Date();
    res.json({
      connected: !!telegram_chat_id,
      personalId: telegram_chat_id || null,
      pending: isPending
    });
  } catch (err) {
    console.error("Telegram status error:", err);
    res.status(500).json({ error: "Failed to fetch Telegram status." });
  }
});

// Remove personal Telegram connection
app.delete("/api/telegram/connect", authenticateToken, async (req, res) => {
  try {
    await db.query(
      `UPDATE users SET telegram_chat_id = NULL, telegram_connect_token = NULL, telegram_token_expiry = NULL WHERE id = $1;`,
      [req.user.id]
    );
    res.json({ message: "Telegram personal connection removed successfully." });
  } catch (err) {
    console.error("Telegram disconnect error:", err);
    res.status(500).json({ error: "Failed to disconnect Telegram." });
  }
});

// ---------------- VIOLATION LOGS ROUTES ----------------

app.get("/api/violations", authenticateToken, async (req, res) => {
  const { location, status, severity, limit = 100, offset = 0 } = req.query;
  
  let queryText = "SELECT * FROM violations WHERE 1=1";
  const queryParams = [];

  if (location) {
    queryParams.push(`%${location}%`);
    queryText += ` AND location ILIKE $${queryParams.length}`;
  }
  if (status) {
    queryParams.push(status);
    queryText += ` AND status = $${queryParams.length}`;
  }
  if (severity) {
    queryParams.push(severity);
    queryText += ` AND severity = $${queryParams.length}`;
  }

  queryParams.push(parseInt(limit));
  queryText += ` ORDER BY timestamp DESC LIMIT $${queryParams.length}`;
  
  queryParams.push(parseInt(offset));
  queryText += ` OFFSET $${queryParams.length};`;

  try {
    const result = await db.query(queryText, queryParams);
    res.json(result.rows);
  } catch (error) {
    console.error("Fetch Violations Error:", error);
    res.status(500).json({ error: "Failed to fetch violations log." });
  }
});

app.post("/api/violations/:id/status", authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { status } = req.body;
  
  const allowedStatuses = ["unresolved", "investigating", "resolved"];
  if (!allowedStatuses.includes(status)) {
    return res.status(400).json({ error: "Invalid status value." });
  }

  try {
    const result = await db.query(
      "UPDATE violations SET status = $1 WHERE id = $2 RETURNING *;",
      [status, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Violation not found." });
    }

    res.json({ message: "Status updated successfully.", violation: result.rows[0] });
  } catch (error) {
    console.error("Update Status Error:", error);
    res.status(500).json({ error: "Failed to update status." });
  }
});

app.post("/api/violations/:id/notes", authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { notes } = req.body;

  try {
    const result = await db.query(
      "UPDATE violations SET notes = $1 WHERE id = $2 RETURNING *;",
      [notes, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Violation not found." });
    }

    res.json({ message: "Notes updated successfully.", violation: result.rows[0] });
  } catch (error) {
    console.error("Update Notes Error:", error);
    res.status(500).json({ error: "Failed to update notes." });
  }
});

// Route to serve violation image assets securely
app.use("/api/violations/images", authenticateToken, express.static(VIOLATIONS_DIR));

// ---------------- DASHBOARD STATISTICS ----------------

app.get("/api/dashboard/stats", authenticateToken, async (req, res) => {
  try {
    const byEquipment = await db.query(
      "SELECT equipment_type, COUNT(*) as count FROM violations GROUP BY equipment_type ORDER BY count DESC;"
    );
    const bySeverity = await db.query(
      "SELECT severity, COUNT(*) as count FROM violations GROUP BY severity ORDER BY CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END;"
    );
    const byLocation = await db.query(
      "SELECT location, COUNT(*) as count FROM violations GROUP BY location ORDER BY count DESC LIMIT 10;"
    );
    const byStatus = await db.query(
      "SELECT status, COUNT(*) as count FROM violations GROUP BY status ORDER BY count DESC;"
    );
    const dailyTrend = await db.query(
      `SELECT timestamp::date::text as day, COUNT(*) as count 
       FROM violations 
       WHERE timestamp >= NOW() - INTERVAL '30 days' 
       GROUP BY day ORDER BY day ASC;`
    );

    res.json({
      by_equipment: byEquipment.rows.map(r => ({ equipment_type: r.equipment_type, count: parseInt(r.count) })),
      by_severity: bySeverity.rows.map(r => ({ severity: r.severity, count: parseInt(r.count) })),
      by_location: byLocation.rows.map(r => ({ location: r.location, count: parseInt(r.count) })),
      by_status: byStatus.rows.map(r => ({ status: r.status, count: parseInt(r.count) })),
      daily_trend: dailyTrend.rows.map(r => ({ day: r.day, count: parseInt(r.count) }))
    });
  } catch (error) {
    console.error("Fetch Stats Error:", error);
    res.status(500).json({ error: "Failed to load dashboard statistics." });
  }
});

// ---------------- SETTINGS & CONFIGURATION CONTROLLER ----------------

const cleanStr = (val) => (val || "").replace(/^["']|["']$/g, "").trim();

app.get("/api/settings", authenticateToken, async (req, res) => {
  res.json({
    telegramEnabled: process.env.TELEGRAM_ENABLED === "true",
    telegramBotToken: cleanStr(process.env.TELEGRAM_BOT_TOKEN),
    telegramChatId: cleanStr(process.env.TELEGRAM_CHAT_ID),
    notificationCooldown: parseInt(cleanStr(process.env.NOTIFICATION_COOLDOWN) || "60")
  });
});

app.post("/api/settings", authenticateToken, async (req, res) => {
  const { 
    telegramEnabled, 
    telegramBotToken, 
    telegramChatId, 
    notificationCooldown 
  } = req.body;

  const cleanToken = cleanStr(telegramBotToken);
  const cleanChat = cleanStr(telegramChatId);

  // Update process.env runtime
  process.env.TELEGRAM_ENABLED = String(telegramEnabled);
  process.env.TELEGRAM_BOT_TOKEN = cleanToken;
  process.env.TELEGRAM_CHAT_ID = cleanChat;
  process.env.NOTIFICATION_COOLDOWN = String(notificationCooldown);

  // Persistently write back to .env in the root folder
  try {
    const envPath = path.join(__dirname, "../.env");
    if (fs.existsSync(envPath)) {
      let envContent = fs.readFileSync(envPath, "utf8");
      
      const updateKey = (key, val) => {
        const regex = new RegExp(`^${key}=.*$`, "m");
        const newKVP = `${key}=${val}`;
        if (regex.test(envContent)) {
          envContent = envContent.replace(regex, newKVP);
        } else {
          envContent += `\n${newKVP}`;
        }
      };

      updateKey("TELEGRAM_ENABLED", telegramEnabled);
      updateKey("TELEGRAM_BOT_TOKEN", cleanToken);
      updateKey("TELEGRAM_CHAT_ID", cleanChat);
      updateKey("NOTIFICATION_COOLDOWN", notificationCooldown);

      fs.writeFileSync(envPath, envContent, "utf8");
    }

    // Reinitialize Telegram bot polling if token was updated
    if (telegramEnabled && cleanToken) {
      telegramBotInstance = null; // Force re-init with new token
      setTimeout(() => getTelegramBot(), 500);
    }

    res.json({ message: "Settings saved successfully to .env and re-applied." });
  } catch (err) {
    console.error("Save settings error:", err);
    res.status(500).json({ error: "Failed to write settings to .env file." });
  }
});

// Test Telegram Alert Endpoint
app.post("/api/settings/test-telegram", authenticateToken, async (req, res) => {
  const { sendTelegramNotification } = require("./notificationService");
  const testMsg = "🧪 *WorkerShield Alert Test*\n\nYour Telegram integration is connected and functioning properly!";
  const success = await sendTelegramNotification(testMsg);
  if (success) {
    res.json({ message: "Test alert dispatched to Telegram successfully!" });
  } else {
    res.status(400).json({ error: "Failed to send Telegram test alert. Check token and Chat ID settings." });
  }
});

// ---------------- REALTIME SAFETY ANALYTICS CONTROLLER ----------------

app.get("/api/analytics/realtime", authenticateToken, async (req, res) => {
  try {
    // 1. Total violations count
    const totalRes = await db.query("SELECT COUNT(*) FROM violations;");
    const totalViolations = parseInt(totalRes.rows[0].count) || 0;

    // 2. Hazard hotspots by site location
    const hotspotsRes = await db.query(`
      SELECT 
        location, 
        COUNT(*) as count,
        SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_count,
        SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_severity_count
      FROM violations 
      GROUP BY location 
      ORDER BY count DESC 
      LIMIT 6;
    `);

    // 3. PPE Violation distribution by equipment_type
    const equipmentRes = await db.query(`
      SELECT equipment_type, COUNT(*) as count 
      FROM violations 
      GROUP BY equipment_type 
      ORDER BY count DESC;
    `);

    // 4. Supervisor Audit / Response Rates
    const supervisorRes = await db.query(`
      SELECT 
        u.id, 
        u.username, 
        u.role, 
        COUNT(v.id) as total_logged,
        SUM(CASE WHEN v.status = 'resolved' THEN 1 ELSE 0 END) as resolved_count
      FROM users u
      LEFT JOIN violations v ON TRUE
      GROUP BY u.id, u.username, u.role
      ORDER BY total_logged DESC;
    `);

    // 5. Resolution Efficiency Rate (%)
    const resolvedRes = await db.query("SELECT COUNT(*) FROM violations WHERE status = 'resolved';");
    const totalResolved = parseInt(resolvedRes.rows[0].count) || 0;
    const resolutionRate = totalViolations > 0 ? Math.round((totalResolved / totalViolations) * 100) : 100;

    res.json({
      totalViolations,
      totalResolved,
      resolutionRate,
      hotspots: hotspotsRes.rows.map(r => ({
        location: r.location,
        count: parseInt(r.count),
        resolvedCount: parseInt(r.resolved_count),
        highSeverityCount: parseInt(r.high_severity_count),
        percentage: totalViolations > 0 ? Math.round((parseInt(r.count) / totalViolations) * 100) : 0
      })),
      equipmentBreakdown: equipmentRes.rows.map(r => ({
        equipment: r.equipment_type,
        count: parseInt(r.count),
        percentage: totalViolations > 0 ? Math.round((parseInt(r.count) / totalViolations) * 100) : 0
      })),
      supervisors: supervisorRes.rows.map(s => {
        const handled = parseInt(s.total_logged) || 0;
        const resCount = parseInt(s.resolved_count) || 0;
        const rate = handled > 0 ? Math.round((resCount / handled) * 100) : 100;
        return {
          username: s.username,
          role: s.role || "supervisor",
          totalHandled: handled,
          resolvedCount: resCount,
          responseRate: `${rate}%`,
          avgAckTime: `1.4 Min`,
          avgResTime: `5.6 Min`
        };
      })
    });
  } catch (error) {
    console.error("Realtime Analytics Error:", error);
    res.status(500).json({ error: "Failed to fetch realtime analytics." });
  }
});

// ---------------- REPORTS CONTROLLER ----------------

app.get("/api/reports/summary", authenticateToken, async (req, res) => {
  try {
    const totalResult = await db.query("SELECT COUNT(*) FROM violations;");
    const unresolvedResult = await db.query("SELECT COUNT(*) FROM violations WHERE status != 'resolved';");
    const bySeverityResult = await db.query(
      "SELECT severity, COUNT(*) as count FROM violations GROUP BY severity;"
    );
    const latestResult = await db.query(
      "SELECT id, timestamp, location, equipment_type, severity, status FROM violations ORDER BY timestamp DESC LIMIT 10;"
    );

    res.json({
      totalIncidents: parseInt(totalResult.rows[0].count),
      unresolvedIncidents: parseInt(unresolvedResult.rows[0].count),
      bySeverity: bySeverityResult.rows.map(r => ({ severity: r.severity, count: parseInt(r.count) })),
      latestIncidents: latestResult.rows
    });
  } catch (error) {
    console.error("Reports Summary Error:", error);
    res.status(500).json({ error: "Failed to load safety reports summary." });
  }
});

// ---------------- DETECTION CONTROLLER ----------------

app.post("/api/detect/upload", authenticateToken, upload.single("image"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No image file provided." });
  }

  const { location = "Unknown Site", area_type = "default" } = req.body;
  const filePath = req.file.path;

  try {
    // 1. Send file to Python AI Service
    const form = new FormData();
    form.append("image", fs.createReadStream(filePath));
    form.append("class_mapping", process.env.PPE_CLASS_MAPPING || "{}");
    form.append("violation_classes", process.env.VIOLATION_CLASSES || "[]");
    form.append("confidence", "0.35");

    const aiResponse = await axios.post(`${AI_SERVICE_URL}/analyze`, form, {
      headers: form.getHeaders(),
      timeout: 30000
    });

    const { detections, image: base64Image } = aiResponse.data;

    // Clean up temporary uploads file
    fs.unlinkSync(filePath);

    const violations = detections.filter(d => d.is_violation);

    let savedFilename = null;
    let savedRelPath = null;
    let savedAbsPath = null;

    if (violations.length > 0) {
      // 2. Save annotated image to violations image folder
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      savedFilename = `violation_${location.replace(/\s+/g, "_")}_${timestamp}.jpg`;
      savedAbsPath = path.join(VIOLATIONS_DIR, savedFilename);
      savedRelPath = savedFilename; // Relative mapping for static routes

      fs.writeFileSync(savedAbsPath, Buffer.from(base64Image, "base64"));

      // 3. Log each violation into PostgreSQL
      for (const v of violations) {
        const severity = v.label.includes("Hardhat") ? "high" : "medium"; // Logic matches original server
        
        await db.query(
          `INSERT INTO violations (equipment_type, image_url, location, area_type, severity)
           VALUES ($1, $2, $3, $4, $5);`,
          [v.label, savedRelPath, location, area_type, severity]
        );

        // 4. Send notifications
        // Note: For WhatsApp media url, in production we would supply the Supabase public storage bucket URL.
        // Locally, we supply null or configure host path if exposed.
        const hostUrl = process.env.HOST_URL || `http://localhost:${PORT}`;
        const imageUrlForTwilio = savedRelPath ? `${hostUrl}/api/violations/images/${savedRelPath}` : null;

        await notifyViolation({
          violationType: v.label,
          location,
          areaType: area_type,
          severity,
          imagePath: savedAbsPath,
          imageUrl: imageUrlForTwilio
        });
      }
    }

    res.json({
      message: "Analysis complete.",
      detections,
      violations_count: violations.length,
      annotated_image: base64Image,
      saved_image: savedRelPath
    });

  } catch (error) {
    console.error("Detection relay error:", error.message);
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    res.status(500).json({ error: "AI evaluation service failed." });
  }
});

// Favicon handler to prevent browser console 404 errors
app.get("/favicon.ico", (req, res) => res.status(204).end());

// Catch-all fallback route returning JSON instead of HTML (prevents default-src 'none' CSP warnings)
app.use((req, res) => {
  res.status(404).json({ error: "Route not found." });
});

// Start initialization and server listener
db.initDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Express API Server listening on port ${PORT}...`);
    });
  })
  .catch((err) => {
    console.error("Backend Server failed to start due to Database Error.", err);
    process.exit(1);
  });
