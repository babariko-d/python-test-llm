from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from pydantic import BaseModel, Field
import pandas as pd
import os

SNOWFLAKE_ACCOUNT = "qv52412.europe-west3.gcp"
USERNAME = "Username"
DATABASE= "DBT_DATABASE"
SCHEMA = "PUBLIC"
WAREHOUSE = "FIVETRAN_WAREHOUSE"
ROLE = "ACCOUNTADMIN"

PROMPT = """
Given an input question, create a syntactically correct snowflake SQL query to run.
Limit your query up to 50 rows.
Use only column names from schema description. Pay attention to which column is in which table.
Take into account field with components may contain text with comma separated words in different case.
Also user can pass names for assignies and reporters partially.
Query explanation is not needed and response should strictly follow the format instructions provided below.

Only use the following tables:
{table_info}

Answer the user query.
{format_instructions}
{question}
"""

class QueryResponse(BaseModel):
    query_text: str = Field(description="answer with text of SQL query")

def ask_about_issue(question: str):
    password = os.environ.get('PASSWORD', '')
    snowflake_url = f"snowflake://{USERNAME}:{password}@{SNOWFLAKE_ACCOUNT}/{DATABASE}/{SCHEMA}?warehouse={WAREHOUSE}&role={ROLE}"
    
    db = SQLDatabase.from_uri(snowflake_url, sample_rows_in_table_info=1, include_tables=['issue'], view_support=True)
    
    ## Build LLM chain
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0,
        max_tokens=1000,
        max_retries=2
    )

    parser = PydanticOutputParser(pydantic_object=QueryResponse)

    prompt = PromptTemplate(
        template=PROMPT,
        input_variables=["question"],
        partial_variables={"format_instructions": parser.get_format_instructions(), "table_info": db.get_table_info()}
    )

    database_chain = prompt | llm | parser
    sql_query = database_chain.invoke({"question": question})
    
    # Execute SQL query
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
    
    df = pd.read_sql(sql_query.query_text, con)
    
    
    result = f"SQL query:\n{sql_query.query_text}\n\nQuery execution result:\n{df.to_string()}" if not df.empty else None

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