# python-test-llm
LLM test

# Build image
docker build -t ask-llm:0.1 .

# Run container
docker run --rm --name ask-llm -p 5000:5000 -e GROQ_API_KEY=&lt;Groq API key&gt; -e PASSWORD=&lt;Password for snowflake user&gt;

# Swagger URL
http://127.0.0.1:5000/apidocs/