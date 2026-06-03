import flet as ft
from db import db, _hash_password

# ── глобальные переменные ──────────────────────────────────────────────────────
user_role = 0  # 0-гость, 1-клиент, 2-менеджер, 3-администратор
user_name = ""
id_update = None  # id редактируемой записи (товар или заказ)


def main(page: ft.Page):
    page.title = "Обувной магазин"
    page.theme_mode = ft.ThemeMode.LIGHT

    global user_role, user_name, id_update

    # ── поля авторизации ───────────────────────────────────────────────────────
    login_tf = ft.TextField(label="Логин", width=400)
    password_tf = ft.TextField(label="Пароль", password=True, width=400)
    error_txt = ft.Text(color=ft.colors.RED)

    # ── поля товара ────────────────────────────────────────────────────────────
    t_article = ft.TextField(label="Артикул", width=350)
    t_name = ft.TextField(label="Наименование", width=350)
    t_unit = ft.TextField(label="Ед. измерения", width=350)
    t_price = ft.TextField(label="Цена", width=350)
    t_supplier = ft.TextField(label="Поставщик", width=350)
    t_manuf = ft.TextField(label="Производитель", width=350)
    t_category = ft.TextField(label="Категория", width=350)
    t_discount = ft.TextField(label="Скидка %", width=350)
    t_count = ft.TextField(label="Кол-во на складе", width=350)
    t_desc = ft.TextField(label="Описание", width=350)
    t_img = ft.TextField(label="Фото (путь)", width=350)
    product_fields = [
        t_article,
        t_name,
        t_unit,
        t_price,
        t_supplier,
        t_manuf,
        t_category,
        t_discount,
        t_count,
        t_desc,
        t_img,
    ]

    # ── поля заказа ────────────────────────────────────────────────────────────
    o_number = ft.TextField(label="Номер заказа", width=350)
    o_article = ft.TextField(label="Артикул заказа", width=350)
    o_date_o = ft.TextField(label="Дата заказа", width=350)
    o_date_d = ft.TextField(label="Дата доставки", width=350)
    o_pick = ft.TextField(label="ID пункта выдачи", width=350)
    o_client = ft.TextField(label="ФИО клиента", width=350)
    o_code = ft.TextField(label="Код получения", width=350)
    o_status = ft.TextField(label="Статус", width=350)
    order_fields = [
        o_number,
        o_article,
        o_date_o,
        o_date_d,
        o_pick,
        o_client,
        o_code,
        o_status,
    ]

    # ── поиск / фильтры ────────────────────────────────────────────────────────
    search_tf = ft.TextField(
        label="Поиск", width=300, on_change=lambda e: reload_products()
    )
    sort_asc = ft.Checkbox(label="По кол-ву ↑", on_change=lambda e: reload_products())
    sort_desc = ft.Checkbox(label="По кол-ву ↓", on_change=lambda e: reload_products())
    filter_dd = ft.Dropdown(
        label="Поставщик", width=200, on_change=lambda e: reload_products()
    )

    product_list = ft.ListView(width=820, height=700, auto_scroll=False)
    order_list = ft.ListView(width=820, height=700, auto_scroll=False)

    # ══════════════════════════════════════════════════════════════════════════
    #  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # ══════════════════════════════════════════════════════════════════════════

    def clear_fields(fields):
        for f in fields:
            f.value = ""

    def show_alert(msg):
        """Простое всплывающее сообщение об ошибке"""
        dlg = ft.AlertDialog(
            title=ft.Text("Ошибка"),
            content=ft.Text(msg),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dlg(dlg))],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(dlg):
        dlg.open = False
        page.update()

    def confirm_dialog(msg, on_yes):
        """Диалог подтверждения опасного действия"""
        dlg = ft.AlertDialog(
            title=ft.Text("Подтверждение"),
            content=ft.Text(msg),
            actions=[
                ft.TextButton("Да", on_click=lambda e: [close_dlg(dlg), on_yes()]),
                ft.TextButton("Нет", on_click=lambda e: close_dlg(dlg)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # ══════════════════════════════════════════════════════════════════════════
    #  ТОВАРЫ
    # ══════════════════════════════════════════════════════════════════════════

    def get_filtered_products():
        """Возвращает список товаров с учётом поиска, фильтра и сортировки"""
        query = ""
        conditions = []
        s = (search_tf.value or "").strip()
        if s:
            # поиск по всем текстовым полям одновременно
            like = f"'%{s}%'"
            conditions.append(
                f"(LOWER(article||' '||name||' '||supplier||' '||manufacturer"
                f"||' '||category||' '||description) LIKE LOWER({like}))"
            )
        sv = filter_dd.value or "Все поставщики"
        if sv != "Все поставщики":
            conditions.append(f"supplier = '{sv}'")
        if conditions:
            query = "WHERE " + " AND ".join(conditions)

        products = db.Table.get(db, "products", request=query)

        # сортировка по количеству
        if sort_asc.value:
            products = sorted(products, key=lambda p: int(p[9] or 0))
        elif sort_desc.value:
            products = sorted(products, key=lambda p: int(p[9] or 0), reverse=True)
        return products

    def build_product_card(p):
        """Строит карточку товара"""
        pid = p[0]
        name = p[2] or "—"
        price = float(p[4] or 0)
        discount = int(p[8] or 0)
        count = int(p[9] or 0)
        supplier = p[5] or ""

        # цвет фона
        bg = None
        if count == 0:
            bg = ft.colors.BLUE_100
        elif discount > 15:
            bg = "#2E8B57"

        # цена со скидкой
        if discount > 0:
            final_price = price * (100 - discount) / 100
            price_row = ft.Row(
                [
                    ft.Text(
                        f"{price} руб.",
                        color=ft.colors.RED,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH),
                    ),
                    ft.Text(f"{final_price:.2f} руб."),
                ]
            )
        else:
            price_row = ft.Text(f"{price} руб.")

        # фото
        img_src = p[11] if p[11] and p[11] != "nan" else "picture.png"
        photo = ft.Image(
            src=f"import/{img_src}",
            width=120,
            height=120,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Image(src="import/picture.png", width=120, height=120),
        )

        # кнопки только для администратора
        edit_btn = (
            ft.IconButton(
                ft.icons.EDIT, on_click=lambda e, i=pid: load_product_for_edit(i)
            )
            if user_role == 3
            else ft.Text("")
        )
        del_btn = (
            ft.IconButton(
                ft.icons.DELETE,
                icon_color=ft.colors.RED,
                on_click=lambda e, i=pid: confirm_dialog(
                    "Удалить товар?", lambda: delete_product(i)
                ),
            )
            if user_role == 3
            else ft.Text("")
        )

        return ft.Card(
            content=ft.Container(
                bgcolor=bg,
                padding=10,
                content=ft.Row(
                    [
                        photo,
                        ft.Column(
                            [
                                ft.Text(f"{p[7]} | {name}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Описание: {p[10]}"),
                                ft.Text(f"Производитель: {p[6]}"),
                                ft.Text(f"Поставщик: {supplier}"),
                                price_row,
                                ft.Text(f"Ед. изм.: {p[3]}"),
                                ft.Text(f"Кол-во на складе: {count}"),
                            ],
                            expand=True,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    f"Скидка: {discount}%",
                                    color=ft.colors.GREEN,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                edit_btn,
                                del_btn,
                            ]
                        ),
                    ],
                    spacing=10,
                ),
            ),
            margin=5,
        )

    def reload_products():
        product_list.controls.clear()
        for p in get_filtered_products():
            product_list.controls.append(build_product_card(p))
        page.update()

    def refresh_supplier_filter():
        """Обновляет выпадающий список поставщиков"""
        suppliers = set(p[5] for p in db.Table.get(db, "products") if p[5])
        filter_dd.options = [ft.dropdown.Option("Все поставщики")] + [
            ft.dropdown.Option(s) for s in sorted(suppliers)
        ]
        filter_dd.value = "Все поставщики"

    def load_product_for_edit(pid):
        global id_update
        p = db.Table.get(db, "products", request=f"WHERE id = {pid}")
        if not p:
            return
        p = p[0]
        id_update = pid
        for i, f in enumerate(product_fields):
            f.value = str(p[i + 1]) if p[i + 1] is not None else ""
        page.update()

    def save_product(e):
        global id_update
        # валидация
        if not t_name.value.strip():
            show_alert("Введите наименование товара.")
            return
        try:
            price = float(t_price.value)
            if price < 0:
                raise ValueError
        except ValueError:
            show_alert("Цена должна быть числом >= 0.")
            return
        try:
            count = int(t_count.value)
            if count < 0:
                raise ValueError
        except ValueError:
            show_alert("Количество должно быть целым числом >= 0.")
            return

        vals = [f.value for f in product_fields]
        if id_update:
            db.Table.update(db, "products", f"id = {id_update}", *vals)
            id_update = None
        else:
            db.Table.write(db, "products", *vals)
        clear_fields(product_fields)
        refresh_supplier_filter()
        reload_products()

    def delete_product(pid):
        # нельзя удалять товар из заказа
        orders = db.Table.get(db, "orders")
        articles_in_orders = [o[2] for o in orders]
        product = db.Table.get(db, "products", request=f"WHERE id = {pid}")
        if product and product[0][1] in articles_in_orders:
            show_alert("Нельзя удалить товар, который есть в заказах.")
            return
        db.Table.delete(db, "products", f"id = {pid}")
        refresh_supplier_filter()
        reload_products()

    # ══════════════════════════════════════════════════════════════════════════
    #  ЗАКАЗЫ
    # ══════════════════════════════════════════════════════════════════════════

    o_search = ft.TextField(
        label="Поиск по заказам", width=300, on_change=lambda e: reload_orders()
    )

    def get_filtered_orders():
        s = (o_search.value or "").strip()
        if s:
            like = f"'%{s}%'"
            q = (
                f"WHERE LOWER(article||' '||status||' '||client"
                f"||' '||date_order||' '||date_delivery) LIKE LOWER({like})"
            )
        else:
            q = ""
        return db.Table.get(db, "orders", request=q)

    def pick_address(pick_id):
        """Возвращает текстовый адрес пункта выдачи по id"""
        try:
            rows = db.Table.get(db, "pick", request=f"WHERE id = {int(pick_id)}")
            return rows[0][1] if rows else str(pick_id)
        except Exception:
            return str(pick_id)

    def build_order_card(o):
        oid = o[0]
        article = o[2] or "—"
        status = o[8] or "—"
        address = pick_address(o[5])
        date_o = o[3] or "—"
        date_d = o[4] or "—"

        edit_btn = (
            ft.IconButton(
                ft.icons.EDIT, on_click=lambda e, i=oid: load_order_for_edit(i)
            )
            if user_role == 3
            else ft.Text("")
        )
        del_btn = (
            ft.IconButton(
                ft.icons.DELETE,
                icon_color=ft.colors.RED,
                on_click=lambda e, i=oid: confirm_dialog(
                    "Удалить заказ?", lambda: delete_order(i)
                ),
            )
            if user_role == 3
            else ft.Text("")
        )

        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(article, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Статус: {status}"),
                                ft.Text(f"Адрес: {address}"),
                                ft.Text(f"Дата заказа: {date_o}"),
                            ],
                            expand=True,
                        ),
                        ft.Column(
                            [
                                ft.Text(f"Дата доставки: {date_d}"),
                                edit_btn,
                                del_btn,
                            ]
                        ),
                    ]
                ),
            ),
            margin=5,
        )

    def reload_orders():
        order_list.controls.clear()
        for o in get_filtered_orders():
            order_list.controls.append(build_order_card(o))
        page.update()

    def load_order_for_edit(oid):
        global id_update
        o = db.Table.get(db, "orders", request=f"WHERE id = {oid}")
        if not o:
            return
        o = o[0]
        id_update = oid
        fields_vals = [o[1], o[2], o[3], o[4], o[5], o[6], o[7], o[8]]
        for i, f in enumerate(order_fields):
            f.value = str(fields_vals[i]) if fields_vals[i] is not None else ""
        page.update()

    def save_order(e):
        global id_update
        if not o_article.value.strip():
            show_alert("Введите артикул заказа.")
            return
        vals = [f.value for f in order_fields]
        if id_update:
            db.Table.update(db, "orders", f"id = {id_update}", *vals)
            id_update = None
        else:
            db.Table.write(db, "orders", *vals)
        clear_fields(order_fields)
        reload_orders()

    def delete_order(oid):
        db.Table.delete(db, "orders", f"id = {oid}")
        reload_orders()

    # ══════════════════════════════════════════════════════════════════════════
    #  МАРШРУТЫ
    # ══════════════════════════════════════════════════════════════════════════

    def route_change(route):
        global user_role, user_name, id_update
        page.views.clear()
        id_update = None

        # ── /log — экран входа ─────────────────────────────────────────────
        if page.route == "/log":
            login_tf.value = ""
            password_tf.value = ""
            error_txt.value = ""
            user_role = 0
            user_name = ""

            def do_login(e):
                global user_role, user_name
                row = db.Table.get(
                    db,
                    "users",
                    "role, full_name",
                    f"WHERE login = '{login_tf.value}' AND "
                    f"password = '{_hash_password(password_tf.value)}'",
                )
                if row:
                    role_str = row[0][0]
                    user_name = row[0][1]
                    if role_str == "Администратор":
                        user_role = 3
                    elif role_str == "Менеджер":
                        user_role = 2
                    else:
                        user_role = 1  # авторизованный клиент
                    page.go("/products")
                else:
                    error_txt.value = "Неверный логин или пароль"
                    page.update()

            page.views.append(
                ft.View(
                    "/log",
                    controls=[
                        ft.Column(
                            [
                                ft.Text(
                                    "Обувной магазин",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text("Вход в систему", size=18),
                                login_tf,
                                password_tf,
                                error_txt,
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Войти", on_click=do_login),
                                        ft.ElevatedButton(
                                            "Войти как гость",
                                            on_click=lambda e: page.go("/products"),
                                        ),
                                    ]
                                ),
                            ],
                            spacing=15,
                        ),
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        # ── /products — список товаров ─────────────────────────────────────
        elif page.route == "/products":
            refresh_supplier_filter()
            reload_products()

            # сортировка и фильтр — только менеджер и админ
            filter_row = ft.Row(
                [search_tf, sort_asc, sort_desc, filter_dd], visible=(user_role >= 2)
            )

            # форма добавления/редактирования — только администратор
            form_col = ft.Column(
                [
                    ft.Text(
                        "Добавить / Редактировать товар", weight=ft.FontWeight.BOLD
                    ),
                    *product_fields,
                    ft.Row(
                        [
                            ft.ElevatedButton("Сохранить", on_click=save_product),
                            ft.ElevatedButton(
                                "Очистить",
                                on_click=lambda e: [
                                    clear_fields(product_fields),
                                    setattr(globals(), "id_update", None),
                                    page.update(),
                                ],
                            ),
                        ]
                    ),
                ],
                visible=(user_role == 3),
                scroll=ft.ScrollMode.AUTO,
                width=370,
            )

            # кнопка «Заказы» — менеджер и админ
            orders_btn = ft.ElevatedButton(
                "Заказы",
                on_click=lambda e: page.go("/orders"),
                visible=(user_role >= 2),
            )

            page.views.append(
                ft.View(
                    "/products",
                    controls=[
                        ft.Row(
                            [
                                ft.Text(
                                    f"ФИО: {user_name}" if user_name else "Гость",
                                    expand=True,
                                ),
                                orders_btn,
                                ft.ElevatedButton(
                                    "Выйти", on_click=lambda e: page.go("/log")
                                ),
                            ]
                        ),
                        filter_row,
                        ft.Row(
                            [
                                ft.Column([product_list], expand=True),
                                form_col,
                            ],
                            expand=True,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        # ── /orders — список заказов ───────────────────────────────────────
        elif page.route == "/orders":
            reload_orders()

            form_col = ft.Column(
                [
                    ft.Text(
                        "Добавить / Редактировать заказ", weight=ft.FontWeight.BOLD
                    ),
                    *order_fields,
                    ft.Row(
                        [
                            ft.ElevatedButton("Сохранить", on_click=save_order),
                            ft.ElevatedButton(
                                "Очистить",
                                on_click=lambda e: [
                                    clear_fields(order_fields),
                                    page.update(),
                                ],
                            ),
                        ]
                    ),
                ],
                visible=(user_role == 3),
                scroll=ft.ScrollMode.AUTO,
                width=370,
            )

            page.views.append(
                ft.View(
                    "/orders",
                    controls=[
                        ft.Row(
                            [
                                ft.Text("Заказы", size=22, expand=True),
                                ft.ElevatedButton(
                                    "Назад", on_click=lambda e: page.go("/products")
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Column([o_search, order_list], expand=True),
                                form_col,
                            ],
                            expand=True,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go("/log")


ft.app(main)
