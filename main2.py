import flet as ft
from db import db, _hash_password

role = 0  # 0-гость, 1-клиент, 2-менеджер, 3-админ
uname = ""
edit_id = None


def main(page: ft.Page):
    global role, uname, edit_id
    page.title = "Обувной магазин"

    login = ft.TextField(label="Логин", width=350)
    pwd = ft.TextField(label="Пароль", password=True, width=350)
    err = ft.Text(color=ft.colors.RED)
    search = ft.TextField(label="Поиск", width=300)
    plist = ft.ListView(width=780, height=600)
    olist = ft.ListView(width=780, height=600)
    # 11 текстовых полей создание
    # ==
    # tf = ft.TextField(label="арт")

    tf = {
        k: ft.TextField(label=k, width=330)
        for k in [
            "Артикул",
            "Название",
            "Ед.изм",
            "Цена",
            "Поставщик",
            "Производитель",
            "Категория",
            "Скидка",
            "Кол-во",
            "Описание",
            "Фото",
        ]
    }
    of = {
        k: ft.TextField(label=k, width=330)
        for k in [
            "Номер",
            "Артикул",
            "Дата заказа",
            "Дата доставки",
            "Пункт выдачи",
            "Клиент",
            "Код",
            "Статус",
        ]
    }
    # 1. Очистить список
    # 2. Получить товары из БД
    # 3. Перебрать их циклом
    # 4. Создать карточки
    # 5. Вывести на экран

    def load_products(e=None):
        plist.controls.clear()
        s = (search.value or "").lower()
        for p in db.Table.get(db, "products"):
            # [
            #  [1,'A01','Кроссовки',...],
            #  [2,'A02','Ботинки',...]
            # ]
            if s and s not in " ".join(str(x) for x in p).lower():
                continue
            count, discount, price = int(p[9] or 0), int(p[8] or 0), float(p[4] or 0)

            if count == 0:
                bg = ft.colors.BLUE

            elif discount > 15:
                bg = "#2E8B57"

            else:
                bg = None

            pw = (
                ft.Row(
                    [
                        ft.Text(
                            f"{price}р.",
                            color=ft.colors.RED,
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH
                            ),
                        ),
                        ft.Text(f"{price*(100-discount)/100:.2f}р."),
                    ]
                )
                if discount > 0
                else ft.Text(f"{price}р.")
            )
            btns = (
                ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.EDIT,
                            on_click=lambda e, i=p[0], v=p[1:]: load_edit(
                                i, list(tf.values()), v
                            ),
                        ),
                        ft.IconButton(
                            ft.icons.DELETE, on_click=lambda e, i=p[0]: del_product(i)
                        ),
                    ]
                )
                if role == 3
                else ft.Text("")
            )
            plist.controls.append(
                ft.Card(
                    ft.Container(
                        bgcolor=bg,
                        padding=8,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{p[7]} | {p[2]}",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"Поставщик: {p[5]}   Производитель: {p[6]}"
                                        ),
                                        pw,
                                        ft.Text(
                                            f"Кол-во: {count}   Скидка: {discount}%"
                                        ),
                                    ],
                                    expand=True,
                                ),
                                btns,
                            ]
                        ),
                    )
                )
            )
        page.update()

    def load_orders(e=None):
        olist.controls.clear()
        for o in db.Table.get(db, "orders"):
            btns = (
                ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.EDIT,
                            on_click=lambda e, i=o[0], v=o[1:]: load_edit(
                                i, list(of.values()), v
                            ),
                        ),
                        ft.IconButton(
                            ft.icons.DELETE,
                            on_click=lambda e, i=o[0]: [
                                db.Table.delete(db, "orders", f"id={i}"),
                                load_orders(),
                            ],
                        ),
                    ]
                )
                if role == 3
                else ft.Text("")
            )
            olist.controls.append(
                ft.Card(
                    ft.Container(
                        padding=8,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"Артикул: {o[2]}",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(f"Статус: {o[8]}   Пункт: {o[5]}"),
                                        ft.Text(
                                            f"Дата заказа: {o[3]}   Доставка: {o[4]}"
                                        ),
                                    ],
                                    expand=True,
                                ),
                                btns,
                            ]
                        ),
                    )
                )
            )
        page.update()

    def load_edit(pid, fields, vals):
        global edit_id
        edit_id = pid
        for i, f in enumerate(fields):
            f.value = str(vals[i]) if i < len(vals) else ""
        page.update()

    def save(table, fields, loader):
        global edit_id
        vals = [f.value for f in fields]
        if edit_id:
            db.Table.update(db, table, f"id={edit_id}", *vals)
            edit_id = None
        else:
            db.Table.write(db, table, *vals)
        [setattr(f, "value", "") for f in fields]
        loader()

    def del_product(pid):
        arts = [o[2] for o in db.Table.get(db, "orders")]
        p = db.Table.get(db, "products", request=f"WHERE id={pid}")
        if p and p[0][1] in arts:
            err.value = "Товар есть в заказе — удалить нельзя"
            page.update()
            return
        db.Table.delete(db, "products", f"id={pid}")
        load_products()

    def do_login(e):
        global role, uname
        row = db.Table.get(
            db,
            "users",
            "role,full_name",
            f"WHERE login='{login.value}' AND password='{_hash_password(pwd.value)}'",
        )
        if not row:
            err.value = "Неверный логин или пароль"
            page.update()
            return
        uname = row[0][1]
        role = {"Администратор": 3, "Менеджер": 2}.get(row[0][0], 1)
        page.go("/products")

    def route_change(e):
        global edit_id
        page.views.clear()
        edit_id = None

        if page.route == "/log":
            login.value = pwd.value = err.value = ""
            page.views.append(
                ft.View(
                    "/log",
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [
                                ft.Text("Вход", size=28),
                                login,
                                pwd,
                                err,
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Войти", on_click=do_login),
                                        ft.ElevatedButton(
                                            "Гость",
                                            on_click=lambda e: page.go("/products"),
                                        ),
                                    ]
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                )
            )

        elif page.route == "/products":
            search.on_change = load_products
            load_products()
            form = ft.Column(
                [
                    ft.Text("Товар", weight=ft.FontWeight.BOLD),
                    *tf.values(),
                    ft.ElevatedButton(
                        "Сохранить",
                        on_click=lambda e: save(
                            "products", list(tf.values()), load_products
                        ),
                    ),
                ],
                visible=(role == 3),
                width=350,
                scroll=ft.ScrollMode.AUTO,
            )
            page.views.append(
                ft.View(
                    "/products",
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row(
                            [
                                ft.Text(uname or "Гость", expand=True),
                                ft.ElevatedButton(
                                    "Заказы",
                                    on_click=lambda e: page.go("/orders"),
                                    visible=(role >= 2),
                                ),
                                ft.ElevatedButton(
                                    "Выйти", on_click=lambda e: page.go("/log")
                                ),
                            ]
                        ),
                        search if role >= 2 else ft.Text(""),
                        ft.Row([ft.Column([plist], expand=True), form]),
                    ],
                )
            )

        elif page.route == "/orders":
            load_orders()
            form = ft.Column(
                [
                    ft.Text("Заказ", weight=ft.FontWeight.BOLD),
                    *of.values(),
                    ft.ElevatedButton(
                        "Сохранить",
                        on_click=lambda e: save(
                            "orders", list(of.values()), load_orders
                        ),
                    ),
                ],
                visible=(role == 3),
                width=350,
                scroll=ft.ScrollMode.AUTO,
            )
            page.views.append(
                ft.View(
                    "/orders",
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row(
                            [
                                ft.Text("Заказы", size=22, expand=True),
                                ft.ElevatedButton(
                                    "Назад", on_click=lambda e: page.go("/products")
                                ),
                            ]
                        ),
                        ft.Row([ft.Column([olist], expand=True), form]),
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go("/log")


ft.app(main)
