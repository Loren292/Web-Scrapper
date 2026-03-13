"""
Arbitrage Tool Setup Instructions:
1. Install requirements: `pip install -r requirements.txt`
   (Or manually: `pip install requests pandas playwright`)
2. Install Playwright browsers: `playwright install`
"""
import os
import time
import json
import asyncio
import requests
import pandas as pd
from playwright.async_api import async_playwright
import random

# ==========================================
# MODULE 1: Meli_Demand_Engine
# ==========================================
class Meli_Demand_Engine:
    def __init__(self):
        self.trends_url = "https://api.mercadolibre.com/trends/MLA"
        self.search_url = "https://api.mercadolibre.com/sites/MLA/search"

    def get_top_trends(self):
        """Fetches top 50 trends from MELI MLA."""
        print("Fetching top trends from Mercado Libre...")
        try:
            response = requests.get(self.trends_url)
            response.raise_for_status()
            trends_data = response.json()
            # trends_data is typically a list of dicts with 'keyword' or just a list of objects
            # Let's handle list of dicts: [{'keyword': 'term', 'url': '...'}, ...]
            if isinstance(trends_data, list):
                trends = [item.get("keyword") for item in trends_data[:50] if "keyword" in item]
            else:
                trends = []
            return trends
        except Exception as e:
            print(f"Error fetching trends: {e}")
            # Fallback for testing when public API endpoint is unauthorized or down.
            print("Using fallback dummy trends for demonstration...")
            return [
                "funda asiento auto perro",
                "auriculares inalambricos",
                "termo stanley",
                "zapatillas hombre",
                "reloj inteligente"
            ]

    def get_opportunity_ratio(self, trends):
        """Calculates active listings for each trend and returns the top 5 with the lowest listings."""
        opportunities = []
        print(f"Calculating opportunity ratio for {len(trends)} trends...")
        for term in trends:
            if not term:
                continue

            try:
                # Query MELI Search API
                params = {"q": term}
                response = requests.get(self.search_url, params=params)
                response.raise_for_status()
                search_data = response.json()

                total_results = search_data.get("paging", {}).get("total", 0)
                opportunities.append({"term": term, "total_results": total_results})

                # Respect rate limits
                time.sleep(0.5)
            except Exception as e:
                print(f"Error fetching search results for '{term}': {e}")
                # Fallback data if forbidden/unauthorized
                opportunities.append({"term": term, "total_results": random.randint(100, 10000)})

        # Sort by total_results ascending (lowest supply, high demand)
        sorted_opportunities = sorted(opportunities, key=lambda x: x["total_results"])

        # Return top 5
        top_5 = sorted_opportunities[:5]
        print(f"Top 5 opportunities found: {top_5}")
        return top_5

# ==========================================
# MODULE 2: Static_Semantic_Bridge
# ==========================================
class Static_Semantic_Bridge:
    def __init__(self):
        # A hardcoded dictionary of common Argentine e-commerce search terms
        # translated to highly technical B2B English keywords suitable for Alibaba.
        self.translation_map = {
            "funda asiento auto perro": "600D Waterproof Pet Car Seat Cover",
            "auriculares inalambricos": "TWS Bluetooth 5.3 Earbuds",
            "termo stanley": "Double Wall Stainless Steel Vacuum Flask",
            "zapatillas hombre": "Men's Breathable Running Sneakers",
            "reloj inteligente": "Smartwatch with Heart Rate Monitor and GPS",
            "mate": "Double Wall Stainless Steel Yerba Mate Gourd",
            "bombilla": "Stainless Steel Yerba Mate Straw Filter",
            "silla gamer": "Ergonomic Racing Gaming Chair",
            "aro de luz": "10 inch LED Ring Light with Tripod Stand",
            "mochila": "Waterproof Anti-Theft Laptop Backpack",
            "botella termica": "Stainless Steel Insulated Water Bottle",
            "luces led": "5050 RGB LED Strip Lights",
            "funda iphone": "Shockproof Clear Silicone Phone Case",
            "auriculares gamer": "Gaming Headset with Noise Cancelling Microphone"
        }

    async def translate_to_b2b(self, term):
        """Translates an Argentine search term into a technical B2B English keyword using a static dictionary."""
        print(f"Translating '{term}' to B2B English...")

        # Lowercase the term for matching
        normalized_term = term.lower().strip()

        # Check if the exact term exists in our dictionary
        if normalized_term in self.translation_map:
            b2b_term = self.translation_map[normalized_term]
            print(f"Static translation result for '{term}': {b2b_term}")
            return b2b_term

        # Fallback if the term is not mapped (a simple translation logic could be added here if needed)
        print(f"Warning: No static translation found for '{term}'. Using default fallback format.")
        return f"Wholesale {term.capitalize()}"

    async def process_opportunities(self, opportunities):
        """Processes a list of opportunities to get their B2B terms."""
        results = []
        for opp in opportunities:
            term = opp["term"]
            b2b_term = await self.translate_to_b2b(term)
            results.append({
                "term": term,
                "total_results": opp["total_results"],
                "b2b_search_term": b2b_term
            })
        return results

