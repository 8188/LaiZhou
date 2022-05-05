FROM python:3
MAINTAINER Li
#add project files to the usr/src/app folder
ADD . /usr/src/app
#set directoty where CMD will execute 
WORKDIR /usr/src/app
COPY requirements.txt ./
# Get pip to download and install requirements:
RUN pip install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt
# Expose ports
EXPOSE 5000
# default command to execute    
CMD ["smart_plant.py"]