import flet as ft
from db import db, _hash_password
import pandas as pd

def import_data(path,table_name):
    data = pd.read_excel(path)
    for data in data.values:
        db.Table.write(db,table_name,*data)

def main(page:ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Обувной магазин"
    login = ft.TextField(label="enter login",width=500)
    password = ft.TextField(label="enter password",width=500)
    error = ft.Text()
    user_role = 0 #0 - гость, клиент, 1 - менеджер, 2 - админ
    log = ""
    
    tovar_field = [ft.TextField(label=i) for i in db.Info.getColumns(db,"products")]
    zakaz_field = [ft.TextField(label=i) for i in db.Info.getColumns(db,"orders")]

    id_update = 0

    def update(id,list,table_name):
        nonlocal id_update
        data = db.Table.get(db,table_name,request=f"WHERE id = {id}")
        for i, field in enumerate(list):
            field.value = data[0][i]
        id_update = id
        page.update()

    def autorization(e):
        nonlocal user_role, log        
        log = db.Table.get(db,"users","role, full_name, login, password",f"WHERE login = '{login.value}' and password = '{password.value}'")
        if log != [] and len(str(log[0][3])) < 30:
            db.Table.update(db,"users",f"login = '{login.value}' and password = '{password.value}'",log[0][0],log[0][1],log[0][2],_hash_password(log[0][3]))
        log = db.Table.get(db,"users","role, login, password",f"WHERE login = '{login.value}' and password = '{_hash_password(password.value)}'")
        
        if log != [] and log[0][0] == "Администратор":            
            user_role = 2            
            page.go("/tovar_admin")
        elif log != [] and log[0][0] == "Авторизированный клиент":
            user_role = 3
            page.go("/tovar_guest_user")
        elif log != [] and log[0][0] == "Менеджер":
            user_role = 1
            page.go("/tovar_meneger")
        else: error.value = "Неверное имя пользователя или пароль"
        page.update()

    def search_tovar(e):
        search = db.Table.get(db,"products",request=f"WHERE LOWER(name || ' ' || price || ' ' || supplier || ' ' || category) LIKE LOWER('%{e.control.value}%')")
        card_tovar_list.controls.clear()
        card_tovar_list.controls = tovar_card(search)
        page.update()

    def search_zakaz(e):
        search = db.Table.get(db,"orders",request=f"WHERE LOWER(article || ' ' || status || ' ' || date_order || ' ' || date_delivery) LIKE LOWER('%{e.control.value}%')")
        card_zakaz_list.controls.clear()
        card_zakaz_list.controls = zakaz_card(search)
        page.update()

    def update_search(e):
        card_tovar_list.controls.clear()
        card_tovar_list.controls = tovar_card(db.Table.get(db,"products"))
        route_change("/tovar_admin")

    def update_search_zakaz(e):
        card_tovar_list.controls.clear()
        card_tovar_list.controls = tovar_card(db.Table.get(db,"products"))
        route_change("/tovar_admin")

    def tovar_card(data_):
        nonlocal user_role
        
        cards = []

        for data in data_:
            dg_color = None
            if int(data[9]) == 0:
                dg_color = ft.colors.BLUE #товары отсутствуют
            elif int(data[8]) > 15:
                dg_color = ft.colors.GREEN_800 #скидка больше 15%

            row = ft.Row([
                # фото товара
                ft.Column([
                    ft.Image(src=f"import\\{"picture.png" if data[11] == "nan"  else data[11]}", width=150, height=150)
                ],alignment=ft.MainAxisAlignment.CENTER),
                # описание
                ft.Column([
                    ft.Row([ft.Text(f"{data[7]} | "),
                            ft.Text(f"{data[2]}")]),
                    ft.Text(f"Описание товара: {data[10]}"),
                    ft.Text(f"Произваодитель: {data[6]}"),
                    ft.Text(f"Поставщик: {data[5]}"),
                    ft.Text(f"Цена: {data[4]}"),
                    ft.Text(f"Единица измерения: {data[3]}"),
                    ft.Text(f"Количество на складке: {data[9]}"),
                ], width=400,alignment=ft.MainAxisAlignment.START),
                # действующая скидка
                ft.Column([
                    ft.Text("Действующая скидка:"),
                    ft.Text(f"{data[8]}%",color=ft.colors.GREEN_300),
                    ft.ElevatedButton("del", on_click=lambda e, a=data[0]: [   
                        db.Table.delete(db,"products",f"id = {a}"),
                        route_change("/tovar_admin")
                    ]) if user_role == 2 else ft.Text("")
                ]),
                
                
            ],spacing=8)
            card = ft.Card(
                content=ft.Container(
                    width=100,
                    padding=20,
                    bgcolor=dg_color,
                    content=row, on_click= lambda e,a=data[0],i=tovar_field:update(a,i,"products") if user_role == 2 else None
                ),
                margin=10
            )
            cards.append(card)

        return cards
    
    def zakaz_card(data_):
        nonlocal user_role

        cards = []

        for data in data_:
                pick = db.Table.get(db,"pick","pick",f"WHERE id = {data[5]}")
                row = ft.Row(
                            [                                                                
                                # Описание заказа
                                ft.Column(
                                    [
                                        ft.Text(f"{data[2]}",weight=ft.FontWeight.BOLD),
                                        ft.Text(f"{data[8]}"),
                                        ft.Text(f"{pick[0][0]}"),
                                        ft.Text(f"{data[3]}"),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    width=600
                                ),
                                
                                # дата доставки
                                ft.Column(
                                    [
                                        ft.Text("Дата доставки:"),
                                        ft.Text(f"{data[4]}"),
                                        ft.ElevatedButton("del", on_click=lambda e, a=data[0]: [   
                                            db.Table.delete(db,"orders",f"id = {a}"),
                                            route_change("/zakaz_admin") 
                                        ]) if user_role == 2 else ft.Text()
                                    ]
                                )
                            ],
                            spacing=8
                        )
                card = ft.Card(
                    content=ft.Container(
                        width=100,
                        padding=20,
                        content=row, on_click =lambda e,a = data[0],i = zakaz_field:update(a,i,"orders") if user_role == 2 else None
                    ),
                    margin=10
                )
                cards.append(card)
            
        return cards

    card_tovar_list = ft.ListView(tovar_card(db.Table.get(db,"products")),auto_scroll=True,width=800,height=800)
    card_zakaz_list = ft.ListView(zakaz_card(db.Table.get(db,"orders")),auto_scroll=True,width=800,height=800)

    def route_change(route):
        page.views.clear()
        nonlocal user_role, card_tovar_list, card_zakaz_list
        for i in tovar_field[1:]:
            i.value = ""

        if page.route == "/log":
            login.value = ""
            password.value = ""
            error.value = ""
            user_role = 0
            page.views.append(
                ft.View(route="/log",
                        controls=[
                            login,
                            password,
                            error,
                            ft.Row([
                                ft.ElevatedButton(text="Войти", on_click=autorization),
                                ft.ElevatedButton(text="Гость", on_click=lambda e: page.go("/tovar_guest_user")),
                            ],alignment=ft.MainAxisAlignment.CENTER)
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        elif page.route == "/tovar_guest_user":
            card_tovar_list = ft.ListView(tovar_card(db.Table.get(db,"products")),auto_scroll=True,width=800,height=800)
            page.views.append(
                ft.View(route="/tovar_guest_user",
                    controls=[
                        ft.Text(f"{"login:" + log[0][1] if user_role != 0 else ""}") if user_role != 0 else ft.Text(visible=False),
                        ft.Row([card_tovar_list,
                            ft.Column([
                                ft.TextField(label="Поиск",on_change=search_tovar),                              
                                ft.ElevatedButton("back",on_click=lambda e:page.go("/log"))
                            ])
                        ])
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/tovar_meneger":
            card_tovar_list = ft.ListView(tovar_card(db.Table.get(db,"products")),auto_scroll=True,width=800,height=800)
            page.views.append(
                ft.View(route="/tovar_meneger",
                    controls=[
                        ft.Row([card_tovar_list,
                            ft.Column([
                                ft.TextField(label="Поиск",on_change=search_tovar),
                                ft.ElevatedButton("Заказы", on_click=lambda e: page.go("/zakaz_manager")),                                
                                ft.ElevatedButton("back",on_click=lambda e:page.go("/log"))
                            ])
                        ])
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/tovar_admin":
            card_tovar_list = ft.ListView(tovar_card(db.Table.get(db,"products")),auto_scroll=True,width=800,height=800)
            page.views.append(
                ft.View(route="/tovar_admin",
                    controls=[
                        ft.Row([card_tovar_list,
                            ft.Column([
                                ft.TextField(label="Поиск",on_change=search_tovar),
                                *tovar_field[1:],
                                ft.ElevatedButton("Заказы", on_click=lambda e: page.go("/zakaz_admin")),
                                ft.ElevatedButton("add", on_click=lambda e: [
                                    db.Table.write(db,"products",*[str(i.value) for i in tovar_field[1:]]),
                                    route_change("/tovar_admin")
                                ]),
                                ft.ElevatedButton("update",on_click=lambda e:[
                                    db.Table.update(db,"products",f"id = {id_update}",*[str(i.value) for i in tovar_field[1:]]),
                                    update_search(e)
                                ]),
                                ft.ElevatedButton("back",on_click=lambda e:page.go("/log"))
                            ])
                        ])
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/zakaz_admin":
            card_zakaz_list = ft.ListView(zakaz_card(db.Table.get(db,"orders")),auto_scroll=True,width=800,height=800)
            page.views.append(
                ft.View(route="/zakaz_admin",
                    controls=[
                        ft.Row([card_zakaz_list,
                            ft.Column([
                                ft.TextField(label="Поиск",on_change=search_zakaz),
                                *zakaz_field[1:],
                                ft.ElevatedButton("add", on_click=lambda e: [
                                    db.Table.write(db,"orders",*[str(i.value) for i in zakaz_field[1:]]),
                                    route_change("/zakaz_admin")
                                ]),
                                ft.ElevatedButton("update",on_click=lambda e:[
                                    db.Table.update(db,"orders",f"id = {id_update}",*[str(i.value) for i in zakaz_field[1:]]),
                                    update_search_zakaz(e)
                                ]),
                                ft.ElevatedButton("back",on_click=lambda e:page.go("/tovar_admin"))
                            ])
                        ])
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/zakaz_manager":
            card_zakaz_list = ft.ListView(zakaz_card(db.Table.get(db,"orders")),auto_scroll=True,width=800,height=800)
            page.views.append(
                ft.View(route="/zakaz_manager",
                    controls=[
                        ft.Row([card_zakaz_list,
                            ft.Column([
                                ft.TextField(label="Поиск",on_change=search_zakaz),
                                ft.ElevatedButton("back",on_click=lambda e:page.go("/tovar_meneger"))
                            ])
                        ])
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        page.update()

    page.on_route_change = route_change

    page.go("/log")

ft.app(main)