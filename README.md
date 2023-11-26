# OpenclassroomsProject.
# Books Online Price Monitoring System

## Overview
This project is a web scraping tool developed in Python, designed to monitor and extract book pricing and information from the ["Books to Scrape"](https://books.toscrape.com/index.html) website. It aims to provide a comprehensive dataset of books, including details like title, price, availability, category, and more.


## Features
- Extracts detailed information from individual book pages.
- Ability to scrape entire categories of books.
- Handles pagination to gather data from multiple pages within a category.
- Collects data across all book categories available on the site.
- Downloads and saves book cover images.

## Requirements
Python 3.x with additional libraries which are listed in the `requirements.txt` file.

## Output
The script outputs CSV files with data for each category or product, depending on the chosen mode. Images (if applicable) are saved in a separate directory.

## Project Structure

- Scraper.py: The main Python script for scraping data.
- requirements.txt: Lists all the necessary Python libraries.
- README.md: This file, containing instructions and project information.

### Clone the Repository
```bash
git clone https://github.com/walter-cueva/Book_Scraper.git

