def run(conn):
    # Root User → Admin
    cur_user = conn.execute("SELECT id FROM users WHERE email = ?", ('root@example.com',)).fetchone()
    cur_role = conn.execute("SELECT id FROM roles WHERE name = ?", ('admin',)).fetchone()
    if cur_user and cur_role:
        conn.execute('INSERT OR IGNORE INTO user_roles (user_id, role_id, company_id) VALUES (?, ?, ?)', (cur_user['id'], cur_role['id'], 1))

    # Alice → Employee
    cur_user = conn.execute("SELECT id FROM users WHERE email = ?", ('alice@example.com',)).fetchone()
    cur_role = conn.execute("SELECT id FROM roles WHERE name = ?", ('employee',)).fetchone()
    if cur_user and cur_role:
        conn.execute('INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)', (cur_user['id'], cur_role['id']))
    conn.commit()
