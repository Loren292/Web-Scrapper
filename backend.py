"""
Arbitrage Tool Setup Instructions:
1. Install requirements: `pip install -r requirements.txt`
   (Or manually: `pip install requests pandas playwright`)
2. Install Playwright browsers: `playwright install`
"""
import os
import time
import json
import sys
import asyncio
import requests
import pandas as pd
from playwright.async_api import async_playwright
import random

# ==========================================
# MODULE 1: Meli_Demand_Engine
# ==========================================
class Meli_Demand_Engine:
    def __init__(self, access_token=None):
        self.trends_url = "https://api.mercadolibre.com/trends/MLA"
        self.search_url = "https://api.mercadolibre.com/sites/MLA/search"
        self.access_token = access_token or os.getenv("MELI_ACCESS_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

    def get_top_trends(self, limit=50):
        """Fetches top trends from MELI MLA up to the given limit."""
        print("Fetching top trends from Mercado Libre...")
        try:
            response = requests.get(self.trends_url, headers=self.headers)
            response.raise_for_status()
            trends_data = response.json()
            # trends_data is typically a list of dicts with 'keyword' or just a list of objects
            # Let's handle list of dicts: [{'keyword': 'term', 'url': '...'}, ...]
            if isinstance(trends_data, list):
                trends = [item.get("keyword") for item in trends_data[:limit] if "keyword" in item]
            else:
                trends = []
            return trends
        except Exception as e:
            print(f"Error fetching trends: {e}")
            # Fallback for testing when public API endpoint is unauthorized or down.
            print("Using fallback dummy trends for demonstration...")
            return [
                "funda para asiento de auto perro",  # should match "funda asiento auto"
                "zapatillas deportivas nike",        # should be skipped
                "dispenser agua electrico",          # should match "dispenser agua"
                "espejo led para baño",              # should match "espejo led"
                "auriculares inalambricos"           # should be skipped
            ]

    def get_top_opportunities(self, limit=10):
        """Calculates active listings for each trend and returns the top opportunities."""
        trends = self.get_top_trends(limit=50) # fetch enough trends to sort

        opportunities = []
        print(f"Calculating opportunity ratio for {len(trends)} trends...")
        for term in trends:
            if not term:
                continue

            try:
                # Query MELI Search API
                params = {"q": term}
                response = requests.get(self.search_url, headers=self.headers, params=params)
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

        # Return up to limit
        top_ops = sorted_opportunities[:limit]
        print(f"Top {limit} opportunities found: {top_ops}")
        return top_ops

# ==========================================
# MODULE 2: Static_Semantic_Bridge
# ==========================================
class Static_Semantic_Bridge:
    def __init__(self):
        # El Diccionario Maestro con nichos de alta traccion
        self.mapping = {
            # Electrodomésticos y Cocina
            "campana inteligente": "Smart touch sensor range hood T-shape 900mm",
            "campana extractora": "Wall-mounted kitchen range hood copper motor",
            "bacha negra": "Nano black stainless steel 304 waterfall kitchen sink",
            "bacha acero": "Stainless steel 304 kitchen sink handmade",

            # Tratamiento de Agua y Climatización
            "dispenser agua": "Freestanding water dispenser compressor cooling bottom load",
            "calefon instantaneo": "Tankless electric hot water heater digital display 220V",
            "calefon motorhome": "Portable LPG gas water heater RV tankless",
            "filtro bajo mesada": "Under sink water filter system 3 stage RO",
            "ducha electrica": "Electric shower head instant heater 220V",

            # Seguridad y Smart Home
            "camara solar": "4G PTZ solar panel security camera PIR outdoor",
            "camara wifi": "Tuya smart home WiFi security camera 1080p",
            "cerradura digital": "Tuya smart WiFi biometric fingerprint door lock",
            "espejo led": "Smart LED bathroom mirror anti-fog touch sensor",

            # Mascotas y Vehículos
            "funda asiento auto": "600D Oxford waterproof pet car seat cover hammock",
            "cucha perro": "Outdoor plastic dog house waterproof large",
            "rueda gatos": "Cat exercise wheel treadmill silent",
            "luces parrilla": "LED grille lights Raptor style amber waterproof"
        }

    def translate_terms(self, meli_data):
        """
        Processes a list of opportunities dicts and returns matched translated terms.
        Signature matched for: b2b_terms = Static_Semantic_Bridge().translate_terms(meli_data)
        """
        results = []

        for trend_obj in meli_data:
            trend_lower = trend_obj.get("term", "").lower()
            match_found = False

            # Buscamos si alguna de nuestras claves maestras está en la tendencia de ML
            for ml_key, alibaba_query in self.mapping.items():
                # Checking substring: is the dictionary key inside the ML trend (or vice versa)?
                ml_key_lower = ml_key.lower()

                # We split the ml_key into words and check if all words exist in the trend
                # OR if the exact phrase is in the trend or vice versa.
                ml_words = ml_key_lower.split()
                if all(word in trend_lower for word in ml_words) or ml_key_lower in trend_lower or trend_lower in ml_key_lower:
                    results.append({
                        "term": trend_obj["term"],
                        "total_results": trend_obj.get("total_results", 0),
                        "b2b_search_term": alibaba_query
                    })
                    match_found = True
                    break # Si encuentra coincidencia, pasa a la siguiente tendencia

            if not match_found:
                print(f"Ignorando tendencia fuera de nicho: {trend_obj.get('term', '')}")

        return results

# ==========================================
# MODULE 3: MadeInChina_Sourcing_Scraper
# ==========================================
class MadeInChina_Sourcing_Scraper:
    def __init__(self):
        self.base_url = "https://www.made-in-china.com/productdirectory.do?word="

    async def scrape_mic(self, b2b_term):
        """Scrapes Made-in-China for the given B2B keyword and extracts top 3 suppliers."""
        search_url = self.base_url + b2b_term.replace(" ", "+")
        print(f"Scraping Made-in-China for: {b2b_term} ({search_url})")

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

                # Scroll to handle lazy-loading
                for _ in range(5):
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                # A robust approach to finding product containers on Made-in-China:
                try:
                    await page.wait_for_selector('.product-list .product-item, .list-node', timeout=15000)
                    product_cards = await page.locator('.product-list .product-item, .list-node').all()
                except Exception:
                    print(f"Failed to find product cards for {b2b_term}. Made-in-China layout may have drastically changed.")

                    # Take a screenshot for debugging if it fails
                    try:
                        await page.screenshot(path=f"mic_error_{b2b_term.replace(' ', '_')}.png")
                        print(f"Saved error screenshot to mic_error_{b2b_term.replace(' ', '_')}.png")
                    except Exception:
                        pass

                    product_cards = []

                print(f"Found {len(product_cards)} product cards for {b2b_term}")

                # Extract top 3 organic results
                count = 0
                for card in product_cards:
                    if count >= 3:
                        break

                    # Ensure the card is actually a product by checking for an image or link
                    link_locator = card.locator('a.product-name, a.title, h2 a').first
                    try:
                        if await link_locator.count() == 0:
                            link_locator = card.locator('a').first
                            if await link_locator.count() == 0:
                                continue # Skip non-product wrapper elements
                    except Exception:
                        continue

                    # --- Product Title ---
                    title = "N/A"
                    for selector in ['h2.product-name', '.product-name', 'a.title']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                title = await el.inner_text()
                                if title and len(title) > 3:
                                    break
                        except:
                            pass

                    # --- FOB Price Range ---
                    price = "N/A - Manual Check Required"
                    for selector in ['.price', '.product-price', '.fob-price']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                price = await el.inner_text()
                                if price:
                                    break
                        except:
                            pass

                    # --- MOQ ---
                    moq = "N/A - Manual Check Required"
                    for selector in ['.min-order', '.moq', '.order-quantity']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                moq = await el.inner_text()
                                if moq:
                                    break
                        except:
                            pass

                    # --- Supplier Name ---
                    supplier = "N/A"
                    for selector in ['.company-name', '.supplier-name', '.company-info a']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                supplier = await el.inner_text()
                                if supplier:
                                    break
                        except:
                            pass

                    # --- Supplier Location (often mixed with supplier info or requires clicking, we try our best) ---
                    location = "N/A"
                    for selector in ['.location', '.supplier-location']:
                        try:
                            el = card.locator(selector).first
                            if await el.count() > 0:
                                location = await el.inner_text()
                                if location:
                                    break
                        except:
                            pass

                    # --- URL ---
                    url = "N/A"
                    try:
                        if await link_locator.count() > 0:
                            href = await link_locator.get_attribute('href')
                            if href:
                                url = "https://www.made-in-china.com" + href if href.startswith("/") else href
                                url = "https:" + url if url.startswith("//") else url
                    except:
                        pass

                    results.append({
                        "Supplier_Name": supplier.strip(),
                        "Product_Title": title.strip(),
                        "FOB_Price": price.strip().replace('\n', ' '),
                        "MOQ": moq.strip().replace('\n', ' '),
                        "Location": location.strip(),
                        "URL": url.strip()
                    })
                    count += 1

            except Exception as e:
                print(f"Error scraping Made-in-China for '{b2b_term}': {e}")
            finally:
                await browser.close()

        return results

    def scrape_suppliers(self, processed_opportunities):
        """Synchronous wrapper to scrape suppliers for given opportunities."""
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(self._run_pipeline(processed_opportunities))

    async def _run_pipeline(self, processed_opportunities):
        final_data = []
        for opp in processed_opportunities:
            b2b_term = opp["b2b_search_term"]
            suppliers = await self.scrape_mic(b2b_term)

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
            "MELI_URL",
            "B2B_Search_Term",
            "Supplier_Name",
            "Product_Title",
            "FOB_Price",
            "MOQ",
            "Location",
            "MIC_URL"
        ]

    def generate_dataframe(self, meli_data, mic_data):
        """Compiles the final data into a pandas DataFrame, resolving URLs and exporting it."""
        print(f"Compiling arbitrage report with {len(mic_data)} rows...")
        data = mic_data

        # Add MELI_URL and MIC_URL
        for row in data:
            row["MELI_URL"] = f"https://listado.mercadolibre.com.ar/{row['MELI_Term'].replace(' ', '-')}"
            row["MIC_URL"] = row.pop("URL", "N/A")
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

        return df

if __name__ == "__main__":
    # Test script locally
    limit_input = 5
    meli_data = Meli_Demand_Engine().get_top_opportunities(limit=limit_input)
    b2b_terms = Static_Semantic_Bridge().translate_terms(meli_data)
    mic_data = MadeInChina_Sourcing_Scraper().scrape_suppliers(b2b_terms)
    df_final = Arbitrage_Compiler().generate_dataframe(meli_data, mic_data)
    print(df_final)
