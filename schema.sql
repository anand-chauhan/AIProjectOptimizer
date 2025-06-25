-- -------------------------------------
-- 🧠 MoodSentry | PostgreSQL Schema
-- -------------------------------------

-- 1️⃣ Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('owner', 'hr', 'employee')) NOT NULL DEFAULT 'employee',
    hr_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_id) REFERENCES users(id) ON DELETE SET NULL
);
 
-- 2️⃣ Moods Table
CREATE TABLE IF NOT EXISTS moods (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    mood_text TEXT,
    mood_source VARCHAR(10) CHECK (mood_source IN ('text', 'voice', 'facial')) NOT NULL,
    detected_emotion VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
-- 3️⃣ Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    assigned_to INT NOT NULL,
    mood VARCHAR(50),
    task_title VARCHAR(255) NOT NULL,
    task_description TEXT,
    priority VARCHAR(10) CHECK (priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    status VARCHAR(20) CHECK (status IN ('In Progress', 'Completed', 'Stuck')) DEFAULT 'In Progress',
    assigned_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 4️⃣ Task Logs
CREATE TABLE IF NOT EXISTS task_logs (
    id SERIAL PRIMARY KEY,
    task_id INT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('In Progress', 'Completed', 'Stuck')) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 5️⃣ Mood History (Analytics)
CREATE TABLE IF NOT EXISTS mood_history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    mood VARCHAR(50),
    detection_method VARCHAR(10) CHECK (detection_method IN ('text', 'voice', 'facial')) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6️⃣ Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INT,
    hr_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (hr_id) REFERENCES users(id)
);
