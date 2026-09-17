import sqlite3
import tornado.ioloop
import tornado.web
import os


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            SELECT id, task, completed
            FROM tasks
            ORDER BY completed ASC, id DESC
            """)
        tasks = cursor.fetchall()

        conn.close()

        error = self.get_argument("error", None)

        self.render("index.html", tasks=tasks, error=error)

    def post(self):
        task = self.get_argument("task").strip()

        if not task:
            self.redirect("/?error=empty")
            return

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO tasks (task) VALUES (?)",
        (task,)
        )

        conn.commit()
        conn.close()

        self.redirect("/")
        return

class CompleteHandler(tornado.web.RequestHandler):
    def post(self):
        task_id = self.get_argument("id")

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET completed = CASE
                WHEN completed = 0 THEN 1
                ELSE 0
            END
            WHERE id = ?
        """,(task_id,))

        conn.commit()
        conn.close()

        self.redirect("/")


class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        task_id = self.get_argument("id")

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        conn.commit()
        conn.close()

        self.redirect("/")

class EditHandler(tornado.web.RequestHandler):
    def get(self):
        task_id = self.get_argument("id")

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, task FROM tasks WHERE id = ?",
            (task_id,)
        )

        task = cursor.fetchone()

        conn.close()

        self.render("edit.html", task=task)

    def post(self):
        task_id = self.get_argument("id")
        task_text = self.get_argument("task")

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tasks SET task = ? WHERE id = ?",
            (task_text, task_id)
        )

        conn.commit()
        conn.close()

        self.redirect("/")

def make_app():
    base_dir = os.path.dirname(__file__)

    return tornado.web.Application([
        (r"/",MainHandler),
        (r"/complete",CompleteHandler),
        (r"/delete",DeleteHandler),
        (r"/edit",EditHandler),
    ],
    template_path=os.path.join(base_dir, "templates"),
    static_path=os.path.join(base_dir, "static"))


if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    print("http://localhost:8888で起動中")
    tornado.ioloop.IOLoop.current().start()