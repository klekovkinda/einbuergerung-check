FROM python:3.13-slim AS builder
WORKDIR /app
ENV PLAYWRIGHT_BROWSERS_PATH=./ms-playwright
ENV PYTHONPATH=./python:${PYTHONPATH}
COPY requirements.txt .
COPY index.py .
RUN pip install --no-cache-dir -r requirements.txt -t ./python
RUN pip install --no-cache-dir playwright==1.58.0 -t ./python
RUN pip install --no-cache-dir awslambdaric==4.0.0 -t ./python
RUN python -m playwright install chromium-headless-shell --with-deps
RUN rm requirements.txt
CMD ["python", "-m", "awslambdaric", "index.lambda_handler"]
