from bs4 import BeautifulSoup as BS
import re
import csv

with open('contacts.html', 'r', encoding='utf-8') as f:
    html_str = f.read()
    res = BS(html_str, features="lxml")
    l_contacts = res.findAll('span', class_='mail-AbookEntry-Contact')
    l_emails = res.findAll('span', class_='mail-AbookEntry-Emails')
    l_phones = res.findAll('span', class_='mail-AbookEntry-Phones')
    l_res = list(zip(l_contacts, l_emails, l_phones))
    
    for i in l_res:
        l_row_contact=[] #список хранящий данные контакта (имя, емейлы, телефон)
        for j in i:
            #Если существует список дополнительных емейлов у контакта, то извлекаем емейлы и сохраняем в список l_a
            if j.find('ul', class_='_nb-popup-menu') is not None:
                l_li = j.findAll('li', class_='_nb-popup-line')
                l_a=[]
                for k in l_li:
                    if k.find('a', class_='_nb-popup-link') is not None:
                        l_a.append(k.find('a', class_='_nb-popup-link').text)            
                l_row_contact.append('\r\n'.join(l_a))
            #если доп списка нет, то извлекаем все данные по контакту
            elif j.find('span', class_='mail-ui-Overflower') is not None:
                l_row_contact.append(j.find('span', class_='mail-ui-Overflower').text)
        #записываем строку с данными контакта в файл
        with open('contacts.csv','a') as f:
            file_writer = csv.writer(f, delimiter = ";", lineterminator="\r")
            file_writer.writerow(['Имя', 'Emails', 'Телефон'])
            file_writer.writerow(l_row_contact)