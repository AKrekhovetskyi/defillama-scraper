## Overview

DefiLlama scraper is a web scraper built with Scrapy and Playwright designed to extract DeFi TVL data from [defillama.com](https://defillama.com/). It handles dynamic content through incremental scrolling, validates proxies to ensure connectivity, and processes data with custom pipelines.

## Notes

- Requires Python 3.11+.
- Ensure that the settings in `settings.py` match your network/environment needs.
- For more details, refer to the Scrapy and Playwright documentation.

## Features

- **Dynamic Data Loading:** Uses Playwright to scroll and load AJAX-based content.
- **Proxy Validation:** Validates proxies to bypass site restrictions.
- **Data Deduplication:** Removes duplicate entries before saving.
- **Pipeline Integration:** Processes and stores data in a JSON file.

## Setup

1. **Clone the repository:**

   ```
   git clone --recurse-submodules https://github.com/AKrekhovetskyi/defillama-scraper.git
   cd defillama-scraper
   ```

1. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

   Install [scrapy-playwright](https://pypi.org/project/scrapy-playwright/).

1. **Adjust Settings (if necessary):**

   - Update proxy and file paths in `./defillama-scraper/defillama_scraper/settings.py`.

1. **Configure Proxies:**

   - Add your proxy entries in `./defillama_scraper/proxies/proxies.txt`.
   - Run proxy validation to generate `proxies.json`:
     ```
     python defillama_scraper/proxies/validate_proxy.py
     ```

1. **Run the Scraper:**

   ```
   python -m scrapy crawl defillama
   ```
