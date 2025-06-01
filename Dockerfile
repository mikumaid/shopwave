FROM python:3.12-alpine
LABEL maintainer="Antakara"
LABEL description="Shopwave is a simple e-commerce platform built with Python and Flask."
LABEL version="1.0"
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
VOLUME /app/shopwave/static
EXPOSE 5000
ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:5000", "-w", "4", "shopwave:app"]