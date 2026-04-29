import os
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "stylmoda_v2.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','manager','buyer')),
                phone TEXT,
                email TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                gender TEXT NOT NULL DEFAULT 'унисекс',
                size TEXT NOT NULL,
                color TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                description TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL CHECK(qty > 0),
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'создан',
                delivery_type TEXT NOT NULL DEFAULT 'доставка',
                address TEXT,
                comment TEXT,
                total REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                size TEXT NOT NULL,
                color TEXT NOT NULL,
                qty INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT NOT NULL,
                message TEXT NOT NULL,
                score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
                status TEXT NOT NULL DEFAULT 'новое',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS alpha_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis TEXT NOT NULL,
                issue TEXT NOT NULL,
                decision TEXT NOT NULL,
                result TEXT NOT NULL,
                is_confirmed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS data_locks (
                entity TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                locked_at TEXT NOT NULL,
                PRIMARY KEY(entity, entity_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        seed_data(conn)
        conn.commit()


def seed_data(conn):
    cur = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")

    users_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if users_count == 0:
        from security import hash_password
        users = [
            ("admin", hash_password("admin123"), "Администратор ИМ StylModa", "admin", "+7 900 000-00-01", "admin@stylmoda.local", now),
            ("manager", hash_password("manager123"), "Менеджер заказов", "manager", "+7 900 000-00-02", "manager@stylmoda.local", now),
            ("buyer", hash_password("buyer123"), "Покупатель Анна", "buyer", "+7 900 000-00-03", "buyer@stylmoda.local", now),
        ]
        cur.executemany(
            "INSERT INTO users(username,password_hash,full_name,role,phone,email,created_at) VALUES (?,?,?,?,?,?,?)",
            users,
        )

    categories = ["Платья", "Верхняя одежда", "Футболки", "Брюки", "Аксессуары", "Обувь"]
    cur.executemany("INSERT OR IGNORE INTO categories(name) VALUES (?)", [(c,) for c in categories])

    products_count = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if products_count == 0:
        cat = {row["name"]: row["id"] for row in cur.execute("SELECT id,name FROM categories")}
        products = [
            (cat["Платья"], "Платье миди Olive", "женский", "M", "оливковый", 4290, 8, "Базовое платье для офиса и прогулки."),
            (cat["Платья"], "Платье вечернее Noir", "женский", "S", "черный", 6990, 3, "Модель для праздничных образов."),
            (cat["Верхняя одежда"], "Тренч бежевый Classic", "унисекс", "L", "бежевый", 8990, 5, "Сезонная верхняя одежда с поясом."),
            (cat["Футболки"], "Футболка базовая White", "унисекс", "M", "белый", 1490, 20, "Хлопковая футболка на каждый день."),
            (cat["Футболки"], "Лонгслив Graphite", "унисекс", "L", "графитовый", 2390, 9, "Подходит для комплектов с джинсами."),
            (cat["Брюки"], "Брюки Wide Leg", "женский", "M", "серый", 4590, 6, "Свободный силуэт, плотная ткань."),
            (cat["Брюки"], "Джинсы Slim Blue", "унисекс", "L", "синий", 3990, 11, "Повседневная модель."),
            (cat["Аксессуары"], "Сумка Mini Caramel", "женский", "one size", "карамельный", 3290, 7, "Аксессуар для базового образа."),
            (cat["Аксессуары"], "Ремень Leather Black", "унисекс", "one size", "черный", 1990, 14, "Классический ремень."),
            (cat["Обувь"], "Кеды Urban", "унисекс", "39", "молочный", 5490, 4, "Удобная повседневная обувь."),
        ]
        cur.executemany(
            """INSERT INTO products(category_id,name,gender,size,color,price,stock,description,created_at,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], now, now) for p in products],
        )

    alpha_count = cur.execute("SELECT COUNT(*) FROM alpha_results").fetchone()[0]
    if alpha_count == 0:
        rows = [
            (
                "Клиенту нужно быстрее находить подходящий размер и цвет",
                "В первой версии каталог был слишком общий, подбор занимал лишнее время",
                "Добавлены фильтры по категории, размеру, цвету, цене и наличию",
                "Гипотеза подтверждена: поиск стал понятнее, покупатель быстрее видит релевантные позиции",
                1,
            ),
            (
                "Покупатель хочет сохранить понравившиеся товары до покупки",
                "В первой версии не было отложенных товаров",
                "Добавлен раздел 'Избранное'",
                "Гипотеза подтверждена: пользователь может вернуться к товару позднее",
                1,
            ),
            (
                "Покупателю важно видеть статус заказа без обращения к менеджеру",
                "После оформления заказа было мало информации о дальнейших действиях",
                "Добавлен раздел 'Мои заказы' и управление статусами менеджером",
                "Гипотеза подтверждена частично: базовая прозрачность статуса появилась",
                1,
            ),
            (
                "Нужно собирать замечания прямо в MVP",
                "После тестирования замечания фиксировались отдельно, терялась связь с пользователем",
                "Добавлена форма обратной связи и панель просмотра отзывов",
                "Гипотеза подтверждена: замечания можно хранить в БД и использовать для следующей доработки",
                1,
            ),
        ]
        cur.executemany(
            "INSERT INTO alpha_results(hypothesis,issue,decision,result,is_confirmed,created_at) VALUES (?,?,?,?,?,?)",
            [(r[0], r[1], r[2], r[3], r[4], now) for r in rows],
        )
