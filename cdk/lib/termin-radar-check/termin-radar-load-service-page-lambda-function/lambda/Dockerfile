FROM public.ecr.aws/docker/library/python:3.13-slim
WORKDIR /app
ENV PLAYWRIGHT_BROWSERS_PATH=./ms-playwright
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir playwright==1.58.0
RUN pip install --no-cache-dir awslambdaric==4.0.0
RUN playwright install chromium-headless-shell --with-deps
RUN rm requirements.txt
COPY index.py .
CMD ["python", "-m", "awslambdaric", "index.lambda_handler"]
