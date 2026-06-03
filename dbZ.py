import database_creatorplus as dc
import pandas as pd
import hashlib

db = dc.Database("DB")

def import_data(path,table_name):
    data = pd.read_excel(path, engine='openpyxl')
    for data in data.values:
        db.Table.write(db,table_name,*data)

db.Table.create(db,"users",
    [
        "id","role","full_name","login","password"
    ],
    [
        "INTEGER PRIMARY KEY AUTOINCREMENT","TEXT","TEXT","TEXT","TEXT"
    ]
)
db.Table.create(db,"products",
    [
        "id","erticle","name","unit","price","supplier","manufacturer","category",
        "discount","count","description","image_path"
    ],
    [
        "INTEGER PRIMARY KEY ","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT",
        "TEXT","TEXT","TEXT","TEXT"
    ]
)
db.Table.create(db,"pick",["id","pick"],["INTEGER PRIMARY KEY ","TEXT"])
db.Table.create(db,"orders",
    [
        "id","nuber_order","article","date_order","date_delivery","pick","client","code","status"
    ],
    [
        "INTEGER PRIMARY KEY ","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT"
    ]
)

def _hash_password(password): #функция хеширования пароля
    return hashlib.sha256(password.encode()).hexdigest()

import_data("users.xlsx","users")
import_data("pick.xlsx","pick")
import_data("orders.xlsx","orders")
import_data("products.xlsx","products")