import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

def download_image(image_url, folder, title):
    """Download and save an image from a given URL."""
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{title.replace('/', '_')}.jpg"
    file_path = os.path.join(folder, filename)

    response = requests.get(image_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    return file_path

def extract_book_data(book_page_url, image_folder):
    """Extract data from a single book page."""
    response = requests.get(book_page_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1').text
    product_description = soup.find('meta', attrs={'name': 'description'})['content'].strip()
    category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text
    review_rating = soup.find('p', class_='star-rating')['class'][-1]
    image_url = requests.compat.urljoin(book_page_url, soup.find('img')['src'])
    image_path = download_image(image_url, image_folder, title)

    product_info = soup.find('table', class_='table table-striped').find_all('tr')
    product_info_dict = {row.find('th').text: row.find('td').text for row in product_info}

    return {
        'product_page_url': book_page_url,
        'title': title,
        'product_description': product_description,
        'category': category,
        'review_rating': review_rating,
        'image_url': image_url,
        'image_path': image_path,
        'universal_product_code (upc)': product_info_dict.get('UPC'),
        'price_including_tax': product_info_dict.get('Price (incl. tax)'),
        'price_excluding_tax': product_info_dict.get('Price (excl. tax)'),
        'quantity_available': product_info_dict.get('Availability')
    }

def scrape_category(category_url, image_folder):
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
            book_data = extract_book_data(book_url, image_folder)
            if book_data:
                books_data.append(book_data)

        next_page = soup.find('li', class_='next')
        if next_page:
            next_page_url = next_page.find('a')['href']
            category_url = requests.compat.urljoin(category_url, next_page_url)
        else:
            break

    return books_data

def get_category_links(main_url):
    """Get links to all book categories."""
    response = requests.get(main_url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    category_links = soup.find('div', class_='side_categories').find('ul').find('li').find('ul').find_all('a')
    return {cat.get_text().strip(): requests.compat.urljoin(main_url, cat['href']) for cat in category_links}

main_url = "https://books.toscrape.com/index.html"
categories = get_category_links(main_url)
image_folder = 'book_images'

for category_name, category_url in categories.items():
    print(f"Scraping category: {category_name}")
    data = scrape_category(category_url, image_folder)

    if data:
        timestamp = datetime.now()
        filename = f"{category_name.replace(' ', '_')}_{timestamp}.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data for {category_name} saved to {filename}")
    else:
        print(f"No data found for {category_name}")
