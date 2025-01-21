FROM python:3.10-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY web.py ./web.py
COPY models.py ./models.py
COPY database.py ./database.py
COPY schema.py ./schema.py

COPY todd_ded_100222.xlsx ./todd_ded_100222.xlsx
COPY uscitiesdataset/uscities_updated.csv ./uscitiesdataset/uscities_updated.csv

EXPOSE 8082
CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8082","--reload"]