FROM python:3.7.2-slim

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV MONGODB_URI=host.docker.internal:27017
ENV MONGODB_SECRET=mongo:mongo123

EXPOSE 5000

CMD [ "python", "-u", "./server.py" ]