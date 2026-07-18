-- ============================================
-- Game Library & Achievement Tracker
-- Script 002: Create Users Table
-- ============================================
-- Stores registered users of the application.
-- Each user has a unique ID, username, email,
-- country, and a timestamp for when they joined.
-- ============================================

USE game_library;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,   -- Unique ID, auto-generated
    username VARCHAR(50) NOT NULL,             -- Required: display name
    email VARCHAR(100) NOT NULL,               -- Required: contact email
    country VARCHAR(50),                       -- Optional: user's country
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Auto-set on insert
);
