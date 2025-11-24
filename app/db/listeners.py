import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.utils.logging import logger

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())
    logger.debug("Executing query", extra={"sql": statement, "parameters": parameters})

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info["query_start_time"].pop(-1)
    logger.debug("Query finished", extra={"total_time": f"{total_time:.2f}s"})
