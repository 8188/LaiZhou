## Microservices of LaiZhou Power Plant "Hydrogen-Oil-Water" System Intelligent Diagnosis 

### quick start with docker
download [TL00101_20210917ADSelect.json](https://pan.baidu.com/s/13-lsmBDUMthyzSXFS-6asA?pwd=n9bw) for test
```
docker network create -d bridge net
docker run -itd --name redis --network net redis
docker pull mongo:5
docker run -itd --name mongo -p 27017:27017 --network net mongo:5
docker cp TL00101_20210917ADSelect.json mongo:/
docker exec -it mongo /bin/bash
mongoimport -d LaiZhouData -c TL00101_20210917AD TL00101_20210917ADSelect.json --legacy
docker build -t REPOSITORY:TAG .
docker run -it --name laizhou -p 8990:8990 --network net REPOSITORY:TAG /bin/bash
python smart_plant.py
```
open another terminal
```
docker exec -it laizhou /bin/bash
cd test
python mongoRunTest.py
```