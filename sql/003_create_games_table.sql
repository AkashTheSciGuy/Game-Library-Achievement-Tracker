-- ============================================
-- Game Library & Achievement Tracker
-- Script 003: Create Games Table
-- ============================================
-- Stores the game catalog. Each game has details
-- like title, description, price, platform, etc.
-- 
-- Version 1: Developer, publisher, and platform
-- are stored as simple text columns. In a future
-- version, these will become separate tables to
-- avoid duplicate data.
-- ============================================

USE game_library;

CREATE TABLE IF NOT EXISTS games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,    -- Unique ID, auto-generated
    title VARCHAR(100) NOT NULL,               -- Required: game name
    description TEXT,                          -- Long text for game summary
    release_date DATE,                         -- Format: YYYY-MM-DD
    price DECIMAL(10,2),                       -- Supports prices like 59.99
    age_rating VARCHAR(10),                    -- E.g., "E", "T", "M"
    platform VARCHAR(50),                      -- E.g., "PC", "PS5", "Xbox"
    developer VARCHAR(100),                    -- Studio that made the game
    publisher VARCHAR(100),                    -- Company that published it
    steam_rating DECIMAL(3,1)                  -- Rating out of 10, e.g. 8.5
);
