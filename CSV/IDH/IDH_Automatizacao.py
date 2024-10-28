#!/usr/bin/env python
# coding: utf-8

# In[54]:


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


# In[63]:


minio_client = Minio(
    "localhost:9000",  # substitua por seu URL MinIO (e.g., "localhost:9000")
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # ou True se usar SSL
)
bucket_name = "idh"

# Caminho para a sua pasta "IDH" dentro de "OneDrive\Documentos"
pasta_download = r'C:\Users\pedro\OneDrive\Documentos\IDH'

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
chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://www.atlasbrasil.org.br")

# Caminho para o ChromeDriver
service = Service(r'C:\Users\pedro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Acessar o site
driver.get('http://www.atlasbrasil.org.br/ranking')

# Selecionar Todos
select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[4]/select')
select = Select(select_element)
select.select_by_visible_text("Todas")


# ## Estados

# In[66]:


select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[1]/select')
select = Select(select_element)
select.select_by_visible_text("Estados")

# Localize o botão de download e clique nele
botao_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[3]/button')
botao_download.click()

# Aguardar o download ser concluído
time.sleep(20)  # Ajuste o tempo conforme necessário

# Verifique se o arquivo foi baixado
arquivos_na_pasta = os.listdir(pasta_download)
arquivo_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]

if arquivo_xlsx:
    # Converter o arquivo .xlsx para .csv
    caminho_arquivo = os.path.join(pasta_download, arquivo_xlsx[0])
    df = pd.read_excel(caminho_arquivo)
    arquivo_csv = 'IDH_Estados.csv'
    df.to_csv(os.path.join(pasta_download, arquivo_csv), index=False)

    # Enviar o arquivo CSV para o MinIO
    try:
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

time.sleep(20)


# ## Municípios

# In[26]:


select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[1]/select')
select = Select(select_element)
select.select_by_visible_text("Municípios")

# Localize o botão de download e clique nele
botao_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[3]/button')
botao_download.click()

# Verifica o diretório de download e aguarda o download ser concluído
print(f"Arquivos estão sendo baixados para: {pasta_download}")

# Aumentar o tempo de espera para garantir que o download seja concluído
time.sleep(20)  # Ajuste conforme necessário

# Verifique se o arquivo foi baixado
arquivos_na_pasta = os.listdir(pasta_download)
arquivo_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]
        
if arquivo_xlsx:
    # Converter .xlsx para .csv usando Pandas
    caminho_arquivo = os.path.join(pasta_download, arquivo_xlsx[0])
    df = pd.read_excel(caminho_arquivo)
    arquivo_csv = 'IDH_Municipios.csv'
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

time.sleep(20)


# ## UDH

# In[29]:


select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[1]/select')
select = Select(select_element)
select.select_by_visible_text("UDH")

# Localize o botão de download e clique nele
botao_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[3]/button')
botao_download.click()

# Verifica o diretório de download e aguarda o download ser concluído
print(f"Arquivos estão sendo baixados para: {pasta_download}")

# Aumentar o tempo de espera para garantir que o download seja concluído
time.sleep(20)  # Ajuste conforme necessário

# Verifique se o arquivo foi baixado
arquivos_na_pasta = os.listdir(pasta_download)
arquivo_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]
        
if arquivo_xlsx:
    # Converter .xlsx para .csv usando Pandas
    caminho_arquivo = os.path.join(pasta_download, arquivo_xlsx[0])
    df = pd.read_excel(caminho_arquivo)
    arquivo_csv = 'IDH_UDH.csv'
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

time.sleep(20)


# ## RM

# In[32]:


select_element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[1]/div/div[2]/div/div/div[1]/select')
select = Select(select_element)
select.select_by_visible_text("RM")

# Localize o botão de download e clique nele
botao_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[3]/button')
botao_download.click()

# Verifica o diretório de download e aguarda o download ser concluído
print(f"Arquivos estão sendo baixados para: {pasta_download}")

# Aumentar o tempo de espera para garantir que o download seja concluído
time.sleep(20)  # Ajuste conforme necessário

# Verifique se o arquivo foi baixado
arquivos_na_pasta = os.listdir(pasta_download)
arquivo_xlsx = [arquivo for arquivo in arquivos_na_pasta if arquivo.endswith('.xlsx')]
        
if arquivo_xlsx:
    # Converter .xlsx para .csv usando Pandas
    caminho_arquivo = os.path.join(pasta_download, arquivo_xlsx[0])
    df = pd.read_excel(caminho_arquivo)
    arquivo_csv = 'IDH_RM.csv'
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

time.sleep(20)


# In[68]:


driver.quit()

