# jules-agent-playground

1. RESTful API for Internal Data Retrieval and Aggregation
   
**Description:**
A backend service that provides a unified RESTful API to aggregate data from two internal data sources (relational databases and CSV files). The API enables retrieval of business-critical information, such as client details, product inventory, or sales figures, in a standardized JSON format.
Technical Objectives & Scope: 
Implement a RESTful service using the programming language and framework most familiar to the development team, such as .NET, Java, Python (Flask/FastAPI), Node.js (Express) or anything else.
Integrate database queries (PostgreSQL) and a flat file data source.
Expose the following endpoints: `/clients`, `/products`, and `/sales`. These endpoints should return JSON payloads without any filtering, providing either a list of records or a single record. `/sales` should include the client and product details in the response.
Use Swagger/OpenAPI for API documentation.

**Business Value and Reasoning:**
Consolidates dispersed data sources into a single access layer.
Provides immediate value for internal teams who need consistent data endpoints.
Swagger documentation simplifies both onboarding and integration into downstream systems.

# FastAPI POC: DB and CSV Aggregation

This project is a Proof-of-Concept (POC) to demonstrate a FastAPI application that aggregates data from a PostgreSQL database and a CSV file.

## Setup and Running

1.  **Prerequisites**:
    *   Python 3.7+
    *   Access to a PostgreSQL database.
    *   A CSV file named `sales.csv` (or update the path in `main.py`).

2.  **Installation**:
    Install the required Python libraries:
    ```bash
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas
    ```

3.  **Configuration**:
    *   **Database URL**: Open `main.py` and update the `DATABASE_URL` placeholder with your actual PostgreSQL connection string.
      ```python
      # Example: DATABASE_URL = "postgresql://youruser:yourpassword@localhost:5432/yourdatabase"
      DATABASE_URL = "postgresql://user:password@host:port/database" # <<< UPDATE THIS
      ```
    *   **CSV File Path**: In `main.py`, update the `CSV_FILE_PATH` placeholder to point to your sales CSV file.
      ```python
      # Example: CSV_FILE_PATH = "data/sales.csv"
      CSV_FILE_PATH = "path/to/your/sales.csv" # <<< UPDATE THIS
      ```

4.  **Create Mock Data (Important for POC)**:
    *   **Database**: Ensure you have `clients` and `products` tables in your PostgreSQL database that match the SQLAlchemy models in `main.py`. Populate them with some sample data.
        *   `clients` table: `id` (Integer, Primary Key), `name` (String)
        *   `products` table: `id` (Integer, Primary Key), `name` (String), `price` (Float)
    *   **CSV File**: Create a `sales.csv` file with columns like: `id`, `client_id`, `product_id`, `sale_amount`. Populate it with sample data ensuring `client_id` and `product_id` values correspond to entries in your database tables.
        Example `sales.csv`:
        ```csv
        id,client_id,product_id,sale_amount
        1,1,101,50.00
        2,2,102,75.50
        3,1,103,120.25
        ```

5.  **Run the Application**:
    Use Uvicorn to run the FastAPI application:
    ```bash
    uvicorn main:app --reload
    ```

6.  **Access API**:
    *   The API will be available at `http://127.0.0.1:8000`.
    *   Interactive API documentation (Swagger UI) can be accessed at `http://127.0.0.1:8000/docs`.
    *   Endpoints:
        *   `GET /clients`
        *   `GET /products`
        *   `GET /sales`
