#!/usr/bin/env python
# coding: utf-8

# In[121]:


import os
import time
import io
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from minio import Minio


# In[123]:


minio_client = Minio(
    "localhost:9000",  # substitua por seu URL MinIO (e.g., "localhost:9000")
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # ou True se usar SSL
)
bucket_name = "pof"

# Caminho para a sua pasta "IDH" dentro de "OneDrive\Documentos"
pasta_download = r'C:\Users\pedro\OneDrive\Documentos\POF'

# Configuração do Chrome para ignorar downloads inseguros e definir o diretório de download
chrome_options = webdriver.ChromeOptions()
prefs = {
    'download.default_directory': pasta_download,  # Define o diretório de download para a pasta IDH
    'download.prompt_for_download': False,
    'directory_upgrade': True,
    'safebrowsing.enabled': False,
    'safebrowsing.disable_download_protection': True  # Ignora o bloqueio de downloads inseguros
}
chrome_options.add_experimental_option('prefs', prefs)

# Adiciona argumentos para permitir conteúdo inseguro
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=https://sidra.ibge.gov.br/pesquisa/pof/tabelas")

# Caminho para o ChromeDriver
service = Service(r'C:\Users\pedro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Acessar o site
driver.get('https://sidra.ibge.gov.br/pesquisa/pof/tabelas')


# ## 3047

# In[125]:


nome_arquivo = "POF_Alimento_Rural_Urbano"

#Entrar no link
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[2]/div[2]/section/div[1]/table/tbody/tr[3]/td[3]/a')
botao.click()

time.sleep(10)

#Aumentar Decimos
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[3]/div/div[2]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/span/button[2]')
botao.click()

#Selecionar Area
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[4]/div/div[2]/div[3]/div/div[1]/div[1]/div/button[1]')
botao.click()

#Selecionar Grupos
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[5]/div/div[2]/div[3]/div/div[1]/div[1]/div/button[1]')
botao.click()

#Selecionar Região
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[4]/div[7]/div/div[2]/div[3]/div/div/div/div[1]/div[2]/ul[1]/li[2]/div/div/div/button')
botao.click()

time.sleep(5)

#Clicar Download
botao = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[1]/div[5]/div[2]/div/div[2]/button[2]')
botao.click()

time.sleep(5)

input_element = driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/input')
input_element.send_keys(nome_arquivo)

botao = driver.find_element(By.XPATH, '/html/body/div[7]/div/div/div[2]/div/div/div[2]/a')
botao.click()

time.sleep(20)

# Verifique se o arquivo foi baixado
arquivos_na_pasta = os.listdir(pasta_download)
arquivo_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]
        
if arquivo_xlsx:
    # Converter .xlsx para .csv usando Pandas
    caminho_arquivo = os.path.join(pasta_download, arquivo_xlsx[0])
    df = pd.read_excel(caminho_arquivo)
    arquivo_csv = nome_arquivo + '.csv'
    df.to_csv(os.path.join(pasta_download, arquivo_csv), index=False)

    # Enviar o arquivo CSV para o MinIO
    try:
        # Cria o bucket caso não exista
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        
        # Caminho completo do CSV
        caminho_csv = os.path.join(pasta_download, arquivo_csv)
        
        # Upload para o MinIO
        minio_client.fput_object(bucket_name, arquivo_csv, caminho_csv)
        print(f'O arquivo {arquivo_csv} foi enviado com sucesso para o bucket {bucket_name} no MinIO!')
    except Exception as e:
        print(f"Erro ao enviar para o MinIO: {e}")
    finally:
        # Remover os arquivos locais após o upload
        os.remove(caminho_arquivo)
        os.remove(caminho_csv)
else:
    print("Erro: Arquivo .xlsx não encontrado.")

time.sleep(5)

driver.quit()


# In[ ]:




