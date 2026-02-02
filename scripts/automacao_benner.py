from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import time
import os
import sys
from datetime import date, timedelta
import re
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


def automacao_agibank_juridico(username, password, dt_inicio, dt_fim):
    """
    Realiza o login no sistema Agibank Jurídico Benner e navega para a página de processos.

    Args:
        username (str): O nome de usuário para login.
        password (str): A senha para login.
    """
    # Estanciar caminho txt para escrever dados coletados
    file_path = "C:\\temp\\agi_novas_pastas.txt"
    # Buscar datas de hoje e ontem
    today = date.today()
    today_str = today.strftime("%d/%m/%Y")
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%d/%m/%Y")

    # 1. Configuração do WebDriver
    print("Iniciando o navegador Chrome...")
    driver = webdriver.Chrome()
    driver.maximize_window()  # Maximiza a janela do navegador

    try:
        # 2. Acessar a URL de Login
        login_url = "https://agibank.bennercloud.com.br/JURIDICO_EXT/"
        print(f"Acessando a URL de login: {login_url}")
        driver.get(login_url)

        # Configura um tempo de espera explícito. O script vai esperar até 20 segundos
        # para que um elemento esteja presente/clicável antes de falhar.
        wait = WebDriverWait(driver, 20)

        # 3. Preencher os Campos de Login
        print("Aguardando os campos de login...")
        try:
            # Seletores para o campo de usuário:
            username_field = wait.until(EC.presence_of_element_located(
                (By.ID, "UserName")))
            username_field.send_keys(username)
            print(f"Usuário '{username}' preenchido.")

            # Seletores para o campo de senha:
            password_field = wait.until(EC.presence_of_element_located(
                (By.ID, "Password")))
            password_field.send_keys(password)
            print("Senha preenchida.")

            # 4. Clicar no Botão de Login
            login_button = wait.until(EC.element_to_be_clickable((By.ID, "LoginButton")))
            login_button.click()
            print("Botão de login clicado. Aguardando redirecionamento...")

        except TimeoutException:
            print(
                "Erro: Os campos de login ou o botão de login não foram encontrados no tempo esperado. Verifique os seletores.")
            return  # Sai da função se não conseguir encontrar os elementos de login
        except NoSuchElementException:
            print("Erro: Um dos elementos de login não foi encontrado. Verifique os seletores.")
            return  # Sai da função

        # 5. Esperar o Processamento do Login e Carregamento da Nova Página
        # A estratégia é esperar que a URL mude para algo diferente da URL de login
        # ou que um elemento específico da página pós-login apareça.
        try:
            wait.until(EC.url_changes(login_url))
            print(f"Login bem-sucedido! URL atual: {driver.current_url}")
        except TimeoutException:
            print(
                "Erro: A URL não mudou após o login. O login pode ter falhado ou a página demorou muito para carregar.")
            return

        # 6. Navegar para a URL Desejada Após o Login
        target_url = "https://agibank.bennercloud.com.br/JURIDICO_EXT/jur/a/PR_PROCESSOS/Grid.aspx?i=PR_PROCESSOS_MENU&m=MAIN"
        print(f"Navegando para a URL alvo: {target_url}")
        driver.get(target_url)

        # 7. Opcional: Confirmar o Carregamento da Página Alvo
        # Podemos esperar por um título específico da página ou um elemento conhecido
        # que só aparece nessa página.
        try:
            wait.until(EC.title_contains("Pastas"))  # Título da página de processos
            print(f"Página '{target_url}' carregada com sucesso. Título: {driver.title}")
        except TimeoutException:
            print("Erro: A página de processos não foi carregada ou o título não correspondeu no tempo esperado.")

        # 8. Selecionar o filtro \"Últimos pendentes\"
        try:
            selectReport = Select(driver.find_element(By.XPATH, "//html/body/form/div[3]/div[3]/div[3]/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/span/div/div/div/div[1]/div/select"))
            # select by visible text
            selectReport.select_by_visible_text('Últimos pendentes')
            print("O filtro 'Ultimos pendentes' foi selecionado")
        except TimeoutException:
            print("Erro: O elemento do report Ultimos pendentes, não foi encontrado.")
            print("\nAutomação concluída!")

        # 9. Preencher o campo das datas de início e fim da pesquisa e clicar na lupa
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']")))
            print("O campo de datas está funcional para digitação")

            # Seletores para o campo de "Cadastrado em":
            range_datas = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='form-control']")))
            # range_datas.send_keys(yesterday_str+"00:00 - "+yesterday_str+"23:59")
            range_datas.send_keys(dt_inicio+" - "+dt_fim)
            print(f"Data inicial ('{dt_inicio}') e data final ({dt_fim})preenchidas.")
            # sleep(5)
            pesquisar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[3]/div[2]/div/div/div[2]/div/div[2]/span/div/div/div/div[3]/a[2][@class='btn btn-primary filter-button']")))
            pesquisar_button.click()
            print("Botão de lupa clicado. Aguardando carregar registros...")
            sleep(3)
            # driver.find_element(By.TAG_NAME, "html").send_keys(Keys.PAGE_DOWN)
        except TimeoutException:
            print("Erro: O campo de datas não foi carregado.")

        # 10. Encontrar paginação e percorrer itens da tabela
        try:
            page_number = 1
            while True:
                # Checar se botão 'Next page' está habilitado
                next_button = driver.find_element(By.XPATH, "//html/body/form/div[3]/div[3]/div[3]/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/div[5]/div/div[1]/ul/li[2]/a[not(@disabled)][contains(@id, 'btNextPage')]")

                # Caso botão estiver habilitado
                if next_button:
                    # Encontra cada linha da tabela
                    items = driver.find_elements(By.XPATH, "//tbody/tr[@rel <= 9]")

                    loop_index = 0
                    # Percorre cada linha da tabela
                    for item in items:
                        loop_index += 1
                        # Limpando variáveis
                        nr_processo = None
                        nr_pasta = None
                        cpf = None
                        cpf_formatado = None
                        cnpj = None
                        cnpj_formatado = None
                        print("Loop index:" + str(loop_index))
                        # Coleta alguns dados da linha dessa tabela
                        # Extrai nr da pasta
                        try:
                            pasta_xpath = f"//table/tbody/tr[{loop_index}]/td[6]/a"
                            nr_pasta = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, pasta_xpath))).text
                            # nr_pasta = driver.find_element(By.XPATH, pasta_xpath).text
                            print(f"Número da pasta: {nr_pasta}")
                        except:
                            print("Entrou no except do nr da pasta")
                            pasta_xpath = f"//table/tbody/tr[{loop_index}]/td[6]/a"
                            print(f"Tenta clicar no xpath {pasta_xpath}")
                            nr_pasta = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, pasta_xpath))).text

                        # Extrai nr do processo
                        try:
                            p_xpath = f"//table/tbody/tr[{loop_index}]/td[7]/a"
                            nr_processo = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, p_xpath))).text
                            # nr_processo = driver.find_element(By.XPATH, p_xpath).text
                            print(f"Número do processo: {nr_processo}")
                        except:
                            print("Entrou no except do nr do processo")
                            p_xpath = f"//table/tbody/tr[{loop_index}]/td[7]/a"
                            nr_processo = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, p_xpath))).text
                            print(f"Número do processo: {nr_processo}")

                        # Extrai data e hora do cadastro da pasta
                        try:
                            dh_cadastro_xpath = f"//table/tbody/tr[{loop_index}]/td[5]/a"
                            dh_cadastro = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, dh_cadastro_xpath))).text
                            print(f"Data cadastro pasta: {dh_cadastro}")

                        except:
                            print("Entrou no except do cadastro da pasta")
                            dh_cadastro_xpath = f"//table/tbody/tr[{loop_index}]/td[5]/a"
                            dh_cadastro = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, dh_cadastro_xpath))).text

                        # Extrai nome do adverso
                        try:
                            nome_xpath = f"//table/tbody/tr[{loop_index}]/td[8]/a"
                            nm_adverso = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, nome_xpath))).text

                        except:
                            print("Entrou no except do Nome do Adverso")
                            nome_xpath = f"//table/tbody/tr[{loop_index}]/td[8]/a"
                            nm_adverso = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, nome_xpath))).text

                        sleep(3)

                        # Entra no detalhe do icone pessoa, para extrair o nr do CPF
                        person_xpath = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//table/tbody/tr[{loop_index}]/td[1]/a[@class = 'btn btn-xs btn-circle default']")))
                        print(f"Tenta clicar no icone pessoa:     //table/tbody/tr[{loop_index}]/td[1]/a[@class = 'btn btn-xs btn-circle default']")
                        person_xpath.click()
                        print(f"Entrou no iframe de Partes")
                        try:
                            # Utilizar waits explicitos
                            sleep(5)
                            # Mudar para o primeiro iframe
                            WebDriverWait(driver, 20).until(
                                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
                            )
                            print("Aguarda carregar Iframe")
                        except Exception as e:
                            print(f"An error occurred: {e}")

                        try:
                            linha_person_iframe = ''
                            print(f"Procura a linha da grid que contenha o nme do adverso: //table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[@data-field='PARTICIPANTE']/a")
                            linha_person_iframe = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[@data-field='PARTICIPANTE']/a"))).text
                            print(f"valor linha com nome do adverso: {linha_person_iframe}")
                        except:
                            print("Caso não encontre a linha com o nome do adverso")
                            next_button_iframe = driver.find_element(By.XPATH, "// *[ @ id = 'ctl00_Main_PARTES_btNextPage']")
                            print("Clica no botao next")
                            next_button_iframe.click()
                            print("Botao next clicado")
                            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                                (By.XPATH, f"//table/tbody/tr[td/a[text()= '{nm_adverso}']]/td[8]/a")))
                        print(f"Aguardou Adverso carregar na tela Iframe")

                        # Extrai valor do CPF
                        cpf_formatado = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                                    f"//table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[8]/a")))
                        print(f"//table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[8]/a")
                        cpf_formatado = driver.find_element(By.XPATH, f"//table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[8]/a").text
                        print(f"CPF formatado do adverso: {cpf_formatado}")
                        cpf = re.findall(r'\d+', cpf_formatado)
                        cpf= "".join(cpf)
                        print(f"CPF do adverso: {cpf}")

                        if not cpf:
                            cnpj_formatado = driver.find_element(By.XPATH,
                                                                f"//table/tbody/tr[td/a[contains(concat(' ', normalize-space(.), ' '), ' {nm_adverso} ')]]/td[9]/a").text
                            print(f"CNPJ formatado do adverso: {cnpj_formatado}")
                            # Extract all sequences of digits (as strings)
                            cnpj = re.findall(r'\d+', cnpj_formatado)
                            cnpj = "".join(cnpj)
                            print(f"CNPJ do adverso: {cnpj}")
                            print(f"CPF não carregou algum valor, verificar ... Loop index é {loop_index}")

                        driver.switch_to.default_content()
                        close_frame = driver.find_element(By.XPATH, "//*[@id='ModalCommand_modalCloseButton']")
                        close_frame.click()
                        print("Saiu do iframe e volta para conteudo principal")
                        #Fecha frame
                        # Tecla ESCAPE key
                        sleep(3)

                        # ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        print("Enviou tecla ESC para sair do popup pessoas")
                        # Escreve dados no txt
                        with open(file_path, 'a') as file:
                            # Escreve no arquivo
                            if cpf:
                                file.write(f'{dh_cadastro}, {{"cpf":"{cpf}","cpfFormatado":"{cpf_formatado}","nrProcesso":"{nr_processo}","status":"ABERTO","tipoProcesso":"JURIDICOBUSCA", "{nm_adverso}"}}\n')
                            else:
                                file.write(
                                    f'{dh_cadastro}, {{"cpf":"{cnpj}","cpfFormatado":"{cnpj_formatado}","nrProcesso":"{nr_processo}","status":"ABERTO","tipoProcesso":"JURIDICOBUSCA", "{nm_adverso}"}}\n')
                            # print("Escreveu a linha no txt")

                        print(f"File '{file_path}' created and written successfully.")

                    # Click the next button to continue the loop
                    print("Busca xpath do botao next")
                    next_button = driver.find_element(By.XPATH,
                                                      "//html/body/form/div[3]/div[3]/div[3]/div[1]/div[3]/div[2]/div/div/div[2]/div/div[2]/div[5]/div/div[1]/ul/li[2]/a[not(@disabled)][contains(@id, 'btNextPage')]")
                    next_button.click()
                    print("Clica no botao next")
                    page_number += 1
                    time.sleep(10)  # Wait for the new page to load
                    driver.find_element(By.TAG_NAME,"html").send_keys(Keys.PAGE_UP)
                else:
                    # The 'Next' button is no longer found (condition is False), so break the loop
                    print(f"Chegou na última apagina após processar {page_number} paginas.")

                    break
        except TimeoutException:
            print("Erro: Não foram encontrados pastas cadastradas para essas datas pesquisadas.")
        except NoSuchElementException:
            print("Erro: Elemento não foi encontrado na tela.")



        # Manter o navegador aberto por um tempo para você poder inspecionar a página.
        print("O navegador permanecerá aberto por 55 segundos para inspeção.")
        time.sleep(55000000)
        print("\nAutomação concluída!")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a automação: {e}")
    finally:
        # 9. Fechar o Navegador
        # print("Fechando o navegador.")
        driver.quit()


if __name__ == "__main__":
    # Carrega as variáveis do arquivo .env
    load_dotenv()

    benner_username = os.getenv("AGIBANK_USER")
    benner_password = os.getenv("AGIBANK_PASS")
    benner_dt_inicial = os.getenv("AGIBANK_INICIO")
    benner_dt_final = os.getenv("AGIBANK_FINAL")


    if not benner_username or not benner_password:
        print("Erro: As variáveis AGIBANK_USER e AGIBANK_PASS não estão definidas.")
        print("Defina-as antes de executar o script, por exemplo:")
        print("  export AGIBANK_USER=seu_usuario")
        print("  export AGIBANK_PASS=sua_senha")
        sys.exit(1)
    automacao_agibank_juridico(benner_username, benner_password, benner_dt_inicial, benner_dt_final)
