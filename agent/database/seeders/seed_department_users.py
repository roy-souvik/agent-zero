def run(conn):
    dept = conn.execute("SELECT id FROM departments WHERE name = ?", ('Engineering',)).fetchone()
    user = conn.execute("SELECT id FROM users WHERE email = ?", ('alice@example.com',)).fetchone()
    if dept and user:
        conn.execute('INSERT OR IGNORE INTO department_users (department_id, user_id) VALUES (?, ?)', (dept['id'], user['id']))
        conn.commit()
