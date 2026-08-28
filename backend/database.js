const { Pool, Client } = require("pg");
const bcrypt = require("bcryptjs");
const dotenv = require("dotenv");
const path = require("path");

// Load environmental variables from project root
dotenv.config({ path: path.join(__dirname, "..", ".env") });

const pool = new Pool({
  user: process.env.DB_USER || "postgres",
  host: process.env.DB_HOST || "localhost",
  database: process.env.DB_DATABASE || "worker_safety",
  password: process.env.DB_PASSWORD || "postgres",
  port: parseInt(process.env.DB_PORT || "5432"),
  // Handle production connection configs if SSL is required
  ssl: process.env.DB_SSL === "true" ? { rejectUnauthorized: false } : false
});

pool.on("connect", (client) => {
  client.query("SET client_encoding = 'UTF8';").catch(() => {});
  console.log("Connected to the PostgreSQL database successfully (UTF8).");
});

pool.on("error", (err) => {
  console.error("Unexpected error on idle PostgreSQL client", err);
});

async function initDB() {
  const dbName = process.env.DB_DATABASE || "worker_safety";
  
  // Connect to the default 'postgres' database to verify/create target database
  const bootstrapClient = new Client({
    user: process.env.DB_USER || "postgres",
    host: process.env.DB_HOST || "localhost",
    database: "postgres",
    password: process.env.DB_PASSWORD || "postgres",
    port: parseInt(process.env.DB_PORT || "5432"),
    ssl: process.env.DB_SSL === "true" ? { rejectUnauthorized: false } : false
  });

  try {
    await bootstrapClient.connect();
    const checkRes = await bootstrapClient.query(
      "SELECT 1 FROM pg_database WHERE datname = $1;",
      [dbName]
    );

    if (checkRes.rows.length === 0) {
      console.log(`Database "${dbName}" does not exist. Attempting to create it...`);
      // Escape database name safely by replacing quotes
      const escapedDbName = dbName.replace(/"/g, '""');
      await bootstrapClient.query(`CREATE DATABASE "${escapedDbName}";`);
      console.log(`Database "${dbName}" created successfully.`);
    }
  } catch (error) {
    console.warn(`Database creation bootstrap skipped or failed for "${dbName}":`, error.message);
  } finally {
    try {
      await bootstrapClient.end();
    } catch (e) {}
  }

  const client = await pool.connect();
  try {
    console.log("Initializing database tables if not existing...");
    
    // Create users table
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
      );
    `);
    
    // Create violations table
    await client.query(`
      CREATE TABLE IF NOT EXISTS violations (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        equipment_type VARCHAR(64) NOT NULL,
        image_url VARCHAR(512),
        location VARCHAR(120),
        area_type VARCHAR(64),
        severity VARCHAR(32),
        status VARCHAR(32) DEFAULT 'unresolved' NOT NULL,
        notes TEXT
      );
    `);

    // Safe migration: Add notes column if it doesn't already exist in an existing table
    await client.query("ALTER TABLE violations ADD COLUMN IF NOT EXISTS notes TEXT;");
    
    // Safe migration: Add role column if it doesn't already exist in users table
    await client.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(32) DEFAULT 'supervisor' NOT NULL;");
    await client.query("UPDATE users SET role = 'manager' WHERE is_admin = TRUE AND role = 'supervisor';");
    
    // Safe migration: Add avatar column if it doesn't already exist in users table
    await client.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar TEXT;");

    // Safe migration: Add Telegram personal connection columns
    await client.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(64);");
    await client.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_connect_token VARCHAR(128);");
    await client.query("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_token_expiry TIMESTAMP;");
    
    // Create indexes for optimization
    await client.query("CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations (timestamp);");
    await client.query("CREATE INDEX IF NOT EXISTS idx_violations_equipment ON violations (equipment_type);");
    await client.query("CREATE INDEX IF NOT EXISTS idx_violations_location ON violations (location);");
    await client.query("CREATE INDEX IF NOT EXISTS idx_violations_status ON violations (status);");

    // Seed default admin user if none exists
    const usersCount = await client.query("SELECT COUNT(*) FROM users;");
    if (parseInt(usersCount.rows[0].count) === 0) {
      console.log("No users found. Seeding default admin account (username: admin, password: changeme)...");
      const defaultUsername = "admin";
      const defaultEmail = "admin@example.com";
      const hashedPassword = await bcrypt.hash("changeme", 10);
      await client.query(
        "INSERT INTO users (username, email, password_hash, is_admin, role) VALUES ($1, $2, $3, $4, $5);",
        [defaultUsername, defaultEmail, hashedPassword, true, "manager"]
      );
      console.log("Default admin account seeded successfully.");
    }

    console.log("Database tables checked and initialized.");
  } catch (err) {
    console.error("Error initializing PostgreSQL database schema:", err);
    throw err;
  } finally {
    client.release();
  }
}

module.exports = {
  pool,
  initDB,
  query: (text, params) => pool.query(text, params)
};
