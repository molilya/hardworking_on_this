import database_creatorplus as dc
import pandas as pd
import hashlib

db=dc.Database("DB")

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

db.Table.create(db, "users",
                ["id", "role", "full_name", "login", "password"],
                ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT", "TEXT"])
db.Table.create(db, "products",
                ["id", "erticle", "name", "unit", "price", "supplier", "manufacturer", "category", "discount", "count", "description", "image_path"],
                ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT"])
db.Table.create(db, "pick",
                ["id", "pick"],
                ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT"])
db.Table.create(db, "orders",
                ["id", "nuber_order", "article", "date_order", "date_delivery", "pick", "client", "code", "status"],
                ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT"])

def import_data(path, table_name):
    data=pd.read_excel(path)
    for row in data.values:
        db.Table.write(db, table_name, *row)

def add_test_users():
    users = db.Table.get(db, "users")
    if not users:
        db.Table.write(db, "users", "Администратор", "Иванов Иван", "admin", _hash_password("admin"))
        db.Table.write(db, "users", "Менеджер", "Петров Петр", "manager", _hash_password("manager"))
        db.Table.write(db, "users", "Авторизованный пользователь", "Сидорова Анна", "user", _hash_password("user"))
        print("Пользователи добавлены")
    
add_test_users()