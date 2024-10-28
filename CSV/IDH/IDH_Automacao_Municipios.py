#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install selenium pandas openpyxl minio webdriver-manager


# In[25]:


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

# Configuração do MinIO
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
bucket_name = "idh"

# Configuração do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://www.atlasbrasil.org.br")
chrome_options.add_argument("--headless")  # Se não precisar de interface gráfica

# Usando o ChromeDriverManager para garantir que o ChromeDriver esteja disponível
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    logging.info("Acessando o site do Atlas Brasil...")
    driver.get('http://www.atlasbrasil.org.br/ranking')

    # Selecionar Todos
    logging.info("Selecionando opções no dropdown...")
    select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[4]/select')
    select = Select(select_element)
    select.select_by_visible_text("Todas")

    select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[1]/select')
    select = Select(select_element)
    select.select_by_visible_text("Municípios")

    # Localize o botão de download e clique nele
    logging.info("Clicando no botão de download...")
    botao_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[3]/button')
    botao_download.click()

    # Aguardar o download ser concluído (ajuste conforme necessário)
    logging.info("Aguardando o download ser concluído...")
    time.sleep(20)

    # Verifique se o arquivo foi baixado
    arquivo_xlsx = None
    try:
        # Verificando a presença do arquivo na pasta de downloads
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")  # Diretório padrão de downloads
        arquivo_xlsx = [f for f in os.listdir(downloads_dir) if f == "data.xlsx"]
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
        minio_client.put_object(bucket_name, 'IDH_Municipios.csv', csv_buffer, csv_buffer.getbuffer().nbytes)
        logging.info(f'O arquivo IDH_Municipios.csv foi enviado com sucesso para o bucket {bucket_name} no MinIO!')
    else:
        logging.error("Erro: Nenhum arquivo XLSX encontrado.")

except Exception as e:
    logging.error(f"Erro ao processar o arquivo: {e}")

finally:
    # Finalize o Selenium
    logging.info("Apagando Arquivo...")
    os.remove("data.xlsx")
    logging.info("Fechando o navegador...")
    driver.quit()


# In[ ]:




