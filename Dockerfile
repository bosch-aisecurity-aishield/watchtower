# -- base image ---
FROM python:3.10.13 as base
WORKDIR /app
    
# -- Dependencies ---
    
FROM base AS dependencies
    
COPY src/requirements.txt ./
    
RUN pip install -r requirements.txt
    
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
    
# -- Copy Files ---
    
FROM dependencies as build
COPY src /app
    
# --- Release with Alpine ----
FROM python:3.10.13 as Release
WORKDIR /app
    
COPY --from=dependencies /app/requirements.txt ./
COPY --from=dependencies /root/.cache /root/.cache
    
RUN pip install -r requirements.txt
    
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
    
COPY --from=build /app/ ./
    
CMD ["python", "watchtower_webapp.py"]