import database_creatorplus as dc
import pandas as pd
import hashlib

db = dc.Database("DB")


def _hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()


# Создание таблиц
db.Table.create(
    db,
    "users",
    ["id", "role", "full_name", "login", "password"],
    ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT", "TEXT"],
)

db.Table.create(
    db,
    "products",
    [
        "id",
        "article",
        "name",
        "unit",
        "price",
        "supplier",
        "manufacturer",
        "category",
        "discount",
        "count",
        "description",
        "image_path",
    ],
    [
        "INTEGER PRIMARY KEY AUTOINCREMENT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
    ],
)

db.Table.create(
    db, "pick", ["id", "pick"], ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT"]
)

db.Table.create(
    db,
    "orders",
    [
        "id",
        "number_order",
        "article",
        "date_order",
        "date_delivery",
        "pick",
        "client",
        "code",
        "status",
    ],
    [
        "INTEGER PRIMARY KEY AUTOINCREMENT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
        "TEXT",
    ],
)


def import_data(path, table_name):
    """Импорт данных из Excel в таблицу БД"""
    data = pd.read_excel(path, engine="openpyxl")
    for row in data.values:
        db.Table.write(db, table_name, *row)


def init_db():
    """Первичная загрузка данных если БД пустая"""
    # Импорт пунктов выдачи
    if not db.Table.get(db, "pick"):
        import_data("pick.xlsx", "pick")

    # Импорт товаров
    if not db.Table.get(db, "products"):
        import_data("products.xlsx", "products")

    # Импорт заказов
    if not db.Table.get(db, "orders"):
        import_data("orders.xlsx", "orders")

    # Импорт пользователей с хешированием пароля
    if not db.Table.get(db, "users"):
        data = pd.read_excel("users.xlsx", engine="openpyxl")
        for row in data.values:
            role, full_name, login, password = row
            db.Table.write(
                db, "users", role, full_name, login, _hash_password(password)
            )


init_db()
