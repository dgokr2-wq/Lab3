from datetime import datetime
import sqlite3
from typing import Optional

from db import get_connection
from security import hash_password, verify_password


class BusinessError(Exception):
    """Предсказуемая ошибка бизнес-логики, которую можно показать пользователю."""


class AuthService:
    def login(self, username: str, password: str):
        username = username.strip()
        if not username or not password:
            raise BusinessError("Введите логин и пароль.")
        with get_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            raise BusinessError("Неверный логин или пароль.")
        return dict(user)

    def register_buyer(self, username: str, password: str, full_name: str, phone: str, email: str):
        username = username.strip()
        full_name = full_name.strip()
        phone = phone.strip()
        email = email.strip()
        if len(username) < 3:
            raise BusinessError("Логин должен содержать минимум 3 символа.")
        if len(password) < 6:
            raise BusinessError("Пароль должен содержать минимум 6 символов.")
        if not full_name:
            raise BusinessError("Укажите имя покупателя.")
        now = datetime.now().isoformat(timespec="seconds")
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users(username,password_hash,full_name,role,phone,email,created_at) VALUES (?,?,?,?,?,?,?)",
                    (username, hash_password(password), full_name, "buyer", phone, email, now),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise BusinessError("Пользователь с таким логином уже существует.")


class ProductService:
    def categories(self):
        with get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM categories ORDER BY name")]

    def filters(self):
        with get_connection() as conn:
            sizes = [r[0] for r in conn.execute("SELECT DISTINCT size FROM products WHERE is_active=1 ORDER BY size")]
            colors = [r[0] for r in conn.execute("SELECT DISTINCT color FROM products WHERE is_active=1 ORDER BY color")]
        return sizes, colors

    def search(self, query: str = "", category_id: Optional[int] = None, size: str = "", color: str = "", max_price: str = "", only_stock: bool = True):
        sql = """
            SELECT p.*, c.name AS category
            FROM products p
            JOIN categories c ON c.id=p.category_id
            WHERE p.is_active=1
        """
        params = []
        if query.strip():
            sql += " AND (LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ? OR LOWER(c.name) LIKE ?)"
            q = f"%{query.strip().lower()}%"
            params.extend([q, q, q])
        if category_id:
            sql += " AND p.category_id=?"
            params.append(category_id)
        if size and size != "Все":
            sql += " AND p.size=?"
            params.append(size)
        if color and color != "Все":
            sql += " AND p.color=?"
            params.append(color)
        if max_price.strip():
            try:
                price = float(max_price.replace(",", "."))
            except ValueError:
                raise BusinessError("Максимальная цена должна быть числом.")
            sql += " AND p.price<=?"
            params.append(price)
        if only_stock:
            sql += " AND p.stock>0"
        sql += " ORDER BY c.name, p.name"
        with get_connection() as conn:
            return [dict(r) for r in conn.execute(sql, params)]

    def get_product(self, product_id: int):
        with get_connection() as conn:
            row = conn.execute(
                "SELECT p.*, c.name AS category FROM products p JOIN categories c ON c.id=p.category_id WHERE p.id=?",
                (product_id,),
            ).fetchone()
        if not row:
            raise BusinessError("Товар не найден.")
        return dict(row)

    def create_or_update(self, current_user, product_id, category_id, name, gender, size, color, price, stock, description):
        self._require_role(current_user, ["admin", "manager"])
        name, gender, size, color, description = [str(x).strip() for x in (name, gender, size, color, description)]
        if not category_id:
            raise BusinessError("Выберите категорию товара.")
        if not name:
            raise BusinessError("Укажите название товара.")
        if not size:
            raise BusinessError("Укажите размер.")
        if not color:
            raise BusinessError("Укажите цвет.")
        try:
            price_value = float(str(price).replace(",", "."))
            stock_value = int(stock)
        except ValueError:
            raise BusinessError("Цена и остаток должны быть числовыми значениями.")
        if price_value < 0 or stock_value < 0:
            raise BusinessError("Цена и остаток не могут быть отрицательными.")
        now = datetime.now().isoformat(timespec="seconds")
        with get_connection() as conn:
            if product_id:
                self._lock_or_fail(conn, "product", int(product_id), current_user["id"])
                conn.execute(
                    """UPDATE products SET category_id=?, name=?, gender=?, size=?, color=?, price=?, stock=?, description=?, updated_at=?
                       WHERE id=?""",
                    (category_id, name, gender or "унисекс", size, color, price_value, stock_value, description, now, product_id),
                )
                self._unlock(conn, "product", int(product_id), current_user["id"])
            else:
                conn.execute(
                    """INSERT INTO products(category_id,name,gender,size,color,price,stock,description,created_at,updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (category_id, name, gender or "унисекс", size, color, price_value, stock_value, description, now, now),
                )
            conn.commit()

    def deactivate(self, current_user, product_id):
        self._require_role(current_user, ["admin"])
        with get_connection() as conn:
            self._lock_or_fail(conn, "product", int(product_id), current_user["id"])
            conn.execute("UPDATE products SET is_active=0, updated_at=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), product_id))
            self._unlock(conn, "product", int(product_id), current_user["id"])
            conn.commit()

    def recommendations_for(self, product_id: int, limit: int = 3):
        product = self.get_product(product_id)
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT p.*, c.name AS category
                   FROM products p JOIN categories c ON c.id=p.category_id
                   WHERE p.is_active=1 AND p.stock>0 AND p.id<>? AND (p.category_id=? OR p.color=? OR p.size=?)
                   ORDER BY CASE WHEN p.category_id=? THEN 0 ELSE 1 END, p.price
                   LIMIT ?""",
                (product_id, product["category_id"], product["color"], product["size"], product["category_id"], limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def low_stock(self, threshold=5):
        with get_connection() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT p.*, c.name AS category FROM products p JOIN categories c ON c.id=p.category_id WHERE p.is_active=1 AND p.stock<=? ORDER BY p.stock, p.name",
                (threshold,),
            )]

    def _require_role(self, current_user, roles):
        if current_user["role"] not in roles:
            raise BusinessError("Недостаточно прав для операции.")

    def _lock_or_fail(self, conn, entity, entity_id, user_id):
        lock = conn.execute("SELECT * FROM data_locks WHERE entity=? AND entity_id=?", (entity, entity_id)).fetchone()
        if lock and lock["user_id"] != user_id:
            owner = conn.execute("SELECT full_name FROM users WHERE id=?", (lock["user_id"],)).fetchone()
            raise BusinessError(f"Запись уже редактируется пользователем: {owner['full_name']}.")
        conn.execute(
            "INSERT OR REPLACE INTO data_locks(entity,entity_id,user_id,locked_at) VALUES (?,?,?,?)",
            (entity, entity_id, user_id, datetime.now().isoformat(timespec="seconds")),
        )

    def _unlock(self, conn, entity, entity_id, user_id):
        conn.execute("DELETE FROM data_locks WHERE entity=? AND entity_id=? AND user_id=?", (entity, entity_id, user_id))


