import sqlite3
from faker import Faker
import random

fake = Faker()

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL UNIQUE
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        status_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY (status_id) REFERENCES status(id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    
    cursor.execute('''
    INSERT OR IGNORE INTO status (name) VALUES 
        ('new'),
        ('in progress'),
        ('completed');
    ''')

def seed_users(n):
    for _ in range(n):
        fullname = fake.name()
        email = fake.unique.email()
        cursor.execute("INSERT INTO users (fullname, email) VALUES (?, ?)", (fullname, email))

def seed_tasks(n):
    user_ids = [row[0] for row in cursor.execute("SELECT id FROM users").fetchall()]
    status_ids = [row[0] for row in cursor.execute("SELECT id FROM status").fetchall()]
    for _ in range(n):
        title = fake.sentence(nb_words=6)
        description = fake.text(max_nb_chars=200)
        status_id = random.choice(status_ids)
        user_id = random.choice(user_ids)
        cursor.execute("INSERT INTO tasks (title, description, status_id, user_id) VALUES (?, ?, ?, ?)", 
                       (title, description, status_id, user_id))

def seed_database():
    create_tables()
    seed_users(10)
    seed_tasks(30)
    conn.commit()

def get_tasks_by_user(user_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def get_tasks_by_status(status_name):
    cursor.execute('''
        SELECT * FROM tasks WHERE status_id = (
            SELECT id FROM status WHERE name = ?
        )
    ''', (status_name,))
    return cursor.fetchall()

def update_task_status(task_id, new_status):
    cursor.execute('''
        UPDATE tasks SET status_id = (
            SELECT id FROM status WHERE name = ?
        ) WHERE id = ?
    ''', (new_status, task_id))
    conn.commit()

def get_users_without_tasks():
    cursor.execute('''
        SELECT * FROM users WHERE id NOT IN (
            SELECT user_id FROM tasks
        )
    ''')
    return cursor.fetchall()

def add_task_for_user(title, description, status_name, user_id):
    cursor.execute('''
        INSERT INTO tasks (title, description, status_id, user_id)
        VALUES (?, ?, (SELECT id FROM status WHERE name = ?), ?)
    ''', (title, description, status_name, user_id))
    conn.commit()

def get_incomplete_tasks():
    cursor.execute('''
        SELECT * FROM tasks WHERE status_id != (
            SELECT id FROM status WHERE name = 'completed'
        )
    ''')
    return cursor.fetchall()

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

def find_users_by_email(email_pattern):
    cursor.execute("SELECT * FROM users WHERE email LIKE ?", (email_pattern,))
    return cursor.fetchall()

def update_user_name(user_id, new_name):
    cursor.execute("UPDATE users SET fullname = ? WHERE id = ?", (new_name, user_id))
    conn.commit()

def count_tasks_by_status():
    cursor.execute('''
        SELECT status.name, COUNT(tasks.id) 
        FROM tasks 
        JOIN status ON tasks.status_id = status.id 
        GROUP BY status.name
    ''')
    return cursor.fetchall()

def get_tasks_by_user_email_domain(domain):
    cursor.execute('''
        SELECT tasks.* FROM tasks 
        JOIN users ON tasks.user_id = users.id 
        WHERE users.email LIKE ?
    ''', ('%' + domain,))
    return cursor.fetchall()

def get_tasks_without_description():
    cursor.execute("SELECT * FROM tasks WHERE description IS NULL")
    return cursor.fetchall()

def get_users_and_tasks_in_progress():
    cursor.execute('''
        SELECT users.*, tasks.* FROM users 
        JOIN tasks ON users.id = tasks.user_id 
        WHERE tasks.status_id = (SELECT id FROM status WHERE name = 'in progress')
    ''')
    return cursor.fetchall()

def count_tasks_per_user():
    cursor.execute('''
        SELECT users.fullname, COUNT(tasks.id) 
        FROM users 
        LEFT JOIN tasks ON users.id = tasks.user_id 
        GROUP BY users.fullname
    ''')
    return cursor.fetchall()

if __name__ == '__main__':
    seed_database()
    
    print(get_tasks_by_user(1))
    
    print(get_tasks_by_status('new'))
    
    update_task_status(1, 'in progress')
    
    print(get_users_without_tasks())
    
    add_task_for_user('Новое задание', 'Описание задания', 'new', 1)
    
    print(get_incomplete_tasks())
    
    delete_task(1)
    
    print(find_users_by_email('%@example.com'))
    
    update_user_name(1, 'Новое Имя')
    
    print(count_tasks_by_status())
    
    print(get_tasks_by_user_email_domain('example.com'))
    
    print(get_tasks_without_description())
    
    print(get_users_and_tasks_in_progress())
    
    print(count_tasks_per_user())
    
    conn.close()
