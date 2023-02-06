from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import os

# librerias analisis
import pandas as pd
import json
from pandas import json_normalize
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score
import pickle


default_args = {
    'owner': 'IvanovaDasha',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def load(ti):

    AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
    df = pd.read_csv(AIRFLOW_HOME + '/dags/dataset.csv', on_bad_lines='skip', delimiter=';', low_memory = False, decimal = ",")
    # df = pd.read_csv(r'dataset.csv', on_bad_lines='skip', delimiter=';', low_memory = False, decimal = ",")
    print(df.shape) # dimensiones de la tabla de datos
    
    # tipología variables
    df["churn"] = df["churn"].astype("bool")
    df = df.drop(["Customer_ID"], axis=1)

    df = df.drop(columns=['area','prizm_social_one','dualband','refurb_new','hnd_webcap','infobase','HHstatin','dwllsize','ethnic',
                        'kid0_2','kid3_5','kid6_10','kid11_15','kid16_17','creditcd'])
    print(df.shape)

    # eliminamos nans
    df = df.dropna()
    print(df.shape)

    # dummy
    var_x_dummy = ['new_cell','crclscod','asl_flag','ownrent','dwlltype','marital']
    df = pd.get_dummies(df, columns = var_x_dummy)

    # balanceo
    print(df.churn.value_counts())

    df.info()
    print(df.shape)

    df_json = df.to_json()

    ti.xcom_push(key='df', value=df_json)


def model(ti):

    df = pd.read_json(ti.xcom_pull(task_ids='load_data', key='df'))

    X_entrena, X_valida, Y_entrena, Y_valida = train_test_split(df.drop(columns = "churn"), df['churn'],train_size=.70)
    print("Estructura de datos de entrenamiento... ", X_entrena.shape)

    model_rf = RandomForestClassifier(n_estimators = 100)
    model_rf.fit(X_entrena, Y_entrena)

    # Almacenar modelo en pickle
    pickle.dump(model_rf, open('model.p', 'wb'))    

    # X_valida_json = X_valida.to_json()
    # Y_valida_json = Y_valida.to_json()

    # ti.xcom_push(key='X_valida', value=X_valida_json)
    # ti.xcom_push(key='Y_valida', value=Y_valida_json)


# def test_model(ti):

    # print('hola')
    # print(ti.xcom_pull(task_ids='model', key='X_valida'))

    # dict_X = json.loads(ti.xcom_pull(task_ids='model', key='X_valida'))
    # X_valida = json_normalize(dict_X) 

    # dict_Y = json.loads(ti.xcom_pull(task_ids='model', key='Y_valida'))
    # Y_valida = json_normalize(dict_Y) 

    # X_valida = pd.read_json(ti.xcom_pull(task_ids='model', key='X_valida'), orient = 'index')
    # Y_valida = pd.read_json(ti.xcom_pull(task_ids='model', key='Y_valida'), orient = 'index')

    # print('adios')

    loaded_model = pickle.load(open('model.p', 'rb'))
    predicciones = loaded_model.predict(X_valida)

    comparaciones = pd.DataFrame(Y_valida)
    # comparaciones = comparaciones.assign(Sales_Real = Y_valida)
    comparaciones = comparaciones.assign(Predicho = predicciones.flatten().tolist())
    print(comparaciones)

    mat_confusion = confusion_matrix(
                        y_true    = Y_valida,
                        y_pred    = predicciones
                    )

    accuracy = accuracy_score(
                y_true    = Y_valida,
                y_pred    = predicciones,
                normalize = True
            )

    print("Matriz de confusión")
    print("-------------------")
    print(mat_confusion)
    print("")
    print(f"El accuracy de test es: {100 * accuracy} %")
   


with DAG(
    default_args=default_args,
    dag_id='a_sdg_test',
    description='Test SDG',
    start_date=datetime(2023, 2, 1),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='load_data',
        python_callable=load,
    )

    task2 = PythonOperator(
        task_id='model',
        python_callable=model,
        retries=0
    )

    # task3 = PythonOperator(
    #     task_id='test_model',
    #     python_callable=test_model
    # )

    task1 >> task2 
    # >> task3