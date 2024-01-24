## 1. docker-compose.yaml 이용하여 jupyter 컨테이너 내용 추가

**(1-1) docker-compose.yaml에 아래 내용 추가**

```
# docker-compose.yaml

services:
  jupyter:
    image: jupyter/base-notebook:latest
    container_name: jupyter-container
    environment:
      # Jupyter notebook 접속시 사용할 패스워드
      - JUPYTER_TOKEN=${password}
    volumes:
      - ./notebooks:/home/jovyan/work
    restart: always
    ports:
      - 8888:8888
    networks:
      network_custom:
        ipv4_address: 172.28.0.2
        
networks:
  network_custom:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1        
```
```
# 내용 설명

> image: jupyter notebook 최신 버전의 이미지 사용
> container_name:  컨테이너명 설정
> environment: jupyter notebook 접속시 사용할 토큰 키 or 패스워드 설정
> volumes
    * 호스트 머신 디렉터리를 컨테이너 내부와 연결하는 바인드 마운트(bind mount) 방식
    * 호스트 머신의 로컬 디렉터리 → ./notebooks
    * 컨테이너 디렉터리 → /home/jovyan/work
> restart: 오류시 재기동 여부
> ports: 로컬 및 컨테이너에서 사용할 포트
> networks: 해당 컨테이너에서 사용할 고정 IP
```


**※ 기존 도커 서비스들에 대해 할당한 고정 IP 정보**
```
# ├── services
#      └── jupyter : 172.28.0.2
#      └── mariadb : 172.28.0.3 (참고로, 172.28.0.4는 다른 테스트용 컨테이너에서 사용중)
#      └── postgres : 172.28.0.5
#      └── redis: 172.28.0.6
#      └── airflow-webserver: 172.28.0.7
#      └── airflow-scheduler: 172.28.0.8
#      └── airflow-worker: 172.28.0.9
#      └── airflow-triggerer: 172.28.0.10
#      └── airflow-init: 172.28.0.11

# ├── networks
#      └── subnet : 172.28.0.0/16
#      └── gateway : 172.28.0.1
```

<br></br>

**(1-2) 로컬 디렉터리 생성**

volumes에서 호스트 머신 디렉터리를 `./notebooks`로 지정하였으므로 해당 디렉터리 생성
```
# docker-compose.yaml 파일이 있는 곳에 notebooks 디렉터리 생성
mkdir notebooks
```


**※ jupyter container default 위치 확인하는 방법**
```
# jupyter container 접근
# sudo docker exec -it ${container명} bash
sudo docker exec -it jupyter-container bash

# bash shell
# 현재 디렉터리 --> /home/jovyan
# 디렉터리 내의 work 폴더에 파일 저장 --> /home/jovyan/work 경로로 설정
pwd
ls
```
<br></br>
<br></br>
## 2. 도커 재기동
```
sudo docker compose down
sudo docker compose up -d
```

<br></br>
<br></br>
## 3. jupyter notebook 접속 (http://localhost:8888/)
Password or Token → `docker-compose.yaml`에서 jupyter 컨테이너에서 설정한 토큰 or 패스워드 입력 후 [Log in] 클릭
```
services:
  jupyter:
    environment:
      # Jupyter notebook 접속시 사용할 패스워드
      - JUPYTER_TOKEN=${password}
```
<br></br>
<br></br>

## 4. jupyter notebook에서 mariadb 컨테이너 데이터 불러오기
**(4-1) jupyter 컨테이너 접속해서 필요한 라이브러리 설치**
```
# jupyter 컨테이너 접근
# sudo docker exec -it ${container명} bash
sudo docker exec -it jupyter-container bash

# bash
pip install mysql-connector-python
```

<br></br>
**(4-2) Jupyter 웹 브라우저에서 work 폴더 더블 클릭 > python3 notebook 선택 > test.ipynb 생성**

jupyter notebook의 컨테이너 디렉터리를 `/home/jovyan/work`로 설정했으므로 work 디렉터리에 들어가서 코드 생성

<br></br>
**(4-3) test.ipynb**

