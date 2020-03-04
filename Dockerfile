FROM python:3.6-alpine
RUN ping -c 2 dl-cdn.alpinelinux.org
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev
COPY requirements.txt /src/
WORKDIR /src/
RUN pip install -r requirements.txt
ADD . .
EXPOSE 5000
CMD ["python","api.py"]
