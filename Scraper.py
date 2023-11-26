import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Define the URL of the product page from the website
product_page_url = 
"https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html"

# Send a request to the URL
response = requests.get(product_page_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract required fields
    title = soup.find('h1').text
    product_description = soup.find('meta', attrs={'name': 
'description'})['content'].strip()
    category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text
    review_rating = soup.find('p', class_='star-rating')['class'][-1]
    image_url = soup.find('img')['src']
    image_url = requests.compat.urljoin(product_page_url, image_url)

    # Find the product information table for the rest of the information
    product_info = soup.find('table', class_='table 
table-striped').find_all('tr')
    product_info_dict = {row.find('th').text: row.find('td').text for row 
in product_info}

    # Create a dictionary for all the information
    product_data = {
        'product_page_url': product_page_url,
        'universal_product_code (upc)': product_info_dict.get('UPC'),
        'book_title': title,
        'price_including_tax': product_info_dict.get('Price (incl. tax)'),
        'price_excluding_tax': product_info_dict.get('Price (excl. tax)'),
        'quantity_available': product_info_dict.get('Availability'),
        'product_description': product_description,
        'category': category,
        'review_rating': review_rating,
        'image_url': image_url
    }

    # Define the CSV file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{title.replace(' ', '_')}_{timestamp}.csv"

    # Write data to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=product_data.keys())
        writer.writeheader()
        writer.writerow(product_data)

    print(f"Data successfully saved to {filename}")
else:
    print("Failed to retrieve the page")

