import aiosqlite
import os

DB_PATH = "data/shio.db"

async def init_db():
    # Asegurar que el directorio data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created TEXT
        )
        """)
        
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY (conversation_id)
            REFERENCES conversations(id)
        )
        """)
        
        await db.commit()

async def get_db():
    # Retornamos el contexto directamente para evitar doble inicio de hilos
    return aiosqlite.connect(DB_PATH)

async def save_conversation_db(conv_id: str, user_id: str, title: str, created: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO conversations (id, user_id, title, created) VALUES (?, ?, ?, ?)", (conv_id, user_id, title, created))
        await db.commit()

async def save_message_db(conv_id: str, role: str, content: str, timestamp: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)", (conv_id, role, content, timestamp))
        await db.commit()

async def get_all_history_db(user_id: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            cursor = await db.execute("SELECT id, title, created FROM conversations WHERE user_id = ? ORDER BY created DESC", (user_id,))
        else:
            cursor = await db.execute("SELECT id, title, created FROM conversations ORDER BY created DESC")
        return await cursor.fetchall()

async def get_messages_db(conv_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT role, content, timestamp FROM messages WHERE conversation_id = ?", (conv_id,))
        return await cursor.fetchall()

async def delete_conversation_db(conv_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        await db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        await db.commit()

async def rename_conversation_db(conv_id: str, new_title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conv_id))
        await db.commit()
