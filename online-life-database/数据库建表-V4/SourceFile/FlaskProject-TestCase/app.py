from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# 数据库配置
DB_HOST = '39.104.19.8'
DB_PORT = 3306
DB_USER = 'Database'
DB_PASSWORD = 'Online-life2025'
DB_NAME = 'Online'

def get_db_connection():
    """建立数据库连接"""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    """获取数据库中所有表的信息并显示在首页"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 获取所有表名
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [table[f'Tables_in_{DB_NAME}'] for table in tables]  # 替换为实际的数据库名称

            # 获取每个表的信息
            table_data = {}
            for table_name in table_names:
                # 获取表中的数据
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()

                # 获取表中的字段及其约束
                cursor.execute(f"""
                    SELECT 
                        COLUMN_NAME, 
                        DATA_TYPE, 
                        IS_NULLABLE, 
                        COLUMN_DEFAULT, 
                        COLUMN_COMMENT
                    FROM 
                        INFORMATION_SCHEMA.COLUMNS 
                    WHERE 
                        TABLE_SCHEMA = '{DB_NAME}' AND 
                        TABLE_NAME = '{table_name}'
                """)
                columns = cursor.fetchall()

                # 获取表的约束信息
                cursor.execute(f"""
                    SELECT 
                        CONSTRAINT_TYPE, 
                        COLUMN_NAME, 
                        CONSTRAINT_NAME
                    FROM 
                        INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                    JOIN 
                        INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    USING (CONSTRAINT_NAME, TABLE_SCHEMA, TABLE_NAME)
                    WHERE 
                        TABLE_SCHEMA = '{DB_NAME}' AND 
                        TABLE_NAME = '{table_name}'
                """)
                constraints = cursor.fetchall()

                table_data[table_name] = {
                    'data': data,
                    'columns': columns,
                    'constraints': constraints
                }

            return render_template('index.html', tables=table_data)
    except Exception as e:
        return f"Error fetching tables: {e}"
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)