FROM python:3-slim

WORKDIR /usr/src/
COPY requirements.txt /usr/src/
RUN pip3 install -r requirements.txt
COPY . /usr/src/
ENTRYPOINT ["python"]
CMD ["collector.py"]
