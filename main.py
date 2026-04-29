from db import init_db
from ui import LoginWindow


if __name__ == "__main__":
    init_db()
    app = LoginWindow()
    app.mainloop()
