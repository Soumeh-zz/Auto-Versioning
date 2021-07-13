FROM python:3
COPY script.py /script.py
RUN pip install requests
CMD ["python", "/script.py"]