class CartService:
    def add_to_cart(self, user, product_id, qty=1):
        if user["role"] != "buyer":
            raise BusinessError("Корзина доступна только покупателю.")
        qty = int(qty)
        if qty <= 0:
            raise BusinessError("Количество должно быть больше нуля.")
        with get_connection() as conn:
            product = conn.execute("SELECT stock FROM products WHERE id=? AND is_active=1", (product_id,)).fetchone()
            if not product:
                raise BusinessError("Товар не найден.")
            current = conn.execute("SELECT qty FROM carts WHERE user_id=? AND product_id=?", (user["id"], product_id)).fetchone()
            new_qty = qty + (current["qty"] if current else 0)
            if new_qty > product["stock"]:
                raise BusinessError("Недостаточно товара на складе.")
            conn.execute(
                "INSERT INTO carts(user_id,product_id,qty) VALUES (?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET qty=excluded.qty",
                (user["id"], product_id, new_qty),
            )
            conn.commit()

    def list_cart(self, user):
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT c.qty, p.id AS product_id, p.name, p.size, p.color, p.price, p.stock, p.price*c.qty AS subtotal
                   FROM carts c JOIN products p ON p.id=c.product_id
                   WHERE c.user_id=? ORDER BY p.name""",
                (user["id"],),
            ).fetchall()
            return [dict(r) for r in rows]

    def remove_from_cart(self, user, product_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM carts WHERE user_id=? AND product_id=?", (user["id"], product_id))
            conn.commit()

    def clear_cart(self, user):
        with get_connection() as conn:
            conn.execute("DELETE FROM carts WHERE user_id=?", (user["id"],))
            conn.commit()


class FavoriteService:
    def toggle(self, user, product_id):
        if user["role"] != "buyer":
            raise BusinessError("Избранное доступно только покупателю.")
        with get_connection() as conn:
            exists = conn.execute("SELECT 1 FROM favorites WHERE user_id=? AND product_id=?", (user["id"], product_id)).fetchone()
            if exists:
                conn.execute("DELETE FROM favorites WHERE user_id=? AND product_id=?", (user["id"], product_id))
                action = "removed"
            else:
                conn.execute(
                    "INSERT INTO favorites(user_id,product_id,created_at) VALUES (?,?,?)",
                    (user["id"], product_id, datetime.now().isoformat(timespec="seconds")),
                )
                action = "added"
            conn.commit()
            return action

    def list_favorites(self, user):
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT p.*, c.name AS category FROM favorites f
                   JOIN products p ON p.id=f.product_id JOIN categories c ON c.id=p.category_id
                   WHERE f.user_id=? AND p.is_active=1 ORDER BY f.created_at DESC""",
                (user["id"],),
            ).fetchall()
            return [dict(r) for r in rows]


