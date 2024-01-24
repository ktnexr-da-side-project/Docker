## 1. mariaDB 컨테이너 올리기(with docker-compose.yaml)
### (1) 컨테이너가 사용하고 있는  default network 확인

→ default network와 겹치지 않아야 하므로 현재 사용하고 있는 IP 확인

```
# 컨테이너 리스트 확인
sudo docker ps

# 컨테이너 상세 정보 --> 컨테이너가 사용하는 IP 확인
# sudo docker inspect ${container_ID}
sudo docker inspect 3eb58ef882b6
```

<br></br>

### (2) 컨테이너 고정 IP 할당하기

컨테이너를 올리게 되면 컨테이너는 기본적으로 유동IP를 가지게 되며, 컨테이너 생명주기에 따라 IP가 계속 변경 된다.
새롭게 올릴 DB(mariaDB)와 기존 컨테이너들간의 통신을 위해서 고정 IP를 만들어 할당해주도록 한다. (컨테이너들 간에 네트워크가 다르면 통신이 불가능하기 때문) 참고로, 새롭게 만들 고정 IP는 default와 겹치지 않도록 설정해야한다.

**(2-1) docker-compose.yaml 파일 수정**

```
# docker-compose.yaml 파일에서 'networks' 부분 내용 수정

networks:
  network_custom:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1

```

**(2-2) 기존 컨테이너들간의 통신을 위해 network 추가 할당**
```
# ├── services
#      └── mariadb : 172.28.0.2 (참고로, 172.28.0.3는 다른 테스트용 컨테이너에서 사용중)
#      └── postgres : 172.28.0.4
#      └── redis: 172.28.0.5
#      └── airflow-webserver: 172.28.0.6
#      └── airflow-scheduler: 172.28.0.7
#      └── airflow-worker: 172.28.0.8
#      └── airflow-triggerer: 172.28.0.9
#      └── airflow-init: 172.28.0.10

# ├── networks
#      └── subnet : 172.28.0.0/16
#      └── gateway : 172.28.0.1
```
```
# docker-compose.yaml 파일의 모든 service 하위에 아래 내용 추가

# (수정전)
services: 
  redis:
    image: redis:latest
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always
        
# (수정후)
services: 
  redis:
    image: redis:latest
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always
    # --------------------------- 아래 내용 추가 --------------------------- #
    networks:
      network_custom:
        ipv4_address: 172.28.0.5        
```
<br></br>

### (3) mariaDB 컨테이너 추가 (볼륨 사용)
`3307:3306`  : 로컬에서는 3307 포트로 접속하고 실제 컨테이너 내부에서는 3306 포트를 사용함을 의미
```
services:
  mariadb:
    image: mariadb:10
    container_name: mariadb-container
    environment:
      MYSQL_USER: ${user}
      MYSQL_PASSWORD: ${passwd}
      MYSQL_ROOT_PASSWORD: ${root_passwd}
      MYSQL_DATABASE: ${db_name}
      TZ: Asia/Seoul
    volumes:
      - mariadb-db-volume:/var/lib/mysql
    restart: always
    ports:
      - 3307:3306
    networks:
      network_custom:
        ipv4_address: 172.28.0.2
      
...


volumes:
  postgres-db-volume:
  mariadb-db-volume:
```

<br></br>
**(참고) mariadb 컨테이너의 default 볼륨 위치 확인**
```
# mariadb container 접근
# sudo docker exec -it ${container명} bash
sudo docker exec -it mariadb-container bash

# mysql 접속 (password : docker-compose.yaml 파일에서 지정한 MYSQL_ROOT_PASSWORD)
mysql -u root -p

# default 저장위치 확인 --> /var/lib/mysql/
select @@datadir;
```

<br></br>
### (4) 도커 재기동

```
sudo docker compose down
sudo docker compose up -d

# 컨테이너 리스트 확인
sudo docker ps
```
<br></br>
<br></br>

## 2. DBeaver로 mariaDB 연결하기

```
Server
* Sever Host: localhost
* Database: ${MYSQL_DATABASE} → docker-compose.yaml mariadb environment
* Port: 3307

Authentication (Database Native)
* Username: ${MYSQL_USER} → docker-compose.yaml mariadb environment
* Password: ${MYSQL_PASSWORD} → docker-compose.yaml mariadb environment
```
<br></br>
<br></br>

## 3. DBeaver 테이블 생성 및 데이터 적재 확인
```
# DBeaver

CREATE TABLE test_table (
	id INT PRIMARY KEY,
	name VARCHAR(50),
	age INT,
	etl_ymd VARCHAR(50)
)
COMMENT '테스트용 테이블'
;

INSERT INTO test_table (id, name, age, etl_ymd) VALUES (1, 'John', 25, 20240116);
INSERT INTO test_table (id, name, age, etl_ymd) VALUES (2, 'Alice', 30, 20240116);
INSERT INTO test_table (id, name, age, etl_ymd) VALUES (3, 'Bob', 28, 20240116);
```