from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
import csv
import pandas as pd # Import pandas for CSV reading

# Pydantic models for request and response data validation
class Client(BaseModel):
    """Pydantic model for Client data."""
    id: int
    name: str

class Product(BaseModel):
    """Pydantic model for Product data."""
    id: int
    name: str
    price: float

class Sale(BaseModel):
    """Pydantic model for basic Sale data (from CSV)."""
    id: int
    client_id: int
    product_id: int
    sale_amount: float

class SaleOutput(Sale):
    """Pydantic model for enriched Sale data, including client and product names for API response."""
    client_name: str
    product_name: str

# SQLAlchemy models for database table structure
Base = declarative_base() # Base class for SQLAlchemy model definitions

class ClientEntity(Base):
    """SQLAlchemy ORM model for the 'clients' table."""
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Relationship for potential future use (e.g., if sales were in DB):
    # sales = relationship("SaleEntity", back_populates="client")

class ProductEntity(Base):
    """SQLAlchemy ORM model for the 'products' table."""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    # Relationship for potential future use:
    # sales = relationship("SaleEntity", back_populates="product")

# SaleEntity is not defined as sales data comes from CSV for this POC.
# If sales were stored in the database, a SaleEntity model would be defined here.
# class SaleEntity(Base):
#     __tablename__ = "sales"
#     id = Column(Integer, primary_key=True, index=True)
#     client_id = Column(Integer, ForeignKey("clients.id"))
#     product_id = Column(Integer, ForeignKey("products.id"))
#     sale_amount = Column(Float) # Renamed from quantity for clarity
#     client = relationship("ClientEntity", back_populates="sales")
#     product = relationship("ProductEntity", back_populates="sales")

# --- Configuration Placeholders ---
# IMPORTANT: Update these placeholders with your actual configuration.

# Database connection string for PostgreSQL.
# Format: "postgresql://user:password@host:port/database"
DATABASE_URL = "postgresql://user:password@host:port/database"  # <<< UPDATE THIS (PLACEHOLDER)

# CSV file path for sales data.
CSV_FILE_PATH = "path/to/your/sales.csv"  # <<< UPDATE THIS (PLACEHOLDER)

# --- Database Setup ---
# SQLAlchemy engine for database interaction.
engine = create_engine(DATABASE_URL)

# SessionLocal factory to create database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables based on SQLAlchemy models.
# For a Proof-of-Concept, this is convenient. In a production environment,
# database migrations (e.g., using Alembic) are strongly recommended.
Base.metadata.create_all(bind=engine) # Comment out if using Alembic for migrations.

def get_db():
    """
    FastAPI dependency to get a database session.
    Ensures the database session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close() # Close the session

# Initialize FastAPI application
app = FastAPI(
    title="FastAPI POC: DB and CSV Aggregation",
    description="A Proof-of-Concept API to aggregate data from PostgreSQL and a CSV file.",
    version="0.1.0"
)

# --- CSV Data Loading ---
def load_sales_from_csv(file_path: str) -> list[dict]:
    """
    Reads sales data from a specified CSV file path using pandas.
    Converts the DataFrame to a list of dictionaries (each dictionary represents a row).
    Includes basic error handling for FileNotFoundError and other potential exceptions during CSV processing.
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records') # Convert DataFrame to list of dicts
    except FileNotFoundError:
        print(f"Warning: CSV file not found at '{file_path}'. Returning an empty list.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the CSV file at '{file_path}': {e}")
        return []

# --- API Endpoint Definitions ---

# Placeholder POST endpoints from initial setup (not implemented in this POC)
# @app.post("/clients/", response_model=Client)
# def create_client(client: Client, db: Session = Depends(get_db)):
#     # db_client = ClientEntity(**client.dict())
#     # db.add(db_client)
#     # db.commit()
#     # db.refresh(db_client)
#     # return db_client
#     pass

@app.get("/clients", response_model=list[Client], summary="Get all clients", tags=["Clients"])
def read_clients(db: Session = Depends(get_db)):
    """
    Retrieve all clients from the database.
    """
    clients = db.query(ClientEntity).all()
    return clients