아래 코드 작성 후 실행
```
import mysql.connector
from mysql.connector import Error

# mariadb container 접속정보
# docker-compose.yaml에 추가한 mariadb 컨테이너 정보
db_config = {
	'host': 'mariadb-container', # mariadb 컨테이너명
	'port': 3306, # mariadb 컨테이너접속포트
	'database': 'mariadb', # mariadb 데이터베이스명
	'user': '${DBeaver_Username}', # mariadb 접속정보 유저명
	'password': '${DBeaver_Password}' # mariadb 접속정보 패스워드
}

query = "SELECT * FROM test_table"

try:
	with mysql.connector.connect(**db_config) as connection:
		with connection.cursor() as cursor:
			cursor.execute(query)
			result = cursor.fetchall()
			print(result)
except Error as e:
	print(f"Error: {e}")
	
```
```
# 코드 설명
> db_config 정보를 이용하여 mariadb 컨테이너를 연결하고, "SELECT * FROM test_table" 쿼리를 실행하여 결과를 가져오는 코드
> try~except를 통해서 모든 과정이 올바르면 데이터를 가져오고, 만약 문제가 발생하면 에러 메세지 표시

# db_config 설명 (모든 내용은 아래 docker-compose.yaml에 추가한 mariadb container 내용 기반)
> host: mariadb 컨테이너명
> port: mariadb 컨테이너 접속 포트
> database: mariadb 데이터베이스명 ${MYSQL_DATABASE}
> user: mariadb 접속 유저명 ${MYSQL_USER}
> password: mariadb 접속 패스워드 ${MYSQL_PASSWORD}

```
**※ docker-compose.yaml의 Mariadb 컨테이너 정보**

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
```
<br></br>
<br></br>
## 5. (선택사항) 바인드 마운트가 정상 작동하는지 확인
**(5-1) 호스트 머신 local directory 확인 → test.ipynb 파일 확인**
```
# 현재위치: docker-compose.yaml 스크립트가 있는 위치
pwd

cd notebooks/
ls
```

**(5-2) container 내부 확인 → test.ipynb 파일 확인**
```
# jupyter 컨테이너 접근
# sudo docker exec -it ${container명} bash
sudo docker exec -it jupyter-container bash

# bash
cd work/
ls
```


→ jupyter notebook의 **바인드 마운트 방식**이 올바르게 적용되었음이 확인되었고, 컨테이너 재기동 여부와 상관없이 작성한 ipynb 파일이 계속 남아있음을 확인할 수 있다. 그리고 호스트, 컨테이너 디렉터리에 모두 접근할 수 있고 서로 간의 데이터 변경이 발생하면 실시간으로 동기화된다.


<br></br>
**※ 볼륨과 바인드 마운트 방식의 차이?**
```
services:
  jupyter:
    volumes:
      - ./notebooks:/home/jovyan/work

  mariadb:
    volumes:
      - mariadb-db-volume:/var/lib/mysql
      
...

volumes:
  mariadb-db-volume:      
```


- 볼륨(volume) - Mariadb
    - mariadb-db-volume 볼륨이 mariadb 컨테이너 내부 디렉터리(`/var/lib/mysql`)에 마운트 되는 방식
    - 볼륨은 **도커가 직접 호스트 파일 시스템(로컬) 일부에 데이터 저장 공간을 지정**하여 관리하는 방식
    - 컨테이너 생명 주기와 상관없이 데이터를 독립적으로 유지할 수 있다. (컨테이너를 재기동해도 데이터가 남아있다)

 
* 바인드 마운트(bind mount) - Jupyter
    - 호스트 머신의 로컬 디렉터리(`./notebooks`)를 jupyter 컨테이너 내부 디렉터리(`/home/jovyan/work`)에 연결하는 바인드 마운트 방식
    - **사용자가 직접 호스트 머신(로컬)의 특정 디렉터리를 컨테이너와 연결**시키는 방식으로
    - 호스트 머신의 파일 시스템에 직접 액세스하여 데이터를 수정할 수 있다. (변경 시 실시간으로 양쪽에 반영된다)

* Q. mariadb 볼륨과 다르게 jupyter에서 바인드 마운트 방식을 사용한 이유는?
    - DB 데이터와 달리 분석용 ipynb 파일에 직접 접근하고 수정해야하는 상황이 있을 수 있다고 생각해서 내가 직접 찾을 수 있는 디렉터리로 지정