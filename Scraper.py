from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from getpass import getpass
import requests
import sys
import os
from Table import Table

from dotenv import load_dotenv
load_dotenv()

delay = 10  # seconds


#def scrapeJobPage(driver, job_urls):
#    for job in driver.find_element_by_class_name('jlGrid').find_elements_by_tag_name('li'):
#        print(job.text, '\n')
#        job.click()
#
#        driver.implicitly_wait(delay)
#        job_data = {}
#        for tab in wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'scrollableTabs'))).find_elements_by_class_name('tab'):
#            ActionChains(driver).move_to_element(tab).click().perform()
#            job_data[tab.text] = wait.until(
#                EC.presence_of_element_located((By.CLASS_NAME, 'tabSection'))).text
#            print(job_data[tab.text])
#            driver.implicitly_wait(delay)


def scrapeHTMLTable(driver):
    print('scraping table')
    htm_table = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'dataTableContainer')))
    attrs = htm_table.find_element_by_tag_name(
        'thead').find_element_by_tag_name('tr').find_elements_by_tag_name('th')
    headers = []
    data = []
    print('getting headers')
    for h in attrs:
        headers.append(h.get_attribute('textContent'))
    print('getting data')
    for row in htm_table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr'):
        cols = row.find_elements_by_tag_name('td')
        row_vals = [None] * len(headers)
        for i in range(len(cols)):
            driver.implicitly_wait(1)
            row_vals[i] = cols[i].get_attribute('textContent')
            print('col: ', i, ' val: ', row_vals[i])
            try:
                addr = cols[i].find_element_by_tag_name('a')

                if headers[i] + '_url' not in headers:
                    headers.append(headers[i] + '_url')
                    row_vals.append(None)

                row_vals[headers.index(headers[i] + '_url')
                         ] = addr.get_attribute('href')
            except NoSuchElementException as ex:
                pass
        data.append(row_vals)
    return headers, data


def getRecommendedJobs(driver):
    wait = WebDriverWait(driver, delay)
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[6]/div/div/div/div/div[2]/div[3]/div[1]/div[4]/strong'))).click()

        t = Table()
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'jobDetails')))
        driver.execute_script(
            "document.getElementsByClassName('MainCol').scrollDown += 100")
        num_pages = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, 'hideMob'))).text.split(' ')[-1]
        popUpCleared = qaCleared = False
        for i in range(int(num_pages) - 1):
            print('page ' + str(i) + ' navigated to')
            driver.execute_script(
                "document.getElementsByClassName('jobDetails').scrollDown += 100")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'showDataTableBtn')))
            headers, data = scrapeHTMLTable(driver)
            if t.headers == [] or i == 0:
                t.headers = headers
            t.data.extend(data)
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal_closeIcon'))).click()
            driver.execute_script(
                "document.getElementsByClassName('MainCol').scrollDown += 100")
            wait.until(EC.visibility_of_element_located((By.ID, 'MainCol')))
            driver.find_element_by_class_name('next').click()
            try:
                wait.until(
                    EC.presence_of_element_located((By.ID, 'JAModal'))).find_element_by_tag_name('span').click()
                popUpCleared = True
                print('popup cleared')
            except NoSuchElementException:
                pass

#            if not qaCleared:
#                try:
#                    wait.until(
#                        EC.presence_of_element_located((By.ID, 'qual_x_close'))).click()
#                    qaCleared = True
#                except:
#                    print('no qa check')
            driver.implicitly_wait(delay)

        return t
    except TimeoutException:
        print("Loading took too much time!")


def login(driver):
    wait = WebDriverWait(driver, delay)
    # = input('Enter Glassdoor email: ')
    email = os.getenv('UNAME')
    pw = os.getenv('PASS') # = getpass('Enter Glassdoor password: ')
    driver.find_element_by_class_name("sign-in").click()
    wait.until(EC.presence_of_element_located(
        (By.NAME, "username"))).send_keys(email)
    driver.find_element_by_name("password").send_keys(pw)
    driver.find_element_by_name('submit').click()


if __name__ == "__main__":
    driver = webdriver.Firefox(executable_path='./geckodriver')
    driver.set_page_load_timeout(delay)
    driver.get('https://www.glassdoor.com/')
    #assert "Glassdoor" in driver.title
    login(driver)
    t = getRecommendedJobs(driver)
    t.exportSql()

    # driver.close()
