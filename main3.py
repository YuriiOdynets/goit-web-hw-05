import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict

class ExchangeRateFetcher:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_rate_for_date(self, session: aiohttp.ClientSession, date: str) -> Dict:
        url = f"{self.base_url}?date={date}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise Exception(f"Failed to fetch data: {response.status}")
        except Exception as e:
            print(f"Error fetching data for {date}: {e}")
            return {}

    async def fetch_rates(self, days: int) -> List[Dict]:
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.fetch_rate_for_date(session, date))

            results = await asyncio.gather(*tasks)
        return results

def display_rates(rates: List[Dict]):
    for rate in rates:
        if not rate:
            continue
        date = rate.get('date')
        print(f"Date: {date}")
        exchange_rates = rate.get('exchangeRate', [])
        for item in exchange_rates:
            if item['currency'] in ['USD', 'EUR']:
                currency = item['currency']
                sale_rate = item.get('saleRate', 'N/A')
                purchase_rate = item.get('purchaseRate', 'N/A')
                print(f"{currency}: Sale Rate - {sale_rate}, Purchase Rate - {purchase_rate}")
        print("")

async def main():
    while True:
        user_input = input("Set number of days you would like to get currency rates for (up to 10), or type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            print("Exiting program.")
            return

        try:
            days = int(user_input)
            if 1 <= days <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 10 or type 'exit' to quit.")

    fetcher = ExchangeRateFetcher("https://api.privatbank.ua/p24api/exchange_rates")
    rates = await fetcher.fetch_rates(days)
    display_rates(rates)

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())