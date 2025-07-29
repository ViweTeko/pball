

# Powerball Historical Draw Analyzer

This project provides a Python script to create, manage, and analyze a SQLite database containing historical South African Powerball draw data. It allows you to store draw details, including Powerball Plus status and a draw sequence number, and query for the observed frequency of specific number combinations.

## Table of Contents

1.  [Features](https://www.google.com/search?q=%23features)
2.  [Database Schema](https://www.google.com/search?q=%23database-schema)
3.  [Installation](https://www.google.com/search?q=%23installation)
4.  [Usage](https://www.google.com/search?q=%23usage)
      * [Running the Script](https://www.google.com/search?q=%23running-the-script)
      * [Data Ingestion (Important)](https://www.google.com/search?q=%23data-ingestion-important)
      * [Analyzing Specific Sets](https://www.google.com/search?q=%23analyzing-specific-sets)
5.  [Project Structure](https://www.google.com/search?q=%23project-structure)
6.  [Important Considerations](https://www.google.com/search?q=%23important-considerations)
7.  [License](https://www.google.com/search?q=%23license)

## Features

  * Creates a SQLite database (`powerball_draws.db`) to store draw information.
  * Uses a normalized schema with two tables: `dates` (for draw metadata) and `draws` (for the numbers).
  * Manages foreign key relationships to ensure data integrity.
  * Automatically sorts main numbers before storage for consistent querying.
  * Creates a composite index on main numbers for efficient lookup of specific combinations.
  * Includes a function to simulate a configurable number of random Powerball draws for testing and demonstration.
  * Calculates the observed frequency of a target set of Powerball numbers based on the data in the database.

## Database Schema

The database consists of two tables:

### `dates` Table

Stores unique draw dates along with associated metadata.

```sql
CREATE TABLE dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL UNIQUE,          -- Date of the draw (YYYY-MM-DD)
    is_powerball_plus INTEGER NOT NULL,      -- 0 for False (regular Powerball), 1 for True (Powerball Plus)
    draw_sequence_num INTEGER UNIQUE         -- Official or sequential draw number
);
```

### `draws` Table

Stores the actual numbers drawn for each Powerball event, linked to the `dates` table via a foreign key.

```sql
CREATE TABLE draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER NOT NULL UNIQUE,         -- Foreign Key to dates.id (ensures one set of numbers per draw date)
    main_num1 INTEGER NOT NULL,
    main_num2 INTEGER NOT NULL,
    main_num3 INTEGER NOT NULL,
    main_num4 INTEGER NOT NULL,
    main_num5 INTEGER NOT NULL,
    powerball_num INTEGER NOT NULL,
    FOREIGN KEY (date_id) REFERENCES dates(id)
);
```

### Index

A composite index `idx_main_numbers` is created on `(main_num1, main_num2, main_num3, main_num4, main_num5)` in the `draws` table to optimize queries for specific number combinations.

## Installation

1.  **Python:** Ensure you have Python 3.6+ installed.
2.  **No External Libraries:** This project uses only built-in Python modules (`sqlite3`, `random`, `datetime`), so no `pip install` commands are strictly necessary.

## Usage

### Running the Script

1.  **Save the Code:** Save the Python script (the one provided in our previous conversations) as `powerball_analyzer.py`.
2.  **Execute:** Open your terminal or command prompt, navigate to the directory where you saved the file, and run:
    ```bash
    python powerball_analyzer.py
    ```

When you run the script, it will:

  * Create or connect to the `powerball_draws.db` file.
  * Ensure the `dates` and `draws` tables are set up.
  * Create the `idx_main_numbers` composite index.
  * By default, it will **simulate** `100,000` Powerball draws and add them to the database (you can adjust this number in the script).
  * Add a couple of specific draws (including your target set `[2, 18, 35, 41, 46]` + `1`) for demonstration.
  * Perform the analysis and print the observed frequency of your target set.
  * Print sample rows from both the `dates` and `draws` tables, and demonstrate a `JOIN` query.

### Data Ingestion (Important)

**The simulated draws are for demonstration and testing purposes only.** They are random and will *not* reflect the true historical distribution or actual draws.

For meaningful analysis, you need to import **real historical Powerball draw data for South Africa**.

**Steps to Import Real Data:**

1.  **Obtain Data:** Find a reliable source for historical South African Powerball results. This is often available as a CSV file or can be scraped from a website.
2.  **Modify `powerball_analyzer.py`:**
      * **Comment out or remove** the line `simulate_and_add_draws(num_simulated_draws)` in the `if __name__ == "__main__":` block.
      * Write a new section of code to read your historical data (e.g., using Python's `csv` module or `pandas`).
      * For each row of your historical data, extract:
          * `draw_date` (e.g., 'YYYY-MM-DD')
          * `is_powerball_plus` (determine if it was a Powerball Plus draw - `0` or `1`)
          * `draw_sequence_num` (if available in your data, otherwise you can generate a sequential number if needed)
          * `main_numbers` (as a list of 5 integers, ensure they are sorted: `sorted([n1, n2, n3, n4, n5])`)
          * `powerball_number`
      * Call the `add_draw()` function for each historical record:
        ```python
        # Example for importing from a CSV (conceptual)
        # import csv
        # with open('your_powerball_history.csv', 'r') as file:
        #     reader = csv.DictReader(file) # Assuming header row
        #     current_sequence = get_max_draw_sequence_num() + 1
        #     for row in reader:
        #         draw_date = row['Date'] # Adjust column name
        #         main_nums = [int(row['N1']), int(row['N2']), ...] # Parse and convert to int
        #         pb_num = int(row['Powerball'])
        #         is_pb_plus = 1 if row['GameType'] == 'Powerball_Plus' else 0 # Example logic
        #         add_draw(draw_date, is_pb_plus, current_sequence, main_nums, pb_num)
        #         current_sequence += 1
        ```

### Analyzing Specific Sets

To analyze the observed frequency of a specific set of numbers, modify the `TARGET_MAIN_NUMBERS` and `TARGET_POWERBALL` variables at the top of the `powerball_analyzer.py` script:

```python
# --- Configuration ---
TARGET_MAIN_NUMBERS = sorted([2, 18, 35, 41, 46]) # Your desired main numbers (always sorted)
TARGET_POWERBALL = 1                             # Your desired Powerball number
```

Then, run the script again to see the analysis results based on the data in your database.

## Project Structure

```
.
├── powerball_analyzer.py  # The main Python script
├── README.md              # This file
└── powerball_draws.db     # The SQLite database file (generated upon first run)
```

## Important Considerations

  * **Observed vs. Theoretical Odds:** The observed frequency you get from the script will likely be very different from the theoretical odds (1 in 42,375,200). For the observed frequency to approach the theoretical odds, you would need an extremely large dataset of real historical draws (millions, potentially billions, of draws).
  * **Data Integrity:** The script includes robust error handling for unique constraints (e.g., preventing duplicate draw dates or sequence numbers) and uses foreign keys to maintain relationships between tables.
  * **Performance:** The composite index on `main_num1` through `main_num5` is crucial for efficient lookups of specific number combinations as your database grows.

## License

This project is open-source and available under the [MIT License](LICENSE.md) (Optional: If you plan to make it public, consider adding a `LICENSE.md` file with the license text).

