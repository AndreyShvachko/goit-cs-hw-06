FROM python:3.10-slim

WORKDIR /app  

COPY . /app   

RUN pip install flask pymongo  

EXPOSE 3000  

CMD ["python", "main.py"]  


