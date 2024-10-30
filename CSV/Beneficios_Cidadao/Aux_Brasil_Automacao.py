#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install selenium pandas openpyxl minio webdriver-manager


# In[19]:


import os
import time
import logging
import zipfile
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from minio import Minio

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Obtém o diretório de downloads padrão do usuário
if os.name == 'nt':  # Windows
    download_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
else:  # Unix-based (Linux/Mac)
    download_path = os.path.join(os.environ['HOME'], 'Downloads')

# Configuração do MinIO
minio_client = Minio(
    "localhost:9000", 
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
bucket_name = "aux-brasil"

# Verifica se o bucket existe e cria se não existir
if not minio_client.bucket_exists(bucket_name):
    logging.info(f"Criando bucket: {bucket_name}")
    minio_client.make_bucket(bucket_name)

# Configuração do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=https://portaldatransparencia.gov.br/download-de-dados/auxilio-brasil")
chrome_options.add_experimental_option("prefs", {"download.default_directory": download_path})

# Usando o ChromeDriverManager para garantir que o ChromeDriver esteja disponível
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Acessar site
    logging.info("Acessando o site do Portal de Transparência...")
    driver.get('https://portaldatransparencia.gov.br/download-de-dados/auxilio-brasil')

    # Fechar o modal de cookies, se presente
    try:
        time.sleep(2)
        cookie_button = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[2]/div/button[3]')
        cookie_button.click()
        logging.info("Cookie modal fechado com sucesso.")
    except Exception as e:
        logging.warning("Modal de cookies não encontrado ou erro ao clicar: " + str(e))
    
    # Selecionar ano
    logging.info("Selecionando Ano...")
    select_element_ano = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div[3]/select')
    select_ano = Select(select_element_ano)
    options_ano = select_ano.options

    for option_ano in options_ano:
        select_ano.select_by_value(option_ano.get_attribute('value'))
        logging.info(f"Ano selecionado: {option_ano.text}")
        time.sleep(1)

        # Selecionar mês para o ano atual
        select_element_mes = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div[4]/select')
        select_mes = Select(select_element_mes)
        options_mes = select_mes.options

        for option_mes in options_mes:
            select_mes.select_by_value(option_mes.get_attribute('value'))
            logging.info(f"Selecionado: {option_mes.text}/{option_ano.text}")
            time.sleep(1)
            
            # Iniciar Download
            logging.info("Iniciando Download...")
            botao = driver.find_element(By.XPATH, "//button[text()='Baixar']")
            botao.click()
            
            # Aguardar até o arquivo de download completar
            time.sleep(20)
            while not any(fname.endswith("_AuxilioBrasil.zip") for fname in os.listdir(download_path)):
                logging.info("Aguardando a conclusão do download...")
                time.sleep(2)  # Verifica a cada 2 segundos

            # Processar arquivos baixados (ZIP)
            downloaded_files = [f for f in os.listdir(download_path) if f.endswith("_AuxilioBrasil.zip")]
            for zip_file_name in downloaded_files:
                zip_file_path = os.path.join(download_path, zip_file_name)

                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    for file_name in zip_ref.namelist():
                        if file_name.endswith('.csv'):
                            with zip_ref.open(file_name) as csv_file:
                                # Criar um buffer para leitura do arquivo CSV
                                csv_buffer = BytesIO(csv_file.read())
                                
                                # Upload do arquivo CSV para o MinIO
                                logging.info(f"Enviando o arquivo CSV para o bucket {bucket_name} no MinIO...")
                                minio_client.put_object(
                                    bucket_name,
                                    file_name,
                                    csv_buffer,
                                    csv_buffer.getbuffer().nbytes,
                                    content_type='text/csv'
                                )
                                logging.info(f"Arquivo {file_name} enviado para o MinIO com sucesso.")
                
                # Remover o arquivo ZIP local após o upload
                os.remove(zip_file_path)
                logging.info(f"Arquivo ZIP {zip_file_name} removido com sucesso.")

except Exception as e:
    logging.error(f"Ocorreu um erro: {e}")

finally:
    # Remove todos os arquivos .crdownload do diretório de downloads
    driver.quit()
    
    for fname in os.listdir(download_path):
        if fname.endswith(".crdownload"):
            os.remove(os.path.join(download_path, fname))
            logging.info(f"Arquivo temporário {fname} removido com sucesso.")


# In[ ]:




