def run(conn):
    cur = conn.execute("SELECT id FROM companies WHERE name = ?", ('Acme Corp',))
    company = cur.fetchone()
    if not company:
        return
    cid = company['id']

    users = conn.execute("SELECT id, email FROM users").fetchall()
    for user in users:
        role = 'employee' if 'alice' in user['email'] or 'bob' in user['email'] else 'admin'
        conn.execute('INSERT OR IGNORE INTO company_users (company_id, user_id, role) VALUES (?, ?, ?)', (cid, user['id'], role))
    conn.commit()
