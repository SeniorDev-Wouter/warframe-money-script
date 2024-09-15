import requests
import random
import time


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


def find_biggest_difference(num_items):
    items = get_items()
    if not items:
        return

    # Filter items to only include those with 'prime' in the name
    prime_items = [item for item in items if 'prime' in item['item_name'].lower()]

    # Determine the number of items to process
    if num_items == 'all':
        selected_items = prime_items
    else:
        num_items = int(num_items)
        selected_items = random.sample(prime_items, num_items)

    print(f"Processing {len(selected_items)} items out of {len(prime_items)} prime items.")

    differences = []

    for item in selected_items:
        item_url_name = item['url_name']
        print(f"Processing item: {item['item_name']}")  # Print the item being processed
        orders = get_orders(item_url_name)

        buy_orders = [order for order in orders if order['order_type'] == 'buy' and order['user']['status'] == 'ingame']
        sell_orders = [order for order in orders if
                       order['order_type'] == 'sell' and order['user']['status'] == 'ingame']

        if not buy_orders or not sell_orders:
            continue

        highest_buy_order = max(buy_orders, key=lambda x: x['platinum'])
        lowest_sell_order = min(sell_orders, key=lambda x: x['platinum'])

        difference = highest_buy_order['platinum'] - lowest_sell_order['platinum']

        differences.append((difference, item, highest_buy_order, lowest_sell_order))

        # Introduce a delay between requests
        time.sleep(0.3)

    # Sort by difference and get the top 3
    differences.sort(reverse=True, key=lambda x: x[0])
    top_3 = differences[:3]

    for diff, item, buy_order, sell_order in top_3:
        print(f"Item: {item['item_name']}")
        print(f"Highest buy order: {buy_order['platinum']} platinum by {buy_order['user']['ingame_name']}")
        print(f"Lowest sell order: {sell_order['platinum']} platinum by {sell_order['user']['ingame_name']}")
        print(f"Difference: {diff} platinum\n")


if __name__ == "__main__":
    print("Select the number of items to process:")
    print("1. All items")
    print("2. Specify the number of items")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        find_biggest_difference('all')
    elif choice == '2':
        num_items = input("Enter the number of items to process: ")
        find_biggest_difference(num_items)
    else:
        print("Invalid choice. Please run the program again and select a valid option.")
