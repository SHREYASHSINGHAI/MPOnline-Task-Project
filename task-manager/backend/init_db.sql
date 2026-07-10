-- ============================================================
--  init_db.sql  --  Task Manager Database Initialization
--  Run once:  mysql -u root -p < init_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS task_manager_db;
USE task_manager_db;

CREATE TABLE IF NOT EXISTS tasks (
    task_id       INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100)  NOT NULL,
    task_title    VARCHAR(255)  NOT NULL,
    completed     BOOLEAN       DEFAULT FALSE,
    created_at    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO tasks (employee_name, task_title, completed) VALUES
('Alice Johnson',   'Design UI Mockups',          TRUE),
('Bob Smith',       'Set Up Database Schema',      TRUE),
('Carol Williams',  'Implement REST API',          FALSE),
('David Lee',       'Write Unit Tests',            FALSE),
('Eve Martinez',    'Deploy to Staging Server',    FALSE),
('Frank Brown',     'Code Review and QA',          FALSE),
('Grace Chen',      'Client Presentation Prep',   TRUE),
('Henry Wilson',    'Documentation Update',        FALSE);
