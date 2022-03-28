from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup as BS
import time
import csv

#Авторизация в яндексе
def login_to_ya(login_name, password, driver) -> 'В случае успешной авторизации вернет URL страницы, иначе None':
    try:
        driver.get('''https://passport.yandex.ru/auth?from=mail&
                      origin=hostroot_homer_auth_ru&retpath=https%3A%2F%2Fmail.yandex.ru%2F&
                      backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1''')

        login = driver.find_element(By.ID, "passp-field-login")
        login.send_keys(login_name)

        driver.find_element(By.ID, "passp:sign-in").click()

        try:
            password_pole = wait(driver, 5).until(EC.presence_of_element_located((By.ID, "passp-field-passwd")))
            password_pole.send_keys(password)
            driver.find_element(By.ID, "passp:sign-in").click()
        except:
            print('Логин введен некорректно или удален')
            driver.quit()
            return None
        else:
            #ждем подгрузки страницы
            time.sleep(3)
            #получаем url
            page_url = driver.current_url
            #если нет в адресе страницы UID пользователя, значит не авторизовались
            if 'uid=' not in page_url:
                print('Неверный пароль')
                driver.quit()
                return None
            else:
                return page_url
    except:
        print('Авторизация не удалась')


def get_page(page_url, driver) -> 'Вернет содержимое страницы с контактами':
    driver.get(page_url)
    #Ждем подгрузки страницы
    time.sleep(5)
    #Скролим вниз, чтобы появилась кнопка "Показать все контакты"
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        element = wait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Показать все контакты']")))
        element.click()
        #Ждем загрузки всех контактов
        time.sleep(3)
    except:
        print('Нет кнопки показать все контакты')
    finally:
        #Получаем код страницы
        pageSource = driver.page_source
        #print(pageSource)
        page_html = pageSource.encode("utf-8")
        return page_html


#Парсит полученную страницу и сохраняет данные в файл file_name.csv
def page_parse(html_str, file_name):
    res = BS(html_str, features="html.parser")
    l_contacts = res.findAll('span', class_='mail-AbookEntry-Contact')
    l_emails = res.findAll('span', class_='mail-AbookEntry-Emails')
    l_phones = res.findAll('span', class_='mail-AbookEntry-Phones')
    l_res = list(zip(l_contacts, l_emails, l_phones))

    for i in l_res:
        l_row_contact = []  # список хранящий данные контакта (имя, емейлы, телефон)
        for j in i:
            # Если существует список дополнительных емейлов у контакта, то извлекаем емейлы и сохраняем в список l_a
            if j.find('ul', class_='_nb-popup-menu') is not None:
                l_li = j.findAll('li', class_='_nb-popup-line')
                l_a = []
                for k in l_li:
                    if k.find('a', class_='_nb-popup-link') is not None:
                        l_a.append(k.find('a', class_='_nb-popup-link').text)
                l_row_contact.append('\r\n'.join(l_a))
            # если лоп списка нет, то извлекаем все данные по контакту
            elif j.find('span', class_='mail-ui-Overflower') is not None:
                l_row_contact.append(j.find('span', class_='mail-ui-Overflower').text)
        # записываем строку с данными контакта в файл
        with open(f'{file_name}.csv', 'a') as f:
            file_writer = csv.writer(f, delimiter=";", lineterminator="\r")
            file_writer.writerow(l_row_contact)


if __name__ == '__main__':
    #Логин почты
    login = ''
    #пароль
    password = ''
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    except ValueError:
        print('Ошибка запуска веб-драйвера')
    else:
        contacts_url = login_to_ya(login, password, driver)
        if (contacts_url is not None):
            #Получение личных контактов
            all_contacts_url = contacts_url.replace('inbox', 'contacts')
            page_to_parse = get_page(all_contacts_url, driver)
            page_parse(page_to_parse, 'own_contacts')

            ##Раскомментировать, если есть общие контакты организации и их нужно сохранить
            #shared_contacts_url = contacts_url.replace('inbox', 'contacts/shared')
            #page_to_parse = get_page(shared_contacts_url, driver)
            #page_parse(page_to_parse, 'shared_contacts')

        driver.quit()
