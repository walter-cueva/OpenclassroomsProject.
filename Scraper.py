import csv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import os
import re

# this function is responsible to replace any invalid characters in file paths
def sanitize_filename(filename):
    # Remove invalid file path characters
    # The pattern [\\/*?:"<>|] matches characters that are generally not allowed in file names
    # across various operating systems. These characters are replaced with an empty string.
    return re.sub(r'[\\/*?:"<>|]', '', filename)

# this function is responsible for downloading an image from a given URL and saving it to a specified directory
def download_image(image_url, folder="book_images", filename="image.jpg"):
    # Check if the specified folder exists; if not, create it
    if not os.path.exists(folder):
        os.makedirs(folder)  # Create the directory if it doesn't exist

    response = requests.get(image_url)
    if response.status_code == 200:
        # the full file path is constructed where the image will be saved.
        # the image is saved with the provided "filename" in the specified "folder"
        filepath = os.path.join(folder, filename)
        # Open the file in binary write mode and write the image content
        with open(filepath, 'wb') as f:
            # the "response.content" contains the binary data of the image, which is written to a file in
            # binary mode ("wb")
            f.write(response.content)

# Function to scrape a single book data
def scrape_book_data(book_url):
    # Fetching the page content by sending the GET request to the book URL
    response = requests.get(book_url)
    # check if the request is successful
    if response.status_code != 200:
        return None  # If the book page request fails, return None
# parse the html content of the book page into a soup object
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize variables and add extract various pieces of info from the book page using BeautifulSoup
    product_page_url = book_url
    universal_product_code = soup.find('th', string='UPC').find_next('td').text
    book_title = soup.find("h1").text
    price_including_tax = soup.find('th', string='Price (incl. tax)').find_next('td').text
    price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next('td').text
    quantity_available = soup.find('th', string='Availability').find_next('td').text
    # responsible to extract the product description
    # find the first meta tag with the attributes "name" set to "description"
    # and use ['content'] to access the content attribute of that tag
    product_description = soup.find('meta', attrs={'name': 'description'})['content'].strip()
    # find ul elements and then find all 'a' elements and select the third "a" element (index [2]),
    # finally get the text part of the "a" element
    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
    # find the first "p" element with a class "start-rating"
    # ['class'] access its class attribute and [1] get the second index
    review_rating = soup.find('p', class_='star-rating')['class'][1]
    # find first "img" tag and then its attribute "src".
    # the urljoin used to combine src URL to book_url and form a full absolute URL of the image
    image_url = urljoin(book_url, soup.find("img")["src"])
    # Book title is sanitized and then used to create the filename for the image
    image_filename = f"{sanitize_filename(book_title)}.jpg"
    download_image(image_url, folder="book_images", filename=image_filename)
    # Data row for the CSV file
    data_row = [
        product_page_url, universal_product_code, book_title,
        price_including_tax, price_excluding_tax, quantity_available,
        product_description, category, review_rating, image_url
    ]
    return data_row


# Function to get all book URLs from a category page
def get_book_urls(category_url):
    # initialize an empty list to stor book's urls
    book_urls = []
    # loop to go through all the pages in the category
    while True:
        # Send a GET request
        response = requests.get(category_url)
        if response.status_code != 200:
            break
        # parse the content of the html into the soup object
        soup = BeautifulSoup(response.content, 'html.parser')
        # Select all the 'h3 > a' elements linked to each book title listed under the category
        books = soup.select('h3 > a')
        # the urljoin used to combine src URL to book_url and form a full absolute URL of the image. Use .extend
        # method to add each element individually to the list
        book_urls.extend([urljoin(category_url, book['href']) for book in books])

        # Look for the 'next' button on the page, and
        next_button = soup.select_one('li.next > a')
        # If a 'next' button is found, update the category_url to the URL of the next page
        # If not, exit the loop as we have reached the last page of the category
        if next_button:
            category_url = urljoin(category_url, next_button['href'])
        else:
            break

    return book_urls

# Function to get all categories URLs from the main URL
def get_categories(main_url):
    # Send a GET request to the main URL of the website
    response = requests.get(main_url)
    # Check if the request was successful
    if response.status_code != 200:
        return []
    # Parse the HTML content of the main page
    soup = BeautifulSoup(response.content, 'html.parser')
    # Select all anchor ('a') elements within the specified CSS path
    # These elements correspond to the different book categories on the site
    category_list = soup.select('div.side_categories ul.nav-list > li > ul > li > a')
    # Create a dictionary where each category name is a key and its URL is the value
    # cat.text.strip() part of the code is used to extract and clean up the text from an HTML element
    categories = {cat.text.strip(): urljoin(main_url, cat['href']) for cat in category_list}
    # print(categories)
    return categories  # Return the dictionary of categories


# Main script
if __name__ == "__main__":
    main_url = "http://books.toscrape.com/index.html"
    # Retrieve all categories and their URLs
    categories = get_categories(main_url)
    # Loop through each category.
    # categories.items():
    # This method returns a view object that displays a list of a dictionary's key-value tuple pairs.

    for category_name, category_url in categories.items():

        # Get all book URLs for the current category
        book_urls = get_book_urls(category_url)
        # Define the filename for the CSV file, using the category name
        # The replace method is used on the string category_name.
        # This method replaces all spaces (' ') in category_name with underscores ('_').
        csv_filename = f"{category_name.replace(' ', '_')}_books.csv"
        # Define the headers for the CSV file
        headers = [
            "Product Page URL", "Universal Product Code", "Book Title",
            "Price Including Tax", "Price Excluding Tax", "Quantity Available",
            "Product Description", "Category", "Review Rating", "Image URL"
        ]
        # Open the CSV file for writing
        # with is used to properly close after the code is executed
        # "newline = "" to avoid extra blank lines btw rows
        # as csvfile to assign the file object returned by open() to a variable
        with open(csv_filename, "w", newline='') as csvfile:
            # create a writer object to write to the file object csvfile
            # use csv.writer to write data in a CSV format and create a write object
            writer = csv.writer(csvfile)
            # use the writerow method to write a single row to a CSV file
            writer.writerow(headers)  # Write the headers to the CSV file
            # Loop over each book URL in the category and scrape its data
            for book_url in book_urls:
                data_row = scrape_book_data(book_url)
                # If data was successfully scraped, write it to the CSV file as a row
                if data_row:
                    writer.writerow(data_row)
        # After processing all books in the category, print a message
        print(f"Data written to {csv_filename}.")
    # After processing all categories, print a final message
    print("All categories processed.")