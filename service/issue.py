from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain.chains import create_sql_query_chain
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import pandas as pd
import os

SNOWFLAKE_ACCOUNT = "qv52412.europe-west3.gcp"
USERNAME = "Username"
DATABASE= "DBT_DATABASE"
SCHEMA = "PUBLIC"
WAREHOUSE = "FIVETRAN_WAREHOUSE"
ROLE = "ACCOUNTADMIN"

def ask_about_issue(question: str):
    password = os.environ.get('PASSWORD', '')
    snowflake_url = f"snowflake://{USERNAME}:{password}@{SNOWFLAKE_ACCOUNT}/{DATABASE}/{SCHEMA}?warehouse={WAREHOUSE}&role={ROLE}"
    
    db = SQLDatabase.from_uri(snowflake_url, sample_rows_in_table_info=1, include_tables=['issue'], view_support=True)
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0,
        max_tokens=1000,
        max_retries=2
    )
    database_chain = create_sql_query_chain(llm, db)
    sql_query: str = database_chain.invoke({"question": question})
    engine = create_engine(URL(
        account=SNOWFLAKE_ACCOUNT,
        user=USERNAME,
        password=password,
        database=DATABASE,
        schema=SCHEMA,
        warehouse=WAREHOUSE,
        role=ROLE
    ))
    con = engine.connect()
    
    query = None
    QUERY_FIELD = "SQLQuery: "
    for s in sql_query.split("\n"):
        if s.startswith(QUERY_FIELD):
            query = s.replace(QUERY_FIELD, "")
            break

    result = None
    if query:
        df = pd.read_sql(query, con)
        result = df.to_string() if not df.empty else None

    if not result:
        print(sql_query)

    try:
        con.close()
    except Exception as e:
        print(e)

    try:
        engine.dispose()
    except Exception as e:
        print(e)
    
    return result