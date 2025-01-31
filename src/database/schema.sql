-- Create Users Table
CREATE TABLE users_new (
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

-- Create User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    preferred_genres TEXT, -- A JSON or comma-separated list of genres
    language TEXT,
    notification_preferences TEXT, -- A JSON or comma-separated list
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create User Activity Log Table
CREATE TABLE IF NOT EXISTS user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL, -- e.g., "login", "view_recommendation", etc.
    activity_details TEXT, -- Optional details about the activity
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create User Favorites Table
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content_id INTEGER NOT NULL, -- ID of the content (book, movie, etc.)
    content_type TEXT NOT NULL, -- e.g., "book", "movie"
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create User Ratings Table
CREATE TABLE IF NOT EXISTS user_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content_id INTEGER NOT NULL, -- ID of the content
    rating INTEGER CHECK (rating >= 1 AND rating <= 10), -- Ratings from 1 to 10
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create User Sessions Table (Optional: for login session management)
/*
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    device_info TEXT, -- Information about the user's device
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
*/

-- Create User Recommendations Table (Tracks personalized recommendations)
CREATE TABLE IF NOT EXISTS user_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content_title TEXT NOT NULL,
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
