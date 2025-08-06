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

def simulate_and_add_draws(num_draws_to_simulate):
    """
    Simulates 'num_draws_to_simulate' Powerball draws and adds them to the database.
    This is for demonstration/testing. For real analysis, you need actual historical data.
    """
    print(f"\nSimulating and adding {num_draws_to_simulate} random draws...")
    start_date = datetime(2020, 1, 1) # Start date for simulated draws
    current_draw_seq_num = get_max_draw_sequence_num() + 1 # Start from last + 1

    for i in range(num_draws_to_simulate):
        draw_date = (start_date + timedelta(weeks=i)).strftime('%Y-%m-%d')

        # Simulate Powerball Plus status (e.g., 50% chance)
        is_pb_plus = random.choice([0, 1]) # 0 for False, 1 for True

        # Simulate main numbers (5 unique numbers from 1 to 50)
        main_nums = sorted(random.sample(range(1, 51), 5))

        # Simulate Powerball number (1 number from 1 to 20)
        pb_num = random.randint(1, 20)

        add_draw(draw_date, is_pb_plus, current_draw_seq_num, main_nums, pb_num)
        current_draw_seq_num += 1 # Increment for next draw
    print(f"Finished simulating {num_draws_to_simulate} draws.")

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

    # 3. Simulate draws (for testing and demonstration)
    # !!! IMPORTANT: For real analysis, you must replace this with actual historical data.
    # A few thousand simulated draws won't yield meaningful "odds" for a specific set.
    # Adding your target set explicitly to ensure it exists for testing
    # Note: If you run simulations that cover this date, it might cause a unique constraint error on draw_sequence_num
    # For testing, it's safer to ensure a unique date/sequence num
    print("\nAttempting to add target specific draw for testing...")
    add_draw('2024-06-19', 0, 999999999, [2, 18, 35, 41, 46], 1) # High draw_sequence_num to avoid conflict
    add_draw('2025-06-18', 1, 999999998, [10, 20, 30, 40, 50], 15)


    # --- Analysis ---
    total_draws = get_total_draws_in_db()
    occurrences = analyze_specific_set_occurrence()

    print(f"\n--- Analysis Results ---")
    print(f"Total draws (entries in 'draws' table): {total_draws}")
    print(f"Target Main Numbers: {TARGET_MAIN_NUMBERS}")
    print(f"Target Powerball Number: {TARGET_POWERBALL}")
    print(f"Occurrences of target set in database: {occurrences}")

    if total_draws > 0:
        observed_frequency = occurrences / total_draws
        print(f"Observed frequency of target set: {occurrences}/{total_draws} = {observed_frequency:.5f}")
    else:
        print("No draws in the database to calculate observed frequency.")

    print("\n--- Important Note ---")
    print(f"Theoretical odds of winning the Powerball jackpot: 1 in 42,375,200")
    print("The 'observed frequency' from a limited dataset (especially simulated random data)")
    print("will almost certainly differ greatly from the theoretical odds.")
    print("For observed frequency to approach theoretical odds, you would need millions of real historical draws.")

    # --- Example of how to view contents of the new tables ---
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    print("\n--- Sample from 'dates' table (first 5 rows) ---")
    cursor.execute("SELECT * FROM dates LIMIT 5")
    dates_rows = cursor.fetchall()
    print("id | draw_date  | is_powerball_plus | draw_sequence_num")
    print("---|------------|-------------------|------------------")
    for row in dates_rows:
        print(f"{row[0]:<2} | {row[1]:<10} | {row[2]:<17} | {row[3]}")

    print("\n--- Sample from 'draws' table (first 5 rows) ---")
    cursor.execute("SELECT * FROM draws LIMIT 5")
    draws_rows = cursor.fetchall()
    print("id | date_id | m1 | m2 | m3 | m4 | m5 | pb")
    print("---|---------|----|----|----|----|----|----")
    for row in draws_rows:
        print(f"{row[0]:<2} | {row[1]:<7} | {row[2]:<2} | {row[3]:<2} | {row[4]:<2} | {row[5]:<2} | {row[6]:<2} | {row[7]}")

    print("\n--- Querying with JOIN for a specific draw details ---")
    specific_draw_date = '2024-06-19'
    cursor.execute(f'''
        SELECT d.draw_date, d.is_powerball_plus, d.draw_sequence_num,
               dr.main_num1, dr.main_num2, dr.main_num3, dr.main_num4, dr.main_num5, dr.powerball_num
        FROM dates AS d
        JOIN draws AS dr ON d.id = dr.date_id
        WHERE d.draw_date = ?
    ''', (specific_draw_date,))
    specific_draw_result = cursor.fetchone()
    if specific_draw_result:
        print(f"Details for {specific_draw_date}:")
        print(f"  Powerball Plus: {bool(specific_draw_result[1])}")
        print(f"  Draw Sequence Num: {specific_draw_result[2]}")
        print(f"  Main Numbers: {specific_draw_result[3:8]}")
        print(f"  Powerball: {specific_draw_result[8]}")
    else:
        print(f"Draw for {specific_draw_date} not found.")

    conn.close()