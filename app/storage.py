
from datetime import datetime
from sqlite3 import IntegrityError
from app.models import get_connection

def insert_message(msg):
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO messages
            (message_id, from_msisdn, to_msisdn, ts, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                msg["message_id"],
                msg["from"],
                msg["to"],
                msg["ts"],
                msg.get("text"),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return "created"
    except IntegrityError:
        return "duplicate"
    finally:
        conn.close()

def list_messages(filters, limit, offset):
    base = "FROM messages WHERE 1=1"
    args = []

    if filters.get("from_msisdn"):
        base += " AND from_msisdn = ?"
        args.append(filters["from_msisdn"])

    if filters.get("since"):
        base += " AND ts >= ?"
        args.append(filters["since"])

    if filters.get("q"):
        base += " AND LOWER(text) LIKE ?"
        args.append(f"%{filters['q'].lower()}%")

    conn = get_connection()
    total = conn.execute(f"SELECT COUNT(*) {base}", args).fetchone()[0]

    rows = conn.execute(
        f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        {base}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
        """,
        args + [limit, offset],
    ).fetchall()

    conn.close()
    return total, rows

def stats():
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]

    senders = conn.execute(
        """
        SELECT from_msisdn, COUNT(*)
        FROM messages
        GROUP BY from_msisdn
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """
    ).fetchall()

    first = conn.execute("SELECT MIN(ts) FROM messages").fetchone()[0]
    last = conn.execute("SELECT MAX(ts) FROM messages").fetchone()[0]

    conn.close()
    return total, senders, first, last
