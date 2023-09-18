from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as soup
import re
import json
import csv


def ssrn_search(search_term):
    driver = webdriver.Firefox()

    driver.get("https://papers.ssrn.com/sol3/DisplayAbstractSearch.cfm")

    
    title = driver.title
    print(title)

    

    cookie_btn = driver.find_element(by=By.ID, value="onetrust-accept-btn-handler")
    cookie_btn.click()

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'ot-fade-in')))

    text_box = driver.find_element(by=By.NAME, value="advanced_search")
    submit_button = driver.find_element(by=By.CLASS_NAME, value="button-wrapper.inline")
    text_box.send_keys(search_term)

    date_select = driver.find_element(by=By.NAME, value="optionDateLimit")
    select = Select(date_select)
    select.select_by_value('2')

    submit_button.click()
#error TimeoutException means there were no results

    try:
        next_element = wait.until(EC.title_is(("SSRN Electronic Library")))
    except TimeoutException as e:
        print(f'There are no results for {search_term}')
        driver.quit()
    else:
        next_title = driver.title
        print(next_title)

        page_source = driver.page_source

        page_soup = soup(page_source, 'html.parser')
        results = page_soup.find("div", class_="papers-list")
        articles = results.find_all("div", id=re.compile('div_\d+'))

        incoming_ssrn = []

        for i, article in enumerate(articles):
            print(i)
            article_link = article.find("a", {"class":"title"})
            article_URL = article_link["href"]
            article_title = article_link.text
            possible_citation = article.find_all('i')
            if len(possible_citation) > 1:
                article_citation = possible_citation[1].text
            else:
                article_citation = 'none listed'
            article_notes = article.find("div", class_="note-list")
            article_numPages = article_notes.find("span", string=re.compile('Number'))
            article_postDate = article_notes.find("span", string=re.compile('Posted'))
            article_revisedDate = article_notes.find("span", string=re.compile('Revised'))
            article_authors = article.find("div", class_="authors-list")
            all_article_authors = ''
            for string in article_authors.stripped_strings:
                all_article_authors += string + ' '
            article_affiliations = article.find("div", class_="afiliations")
            affiliation_list = article_affiliations.get_text(strip=True)
            downloads = article.find("div", class_="downloads")
            article_downloads = downloads.find('span', string=re.compile('(\d+)'))
            article_keywords = article.find("div", class_="keywords")
        
        
            print("New Article")
            ssrn_abstract_url = article_URL
            print(f'Abstract URL: {ssrn_abstract_url}')
            article_id = article_URL.split('=')[1]
            print(f'Article ID: {article_id}')
            article_title = article_link.text
            print(f'Title: {article_title}')
            if article_numPages:
                article_numPages = article_numPages.text
                match_numPages = re.match(r'Number of pages: (\d+)',article_numPages)
                article_numPages = match_numPages[1]
                print(f'Number of Pages: {article_numPages}')
            if article_postDate:
                article_postDate = article_postDate.text
                print(f'Date Posted: {article_postDate}')
            if article_revisedDate:
                revision_date = article_revisedDate.text
            else:
                revision_date = 'None'
                print("Date Revised: " + revision_date)

            authlist = all_article_authors
            affList = affiliation_list
            print(f'Author(s): {authlist}')
            print(f'Affiliation(s): {affList}')

            if article_downloads:
                ssrn_downloads = article_downloads.text.strip()
                print(f'SSRN Downloads: {ssrn_downloads}')
            else:
                ssrn_downloads = 'none'
            if article_keywords:
                article_keywords = article_keywords.get_text(strip=True)
                #article_keywords = article_keywords.text.strip('\\n\\t')
                print(article_keywords)

            incoming_ssrn.append({"search term":search_term, "SSRN Abstract URL":ssrn_abstract_url, "SSRN Article id":article_id, "Article Title":article_title, "Article Citation":article_citation, "Number of pages":article_numPages, "Posted date": article_postDate, "Last Revised":revision_date, "Authors":authlist, "Affiliations":affList, "SSRN Downloads":ssrn_downloads, "Keywords":article_keywords})

        driver.quit()
    
        return incoming_ssrn
    

    



fac_search_terms = ["'election law'", "'felon disenfranchisement'"]

for term in fac_search_terms:
    results = ssrn_search(term)
    print(type(results))
    if results is None:
        no_results = 'no results'
        results = [{"search term":term, "SSRN Abstract URL":no_results, "SSRN Article id":no_results, "Article Title":no_results, "Article Citation":no_results, "Number of pages":no_results, "Posted date":no_results, "Last Revised":no_results, "Authors":no_results, "Affiliations":no_results, "SSRN Downloads":no_results, "Keywords":no_results}]
    
    print(results)
    
    # Append the results to a JSON file
    filename = "SSRNSearchData.json"
    with open(filename, 'a') as f:
        json.dump(results, f)


    # Append results into a CSV file with headers
    updater = "ssrn_search_data.csv"
    field_names=["search term", "SSRN Abstract URL", "SSRN Article id", "Article Title", "Article Citation", "Number of pages", "Posted date", "Last Revised", "Authors","Affiliations", "SSRN Downloads", "Keywords"]

    with open(updater, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(results)
    
#results = ssrn_search("'election law'")


