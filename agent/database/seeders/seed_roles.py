def run(conn):
    roles = ['admin', 'manager', 'employee']
    for r in roles:
        conn.execute('INSERT OR IGNORE INTO roles (name) VALUES (?)', (r,))
    conn.commit()