class OrderService:
    def checkout(self, user, delivery_type, address, comment):
        if user["role"] != "buyer":
            raise BusinessError("Заказ может оформить только покупатель.")
        delivery_type = delivery_type.strip() or "доставка"
        address = address.strip()
        comment = comment.strip()
        if delivery_type == "доставка" and not address:
            raise BusinessError("Для доставки укажите адрес.")
        now = datetime.now().isoformat(timespec="seconds")
        with get_connection() as conn:
            items = conn.execute(
                """SELECT c.product_id, c.qty, p.name, p.size, p.color, p.price, p.stock
                   FROM carts c JOIN products p ON p.id=c.product_id WHERE c.user_id=?""",
                (user["id"],),
            ).fetchall()
            if not items:
                raise BusinessError("Корзина пуста.")
            for item in items:
                if item["qty"] > item["stock"]:
                    raise BusinessError(f"Недостаточно товара: {item['name']}.")
            total = sum(item["qty"] * item["price"] for item in items)
            cur = conn.execute(
                "INSERT INTO orders(user_id,status,delivery_type,address,comment,total,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (user["id"], "создан", delivery_type, address, comment, total, now, now),
            )
            order_id = cur.lastrowid
            for item in items:
                conn.execute(
                    "INSERT INTO order_items(order_id,product_id,product_name,size,color,qty,price) VALUES (?,?,?,?,?,?,?)",
                    (order_id, item["product_id"], item["name"], item["size"], item["color"], item["qty"], item["price"]),
                )
                conn.execute("UPDATE products SET stock=stock-?, updated_at=? WHERE id=?", (item["qty"], now, item["product_id"]))
            conn.execute("DELETE FROM carts WHERE user_id=?", (user["id"],))
            conn.commit()
            return order_id

    def list_orders(self, user):
        sql = """
            SELECT o.*, u.full_name AS buyer, u.phone, u.email,
                   GROUP_CONCAT(oi.product_name || ' × ' || oi.qty, '; ') AS items
            FROM orders o
            JOIN users u ON u.id=o.user_id
            LEFT JOIN order_items oi ON oi.order_id=o.id
        """
        params = []
        if user["role"] == "buyer":
            sql += " WHERE o.user_id=?"
            params.append(user["id"])
        sql += " GROUP BY o.id ORDER BY o.created_at DESC"
        with get_connection() as conn:
            return [dict(r) for r in conn.execute(sql, params)]

    def update_status(self, user, order_id, status):
        if user["role"] not in ["admin", "manager"]:
            raise BusinessError("Недостаточно прав для изменения статуса.")
        allowed = ["создан", "подтвержден", "собран", "передан в доставку", "завершен", "отменен"]
        if status not in allowed:
            raise BusinessError("Некорректный статус заказа.")
        with get_connection() as conn:
            conn.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?", (status, datetime.now().isoformat(timespec="seconds"), order_id))
            conn.commit()


class FeedbackService:
    def create(self, user, topic, message, score):
        topic = topic.strip()
        message = message.strip()
        if not topic:
            raise BusinessError("Укажите тему замечания.")
        if len(message) < 10:
            raise BusinessError("Опишите замечание подробнее: минимум 10 символов.")
        try:
            score = int(score)
        except ValueError:
            raise BusinessError("Оценка должна быть числом от 1 до 5.")
        if score < 1 or score > 5:
            raise BusinessError("Оценка должна быть от 1 до 5.")
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO feedback(user_id,topic,message,score,created_at) VALUES (?,?,?,?,?)",
                (user["id"], topic, message, score, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()

    def list_feedback(self):
        with get_connection() as conn:
            return [dict(r) for r in conn.execute(
                """SELECT f.*, COALESCE(u.full_name,'Гость') AS user_name
                   FROM feedback f LEFT JOIN users u ON u.id=f.user_id ORDER BY f.created_at DESC"""
            )]

    def list_alpha_results(self):
        with get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM alpha_results ORDER BY id")]


class AnalyticsService:
    def dashboard(self):
        with get_connection() as conn:
            users = conn.execute("SELECT COUNT(*) FROM users WHERE role='buyer'").fetchone()[0]
            active_products = conn.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0]
            orders = conn.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM orders").fetchone()
            feedback = conn.execute("SELECT COUNT(*), COALESCE(AVG(score),0) FROM feedback").fetchone()
            low = conn.execute("SELECT COUNT(*) FROM products WHERE is_active=1 AND stock<=5").fetchone()[0]
        return {
            "buyers": users,
            "products": active_products,
            "orders_count": orders[0],
            "orders_sum": orders[1],
            "feedback_count": feedback[0],
            "avg_score": feedback[1],
            "low_stock": low,
        }
