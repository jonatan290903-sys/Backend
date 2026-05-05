import os
import django
from django.core.management import call_command
from django.db import connection
from io import StringIO

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def reset_all_sequences():
    print("--- Iniciando sincronización de secuencias (SQL Profundo) ---")
    
    # Query para generar el SQL de reset de todas las secuencias
    find_sequences_sql = """
        SELECT 'SELECT SETVAL(' ||
               quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
               ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
               quote_ident(PGT.schemaname) || '.' || quote_ident(T.relname) || ';'
        FROM pg_class AS S,
             pg_depend AS D,
             pg_class AS T,
             pg_attribute AS C,
             pg_tables AS PGT
        WHERE S.relkind = 'S'
            AND S.oid = D.objid
            AND D.refobjid = T.oid
            AND D.refobjid = C.attrelid
            AND D.refobjsubid = C.attnum
            AND T.relname = PGT.tablename
        ORDER BY S.relname;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(find_sequences_sql)
            rows = cursor.fetchall()
            
            if not rows:
                print("No se encontraron secuencias.")
                return

            print(f"Sincronizando {len(rows)} tablas...")
            for row in rows:
                reset_sql = row[0]
                cursor.execute(reset_sql)
            
        print("\n--- ¡Sincronización PROFUNDA completada! ---")
        print("Todos los contadores de ID han sido actualizados al valor máximo actual.")
    except Exception as e:
        print(f"Error durante el reset: {e}")
    finally:
        connection.close()
        print("Conexión de sincronización cerrada.")

if __name__ == "__main__":
    reset_all_sequences()
