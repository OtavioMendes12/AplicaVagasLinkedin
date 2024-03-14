from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json

class AplicaLinkedin:

    def __init__(self, data):


        self.email = data['email']
        self.password = data['senha']
        self.keywords = data['palavra-chave']
        self.location = data['Local']
        self.driver = webdriver.Chrome(data['caminho do chromedriver'])

    def login_linkedin(self):

        self.driver.get("https://www.linkedin.com/login")


        login_email = self.driver.find_element_by_name('session_key')
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element_by_name('session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)
    
    def job_search(self):

        # go to Jobs
        jobs_link = self.driver.find_element_by_link_text('Jobs')
        jobs_link.click()

        # search based on keywords and location and hit enter
        search_keywords = self.driver.find_element_by_css_selector(".jobs-search-box__text-input[aria-label='Search jobs']")
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)
        search_location = self.driver.find_element_by_css_selector(".jobs-search-box__text-input[aria-label='Search location']")
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):

        all_filters_button = self.driver.find_element_by_xpath("//button[@data-control-name='all_filters']")
        all_filters_button.click()
        time.sleep(1)
        easy_apply_button = self.driver.find_element_by_xpath("//label[@for='f_LF-f_AL']")
        easy_apply_button.click()
        time.sleep(1)
        apply_filter_button = self.driver.find_element_by_xpath("//button[@data-control-name='all_filters_apply']")
        apply_filter_button.click()

    def find_offers(self):


        # find the total amount of results (if the results are above 24-more than one page-, we will scroll trhough all available pages)
        total_results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(total_results_int)

        time.sleep(2)

        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name("occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")


        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name('job-card-search__title.artdeco-entity-lockup__title.ember-view')
            for title in titles:
                self.submit_apply(title)


        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url of each page based on the total amount of pages
            find_pages = self.driver.find_elements_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=',1)[1])


            for page_number in range(25,total_jobs+25,25):
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements_by_class_name("occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name('job-card-search__title.artdeco-entity-lockup__title.ember-view')
                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self,job_add):


        print('Você está aplicando para essa vaga: ', job_add.text)
        job_add.click()
        time.sleep(2)
        

        try:
            in_apply = self.driver.find_element_by_xpath("//button[@data-control-name='jobdetails_topcard_inapply']")
            in_apply.click()
        except NoSuchElementException:
            print('Você já aplicou para essa vaga, próxima...')
            pass
        time.sleep(1)


        try:
            submit = self.driver.find_element_by_xpath("//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
        

        except NoSuchElementException:
            print('Não achado, indo para o próximo')
            try:
                discard = self.driver.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass

        time.sleep(1)

    def close_session(self):

        print('Finalizado!')
        self.driver.close()

    def apply(self):


        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(2)
        self.find_offers()
        time.sleep(2)
        self.close_session()


if __name__ == '__main__':

    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = AplicaLinkedin(data)
    bot.apply()