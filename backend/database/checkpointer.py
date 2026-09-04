import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver

DB_PATH = os.getenv("CHATBOT_DB_PATH", "chatbot.db")

db_directory = os.path.dirname(DB_PATH)
if db_directory:
    os.makedirs(db_directory, exist_ok=True)

# check_same_thread=False because FastAPI/Starlette may call this from
# different threads depending on how requests are handled
conn = sqlite3.connect(database=DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)


def retrieve_all_threads() -> list[str]:
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def delete_thread(thread_id: str) -> None:
    thread_id = str(thread_id)
    with sqlite3.connect(DB_PATH) as delete_conn:
        cursor = delete_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}

        tables_to_clean = [
            "checkpoint_writes",
            "checkpoint_blobs",
            "checkpoints",
        ]
        for table_name in tables_to_clean:
            if table_name in existing_tables:
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE thread_id = ?",
                    (thread_id,),
                )
        delete_conn.commit()
