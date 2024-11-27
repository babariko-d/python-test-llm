FROM python:3.12-bookworm

COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . /opt/workspace/llm-ask

WORKDIR /opt/workspace/llm-ask

CMD ["python3", "run.py"]