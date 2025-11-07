from db.connection import get_connection
from models.user import UserModel
from models.company_user import CompanyUserModel
from models.user_role import UserRoleModel

conn = get_connection()
users = UserModel(conn)

# 🟢 CREATE
new_user_id = users.insert({
    'name': 'Charlie',
    'email': 'charlie@example.com',
    'password': 'hashed_pw_123'
})
print("New user created:", users.find(new_user_id))

# 🟡 READ
all_users = users.all()
print("All Users:", all_users)

# 🔵 UPDATE
users.update(new_user_id, {'name': 'Charlie Brown'})
print("Updated:", users.find(new_user_id))

# 🔴 DELETE
users.delete(new_user_id)
print("After delete:", users.find(new_user_id))

# 📎 Check user roles
user_roles = UserRoleModel(conn).for_user(1)
print("Roles for Root User:", user_roles)

# 🏢 Check company users
company_users = CompanyUserModel(conn).for_company(2)
print("Company users for Acme Corp:", company_users)
