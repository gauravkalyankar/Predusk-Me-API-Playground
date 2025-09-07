-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS profile;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS work_experience;
DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS project_skills;

-- Main profile information
CREATE TABLE profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    education TEXT
);

-- List of skills
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Projects worked on
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    links TEXT -- Storing as JSON string for simplicity e.g., '{"github": "url", "live": "url"}'
);

-- Join table for many-to-many relationship between projects and skills
CREATE TABLE project_skills (
    project_id INTEGER,
    skill_id INTEGER,
    PRIMARY KEY (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- Work experience history
CREATE TABLE work_experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    duration TEXT NOT NULL,
    description TEXT
);

-- Personal and professional links
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, -- e.g., 'github', 'linkedin'
    url TEXT NOT NULL
);
