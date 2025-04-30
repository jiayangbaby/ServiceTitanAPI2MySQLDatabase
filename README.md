ServiceTitan API to MySQL
This repository contains Python scripts used to extract various datasets from the ServiceTitan API based on specific endpoints and load the extracted data into a MySQL database.

Overview
Data Extraction: Python scripts are used to fetch data from the ServiceTitan API using different API endpoints.

MySQL Integration: The extracted data is processed and then loaded into a MySQL database for further querying and analysis.

Python Files Overview
business_unit_id.py: Extracts business unit IDs from the ServiceTitan API.

calls_jia.py: Fetches call-related data from the ServiceTitan API.

campaign_ids.py: Retrieves campaign-related data from the ServiceTitan API.

job_type_id.py: Extracts job type IDs from the ServiceTitan API.

jobs_data.py: Extracts detailed jobs data using relevant API endpoints.

load_to_mysql.py: Main script that processes the extracted data and loads it into the MySQL database.

.env Configuration
Ensure that you configure the environment variables (API keys and MySQL credentials) in the .env file to securely manage your sensitive data. You can refer to the .env file for configuring your ServiceTitan API credentials and MySQL database connection details.

Setup and Usage
Configure Environment Variables:

Populate the .env file with your API keys for ServiceTitan and MySQL connection credentials.

Install Dependencies: Install the required Python libraries by running:

bash
Copy
pip install -r requirements.txt
Run the Extraction and Loading Process:

Use the load_to_mysql.py script to fetch data from the ServiceTitan API and load it into the MySQL database:

bash
Copy
python load_to_mysql.py
Verify Data in MySQL: After running the script, you can check the MySQL database to verify that the data has been successfully loaded.

Requirements
Python 3.x

MySQL Database

ServiceTitan API credentials (configured in .env)

Contributing
Feel free to fork this repository, make improvements, or submit issues for any bugs or new features.

