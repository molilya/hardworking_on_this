import flet as ft
from db import db, _hash_password


def main(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO
    login = ft.TextField(label="Логин")
    password = ft.TextField(label="Пароль", password=True)
    error = ft.Text(color=ft.colors.RED)
    name = ft.TextField(label="Название")
    price = ft.TextField(label="Цена")
    count = ft.TextField(label="Количество")
    discount = ft.TextField(label="Скидка %")
    supplier = ft.TextField(label="Поставщик")
    search = ft.TextField(label="Поиск")
    products = ft.Column()
    pick = ft.Column()
    role = "Гость"

    def load():
        products.controls.clear()
        all_products = db.Table.get(db, "products")
        if search.value:
            search_lower = search.value.lower()
            all_products = [
                p for p in all_products if search_lower in (p[2] or "").lower()]
        for p in all_products:
            delete_btn = ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED,
                                       on_click=lambda e, pid=p[0]: delete_product(pid)) if role == "admin" else ft.Text("")
            products.controls.append(ft.Card(ft.Container(
                ft.Row([
                    ft.Column([
                        ft.Text(p[2] or "Без названия",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(f"{p[4]} руб."),
                        ft.Text(f"Остаток: {p[9] or 0}"),
                        ft.Text(f"Скидка: {p[8] or 0}%"),
                    ], expand=True),
                    delete_btn,
                ]), padding=15)))
        page.update()

    def load_pick():
        pick.controls.clear()
        all_picks = db.Table.get(db, "pick")
        if search.value:
            search_lower = search.value.lower()
            all_picks = [p for p in all_picks if search_lower in (
                p[2] or "").lower()]
        for p in all_picks:
            delete_btn = ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED,
                                       on_click=lambda e, pid=p[0]: delete_pick(pid)) if role == "admin" else ft.Text("")

            pick.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Row
                                (
                                    [
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    p[0] or "Id", weight=ft.FontWeight.BOLD),
                                                ft.Text(f"{p[1]} улица."),
                                            ], expand=True),
                                        delete_btn,
                                    ]), padding=15)))
        page.update()

    def delete_pick(pid):
        db.Table.delete(db, "picks", f"id = {pid}")
        load_pick()

    def delete_product(pid):
        db.Table.delete(db, "products", f"id = {pid}")
        load()

    def add(e):
        db.Table.write(db, "products", "ART001", name.value or "Товар", "шт",
                       price.value or "0", supplier.value or "", "", "",
                       discount.value or "0", count.value or "0", "", "")
        name.value = price.value = count.value = discount.value = supplier.value = ""
        load()

    def on_search(e):
        load()

    def show_shop(user_role, user_name):
        nonlocal role
        role = "admin" if user_role == "Администратор" else (
            "manager" if user_role == "Менеджер" else "client")
        page.controls.clear()
        search.on_change = on_search
        search.visible = (role != "client")
        add_panel = ft.Column([
            ft.Text("Добавить товар"), name, price, count, discount, supplier,
            ft.ElevatedButton("Добавить", on_click=add), ft.ElevatedButton("Показать поставки", on_click=lambda e: load_pick())
        ], visible=(role == "admin"))
        page.add(ft.Column([
            ft.Row([ft.Text(f"{user_role}: {user_name}"), ft.ElevatedButton(
                "Выйти", on_click=lambda e: start())]),
            search,
            add_panel,
            ft.Text("Список товаров"), products,
        ], scroll=ft.ScrollMode.AUTO))
        load()

    def login_click(e):
        user = db.Table.get(db, "users", "role, full_name",
                            f"WHERE login='{login.value}' AND password='{_hash_password(password.value)}'")
        if user:
            show_shop(user[0][0], user[0][1])
        else:
            error.value = "Ошибка"
            page.update()

    def start():
        page.controls.clear()
        page.add(ft.Column([
            login, password,
            ft.Row([ft.ElevatedButton("Войти", on_click=login_click), ft.ElevatedButton(
                "Гость", on_click=lambda e: show_shop("guest", "Гость"))]),
            error
        ]))
        page.update()
    start()

ft.app(main)