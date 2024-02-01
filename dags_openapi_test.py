# --------------------------------------------------------------------- #
# 데이터셋: 국토교통부 실거래가 정보 OpenAPI
# 데이터 설명: 지역코드와 기간을 설정하여 해당지역, 해당기간의 아파트 매매 신고 자료를 제공하는 아파트 매매 신고 정보
# 데이터 갱신주기: 일 1회
# 요청 메시지 명세 : 지역코드(LAWD_CD) / 계약월(DEAL_YMD) / 인증키(serviceKey)
# --------------------------------------------------------------------- #

from airflow import DAG
from airflow.models.variable import Variable
from airflow.operators.python import PythonOperator
import pendulum # python에서 timezone을 쉽게 사용할 수 있도록 도와주는 라이브러리

def get_openapi_data():
    import requests
    import bs4
    import pandas as pd 

    # 공공데이터 OpenAPI 커넥션 정보
    base_url = 'http://openapi.molit.go.kr'
    port = '8081'
    endpoint = 'OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade'
    service_key = Variable.get('apikey_getRTMS_openapi_molit') # 공공데이터 활용 인증키
    headers = {'Content-Type':'application/xml'} # xml 데이터 활용

    # OpenAPI 수집요청 
    request_url = f'{base_url}:{port}/{endpoint}?serviceKey={service_key}&LAWD_CD=11110&DEAL_YMD=201512'   
    response = requests.get(request_url, headers=headers)
    
    # xml parsing --> DataFrame 변환
    content = response.text
    xml_obj = bs4.BeautifulSoup(content,'lxml-xml')
    rows = xml_obj.findAll('item')
    
    name_list, value_list, row_list = list(), list(), list()

    for i in range(0, len(rows)):
        columns = rows[i].find_all()
        for j in range(0,len(columns)):
            if i ==0:
                name_list.append(columns[j].name)   # 컬럼리스트
            value_list.append(columns[j].text)  # 데이터리스트
        row_list.append(value_list)
        value_list=[]
   
    df = pd.DataFrame(row_list, columns=name_list) # 컬럼별 데이터 정보 --> DataFrame 변환
    print(df)
    
    return df

with DAG(
    dag_id = 'dags_openapi_test',
    start_date = pendulum.datetime(2024, 1, 29, tz='Asia/Seoul'),
    schedule = None,
    catchup = False, # dag가 실행되지 않았던 과거 시점 task를 실행할지에 대한 여부
    tags = ['project']
) as dag:

    getRTMS_task = PythonOperator(
        task_id = 'getRTMS_task',
        python_callable = get_openapi_data,
        dag = dag
    )

    # task 실행
    getRTMS_task
