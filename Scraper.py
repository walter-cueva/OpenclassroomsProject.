import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def extract_book_data(book_page_url):
    """Extract data from a single book page."""
    response = requests.get(book_page_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1').text
    product_description = soup.find('meta', attrs={'name': 'description'})['content'].strip()
    category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text
    review_rating = soup.find('p', class_='star-rating')['class'][-1]
    image_url = soup.find('img')['src']
    image_url = requests.compat.urljoin(book_page_url, image_url)

    product_info = soup.find('table', class_='table table-striped').find_all('tr')
    product_info_dict = {row.find('th').text: row.find('td').text for row in product_info}

    return {
        'product_page_url': book_page_url,
        'title': title,
        'product_description': product_description,
        'category': category,
        'review_rating': review_rating,
        'image_url': image_url,
        'universal_product_code (upc)': product_info_dict.get('UPC'),
        'price_including_tax': product_info_dict.get('Price (incl. tax)'),
        'price_excluding_tax': product_info_dict.get('Price (excl. tax)'),
        'quantity_available': product_info_dict.get('Availability')
    }

def scrape_category(category_url):
    """Scrape all books in a given category."""
    books_data = []
    while True:
        response = requests.get(category_url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        for book in books:
            book_url = requests.compat.urljoin(category_url, book.find('h3').find('a')['href'])
            book_data = extract_book_data(book_url)
            if book_data:
                books_data.append(book_data)

        # Check for next page
        next_page = soup.find('li', class_='next')
        if next_page:
            next_page_url = next_page.find('a')['href']
            category_url = requests.compat.urljoin(category_url, next_page_url)
        else:
            break

    return books_data

# Define the category URL (change this URL to the category you want to scrape)
category_url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
data = scrape_category(category_url)

# Write data to CSV
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
filename = f"books_{timestamp}.csv"
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print(f"Data successfully saved to {filename}")
