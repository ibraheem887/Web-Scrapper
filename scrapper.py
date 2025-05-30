import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import os
import ssl
import certifi
import traceback
import random
import re       
from urllib.parse import urljoin

# Base URL and Paths
BASE_URL = "https://papers.nips.cc"
DESKTOP_PATH = "E:/python/NeurIPS_Papers/"
os.makedirs(DESKTOP_PATH, exist_ok=True)

# Custom Headers to Avoid Blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# SSL Context Fix
ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())  
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Function to sanitize filenames (remove invalid characters)
def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '_', title).strip()[:200] + ".pdf"

# Setup CSV File
async def setup_csv():
    async with aiofiles.open(os.path.join(DESKTOP_PATH, "output.csv"), mode='w', encoding="utf-8") as f:
        await f.write("Year,Title,Authors,Paper Link,PDF Link\n")

# Download file with a maximum of 3 retries
async def download_file(session, file_url, save_path):
    for attempt in range(1, 4):  # Max 3 attempts
        try:
            print(f"🔄 Attempt {attempt}: Downloading {file_url}")
            async with session.get(file_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=120, connect=60)) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, 'wb') as f:
                        await f.write(await response.read())
                    print(f"✅ Downloaded: {save_path}")
                    return
                else:
                    print(f"❌ Failed {file_url}, Status: {response.status}")

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            traceback.print_exc()

        if attempt < 3:
            wait_time = random.randint(5, 15)
            print(f"🔁 Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    print(f"❌ Skipped file (after 3 failed attempts): {file_url}")

# Fetch paper details with a max of 3 retries
async def fetch_paper_details(session, year, paper_title, paper_page_url, year_folder):
    for attempt in range(1, 4):  # Max 3 attempts
        try:
            print(f"🔍 Fetching details for: {paper_title} ({year}) - Attempt {attempt}")
            async with session.get(paper_page_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=120, connect=60)) as response:
                if response.status == 200:
                    paper_doc = await response.text()
                    soup = BeautifulSoup(paper_doc, 'html.parser')

                    # Extract authors
                    author_elements = soup.select('i')
                    authors = ', '.join([author.text.strip() for author in author_elements])

                    # Find PDF link
                    pdf_element = soup.select_one('a[href$=".pdf"]')
                    pdf_url = urljoin(BASE_URL, pdf_element['href']) if pdf_element else "N/A"

                    if pdf_url != "N/A":
                        sanitized_title = sanitize_filename(paper_title)
                        pdf_save_path = os.path.join(year_folder, sanitized_title)
                        await download_file(session, pdf_url, pdf_save_path)

                    # Write data to CSV with UTF-8 encoding
                    async with aiofiles.open(os.path.join(DESKTOP_PATH, "output.csv"), mode='a', encoding="utf-8") as f:
                        await f.write(f'"{year}","{paper_title}","{authors}","{paper_page_url}","{pdf_url}"\n')
                    print(f"✅ Processed paper: {paper_title}")
                    return

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for {paper_title}: {e}")
            traceback.print_exc()

        if attempt < 3:
            wait_time = random.randint(5, 15)
            print(f"🔁 Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    print(f"❌ Skipped paper (after 3 failed attempts): {paper_title}")

# Process year with a max of 3 retries
async def process_year(session, year):
    year_url = f"{BASE_URL}/paper_files/paper/{year}"  # Update if needed
    year_folder = os.path.join(DESKTOP_PATH, str(year))
    os.makedirs(year_folder, exist_ok=True)

    for attempt in range(1, 4):  # Max 3 attempts
        try:
            print(f"📅 Fetching year: {year} - Attempt {attempt}")
            async with session.get(year_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=120, connect=60)) as response:
                if response.status == 200:
                    year_doc = await response.text()
                    soup = BeautifulSoup(year_doc, 'html.parser')

                    # Extract paper links
                    paper_links = soup.select("ul.paper-list li a")
                    if not paper_links:
                        print(f"⚠️ No papers found for {year_url}")
                        return

                    tasks = []
                    for paper_link in paper_links:
                        paper_title = paper_link.text.strip()
                        paper_page_url = urljoin(BASE_URL, paper_link['href'])
                        tasks.append(fetch_paper_details(session, year, paper_title, paper_page_url, year_folder))

                        # Limit concurrency (50 at a time)
                        if len(tasks) >= 50:
                            await asyncio.gather(*tasks)
                            tasks = []

                    if tasks:
                        await asyncio.gather(*tasks)

                    print(f"✅ Completed processing year: {year}")
                    return

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for {year}: {e}")
            traceback.print_exc()

        if attempt < 3:
            wait_time = random.randint(10, 30)
            print(f"🔁 Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    print(f"❌ Skipped year (after 3 failed attempts): {year}")

# Main function (Process one year at a time)
async def main():
    await setup_csv()
    years_to_scrape = [2020, 2019]  # Process 2020 first, then others

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        for year in years_to_scrape:
            print(f"📂 Processing year {year}")
            await process_year(session, year)

# Run script
if __name__ == '__main__':
    asyncio.run(main())
