FROM python:3.6
LABEL maintainer="jsy"
WORKDIR /app/LaiZhou
COPY requirements.txt ./
RUN pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt
ENV RELOAD False
COPY . . 
CMD uvicorn smart_plant:app --host 0.0.0.0 --port 8990