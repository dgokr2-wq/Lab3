import tkinter as tk
from tkinter import ttk, messagebox

from services import (
    AnalyticsService,
    AuthService,
    BusinessError,
    CartService,
    FavoriteService,
    FeedbackService,
    OrderService,
    ProductService,
)

BG = "#F6F1E8"
PANEL = "#FFFFFF"
TEXT = "#2B2B2B"
MUTED = "#6F6A63"
ACCENT = "#6A8F55"
ACCENT_DARK = "#3F5D3A"
WARN = "#C77D2E"


def setup_style(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL, relief="flat")
    style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("Title.TLabel", background=BG, foreground=ACCENT_DARK, font=("Segoe UI", 20, "bold"))
    style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 11))
    style.configure("Section.TLabel", background=BG, foreground=ACCENT_DARK, font=("Segoe UI", 13, "bold"))
    style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10))
    style.configure("Accent.TButton", background=ACCENT, foreground="white")
    style.map("Accent.TButton", background=[("active", ACCENT_DARK)])
    style.configure("Danger.TButton", background="#B45B4A", foreground="white")
    style.configure("TEntry", fieldbackground="white", padding=4)
    style.configure("TCombobox", fieldbackground="white", padding=4)
    style.configure("Treeview", background="white", fieldbackground="white", rowheight=28, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E9E1D2")
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))


def show_error(err):
    messagebox.showerror("StylModa", str(err))


def show_info(text):
    messagebox.showinfo("StylModa", text)


