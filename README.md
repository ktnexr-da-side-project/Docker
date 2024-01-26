
인프라 구축 과정

담당자: 박범수(Parker), 김도현(Elly)

### **2024년 1월 구축 단계**

| <center>기간</center> | <center>계획</center> | <center>결과</center> |
|---|---|---|
| 1주차 | `docker-compose.yaml` 이용하여 container 생성 및 관리 방법 확인 | 1. DB 버전 관리 방법 및 IP, Port 지정 방법 확인 
| 2주차 | `docker-compose.yaml`에서 container 세부 정보 확인하는 방법 확인 | 1. version, services 정보로 container 설정 정보 확인 <br> 2. volumes, networks 설정해서 컨테이너 간의 통신하는 방법 확인
| 3주차 | mariaDB container 올리기 | 1. 고정IP 할당하여 컨테이너들 간에 network 할당 <br> 2. `local(3307), container(3306)` port 사용하여 충돌 방지 <br> 3. `volumes` 설정해서 데이터 유실 방지 <br> 4. DBeaver 연결 후 샘플 데이터 적재 완료
| 4주차 | Airflow내에서 Jupyter 활용 및 연동 방법 확인 | 1. yaml 파일 수정해서 Jupyter container 올리기 <br> 2. `bind mount` 설정해서 로컬과 컨테이너 디렉터리 연결 <br> 3. Jupyter에서 `mysql.connector` 라이브러리 이용하여 mariaDB container 데이터 불러오기 완료


### **2024년 2월 구축 단계**
| <center>기간</center> | <center>계획</center> | <center>결과</center> |
|---|---|---|
| 1주차 | openAPI dags 개발 방법 결정 | 
