# Microservices of LaiZhou Power Plant "Hydrogen-Oil-Water" System Intelligent Diagnosis 

- quick start with docker
```
docker build -t REPOSITORY:TAG .
docker run -d --name laizhou -p 8990:8990 REPOSITORY:TAG python smart_plant.py
```