def as_money(value):
    return f"{float(value):,.2f} ₽".replace(",", " ").replace(".", ",")


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StylModa v2 — вход")
        self.geometry("900x560")
        self.minsize(850, 520)
        self.configure(bg=BG)
        setup_style(self)
        self.auth = AuthService()
        self._build()

    def _build(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=28, pady=24)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        left = tk.Frame(container, bg=ACCENT_DARK)
        left.grid(row=0, column=0, sticky="nsew")
        tk.Label(left, text="StylModa", bg=ACCENT_DARK, fg="white", font=("Segoe UI", 34, "bold")).pack(anchor="w", padx=34, pady=(45, 10))
        tk.Label(left, text="MVP после CustDev и α-тестирования", bg=ACCENT_DARK, fg="#E8F0E0", font=("Segoe UI", 13)).pack(anchor="w", padx=36)
        tk.Label(
            left,
            text="Новая версия: фильтры каталога, избранное,\nоформление заказа, статусы и обратная связь.",
            bg=ACCENT_DARK,
            fg="#FFFFFF",
            justify="left",
            font=("Segoe UI", 12),
        ).pack(anchor="w", padx=36, pady=50)
        tk.Label(
            left,
            text="Тестовые учетные записи:\nadmin / admin123\nmanager / manager123\nbuyer / buyer123",
            bg=ACCENT_DARK,
            fg="#DDE8D3",
            justify="left",
            font=("Segoe UI", 11),
        ).pack(anchor="sw", padx=36, pady=(90, 10))

        right = ttk.Frame(container, style="Panel.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Вход в систему", style="Panel.TLabel", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w", padx=42, pady=(42, 10))
        ttk.Label(right, text="Выберите роль через логин или зарегистрируйте покупателя", style="Panel.TLabel").grid(row=1, column=0, sticky="w", padx=42)

        tabs = ttk.Notebook(right)
        tabs.grid(row=2, column=0, sticky="nsew", padx=36, pady=26)
        right.rowconfigure(2, weight=1)

        login_tab = ttk.Frame(tabs, style="Panel.TFrame")
        reg_tab = ttk.Frame(tabs, style="Panel.TFrame")
        tabs.add(login_tab, text="Вход")
        tabs.add(reg_tab, text="Регистрация")
        self._build_login_tab(login_tab)
        self._build_register_tab(reg_tab)

    def _build_login_tab(self, parent):
        self.login_username = tk.StringVar(value="buyer")
        self.login_password = tk.StringVar(value="buyer123")
        self._labeled_entry(parent, "Логин", self.login_username, 0)
        self._labeled_entry(parent, "Пароль", self.login_password, 1, show="*")
        ttk.Button(parent, text="Войти", style="Accent.TButton", command=self._login).grid(row=4, column=0, sticky="ew", padx=10, pady=22)
        parent.columnconfigure(0, weight=1)

    def _build_register_tab(self, parent):
        self.reg_username = tk.StringVar()
        self.reg_password = tk.StringVar()
        self.reg_name = tk.StringVar()
        self.reg_phone = tk.StringVar()
        self.reg_email = tk.StringVar()
        fields = [
            ("Логин", self.reg_username, ""),
            ("Пароль", self.reg_password, "*"),
            ("ФИО", self.reg_name, ""),
            ("Телефон", self.reg_phone, ""),
            ("E-mail", self.reg_email, ""),
        ]
        for i, (label, var, show) in enumerate(fields):
            self._labeled_entry(parent, label, var, i, show=show)
        ttk.Button(parent, text="Создать аккаунт покупателя", style="Accent.TButton", command=self._register_buyer).grid(row=10, column=0, sticky="ew", padx=10, pady=20)
        parent.columnconfigure(0, weight=1)

    def _labeled_entry(self, parent, label, variable, row, show=""):
        ttk.Label(parent, text=label, style="Panel.TLabel").grid(row=row * 2, column=0, sticky="w", padx=10, pady=(10, 4))
        ttk.Entry(parent, textvariable=variable, show=show).grid(row=row * 2 + 1, column=0, sticky="ew", padx=10)

    def _login(self):
        try:
            user = self.auth.login(self.login_username.get(), self.login_password.get())
        except BusinessError as err:
            show_error(err)
            return
        self.destroy()
        app = MainWindow(user)
        app.mainloop()

    def _register_buyer(self):
        try:
            self.auth.register_buyer(
                self.reg_username.get(), self.reg_password.get(), self.reg_name.get(), self.reg_phone.get(), self.reg_email.get()
            )
        except BusinessError as err:
            show_error(err)
            return
        show_info("Аккаунт покупателя создан. Теперь можно войти.")
        self.login_username.set(self.reg_username.get())
        self.login_password.set(self.reg_password.get())


class MainWindow(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"StylModa v2 — {user['full_name']}")
        self.geometry("1180x760")
        self.minsize(1050, 680)
        self.configure(bg=BG)
        setup_style(self)
        self.product_service = ProductService()
        self.cart_service = CartService()
        self.favorite_service = FavoriteService()
        self.order_service = OrderService()
        self.feedback_service = FeedbackService()
        self.analytics_service = AnalyticsService()
        self.categories_cache = []
        self.selected_product_id = None
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 6))
        ttk.Label(header, text="StylModa v2", style="Title.TLabel").pack(side="left")
        role_name = {"admin": "администратор", "manager": "менеджер", "buyer": "покупатель"}.get(self.user["role"], self.user["role"])
        ttk.Label(header, text=f"{self.user['full_name']} • роль: {role_name}", style="Subtitle.TLabel").pack(side="left", padx=18)
        ttk.Button(header, text="Выйти", command=self._logout).pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=22, pady=12)

        if self.user["role"] == "buyer":
            self._build_buyer_catalog()
            self._build_favorites_tab()
            self._build_cart_tab()
            self._build_orders_tab()
            self._build_feedback_tab()
        elif self.user["role"] == "manager":
            self._build_orders_tab()
            self._build_inventory_tab()
            self._build_feedback_review_tab()
            self._build_alpha_tab()
        elif self.user["role"] == "admin":
            self._build_admin_dashboard_tab()
            self._build_product_admin_tab()
            self._build_orders_tab()
            self._build_feedback_review_tab()
            self._build_alpha_tab()

    def _logout(self):
        self.destroy()
        LoginWindow().mainloop()

    # ---------- shared helpers ----------
    def _make_tree(self, parent, columns, headings, widths):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        for col, head, width in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=width, minwidth=70, anchor="w")
        return tree

    def _clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _selected_id(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        return int(tree.item(sel[0], "values")[0])

    def _category_items(self):
        self.categories_cache = self.product_service.categories()
        return ["Все"] + [c["name"] for c in self.categories_cache]

    def _category_id_by_name(self, name):
        for c in self.categories_cache:
            if c["name"] == name:
                return c["id"]
        return None

    # ---------- buyer catalog ----------
    def _build_buyer_catalog(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Каталог")

        top = ttk.Frame(tab)
        top.pack(fill="x", pady=(8, 10))
        ttk.Label(top, text="Каталог с фильтрами после α-тестирования", style="Section.TLabel").pack(anchor="w")
        ttk.Label(top, text="Добавлены поиск по размеру, цвету, цене, наличие, избранное и быстрый переход в корзину.", style="Muted.TLabel").pack(anchor="w")

        filters = ttk.Frame(tab, style="Panel.TFrame")
        filters.pack(fill="x", pady=8, ipady=8)
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все")
        self.size_var = tk.StringVar(value="Все")
        self.color_var = tk.StringVar(value="Все")
        self.max_price_var = tk.StringVar()
        self.only_stock_var = tk.BooleanVar(value=True)

        sizes, colors = self.product_service.filters()
        ttk.Label(filters, text="Поиск", style="Panel.TLabel").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(filters, textvariable=self.search_var, width=22).grid(row=1, column=0, padx=8, sticky="ew")
        ttk.Label(filters, text="Категория", style="Panel.TLabel").grid(row=0, column=1, padx=8, sticky="w")
        ttk.Combobox(filters, textvariable=self.category_var, values=self._category_items(), state="readonly", width=18).grid(row=1, column=1, padx=8, sticky="ew")
        ttk.Label(filters, text="Размер", style="Panel.TLabel").grid(row=0, column=2, padx=8, sticky="w")
        ttk.Combobox(filters, textvariable=self.size_var, values=["Все"] + sizes, state="readonly", width=12).grid(row=1, column=2, padx=8, sticky="ew")
        ttk.Label(filters, text="Цвет", style="Panel.TLabel").grid(row=0, column=3, padx=8, sticky="w")
        ttk.Combobox(filters, textvariable=self.color_var, values=["Все"] + colors, state="readonly", width=14).grid(row=1, column=3, padx=8, sticky="ew")
        ttk.Label(filters, text="Цена до", style="Panel.TLabel").grid(row=0, column=4, padx=8, sticky="w")
        ttk.Entry(filters, textvariable=self.max_price_var, width=12).grid(row=1, column=4, padx=8, sticky="ew")
        ttk.Checkbutton(filters, text="только в наличии", variable=self.only_stock_var).grid(row=1, column=5, padx=8, sticky="w")
        ttk.Button(filters, text="Найти", style="Accent.TButton", command=self._load_catalog).grid(row=1, column=6, padx=8, sticky="ew")
        for i in range(7):
            filters.columnconfigure(i, weight=1)

        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.catalog_tree = self._make_tree(
            left,
            ("id", "category", "name", "size", "color", "price", "stock"),
            ("ID", "Категория", "Товар", "Размер", "Цвет", "Цена", "Остаток"),
            (55, 120, 230, 80, 110, 90, 80),
        )
        self.catalog_tree.bind("<<TreeviewSelect>>", self._on_catalog_select)

        right = ttk.Frame(body, style="Panel.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        ttk.Label(right, text="Карточка товара", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 6))
        self.product_info = tk.Text(right, height=12, wrap="word", bg="white", relief="flat", font=("Segoe UI", 10))
        self.product_info.grid(row=1, column=0, sticky="nsew", padx=15, pady=6)
        ttk.Button(right, text="Добавить в корзину", style="Accent.TButton", command=self._add_selected_to_cart).grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        ttk.Button(right, text="Добавить / убрать избранное", command=self._toggle_favorite).grid(row=3, column=0, sticky="ew", padx=15, pady=5)
        ttk.Label(right, text="Рекомендации", style="Panel.TLabel", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", padx=15, pady=(18, 3))
        self.rec_text = tk.Text(right, height=8, wrap="word", bg="white", relief="flat", font=("Segoe UI", 9))
        self.rec_text.grid(row=5, column=0, sticky="nsew", padx=15, pady=(0, 15))
        right.rowconfigure(1, weight=1)
        right.rowconfigure(5, weight=1)
        self._load_catalog()

    def _load_catalog(self):
        try:
            rows = self.product_service.search(
                self.search_var.get(),
                self._category_id_by_name(self.category_var.get()),
                self.size_var.get(),
                self.color_var.get(),
                self.max_price_var.get(),
                self.only_stock_var.get(),
            )
        except BusinessError as err:
            show_error(err)
            return
        self._clear_tree(self.catalog_tree)
        for r in rows:
            self.catalog_tree.insert(
                "", "end", values=(r["id"], r["category"], r["name"], r["size"], r["color"], as_money(r["price"]), r["stock"])
            )
        self.product_info.delete("1.0", "end")
        self.rec_text.delete("1.0", "end")
        self.selected_product_id = None

    def _on_catalog_select(self, event=None):
        pid = self._selected_id(self.catalog_tree)
        if not pid:
            return
        self.selected_product_id = pid
        try:
            p = self.product_service.get_product(pid)
            recs = self.product_service.recommendations_for(pid)
        except BusinessError as err:
            show_error(err)
            return
        self.product_info.delete("1.0", "end")
        self.product_info.insert(
            "end",
            f"{p['name']}\n\nКатегория: {p['category']}\nРазмер: {p['size']}\nЦвет: {p['color']}\nЦена: {as_money(p['price'])}\nОстаток: {p['stock']}\n\n{p['description'] or ''}",
        )
        self.rec_text.delete("1.0", "end")
        if recs:
            for rec in recs:
                self.rec_text.insert("end", f"• {rec['name']} — {rec['size']}, {rec['color']}, {as_money(rec['price'])}\n")
        else:
            self.rec_text.insert("end", "Нет рекомендаций по выбранному товару.")

    def _add_selected_to_cart(self):
        if not self.selected_product_id:
            show_error("Выберите товар в каталоге.")
            return
        try:
            self.cart_service.add_to_cart(self.user, self.selected_product_id, 1)
            show_info("Товар добавлен в корзину.")
            self._load_cart()
        except BusinessError as err:
            show_error(err)

    def _toggle_favorite(self):
        if not self.selected_product_id:
            show_error("Выберите товар в каталоге.")
            return
        try:
            action = self.favorite_service.toggle(self.user, self.selected_product_id)
            self._load_favorites()
            show_info("Товар добавлен в избранное." if action == "added" else "Товар удален из избранного.")
        except BusinessError as err:
            show_error(err)

    # ---------- favorites ----------
    def _build_favorites_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Избранное")
        ttk.Label(tab, text="Избранное: новая функция после интервью с покупателями", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.fav_tree = self._make_tree(
            tab,
            ("id", "category", "name", "size", "color", "price", "stock"),
            ("ID", "Категория", "Товар", "Размер", "Цвет", "Цена", "Остаток"),
            (55, 130, 250, 80, 110, 90, 80),
        )
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=10)
        ttk.Button(buttons, text="Добавить выбранное в корзину", style="Accent.TButton", command=self._favorite_to_cart).pack(side="left")
        ttk.Button(buttons, text="Обновить", command=self._load_favorites).pack(side="left", padx=8)
        self._load_favorites()

    def _load_favorites(self):
        if not hasattr(self, "fav_tree"):
            return
        self._clear_tree(self.fav_tree)
        for r in self.favorite_service.list_favorites(self.user):
            self.fav_tree.insert("", "end", values=(r["id"], r["category"], r["name"], r["size"], r["color"], as_money(r["price"]), r["stock"]))

    def _favorite_to_cart(self):
        pid = self._selected_id(self.fav_tree)
        if not pid:
            show_error("Выберите товар.")
            return
        try:
            self.cart_service.add_to_cart(self.user, pid, 1)
            self._load_cart()
            show_info("Товар добавлен в корзину.")
        except BusinessError as err:
            show_error(err)

    # ---------- cart ----------
    def _build_cart_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Корзина")
        ttk.Label(tab, text="Корзина и оформление заказа", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.cart_tree = self._make_tree(
            tab,
            ("id", "name", "size", "color", "qty", "price", "subtotal", "stock"),
            ("ID", "Товар", "Размер", "Цвет", "Кол-во", "Цена", "Сумма", "Остаток"),
            (55, 250, 80, 110, 80, 100, 110, 80),
        )
        form = ttk.Frame(tab, style="Panel.TFrame")
        form.pack(fill="x", pady=12, ipady=8)
        self.delivery_var = tk.StringVar(value="доставка")
        self.address_var = tk.StringVar(value="г. Москва, ул. Примерная, д. 1")
        self.comment_var = tk.StringVar()
        ttk.Label(form, text="Способ получения", style="Panel.TLabel").grid(row=0, column=0, padx=8, sticky="w")
        ttk.Combobox(form, textvariable=self.delivery_var, values=["доставка", "самовывоз"], state="readonly").grid(row=1, column=0, padx=8, sticky="ew")
        ttk.Label(form, text="Адрес", style="Panel.TLabel").grid(row=0, column=1, padx=8, sticky="w")
        ttk.Entry(form, textvariable=self.address_var).grid(row=1, column=1, padx=8, sticky="ew")
        ttk.Label(form, text="Комментарий", style="Panel.TLabel").grid(row=0, column=2, padx=8, sticky="w")
        ttk.Entry(form, textvariable=self.comment_var).grid(row=1, column=2, padx=8, sticky="ew")
        ttk.Button(form, text="Оформить заказ", style="Accent.TButton", command=self._checkout).grid(row=1, column=3, padx=8, sticky="ew")
        ttk.Button(form, text="Удалить позицию", command=self._remove_cart_item).grid(row=1, column=4, padx=8, sticky="ew")
        for i in range(5):
            form.columnconfigure(i, weight=1)
        self.cart_total_label = ttk.Label(tab, text="Итого: 0,00 ₽", style="Section.TLabel")
        self.cart_total_label.pack(anchor="e")
        self._load_cart()

    def _load_cart(self):
        if not hasattr(self, "cart_tree"):
            return
        self._clear_tree(self.cart_tree)
        total = 0
        for r in self.cart_service.list_cart(self.user):
            total += r["subtotal"]
            self.cart_tree.insert("", "end", values=(r["product_id"], r["name"], r["size"], r["color"], r["qty"], as_money(r["price"]), as_money(r["subtotal"]), r["stock"]))
        self.cart_total_label.configure(text=f"Итого: {as_money(total)}")

    def _remove_cart_item(self):
        pid = self._selected_id(self.cart_tree)
        if not pid:
            show_error("Выберите позицию в корзине.")
            return
        self.cart_service.remove_from_cart(self.user, pid)
        self._load_cart()

    def _checkout(self):
        try:
            order_id = self.order_service.checkout(self.user, self.delivery_var.get(), self.address_var.get(), self.comment_var.get())
            self._load_cart()
            self._load_orders()
            self._load_catalog()
            show_info(f"Заказ №{order_id} оформлен.")
        except BusinessError as err:
            show_error(err)

    # ---------- orders ----------
    def _build_orders_tab(self):
        tab = ttk.Frame(self.tabs)
        title = "Заказы покупателей" if self.user["role"] in ["admin", "manager"] else "Мои заказы"
        self.tabs.add(tab, text=title)
        ttk.Label(tab, text=title, style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.orders_tree = self._make_tree(
            tab,
            ("id", "status", "buyer", "items", "delivery", "address", "total", "created"),
            ("№", "Статус", "Покупатель", "Состав", "Получение", "Адрес", "Сумма", "Дата"),
            (60, 130, 160, 330, 100, 230, 100, 140),
        )
        panel = ttk.Frame(tab)
        panel.pack(fill="x", pady=10)
        ttk.Button(panel, text="Обновить", command=self._load_orders).pack(side="left")
        if self.user["role"] in ["admin", "manager"]:
            self.status_var = tk.StringVar(value="подтвержден")
            ttk.Combobox(panel, textvariable=self.status_var, values=["создан", "подтвержден", "собран", "передан в доставку", "завершен", "отменен"], state="readonly", width=22).pack(side="left", padx=8)
            ttk.Button(panel, text="Изменить статус", style="Accent.TButton", command=self._change_order_status).pack(side="left")
        self._load_orders()

    def _load_orders(self):
        if not hasattr(self, "orders_tree"):
            return
        self._clear_tree(self.orders_tree)
        for r in self.order_service.list_orders(self.user):
            self.orders_tree.insert(
                "", "end",
                values=(r["id"], r["status"], r.get("buyer", ""), r.get("items") or "", r["delivery_type"], r.get("address") or "", as_money(r["total"]), r["created_at"]),
            )

    def _change_order_status(self):
        oid = self._selected_id(self.orders_tree)
        if not oid:
            show_error("Выберите заказ.")
            return
        try:
            self.order_service.update_status(self.user, oid, self.status_var.get())
            self._load_orders()
        except BusinessError as err:
            show_error(err)

    # ---------- feedback ----------
    def _build_feedback_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Обратная связь")
        ttk.Label(tab, text="Форма обратной связи по результатам α-тестирования", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        form = ttk.Frame(tab, style="Panel.TFrame")
        form.pack(fill="x", pady=10, ipady=10)
        self.fb_topic = tk.StringVar(value="Каталог и оформление заказа")
        self.fb_score = tk.StringVar(value="5")
        ttk.Label(form, text="Тема", style="Panel.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(form, textvariable=self.fb_topic).grid(row=1, column=0, padx=10, sticky="ew")
        ttk.Label(form, text="Оценка 1–5", style="Panel.TLabel").grid(row=0, column=1, padx=10, sticky="w")
        ttk.Combobox(form, textvariable=self.fb_score, values=["1", "2", "3", "4", "5"], state="readonly", width=10).grid(row=1, column=1, padx=10, sticky="ew")
        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=1)
        ttk.Label(tab, text="Что было неудобно или что нужно улучшить?", style="Muted.TLabel").pack(anchor="w")
        self.fb_message = tk.Text(tab, height=10, wrap="word", font=("Segoe UI", 10))
        self.fb_message.pack(fill="both", expand=True, pady=8)
        ttk.Button(tab, text="Отправить замечание", style="Accent.TButton", command=self._send_feedback).pack(anchor="e")

    def _send_feedback(self):
        try:
            self.feedback_service.create(self.user, self.fb_topic.get(), self.fb_message.get("1.0", "end").strip(), self.fb_score.get())
            self.fb_message.delete("1.0", "end")
            show_info("Замечание сохранено. Его увидит менеджер/администратор.")
        except BusinessError as err:
            show_error(err)

    def _build_feedback_review_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Отзывы α-теста")
        ttk.Label(tab, text="Отзывы и замечания пользователей", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.feedback_tree = self._make_tree(
            tab,
            ("id", "user", "topic", "score", "status", "message", "date"),
            ("ID", "Пользователь", "Тема", "Оценка", "Статус", "Сообщение", "Дата"),
            (55, 170, 190, 70, 100, 360, 140),
        )
        ttk.Button(tab, text="Обновить", command=self._load_feedback).pack(anchor="w", pady=10)
        self._load_feedback()

    def _load_feedback(self):
        if not hasattr(self, "feedback_tree"):
            return
        self._clear_tree(self.feedback_tree)
        for r in self.feedback_service.list_feedback():
            msg = (r["message"][:95] + "...") if len(r["message"]) > 95 else r["message"]
            self.feedback_tree.insert("", "end", values=(r["id"], r["user_name"], r["topic"], r["score"], r["status"], msg, r["created_at"]))

    # ---------- alpha results ----------
    def _build_alpha_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Карта гипотез")
        ttk.Label(tab, text="Карта гипотез и корректировки после CustDev", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        ttk.Label(tab, text="Этот раздел показывает, какие изменения были внесены во вторую версию приложения.", style="Muted.TLabel").pack(anchor="w")
        self.alpha_tree = self._make_tree(
            tab,
            ("id", "hypothesis", "issue", "decision", "result", "confirmed"),
            ("ID", "Гипотеза клиента", "Проблема", "Решение в системе", "Результат", "Подтв."),
            (45, 250, 250, 260, 300, 70),
        )
        for r in self.feedback_service.list_alpha_results():
            self.alpha_tree.insert("", "end", values=(r["id"], r["hypothesis"], r["issue"], r["decision"], r["result"], "да" if r["is_confirmed"] else "нет"))

    # ---------- manager inventory ----------
    def _build_inventory_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Склад")
        ttk.Label(tab, text="Контроль остатков", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        self.low_stock_tree = self._make_tree(
            tab,
            ("id", "category", "name", "size", "color", "stock", "price"),
            ("ID", "Категория", "Товар", "Размер", "Цвет", "Остаток", "Цена"),
            (55, 140, 260, 80, 110, 90, 100),
        )
        ttk.Button(tab, text="Обновить", command=self._load_low_stock).pack(anchor="w", pady=10)
        self._load_low_stock()

    def _load_low_stock(self):
        self._clear_tree(self.low_stock_tree)
        for r in self.product_service.low_stock(5):
            self.low_stock_tree.insert("", "end", values=(r["id"], r["category"], r["name"], r["size"], r["color"], r["stock"], as_money(r["price"])))

    # ---------- admin dashboard ----------
    def _build_admin_dashboard_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Панель")
        ttk.Label(tab, text="Административная панель MVP v2", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        cards = ttk.Frame(tab)
        cards.pack(fill="x", pady=14)
        self.dashboard_labels = []
        titles = ["Покупатели", "Активные товары", "Заказы", "Выручка", "Отзывы", "Низкий остаток"]
        for i, title in enumerate(titles):
            card = ttk.Frame(cards, style="Panel.TFrame")
            card.grid(row=0, column=i, sticky="nsew", padx=6, ipady=18)
            cards.columnconfigure(i, weight=1)
            ttk.Label(card, text=title, style="Panel.TLabel").pack(padx=12)
            lbl = ttk.Label(card, text="0", style="Panel.TLabel", font=("Segoe UI", 16, "bold"))
            lbl.pack(padx=12, pady=6)
            self.dashboard_labels.append(lbl)
        ttk.Button(tab, text="Обновить показатели", style="Accent.TButton", command=self._load_dashboard).pack(anchor="w", pady=10)
        ttk.Label(tab, text="Панель добавлена как управленческий итог доработки: видно продажи, отзывы и проблемные остатки.", style="Muted.TLabel").pack(anchor="w", pady=10)
        self._load_dashboard()

    def _load_dashboard(self):
        data = self.analytics_service.dashboard()
        values = [
            str(data["buyers"]),
            str(data["products"]),
            str(data["orders_count"]),
            as_money(data["orders_sum"]),
            f"{data['feedback_count']} / ср. {data['avg_score']:.1f}",
            str(data["low_stock"]),
        ]
        for lbl, value in zip(self.dashboard_labels, values):
            lbl.configure(text=value)

    # ---------- admin product editor ----------
    def _build_product_admin_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Товары")
        ttk.Label(tab, text="Управление товарами", style="Section.TLabel").pack(anchor="w", pady=(10, 6))
        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.admin_products_tree = self._make_tree(
            left,
            ("id", "category", "name", "size", "color", "price", "stock"),
            ("ID", "Категория", "Товар", "Размер", "Цвет", "Цена", "Остаток"),
            (55, 120, 240, 80, 110, 90, 80),
        )
        self.admin_products_tree.bind("<<TreeviewSelect>>", self._on_admin_product_select)
        right = ttk.Frame(body, style="Panel.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)
        self.edit_product_id = None
        self.p_name = tk.StringVar()
        self.p_gender = tk.StringVar(value="унисекс")
        self.p_category = tk.StringVar()
        self.p_size = tk.StringVar()
        self.p_color = tk.StringVar()
        self.p_price = tk.StringVar()
        self.p_stock = tk.StringVar()
        self.p_description = tk.StringVar()
        labels = [
            ("Категория", self.p_category, "combo"),
            ("Название", self.p_name, "entry"),
            ("Пол", self.p_gender, "combo_gender"),
            ("Размер", self.p_size, "entry"),
            ("Цвет", self.p_color, "entry"),
            ("Цена", self.p_price, "entry"),
            ("Остаток", self.p_stock, "entry"),
            ("Описание", self.p_description, "entry"),
        ]
        for i, (label, var, kind) in enumerate(labels):
            ttk.Label(right, text=label, style="Panel.TLabel").grid(row=i, column=0, sticky="w", padx=12, pady=6)
            if kind == "combo":
                ttk.Combobox(right, textvariable=var, values=[c["name"] for c in self.product_service.categories()], state="readonly").grid(row=i, column=1, sticky="ew", padx=12)
            elif kind == "combo_gender":
                ttk.Combobox(right, textvariable=var, values=["женский", "мужской", "унисекс"], state="readonly").grid(row=i, column=1, sticky="ew", padx=12)
            else:
                ttk.Entry(right, textvariable=var).grid(row=i, column=1, sticky="ew", padx=12)
        ttk.Button(right, text="Сохранить", style="Accent.TButton", command=self._save_product).grid(row=9, column=0, columnspan=2, sticky="ew", padx=12, pady=(18, 5))
        ttk.Button(right, text="Новый товар", command=self._clear_product_form).grid(row=10, column=0, columnspan=2, sticky="ew", padx=12, pady=5)
        ttk.Button(right, text="Скрыть товар", style="Danger.TButton", command=self._deactivate_product).grid(row=11, column=0, columnspan=2, sticky="ew", padx=12, pady=5)
        self._load_admin_products()

    def _load_admin_products(self):
        self._clear_tree(self.admin_products_tree)
        for r in self.product_service.search(only_stock=False):
            self.admin_products_tree.insert("", "end", values=(r["id"], r["category"], r["name"], r["size"], r["color"], as_money(r["price"]), r["stock"]))

    def _on_admin_product_select(self, event=None):
        pid = self._selected_id(self.admin_products_tree)
        if not pid:
            return
        p = self.product_service.get_product(pid)
        self.edit_product_id = pid
        self.p_category.set(p["category"])
        self.p_name.set(p["name"])
        self.p_gender.set(p["gender"])
        self.p_size.set(p["size"])
        self.p_color.set(p["color"])
        self.p_price.set(str(p["price"]))
        self.p_stock.set(str(p["stock"]))
        self.p_description.set(p["description"] or "")

    def _clear_product_form(self):
        self.edit_product_id = None
        self.p_category.set("")
        self.p_name.set("")
        self.p_gender.set("унисекс")
        self.p_size.set("")
        self.p_color.set("")
        self.p_price.set("")
        self.p_stock.set("")
        self.p_description.set("")

    def _save_product(self):
        try:
            self.product_service.create_or_update(
                self.user,
                self.edit_product_id,
                self._category_id_by_name_admin(self.p_category.get()),
                self.p_name.get(),
                self.p_gender.get(),
                self.p_size.get(),
                self.p_color.get(),
                self.p_price.get(),
                self.p_stock.get(),
                self.p_description.get(),
            )
            self._load_admin_products()
            self._clear_product_form()
            show_info("Товар сохранен.")
        except BusinessError as err:
            show_error(err)

    def _category_id_by_name_admin(self, name):
        for c in self.product_service.categories():
            if c["name"] == name:
                return c["id"]
        return None

    def _deactivate_product(self):
        if not self.edit_product_id:
            show_error("Выберите товар.")
            return
        try:
            self.product_service.deactivate(self.user, self.edit_product_id)
            self._load_admin_products()
            self._clear_product_form()
            show_info("Товар скрыт из каталога.")
        except BusinessError as err:
            show_error(err)
