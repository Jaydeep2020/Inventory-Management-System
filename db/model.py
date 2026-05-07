

from db_connection import get_cursor

# -- =====================================================
# -- INVENTORY MANAGEMENT SYSTEM (PostgreSQL)
# -- Production-Ready Schema
# -- Includes:
# -- 1. Products
# -- 2. Inventories
# -- 3. Inventory Stock
# -- 4. Stock Transactions
# -- =====================================================
#
#
# -- =====================================================
# -- OPTIONAL: ENUM TYPES
# -- Better than plain VARCHAR for fixed values
# -- =====================================================

enum_type1 = """
CREATE TYPE category_type AS ENUM (
    'Grocery',
    'Electrical'
)
"""

enum_type2 = """
CREATE TYPE transaction_type AS ENUM (
    'ADD',
    'REMOVE',
    'TRANSFER',
    'ADJUSTMENT'
);
"""

# -- =====================================================
# -- 1. PRODUCTS TABLE
# -- Global product definition
# -- =====================================================

create_product_table = """
CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    
    name VARCHAR(255) NOT NULL,
    
    category category_type NOT NULL,
    
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    
    -- Used mainly for grocery products
    expiry_date DATE,
    
    -- Used mainly for Electrical products
    warranty_months INT CHECK (warranty_months >= 0),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# -- =====================================================
# -- 2. INVENTORIES TABLE
# -- Stores warehouse / branch / store information
# -- =====================================================

create_inventory_table = """
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_inventory UNIQUE (name, location)
);"""

# -- =====================================================
# -- 3. INVENTORY STOCK TABLE
# -- Junction table between product + inventory
# -- Stores actual stock quantity
# -- =====================================================

create_table_inventory_stock = """
CREATE TABLE inventory_stock (
    id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    product_id INT NOT NULL,

    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES product(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_inventory_product
        UNIQUE (inventory_id, product_id)
);
"""

# -- =====================================================
# -- 4. STOCK TRANSACTIONS TABLE
# -- Tracks every stock movement
# -- Important for audit/history
# -- Do NOT use cascade here
# -- =====================================================

create_table_transaction = """
CREATE TABLE stock_transactions (
    id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,

    -- Nullable because ADD may not have source
    source_inventory_id INT,

    -- Nullable because REMOVE may not have destination
    destination_inventory_id INT,

    quantity INT NOT NULL CHECK (quantity > 0),

    transaction_type transaction_type NOT NULL,

    remarks TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transaction_product
        FOREIGN KEY (product_id)
        REFERENCES product(id),

    CONSTRAINT fk_source_inventory
        FOREIGN KEY (source_inventory_id)
        REFERENCES inventory(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_destination_inventory
        FOREIGN KEY (destination_inventory_id) 
        REFERENCES inventory(id)
        ON DELETE SET NULL
);
"""

# -- =====================================================
# -- INDEXES (Important for performance)
# -- =====================================================

index_query = """

CREATE INDEX idx_inventory_stock_product
ON inventory_stock(product_id);

CREATE INDEX idx_inventory_stock_inventory
ON inventory_stock(inventory_id);

CREATE INDEX idx_stock_transactions_product
ON stock_transactions(product_id);

CREATE INDEX idx_stock_transactions_created_at
ON stock_transactions(created_at);
"""



def create_db_schema():
    with get_cursor() as cursor:
        cursor.execute(enum_type1)
        cursor.execute(enum_type2)
        cursor.execute(create_product_table)
        cursor.execute(create_inventory_table)
        cursor.execute(create_table_inventory_stock)
        cursor.execute(create_table_transaction)
        cursor.execute(index_query)


if __name__ == "__main__":
    create_db_schema()
    print("Product table created successfully!")