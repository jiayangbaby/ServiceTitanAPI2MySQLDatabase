import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password = os.getenv("SQL_PASSWORD"),
    database="MRP_data",
    allow_local_infile=True
)
cursor = conn.cursor()

# Path to folder with monthly CSV files
folder_path = os.getenv("OUTPUT_CSV")

def generate_sql_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "INT"
    elif pd.api.types.is_float_dtype(series):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "DATETIME"
    elif pd.api.types.is_object_dtype(series):
        max_len = series.dropna().astype(str).map(len).max()
        if max_len and max_len > 255:
            return "TEXT"
        else:
            return f"VARCHAR({max_len if max_len and max_len > 0 else 255})"
    else:
        return "VARCHAR(255)"


# Loop through all CSV files
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)

        table_name = os.path.splitext(file)[0]
        df.columns = [col.strip().replace(" ", "_") for col in df.columns]

        # Auto-generate CREATE TABLE statement
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

        column_defs = ", ".join(
            f"`{col}` {generate_sql_type(df[col])}" for col in df.columns
        )
        
        if 'id' in df.columns:
            column_defs += ", PRIMARY KEY(`id`)"

        create_sql = f"CREATE TABLE `{table_name}` ({column_defs});"
        cursor.execute(create_sql)

        # Prepare and insert data
        columns = ', '.join(f"`{col}`" for col in df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        cursor.execute(f"""
            LOAD DATA LOCAL INFILE '{file_path.replace("\\", "/")}'
            INTO TABLE `{table_name}`
            FIELDS TERMINATED BY ',' 
            ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
            IGNORE 1 ROWS;
        """)

# Commit and close
conn.commit()
cursor.close()
conn.close()
