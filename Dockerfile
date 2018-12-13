FROM python:3.7
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY hello_world.html .
COPY hello_world.py .
WORKDIR .
CMD ["python", "hello_world.py"]