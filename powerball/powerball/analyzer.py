#!/usr/bin/env python3
import sqlite3
import random
from datetime import datetime, timedelta

# --- Configuration ---
DATABASE_NAME = 'powerball_draws.db'
TARGET_MAIN_NUMBERS = sorted([2, 18, 35, 41, 46]) # Sort for consistent comparison
TARGET_POWERBALL = 1

# --- Database Functions ---

def create_database():
    """Creates the SQLite database and the 'draws' and 'dates' tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Create 'dates' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT NOT NULL UNIQUE,
            is_powerball_plus INTEGER NOT NULL, -- 0 for False, 1 for True
            draw_sequence_num INTEGER UNIQUE
        )
    ''')

    # Create 'draws' table (modified to use date_id as FK)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER NOT NULL UNIQUE, -- Foreign Key to dates.id
            main_num1 INTEGER NOT NULL,
            main_num2 INTEGER NOT NULL,
            main_num3 INTEGER NOT NULL,
            main_num4 INTEGER NOT NULL,
            main_num5 INTEGER NOT NULL,
            powerball_num INTEGER NOT NULL,
            FOREIGN KEY (date_id) REFERENCES dates(id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' and tables 'draws', 'dates' ensured.")

def add_draw(draw_date, is_powerball_plus, draw_sequence_num, main_numbers, powerball_number):
    """
    Adds a single Powerball draw to the database, managing both dates and draws tables.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Ensure FK enforcement
    cursor = conn.cursor()

    try:
        # 1. Insert into 'dates' table first or get existing date_id
        cursor.execute('''
            INSERT OR IGNORE INTO dates (draw_date, is_powerball_plus, draw_sequence_num)
            VALUES (?, ?, ?)
        ''', (draw_date, is_powerball_plus, draw_sequence_num))
        conn.commit()

        # Get the ID of the date entry (whether newly inserted or existing)
        cursor.execute("SELECT id FROM dates WHERE draw_date = ?", (draw_date,))
        date_id = cursor.fetchone()[0]

        # 2. Insert into 'draws' table using the date_id
        sorted_main = sorted(main_numbers) # Ensure main numbers are sorted

        cursor.execute('''
            INSERT INTO draws (date_id, main_num1, main_num2, main_num3, main_num4, main_num5, powerball_num)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_id, sorted_main[0], sorted_main[1], sorted_main[2], sorted_main[3], sorted_main[4], powerball_number))
        conn.commit()
        # print(f"Added draw for {draw_date} (PB+:{bool(is_powerball_plus)}, Draw #{draw_sequence_num}): {sorted_main} + {powerball_number}")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: draws.date_id" in str(e):
            print(f"Skipped draw for {draw_date}: Draw numbers already exist for this date.")
        else:
            print(f"Error adding draw for {draw_date} (IntegrityError): {e}")
            conn.rollback() # Rollback the transaction in case of error
    except Exception as e:
        print(f"Error adding draw for {draw_date}: {e}")
        conn.rollback()
    finally:
        conn.close()

def add_draws_interactively():
    """
    Prompts the user for Powerball draw details and adds them to the database.
    Allows adding multiple draws until the user chooses to stop.
    """
    print("\n--- Add New Powerball Draws Interactively ---")
    while True:
        try:
            draw_date = input("Enter Draw Date (YYYY-MM-DD): ")
            # Basic date format validation
            datetime.strptime(draw_date, '%Y-%m-%d')

            is_powerball_plus_input = input("Is this a Powerball Plus draw? (yes/no): ").lower()
            is_powerball_plus = 1 if is_powerball_plus_input in ['yes', 'y'] else 0

            draw_sequence_num = int(input("Enter Draw Sequence Number: "))

            main_numbers_str = input("Enter Main Numbers (comma-separated, e.g., 1,2,3,4,5): ")
            main_numbers = [int(num.strip()) for num in main_numbers_str.split(',')]
            if len(main_numbers) != 5:
                raise ValueError("Please enter exactly 5 main numbers.")
            if not all(1 <= num <= 50 for num in main_numbers):
                 raise ValueError("Main numbers must be between 1 and 50.")

            powerball_number = int(input("Enter Powerball Number (1-20): "))
            if not 1 <= powerball_number <= 20:
                raise ValueError("Powerball number must be between 1 and 20.")

            add_draw(draw_date, is_powerball_plus, draw_sequence_num, main_numbers, powerball_number)
            print(f"Successfully added draw for {draw_date}.")

        except ValueError as ve:
            print(f"Input error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        add_another = input("Add another draw? (yes/no): ").lower()
        if add_another in ['no', 'n']:
            break


def get_max_draw_sequence_num():
    """Returns the highest draw_sequence_num in the database, or 0 if none exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(draw_sequence_num) FROM dates")
    max_num = cursor.fetchone()[0]
    conn.close()
    return max_num if max_num is not None else 0

def get_total_draws_in_db():
    """Returns the total number of draws currently in the 'draws' table."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM draws")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def create_composite_index():
    """Creates a composite index on the five main number columns."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Ensure FK enforcement
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_main_numbers
            ON draws (main_num1, main_num2, main_num3, main_num4, main_num5);
        ''')
        conn.commit()
        print("Composite index 'idx_main_numbers' created successfully (or already exists).")
    except sqlite3.Error as e:
        print(f"Error creating index: {e}")
    finally:
        conn.close()

def analyze_specific_set_occurrence():
    """
    Queries the 'draws' table to find how many times the target set of numbers
    has appeared.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # The query checks for the exact match of the sorted main numbers
    # and the Powerball number from the 'draws' table.
    cursor.execute('''
        SELECT COUNT(*)
        FROM draws
        WHERE main_num1 = ? AND main_num2 = ? AND main_num3 = ? AND main_num4 = ? AND main_num5 = ?
          AND powerball_num = ?
    ''', (TARGET_MAIN_NUMBERS[0], TARGET_MAIN_NUMBERS[1], TARGET_MAIN_NUMBERS[2],
          TARGET_MAIN_NUMBERS[3], TARGET_MAIN_NUMBERS[4], TARGET_POWERBALL))

    occurrences = cursor.fetchone()[0]
    conn.close()
    return occurrences

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Create database and tables
    create_database()
    # 2. Create the composite index
    create_composite_index()

    # Start interactive draw input
    add_draws_interactively()