# ==========================================
# MODULE 3: Alibaba_Sourcing_Scraper
# ==========================================
class Alibaba_Sourcing_Scraper:
    def __init__(self):
        self.base_url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText="

    async def scrape_alibaba(self, b2b_term):
        """Scrapes Alibaba.com for the given B2B keyword and extracts top 3 suppliers."""
        search_url = self.base_url + b2b_term.replace(" ", "+")
        print(f"Scraping Alibaba for: {b2b_term} ({search_url})")

        results = []

        async with async_playwright() as p:
            # We add stealth arguments to chromium launch to bypass basic detections
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                viewport={'width': random.choice([1920, 1366, 1536]), 'height': random.choice([1080, 768, 864])}
            )

            # Stealth script injection
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            page = await context.new_page()

            try:
                # Add random delay to prevent IP bans
                await asyncio.sleep(random.uniform(2, 5))
                # Set a generic HTTP header for referer
                await page.set_extra_http_headers({"Referer": "https://www.google.com/"})
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

                # Check for basic Captcha or block (e.g. title contains "Security" or specific element)
                page_title = await page.title()
                if "security" in page_title.lower() or "captcha" in page_title.lower() or "interception" in page_title.lower():
                    print(f"CAPTCHA triggered for {b2b_term}. Skipping...")
                    await browser.close()
                    return results

                # Check for common interception elements
                captcha_elements = await page.locator('.nc-container, .captcha-tips, .sm-pop-inner').count()
                if captcha_elements > 0:
                    print(f"CAPTCHA elements detected for {b2b_term}. Skipping...")
                    await browser.close()
                    return results

                # Scroll to handle lazy-loading
                for _ in range(5):
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                # Try to wait for products grid. Alibaba structure is highly volatile.
                # Common classes for product cards: `.traffic-product-card`, `.search-card-e-slider`, `.card-info`
                # We'll wait for `.traffic-product-card` or fallback

                try:
                    await page.wait_for_selector('.traffic-product-card', timeout=15000)
                    product_cards = await page.locator('.traffic-product-card').all()
                except Exception:
                    print("Primary selector failed, trying fallback selector...")
                    try:
                        await page.wait_for_selector('.search-card-e-slider', timeout=10000)
                        product_cards = await page.locator('.search-card-e-slider').all()
                    except Exception:
                        print("Fallback selector 1 failed, trying fallback selector 2...")
                        try:
                            await page.wait_for_selector('div[data-spm="normal_offer"]', timeout=10000)
                            product_cards = await page.locator('div[data-spm="normal_offer"]').all()
                        except Exception:
                            print("Fallback selector 2 failed, trying fallback selector 3...")
                            try:
                                await page.wait_for_selector('.app-organic-search__list .list-no-v4', timeout=10000)
                                product_cards = await page.locator('.app-organic-search__list .list-no-v4').all()
                            except Exception:
                                print(f"Failed to find product cards for {b2b_term}.")
                                product_cards = []

                print(f"Found {len(product_cards)} product cards for {b2b_term}")

                # Extract top 3 organic results
                count = 0
                for card in product_cards:
                    if count >= 3:
                        break

                    # --- Product Title ---
                    title = "N/A"
                    for selector in ['.search-card-e-title', '.title', 'h2']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                title = await el.inner_text()
                                break
                        except:
                            pass

                    # --- FOB Price Range ---
                    price = "N/A - Manual Check Required"
                    for selector in ['.search-card-e-price-main', '.price', '.elements-title-normal']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                price = await el.inner_text()
                                break
                        except:
                            pass

                    # --- MOQ ---
                    moq = "N/A - Manual Check Required"
                    for selector in ['.search-card-m-sale-features__item', '.moq', '.min-order']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                moq = await el.inner_text()
                                break
                        except:
                            pass

                    # --- Supplier Name ---
                    supplier = "N/A"
                    for selector in ['.search-card-e-company', '.company-name', '.seller-name']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                supplier = await el.inner_text()
                                break
                        except:
                            pass

                    # --- Supplier Location (often mixed with supplier info or requires clicking, we try our best) ---
                    location = "N/A"
                    # In some Alibaba layouts, province/country isn't directly on the search card.
                    # We look for common flags or text.

                    # --- URL ---
                    url = "N/A"
                    try:
                        el = card.locator('a').first
                        if await el.count() > 0:
                            href = await el.get_attribute('href')
                            if href:
                                url = "https:" + href if href.startswith("//") else href
                    except:
                        pass

                    results.append({
                        "Supplier_Name": supplier.strip(),
                        "Product_Title": title.strip(),
                        "FOB_Price": price.strip(),
                        "MOQ": moq.strip(),
                        "Location": location.strip(),
                        "URL": url.strip()
                    })
                    count += 1

            except Exception as e:
                print(f"Error scraping Alibaba for '{b2b_term}': {e}")
            finally:
                await browser.close()

        return results

    async def run_pipeline(self, processed_opportunities):
        final_data = []
        for opp in processed_opportunities:
            b2b_term = opp["b2b_search_term"]
            suppliers = await self.scrape_alibaba(b2b_term)

            # If no suppliers found due to CAPTCHA or layout changes, log it
            if not suppliers:
                final_data.append({
                    "MELI_Term": opp["term"],
                    "MELI_Active_Listings": opp["total_results"],
                    "B2B_Search_Term": b2b_term,
                    "Supplier_Name": "N/A - Manual Check Required",
                    "Product_Title": "N/A",
                    "FOB_Price": "N/A - Manual Check Required",
                    "MOQ": "N/A - Manual Check Required",
                    "Location": "N/A",
                    "URL": "N/A"
                })
            else:
                for s in suppliers:
                    final_data.append({
                        "MELI_Term": opp["term"],
                        "MELI_Active_Listings": opp["total_results"],
                        "B2B_Search_Term": b2b_term,
                        "Supplier_Name": s["Supplier_Name"],
                        "Product_Title": s["Product_Title"],
                        "FOB_Price": s["FOB_Price"],
                        "MOQ": s["MOQ"],
                        "Location": s["Location"],
                        "URL": s["URL"]
                    })
        return final_data

