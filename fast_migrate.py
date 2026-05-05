import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración SQLite
sqlite_conn = sqlite3.connect('db.sqlite3')
sqlite_cur = sqlite_conn.cursor()

# Configuración Postgres (Supabase)
pg_conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
pg_cur = pg_conn.cursor()

def migrate():
    # Desactivar restricciones temporalmente
    print("Desactivando restricciones en Postgres...")
    pg_cur.execute("SET session_replication_role = 'replica';")

    # Obtener lista de tablas de SQLite
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [t[0] for t in sqlite_cur.fetchall()]

    # Tablas a excluir (ya manejadas por migraciones o innecesarias)
    exclude_tables = ['django_migrations', 'django_content_type', 'auth_permission']
    
    for table in tables:
        if table in exclude_tables:
            continue
            
        print(f"Migrando tabla: {table}...")
        
        # Limpiar tabla en Postgres (por si acaso)
        # pg_cur.execute(f"TRUNCATE TABLE \"{table}\" CASCADE;")
        
        # Obtener datos de SQLite
        sqlite_cur.execute(f"SELECT * FROM \"{table}\";")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            continue
            
        # Preparar INSERT múltiple
        columns = [d[0] for d in sqlite_cur.description]
        placeholders = ",".join(["%s"] * len(columns))
        columns_str = ",".join([f"\"{c}\"" for c in columns])
        
        query = f"INSERT INTO \"{table}\" ({columns_str}) VALUES ({placeholders})"
        
        # Insertar en lotes de 1000
        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            pg_cur.executemany(query, batch)
        
        print(f"  {len(rows)} registros migrados.")

    # Reactivar restricciones
    print("Reactivando restricciones...")
    pg_cur.execute("SET session_replication_role = 'origin';")
    
    # Actualizar secuencias
    print("Actualizando secuencias...")
    pg_cur.execute("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename, columnname FROM (
                SELECT t.relname AS tablename, a.attname AS columnname,
                       format_type(a.atttypid, a.atttypmod) AS datatype
                FROM pg_class t
                JOIN pg_attribute a ON a.attrelid = t.oid
                WHERE t.relkind = 'r' AND a.attnum > 0 AND NOT a.attisdropped
                AND a.attname = 'id' -- Asumimos que la PK es 'id'
                AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ) s WHERE datatype LIKE 'bigint' OR datatype LIKE 'integer')
            LOOP
                EXECUTE 'SELECT setval(pg_get_serial_sequence(''' || r.tablename || ''', ''' || r.columnname || '''), COALESCE(MAX(' || r.columnname || '), 1)) FROM ' || r.tablename;
            END LOOP;
        END $$;
    """)

    pg_conn.commit()
    print("¡Migración completada con éxito!")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Error durante la migración: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()
