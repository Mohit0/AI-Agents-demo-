from langchain_community.tools import Tool # DuckDuckGoSearchRun


def execute_code(code: str) -> str:
    try:
        exec(code)
        return "Code Passed"
    except Exception as e:
        return f"Error: {e}"


code_complier = Tool.from_function(
    func=execute_code,
    name="Execute Code",
    description="Executes arbitrary Python code.",
)


from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///mydatabase.db')
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """))
    connection.execute(text("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'securepass')"))
    connection.commit()


def execute_sql(sql_query: str) -> str:
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return str(result.fetchall())
    except Exception as e:
        return f"Error: {e}"


sql_tool = Tool.from_function(
    func=execute_sql,
    name="Execute SQL",
    description="Executes an SQL query.",
)

