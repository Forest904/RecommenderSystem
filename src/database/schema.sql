
-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);


-- Create User Profiles Table (Optional: for additional user details)
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    avatar_url TEXT,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);


-- Create User Library Table (Tracks personalized recommendations)
CREATE TABLE IF NOT EXISTS user_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content_title TEXT NOT NULL,
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create Movies and Books Table
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    genres TEXT,
    plot TEXT,
    vote_average REAL,
    vote_count INTEGER,
    release_date DATE,
    large_cover_url TEXT
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    genres TEXT,
    plot TEXT,
    vote_average REAL,
    vote_count INTEGER,
    release_date INTEGER,
    large_cover_url TEXT
);
