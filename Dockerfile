FROM python:3.7-alpine
COPY requirements.txt .
RUN pip install -i https://pypi.anaconda.org/bokeh/channel/dev/simple --extra-index-url https://pypi.python.org/simple/ -r requirements.txt
COPY hello_world.py .
WORKDIR .
CMD ["python", "hello_world.py"]