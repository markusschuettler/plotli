FROM python:3.7
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY plotli.html .
COPY plotli.py .
WORKDIR .
CMD ["python", "plotli.py"]