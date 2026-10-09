USE taskapp;

-- Create the users table if it does not already exist.
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add user_id only if the column is missing.
-- Keep it nullable temporarily so existing tasks remain intact.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'taskapp'
      AND TABLE_NAME = 'tasks'
      AND COLUMN_NAME = 'user_id'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE tasks ADD COLUMN user_id INT NULL',
    'SELECT ''user_id column already exists'' AS migration_status'
);

PREPARE migration_stmt FROM @sql;
EXECUTE migration_stmt;
DEALLOCATE PREPARE migration_stmt;

-- Intentionally stop here until the moyo account exists.
-- We will assign existing tasks and add the foreign key
-- only after verifying the account ID and current schema.
