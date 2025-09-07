import sqlite3
import json

DATABASE = 'profile.db'

def seed_data():
    """Seeds the database with personal information."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # --- Clear existing data ---
    tables = ['profile', 'skills', 'projects', 'work_experience', 'links', 'project_skills']
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        try:
            # Reset autoincrement sequence for sqlite
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
        except sqlite3.OperationalError:
            # This fails if the table has no autoincrement, which is fine
            pass

    # --- Profile Data ---
    profile = {
        'name': 'Gaurav Kalyankar',
        'email': 'gauravkalyankar844@gmail.com', 
        'education': 'B.Tech in Information Technology'
    }
    cursor.execute("INSERT INTO profile (name, email, education) VALUES (?, ?, ?)",
                   (profile['name'], profile['email'], profile['education']))

    # --- Skills Data ---
    skills = ['Python', 'JavaScript', 'React', 'Node.js', 'Flask', 'PostgreSQL', 'MongoDB', 'Docker', 'AWS']
    skill_ids = {}
    for skill in skills:
        cursor.execute("INSERT INTO skills (name) VALUES (?)", (skill,))
        skill_ids[skill] = cursor.lastrowid

    # --- Links Data ---
    links = {
        'github': 'https://github.com/gauravkalyankare',
        'linkedin': 'https://www.linkedin.com/in/gaurav-k-859404253/',
        
    }
    for name, url in links.items():
        cursor.execute("INSERT INTO links (name, url) VALUES (?, ?)", (name, url))

    # --- Projects Data ---
    projects = [
        {
            'title': 'E-commerce Analytics Dashboard',
            'description': 'A web-based dashboard for visualizing sales data, customer behavior, and inventory metrics. Built with React for the frontend and a Node.js/Express backend.',
            'links': json.dumps({'github': 'https://github.com/alexdoe/ecom-dashboard', 'live': 'https://ecom-dash.alexdoe.com'}),
            'skills': ['React', 'Node.js', 'MongoDB']
        },
        {
            'title': 'Flask API for IoT Devices',
            'description': 'A RESTful API to collect, store, and process sensor data from a network of IoT devices. Deployed on AWS using Docker containers.',
            'links': json.dumps({'github': 'https://github.com/alexdoe/iot-api'}),
            'skills': ['Python', 'Flask', 'PostgreSQL', 'Docker', 'AWS']
        }
    ]

    for proj in projects:
        cursor.execute("INSERT INTO projects (title, description, links) VALUES (?, ?, ?)",
                       (proj['title'], proj['description'], proj['links']))
        project_id = cursor.lastrowid
        # Link skills to this project
        for skill_name in proj['skills']:
            skill_id = skill_ids[skill_name]
            cursor.execute("INSERT INTO project_skills (project_id, skill_id) VALUES (?, ?)", (project_id, skill_id))

    # --- Work Experience Data ---
    work_experience = [
        {
            'company': 'Tech Solutions Inc.',
            'role': 'Senior Software Engineer',
            'duration': '2020 - Present',
            'description': 'Led the development of a cloud-native platform. Mentored junior engineers and improved CI/CD pipeline efficiency by 30%.'
        },
        {
            'company': 'Web Crafters LLC',
            'role': 'Full-Stack Developer',
            'duration': '2018 - 2020',
            'description': 'Developed and maintained client websites and web applications using the MERN stack. Collaborated with designers to create responsive and user-friendly interfaces.'
        }
    ]

    for work in work_experience:
        cursor.execute("INSERT INTO work_experience (company, role, duration, description) VALUES (?, ?, ?, ?)",
                       (work['company'], work['role'], work['duration'], work['description']))

    conn.commit()
    conn.close()
    print("Database seeded with sample data.")

if __name__ == '__main__':
    seed_data()