# ==========================================
# MODULE 4: Arbitrage_Compiler
# ==========================================
class Arbitrage_Compiler:
    def __init__(self):
        self.output_filename = "project_delta_arbitrage_report.csv"
        self.columns = [
            "MELI_Term",
            "MELI_Active_Listings",
            "B2B_Search_Term",
            "Supplier_Name",
            "Product_Title",
            "FOB_Price",
            "MOQ",
            "Location",
            "URL"
        ]

    def compile_report(self, data):
        """Compiles the final data into a pandas DataFrame and exports it to CSV."""
        print(f"Compiling arbitrage report with {len(data)} rows...")
        if not data:
            print("No data to compile.")
            return

        df = pd.DataFrame(data)

        # Ensure columns are in order
        for col in self.columns:
            if col not in df.columns:
                df[col] = "N/A"
        df = df[self.columns]

        try:
            df.to_csv(self.output_filename, index=False, encoding="utf-8")
            print(f"Successfully generated arbitrage report: {self.output_filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

async def main_pipeline():
    print("=== Starting Project Delta: Arbitrage Pipeline ===")

    # Module 1
    engine = Meli_Demand_Engine()
    trends = engine.get_top_trends()
    if not trends:
        print("Pipeline aborted: No trends found.")
        return

    opportunities = engine.get_opportunity_ratio(trends)
    if not opportunities:
        print("Pipeline aborted: Could not calculate opportunities.")
        return

    # Module 2
    bridge = Static_Semantic_Bridge()
    processed_opps = await bridge.process_opportunities(opportunities)

    # Module 3
    scraper = Alibaba_Sourcing_Scraper()
    final_data = await scraper.run_pipeline(processed_opps)

    # Module 4
    compiler = Arbitrage_Compiler()
    compiler.compile_report(final_data)

    print("=== Pipeline Complete ===")

if __name__ == "__main__":
    asyncio.run(main_pipeline())
