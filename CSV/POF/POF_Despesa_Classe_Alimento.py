#!/usr/bin/env python
# coding: utf-8

# In[151]:


pip install selenium pandas openpyxl minio webdriver-manager


# In[159]:


import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from minio import Minio
from io import BytesIO

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

minio_client = Minio(
    "localhost:9000", 
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
bucket_name = "pof"

# Configuração do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=https://sidra.ibge.gov.br/pesquisa/pof/tabelas")
chrome_options.add_argument("--headless")  # Se não precisar de interface gráfica

# Usando o ChromeDriverManager para garantir que o ChromeDriver esteja disponível
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    logging.info("Acessando o site do IBGE...")
    driver.get('https://sidra.ibge.gov.br/pesquisa/pof/tabelas')

    # Entrando no Site dos Dados
    logging.info("Acessando Dados...")
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[2]/div[2]/section/div[3]/table/tbody/tr[5]/td[3]/a')
    botao.click()

    time.sleep(7)

    logging.info("Selecionando opções...")
    #Selecionar Variáveis
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[3]/div/div[2]/div[3]/div/div[1]/div[1]/div/button[1]')
    botao.click()

    #Selecionar Renda
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[4]/div/div[2]/div[3]/div/div[1]/div[1]/div/button[1]')
    botao.click()

    #Selecionar Despesa
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[5]/div/div[2]/div[3]/div/div[1]/div[1]/div/button[1]')
    botao.click()

    #Selecionar Região
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[7]/div/div[2]/div[3]/div/div/div/div[1]/div[2]/ul[1]/li[2]/div/div/div/button')
    botao.click()

    #Selecionar Estado
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[7]/div/div[2]/div[3]/div/div/div/div[1]/div[2]/ul[1]/li[3]/div/div/div/button')
    botao.click()

    time.sleep(5)
    
    # Localize o botão de download e clique nele
    logging.info("Clicando no botão de download 1...")
    botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[5]/div[2]/div/div[2]/button[2]')
    botao.click()

    time.sleep(5)
    
    # Definindo nome do arquivo
    logging.info("Definindo nome...")
    campo_input = driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/input')
    campo_input.send_keys("arquivo_para_minio")

    # Localize o botão de download e clique nele
    logging.info("Clicando no botão de download 2...")
    botao = driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/div/div/div[2]/a')
    botao.click()

    # Aguardar o download ser concluído (ajuste conforme necessário)
    logging.info("Aguardando o download ser concluído...")
    time.sleep(15)

    # Verifique se o arquivo foi baixado
    arquivo_xlsx = None
    try:
        # Verificando a presença do arquivo na pasta de downloads
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")  # Diretório padrão de downloads
        arquivo_xlsx = [f for f in os.listdir(downloads_dir) if f == "arquivo_para_minio.xlsx"]
    except Exception as e:
        logging.error(f"Erro ao listar os arquivos na pasta de downloads: {e}")

    if arquivo_xlsx:
        logging.info(f"Arquivo encontrado: {arquivo_xlsx[0]}")

        # Ler o arquivo XLSX diretamente para um DataFrame
        caminho_arquivo = os.path.join(downloads_dir, arquivo_xlsx[0])
        df = pd.read_excel(caminho_arquivo)

        # Converter o DataFrame para CSV
        logging.info("Convertendo o arquivo XLSX para CSV...")
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Retorna ao início do buffer

        # Enviar o arquivo CSV para o MinIO
        if not minio_client.bucket_exists(bucket_name):
            logging.info(f"Criando bucket: {bucket_name}")
            minio_client.make_bucket(bucket_name)

        # Upload do arquivo CSV
        logging.info(f"Enviando o arquivo CSV para o bucket {bucket_name} no MinIO...")
        minio_client.put_object(bucket_name, 'POF_Despesa_Classe_Alimento.csv', csv_buffer, csv_buffer.getbuffer().nbytes)
        logging.info(f'O arquivo POF_Despesa_Classe_Alimento.csv foi enviado com sucesso para o bucket {bucket_name} no MinIO!')
    else:
        logging.error("Erro: Nenhum arquivo XLSX encontrado.")

except Exception as e:
    logging.error(f"Erro ao processar o arquivo: {e}")

finally:
    # Finalize o Selenium
    logging.info("Apagando Arquivo...")
    os.remove("arquivo_para_minio.xlsx")
    logging.info("Fechando o navegador...")
    driver.quit()


# In[ ]:




