import requests
import random
import time
from tqdm import tqdm  # Import tqdm for the loading bar

def get_items():
    url = "https://api.warframe.market/v1/items"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch items. HTTP Status code: {response.status_code}")
        return []

    data = response.json()
    items = data.get('payload', {}).get('items', [])
    return items

def get_orders(item_url_name):
    url = f"https://api.warframe.market/v1/items/{item_url_name}/orders"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch orders for {item_url_name}. HTTP Status code: {response.status_code}")
        return []

    data = response.json()
    orders = data.get('payload', {}).get('orders', [])
    return orders

def find_biggest_difference(num_items, filter_string):
    items = get_items()
    if not items:
        return

    # Filter items to only include those with the filter_string in the name
    filtered_items = [item for item in items if filter_string.lower() in item['item_name'].lower()]

    # Determine the number of items to process
    if num_items == 'all':
        selected_items = filtered_items
    else:
        num_items = int(num_items)
        selected_items = random.sample(filtered_items, num_items)

    print(f"Processing {len(selected_items)} items out of {len(filtered_items)} filtered items.")

    differences = []

    # Use tqdm to create a loading bar
    for item in tqdm(selected_items, desc="Processing items", unit="item"):
        item_url_name = item['url_name']
        orders = get_orders(item_url_name)

        # Group orders by rank
        orders_by_rank = {}
        for order in orders:
            rank = order.get('mod_rank', 0)
            if rank not in orders_by_rank:
                orders_by_rank[rank] = {'buy': [], 'sell': []}
            if order['order_type'] == 'buy' and order['user']['status'] == 'ingame':
                orders_by_rank[rank]['buy'].append(order)
            elif order['order_type'] == 'sell' and order['user']['status'] == 'ingame':
                orders_by_rank[rank]['sell'].append(order)

        # Compare orders within the same rank
        for rank, rank_orders in orders_by_rank.items():
            buy_orders = rank_orders['buy']
            sell_orders = rank_orders['sell']

            if not buy_orders or not sell_orders:
                continue

            highest_buy_order = max(buy_orders, key=lambda x: x['platinum'])
            lowest_sell_order = min(sell_orders, key=lambda x: x['platinum'])

            difference = highest_buy_order['platinum'] - lowest_sell_order['platinum']
            differences.append((difference, item, highest_buy_order, lowest_sell_order, rank))

        # Introduce a delay between requests
        time.sleep(0.25)

    # Sort by difference and get the top 10
    differences.sort(reverse=True, key=lambda x: x[0])
    top_10 = differences[:10]

    for diff, item, buy_order, sell_order, rank in top_10:
        print(f"Item: {item['item_name']} (Rank: {rank})")
        print(f"Highest buy order: {buy_order['platinum']} platinum by {buy_order['user']['ingame_name']}")
        print(f"Lowest sell order: {sell_order['platinum']} platinum by {sell_order['user']['ingame_name']}")
        print(f"Difference: {diff} platinum\n")

if __name__ == "__main__":
    filter_string = input("Enter the string that the item name should contain: ")
    print("Select the number of items to process:")
    print("1. All items")
    print("2. Specify the number of items")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        find_biggest_difference('all', filter_string)
    elif choice == '2':
        num_items = input("Enter the number of items to process: ")
        find_biggest_difference(num_items, filter_string)
    else:
        print("Invalid choice. Please run the program again and select a valid option.")
