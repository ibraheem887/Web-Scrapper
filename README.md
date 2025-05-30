# NeurIPS Paper Scraper

## Overview
This project implements web scrapers in Python to extract research paper details from the NeurIPS Proceedings website (https://papers.nips.cc). The goal is to gather data for papers from the last five years, handling challenges such as pagination and JavaScript-rendered content.

## What is Web Scraping?
Web scraping is the automated process of extracting information from websites. It is useful for academic research as it allows researchers to gather large amounts of data quickly, enabling analysis of trends, patterns, and insights that would be difficult to obtain manually.

## Features
- Scrapes research paper details, including titles, authors, publication years, and abstracts.
- Utilizes Java for faster extraction and downloads.
- Employs Python with `aiohttp` for asynchronous scraping to speed up data retrieval.
- Handles JavaScript-rendered content when necessary.
- Data is stored locally for easy querying.

## Challenges Encountered
- **Rate Limiting**: Encountered restrictions on the number of requests per minute. Implemented delays to avoid being blocked.
- **Pagination**: Managed multiple pages of results, ensuring all papers were scraped efficiently.
- **JavaScript Loading**: Dealt with content that required JavaScript to load by using headless browsers in Java.

## Comparison of Implementations
- **Java**: 
  - **Strengths**: Faster execution, more efficient for large-scale data extraction.
  - **Weaknesses**: More complex setup and configuration.
  
- **Python**: 
  - **Strengths**: Easier to write and maintain, excellent libraries for handling asynchronous requests.
  - **Weaknesses**: Slower compared to Java for large data sets.

## Insights from Extracted Data
- Total number of papers extracted.
- Patterns in authorship, such as collaboration networks or frequent contributors.
- Trends in research topics over the past five years.

## Responsible Web Scraping Practices
- Respect the website's `robots.txt` file and terms of service.
- Implement rate limiting to avoid overwhelming the server.
- Ensure that the data is used ethically and responsibly.

## What I Learned
This project enhanced my skills in web scraping, understanding the intricacies of data extraction, and the importance of ethical considerations in handling web data.


   
