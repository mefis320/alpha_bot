import sqlite3

DB = "study.db"

def connect():
    return sqlite3.connect(DB)

def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS folders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        parent_id INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER,
        file_id TEXT,
        name TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_folders(parent_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id,name FROM folders WHERE parent_id IS ?",
        (parent_id,)
    )
    data = cur.fetchall()
    conn.close()
    return data

def add_folder(name, parent_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO folders(name,parent_id) VALUES(?,?)",
        (name, parent_id)
    )
    conn.commit()
    conn.close()

def get_files(folder_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id,name FROM files WHERE folder_id=?",
        (folder_id,)
    )
    data = cur.fetchall()
    conn.close()
    return data

def add_file(folder_id, file_id, name):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files(folder_id,file_id,name) VALUES(?,?,?)",
        (folder_id, file_id, name)
    )
    conn.commit()
    conn.close()

def get_file(file_db_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT file_id FROM files WHERE id=?",
        (file_db_id,)
    )
    data = cur.fetchone()
    conn.close()
    return data[0] if data else None

def get_parent(folder_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT parent_id FROM folders WHERE id=?",
        (folder_id,)
    )
    data = cur.fetchone()
    conn.close()
    return data[0] if data else None