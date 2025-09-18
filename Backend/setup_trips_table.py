import sys
import os
sys.path.append('.')

from database.connection import db

def check_and_create_trips_table():
    try:
        print('Checking if trips table exists...')
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'trips';
            """)
            result = cursor.fetchone()
            
            if result:
                print(f'Trips table already exists: {result["table_name"]}')
                
                # Show table structure
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'trips'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print('Table structure:')
                for col in columns:
                    print(f'  {col["column_name"]} ({col["data_type"]}) - Nullable: {col["is_nullable"]}')
            else:
                print('Trips table does not exist - creating it now...')
                
                # Read and execute SQL file
                with open('create_trips_table.sql', 'r') as file:
                    sql = file.read()
                print(f'SQL content length: {len(sql)} characters')
                
                cursor.execute(sql)
                conn.commit()
                print('Trips table created successfully!')
                
                # Verify creation
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'trips'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print('New table structure:')
                for col in columns:
                    print(f'  {col["column_name"]} ({col["data_type"]}) - Nullable: {col["is_nullable"]}')
        
        print('SUCCESS: Trips table is ready!')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_create_trips_table()
