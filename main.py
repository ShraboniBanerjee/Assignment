import csv
import requests
from bs4 import BeautifulSoup
from time import sleep

def extract_element_text(soup, element, selector=None, string=None, default='N/A'):
    """
    A utility function to extract the text from an element identified by a selector or string.
    Returns the default value if the element is not found.
    """
    elem = soup.find(element, selector, string=string)
    return elem.text.strip() if elem else default

def get_product_data(product_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_name = extract_element_text(soup, 'span', {'class': 'a-size-medium'})
    product_price = extract_element_text(soup, 'span', {'class': 'a-offscreen'})
    product_rating = extract_element_text(soup, 'span', {'class': 'a-icon-alt', 'aria-label': True}, default='0').split()[0]
    num_reviews = extract_element_text(soup, 'span', {'id': 'acrCustomerReviewText'}, default='0').split()[0]

    # Additional data to fetch from individual product page (Part 2)
    product_description = extract_element_text(soup, 'div', {'id': 'productDescription'})
    asin = extract_element_text(soup, 'th', string='ASIN:')
    manufacturer = extract_element_text(soup, 'th', string='Manufacturer:')

    return [product_name, product_price, product_rating, num_reviews, product_description, asin, manufacturer]

def scrape_product_listings(base_url, num_pages):
    data = []
    for page_num in range(1, num_pages + 1):
        url = f"{base_url}&page={page_num}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

        for container in product_containers:
            product_url = "https://www.amazon.in" + container.find('a', {'class': 'a-link-normal'})['href']
            product_data = [product_url] + get_product_data(product_url)
            data.append(product_data)

        # Sleep to avoid overloading Amazon's servers
        sleep(2)

    return data

def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
                             'Product Description', 'ASIN', 'Manufacturer'])
        csv_writer.writerows(data)

if __name__ == "__main__":
    base_url = "https://www.amazon.in/s?k=bags"
    num_pages = 20
    scraped_data = scrape_product_listings(base_url, num_pages)
    export_to_csv(scraped_data, "amazon_bags_data.csv")
