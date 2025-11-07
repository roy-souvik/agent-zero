import hashlib

def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def run(conn):
    conn.execute(
        "INSERT OR IGNORE INTO users (id, name, email, password) VALUES (1, ?, ?, ?)",
        ('Root User', 'root@example.com', _hash('rootpass'))
    )
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Alice', 'alice@example.com', _hash('alice123')))
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Bob', 'bob@example.com', _hash('bob123')))
    conn.commit()
