@echo off

:: Install the required Python packages
pip install -r src/requirements.txt

:: Download the spaCy model
python -m spacy download en_core_web_lg

git lfs install

echo Installation complete!

