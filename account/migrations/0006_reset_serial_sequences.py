from django.db import migrations

def reset_all_serial_sequences(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # Find only tables with serial integer id columns
        cursor.execute("""
            SELECT c.relname AS table_name
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_attribute a ON a.attrelid = c.oid
            JOIN pg_type t ON a.atttypid = t.oid
            WHERE
                a.attname = 'id'
                AND a.attnum > 0
                AND NOT a.attisdropped
                AND c.relkind = 'r'
                AND n.nspname = 'public'
                AND t.typname IN ('int4', 'int8') -- int4 = integer, int8 = bigint
        """)
        tables = cursor.fetchall()

        for (table_name,) in tables:
            sql = f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE((SELECT MAX(id) + 1 FROM {table_name}), 1),
                    false
                )
            """
            print(f"🔄 Resetting sequence for table: {table_name}")
            cursor.execute(sql)

class Migration(migrations.Migration):

    dependencies = [
        ("account", "0005_passwordresetcode_user_is_email_verified"),
        ("device", "0005_remove_sensordata_session_id_sensordata_session"),
        ("geo", "0007_auto_20250501_0415"),
        ("navigation", "0001_initial"),
        ("wheelchair", "0002_insert_wheelchair_metadata"),
    ]

    operations = [
        migrations.RunPython(reset_all_serial_sequences),
    ]
