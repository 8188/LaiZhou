FROM python:3.6
LABEL maintainer="jsy"
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt
COPY . /usr/src/app 
CMD python smart_plant.py