# @app.post("/products/", response_model=Product)
# def create_product(product: Product, db: Session = Depends(get_db)):
#     # db_product = ProductEntity(**product.dict())
#     # db.add(db_product)
#     # db.commit()
#     # db.refresh(db_product)
#     # return db_product
#     pass

@app.get("/products", response_model=list[Product], summary="Get all products", tags=["Products"])
def read_products(db: Session = Depends(get_db)):
    """
    Retrieve all products from the database.
    """
    products = db.query(ProductEntity).all()
    return products

# @app.post("/sales/", response_model=Sale) # Basic sale from CSV, not enriched
# def create_sale(sale: Sale, db: Session = Depends(get_db)): # This would typically write to DB or process
#     # For this POC, sales are read from CSV, so a POST for individual sale creation might differ.
#     # If sales were to be added to a DB:
#     # db_sale = SaleEntity(**sale.dict())
#     # db.add(db_sale)
#     # db.commit()
#     # db.refresh(db_sale)
#     # return db_sale
#     pass

@app.get("/sales", response_model=list[SaleOutput], summary="Get all sales with aggregated client and product data", tags=["Sales"])
def read_sales(db: Session = Depends(get_db)):
    """
    Retrieve sales data from the CSV file and enrich it with client and product details from the database.
    - Loads sales records from the CSV file specified by `CSV_FILE_PATH`.
    - For each sale record, it queries the database to find the corresponding client and product.
    - If a client or product is found, their names are added to the sale record.
    - If not found, names are set to "N/A" to indicate missing related data.
    - Returns a list of `SaleOutput` objects containing the aggregated information.
    """
    sales_data_from_csv = load_sales_from_csv(CSV_FILE_PATH)
    enriched_sales_data = []

    if not sales_data_from_csv:
        # Early exit if CSV is empty or not found, avoids further processing.
        return []

    for sale_record_csv in sales_data_from_csv:
        # Fetch client details from the database
        client_db = db.query(ClientEntity).filter(ClientEntity.id == sale_record_csv.get('client_id')).first()
        # Fetch product details from the database
        product_db = db.query(ProductEntity).filter(ProductEntity.id == sale_record_csv.get('product_id')).first()

        # Create the enriched SaleOutput object
        # Assumes CSV headers match Pydantic model fields: 'id', 'client_id', 'product_id', 'sale_amount'
        # Uses .get() for safety if a key might be missing in a CSV row, though pandas usually ensures all columns.
        sale_output_enriched = SaleOutput(
            id=sale_record_csv.get('id', 0), # Default to 0 or handle error if 'id' is critical and missing
            client_id=sale_record_csv.get('client_id'),
            product_id=sale_record_csv.get('product_id'),
            sale_amount=sale_record_csv.get('sale_amount', 0.0), # Default to 0.0 or handle error
            client_name=client_db.name if client_db else "N/A",
            product_name=product_db.name if product_db else "N/A"
        )
        enriched_sales_data.append(sale_output_enriched)

    return enriched_sales_data

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    Placeholder for actions to be performed on application startup.
    For example, this could be used to:
    - Pre-load some data into memory.
    - Initialize connections to other services.
    - Run a one-time setup task.
    For this POC, it currently closes a DB session which might not be necessary
    if load_data_from_csv is not used at startup or is refactored.
    If `load_data_from_csv` were to populate the DB from CSV on startup,
    it would be called here.
    """
    # Example: Load initial data into the database if tables are empty.
    # db = SessionLocal()
    # try:
    #     if db.query(ClientEntity).count() == 0:
    #         print("Database appears empty, attempting to load initial data (if implemented).")
    #         # load_initial_db_data(db) # A hypothetical function
    # finally:
    #     db.close()
    print("FastAPI application startup complete.")
    # The original db session handling here was minimal; expanded for clarity.
    # db = SessionLocal()
    # # load_data_from_csv(db, CSV_FILE_PATH) # This function was for reading CSV not populating DB
    # db.close()
    pass
