FROM mcr.microsoft.com/playwright/python:v1.58.0-noble
ENV TMPDIR=/tmp
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY index.py .

CMD ["python3", "-m", "awslambdaric", "index.lambda_handler"]
