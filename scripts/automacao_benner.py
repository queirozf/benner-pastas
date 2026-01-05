from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import sys


def automacao_agibank_juridico(username, password):
    """
    Realiza o login no sistema Agibank Jurídico Benner e navega para a página de processos.

    Args:
        username (str): O nome de usuário para login.
        password (str): A senha para login.
    """
    # 1. Configuração do WebDriver
    # Você precisará ter o ChromeDriver (para Google Chrome) ou o driver correspondente
    # para o seu navegador (ex: GeckoDriver para Firefox) instalado e acessível.
    # O executável do driver deve estar no PATH do sistema ou você pode especificar
    # o caminho completo, por exemplo:
    # driver = webdriver.Chrome(executable_path='/caminho/para/chromedriver')

    # Para simplicidade, assumimos que o chromedriver está no PATH.
    # Certifique-se de que a versão do ChromeDriver seja compatível com a sua versão do Google Chrome.
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

        # Manter o navegador aberto por um tempo para você poder inspecionar a página.
        print("O navegador permanecerá aberto por 25 segundos para inspeção.")
        time.sleep(25)

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a automação: {e}")
    finally:
        # 9. Fechar o Navegador
        # print("Fechando o navegador.")
        driver.quit()


if __name__ == "__main__":
    # Carrega credenciais das variáveis de ambiente
    usuario_agibank = os.environ.get("AGIBANK_USER")
    senha_agibank = os.environ.get("AGIBANK_PASS")

    if not usuario_agibank or not senha_agibank:
        print("Erro: As variáveis de ambiente AGIBANK_USER e AGIBANK_PASS não estão definidas.")
        print("Defina-as antes de executar o script, por exemplo:")
        print("  export AGIBANK_USER=seu_usuario")
        print("  export AGIBANK_PASS=sua_senha")
        sys.exit(1)

    automacao_agibank_juridico(usuario_agibank, senha_agibank)
