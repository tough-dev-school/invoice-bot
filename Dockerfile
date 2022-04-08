FROM python:3.10.2-slim-bullseye

WORKDIR /
COPY requirements.txt /
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /requirements.txt

COPY src/ /src

CMD python -m src.bot
