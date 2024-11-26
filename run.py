from dotenv import load_dotenv
from flask import Flask, request, Response
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

snowflake_account = "qv52412.europe-west3.gcp"
username = "Username"
password = "NBMLj4X3ZcRY"
database= "DBT_DATABASE"
schema = "PUBLIC"
warehouse = "FIVETRAN_WAREHOUSE"
role = "ACCOUNTADMIN"
snowflake_url = f"snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}"

@app.route("/ask", methods=['GET'])
def askme():
    question = request.args.get("question")
    if question != None:
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
            account=snowflake_account,
            user=username,
            password=password,
            database=database,
            schema=schema,
            warehouse=warehouse,
            role=role
        ))
        con = engine.connect()
        query = None
        for s in sql_query.split("\n"):
            if s.startswith("SQLQuery: "):
                query = s.replace("SQLQuery: ", "")
                break
        result = None
        if query != None:
            df = pd.read_sql(query, con)
            result = df.to_string()
            #print(df)
        try:
            con.close()
        except Exception as e:
            print(e)
        try:
            engine.dispose()
        except Exception as e:
            print(e)
        if result != None and not df.empty:
            return Response(response=result + "\n", status=200)
        else:
            return Response(response="No response", status=404)

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True)