import sqlite3
import json
from models import Entries, Moods

def get_all_entries():
    # Open a connection to the database
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()
        db_cursor.execute("""
        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label
        FROM Entries e
        JOIN Moods m 
            ON m.id = e.mood_id
        """)
        entries = []
        dataset = db_cursor.fetchall()
        for row in dataset:
            entry = Entries(row['id'], row['concept'], row['entry'], row['mood_id'], row['date'])
            mood = Moods(row['mood_id'], row['label'])
            entry.mood = mood.__dict__
            entries.append(entry.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(entries)

def get_single_entry(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label
        FROM Entries e
        JOIN Moods m 
            ON m.id = e.mood_id
        WHERE e.id = ?
        """, ( id, ))

        # Load the single result into memory
        data = db_cursor.fetchone()
        entry = Entries(data['id'], data['concept'], data['entry'],
                            data['mood_id'], data['date'])
        mood = Moods(data['mood_id'], data['label'])
        entry.mood = mood.__dict__
        return json.dumps(entry.__dict__)

def delete_entry(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM Entries
        WHERE id = ?
        """, (id, ))

def create_entry(new_entry):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Entries
            ( concept, entry, mood_id, date )
        VALUES
            ( ?, ?, ?, ? );
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['mood_id'], new_entry['date'] ))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the entry dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_entry['id'] = id
        
        for tag_id in new_entry['tag']:
            db_cursor.execute("""
                insert into Entries_Tag values (null, ?)
            """, (tag_id, new_entry['id']))

    return json.dumps(new_entry)

def update_entry(id, new_entry):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Entries
            SET
                concept = ?,
                entry = ?,
                mood_id = ?,
                date = ?
        WHERE id = ?
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['mood_id'], new_entry['date'], id, ))

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True