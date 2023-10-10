# -- base image ---
FROM python:3.11 as base
WORKDIR /app

# -- Dependencies ---

FROM base AS dependencies

COPY src/requirements.txt ./

RUN pip install -r requirements.txt

RUN python3 -m spacy download en_core_web_lg

# -- Copy Files ---

FROM dependencies as build
COPY src /app

# --- Release with Alpine ----
FROM python:3.11 as Release
WORKDIR /app

COPY --from=dependencies /app/requirements.txt ./
COPY --from=dependencies /root/.cache /root/.cache

RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_lg
COPY --from=build /app/ ./

CMD ["python", "watchtower_webapp.py"]