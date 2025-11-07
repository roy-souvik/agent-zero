from .base_model import BaseModel

class UserModel(BaseModel):
    table = 'users'
    fields = ['id', 'name', 'email', 'password', 'created_at', 'updated_at']


    def find_by_email(self, email):
        cur = self.conn.execute('SELECT * FROM users WHERE email = ?', (email,))
        r = cur.fetchone()

        return dict(r) if r else None