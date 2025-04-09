import requests
from bs4 import BeautifulSoup
import csv
import os

# Base URL for category 26
base_url = "https://freeplrdownloads.com/page/{}/?cat=26"
csv_file = "plr_ebooks_category_26.csv"
download_folder = "downloads"  # Folder where the files will be saved locally

# Create download folder if it doesn't exist
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Function to extract data from the individual ebook page
def extract_ebook_details(ebook_url):
    response = requests.get(ebook_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize variables
    full_description = "No full description"
    license_type = "No license"
    source_file = "No source file"
    ecover = "No eCover"
    sales_page = "No sales page"
    squeeze_page = "No squeeze page"
    niche = "No niche"
    file_size = "No file size"
    download_link = "No download link"  # Initialize with default value

    # Extract the details from the individual eBook page's table
    details_table = soup.find('table', class_='products-details')

    if details_table:
        # Go through each row (tr) in the table and extract the data
        rows = details_table.find_all('tr')

        # First row for Full Description
        description_row = rows[0].find('td', class_='row')
        if description_row:
            full_description = description_row.get_text().strip().replace("Description:", "").strip()

        # Second row for License
        if len(rows) > 1:
            license_row = rows[1].find('td', class_='row2')
            if license_row:
                license_type = license_row.get_text().strip().replace("License:", "").strip()

        # Row for Source File (usually the 3rd row)
        if len(rows) > 2:
            source_file_row = rows[2].find('td', class_='row')
            if source_file_row:
                source_file = source_file_row.get_text().strip().replace("Source File:", "").strip()

        # Row for eCover (usually the 4th row)
        if len(rows) > 3:
            ecover_row = rows[3].find('td', class_='row2')
            if ecover_row:
                ecover = ecover_row.get_text().strip().replace("eCover:", "").strip()

        # Row for Sales Page (usually the 5th row)
        if len(rows) > 4:
            sales_page_row = rows[4].find('td', class_='row')
            if sales_page_row:
                sales_page = sales_page_row.get_text().strip().replace("Sales Page:", "").strip()

        # Row for Squeeze Page (usually the 6th row)
        if len(rows) > 5:
            squeeze_page_row = rows[5].find('td', class_='row2')
            if squeeze_page_row:
                squeeze_page = squeeze_page_row.get_text().strip().replace("Squeeze Page:", "").strip()

        # Row with Niche (usually the 7th row)
        if len(rows) > 6:
            niche_row = rows[6].find('td', class_='row')
            if niche_row:
                niche = niche_row.get_text().strip().replace("Niche:", "").strip()

        # Row with File Size (usually the 8th row)
        if len(rows) > 7:
            file_size_row = rows[7].find('td', class_='row2')
            if file_size_row:
                file_size = file_size_row.get_text().strip().replace("File Size:", "").strip()

    # Now fetch the download link (relative URL, so we need to append the base URL)
    download_link_tag = soup.find('a', class_='btn', href=True, title="Download")
    if download_link_tag:
        relative_download_link = download_link_tag['href']
        download_link = f"https://freeplrdownloads.com{relative_download_link}"

    return {
        "Full Description": full_description,
        "License": license_type,
        "Source File": source_file,
        "eCover": ecover,
        "Sales Page": sales_page,
        "Squeeze Page": squeeze_page,
        "Niche": niche,
        "File Size": file_size,
        "Download Link": download_link
    }

# Function to extract data from one page
def extract_page_data(page_num):
    url = base_url.format(page_num)
    print(f"Scraping page {page_num}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the eBook containers (div with class "posthome")
    ebook_containers = soup.find_all('div', class_='posthome')

    # If no ebooks are found on the page, log and return an empty list
    if not ebook_containers:
        print(f"No eBooks found on page {page_num}. Skipping this page.")
        return []

    ebook_list = []

    for ebook in ebook_containers:
        # Title
        title_tag = ebook.find('h2', class_='entry-title')
        title = title_tag.get_text().strip() if title_tag else "No title"

        # Short Description (from the homepage)
        description_tag = ebook.find('div', class_='entry-content-home')
        description = description_tag.get_text().strip() if description_tag else "No description"

        # eBook Link (to the full page)
        ebook_link_tag = ebook.find('a', href=True)
        ebook_link = ebook_link_tag['href'] if ebook_link_tag else "No link"

        # Image URL
        img_tag = ebook.find('img')
        img_url = img_tag['src'] if img_tag else "No image"

        # Now fetch additional details from the individual eBook page
        ebook_details = extract_ebook_details(ebook_link)

        # Combine data
        ebook_data = {
            "Title": title,
            "Description": description,
            "Link": ebook_link,
            "Image URL": img_url,
            "Page": url,
            "Full Description": ebook_details["Full Description"],
            "License": ebook_details["License"],
            "Source File": ebook_details["Source File"],
            "eCover": ebook_details["eCover"],
            "Sales Page": ebook_details["Sales Page"],
            "Squeeze Page": ebook_details["Squeeze Page"],
            "Niche": ebook_details["Niche"],
            "File Size": ebook_details["File Size"],
            "Download Link": ebook_details["Download Link"]
        }

        ebook_list.append(ebook_data)

        # Download the file locally
        download_file(ebook_details["Download Link"], title)

    return ebook_list

# Function to download the file locally
def download_file(download_url, title):
    try:
        # Fetch the file content from the download link
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            # Construct the filename (sanitize title to avoid issues with file systems)
            filename = os.path.join(download_folder, f"{title}.zip")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded {title} successfully.")
        else:
            print(f"Failed to download {title}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {title}: {str(e)}")

# Function to save data to CSV
def save_to_csv(data, filename):
    # Check if there is data to save
    if not data:
        print("No data to save. Exiting.")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

# Main script to iterate over pages and collect data
def main():
    all_ebooks = []
    for page_num in range(1, 81):  # Iterate through 80 pages
        page_data = extract_page_data(page_num)

        # Only add data to the list if the page had eBooks
        if page_data:
            all_ebooks.extend(page_data)

    # Save the data to CSV
    save_to_csv(all_ebooks, csv_file)
    print(f"Scraping complete. Data saved to {csv_file}.")

if __name__ == "__main__":
    main()
