import requests
import time

# List of the 30 most expensive items (replace with actual item URL names)
most_expensive_items = [
    "primed_chamber", "artax_riven_mod", "phased_ankyros_skin", "phased_tigris_skin",
    "rubedo_plated_viper_skin", "primed_fury", "primed_continuity", "primed_flow",
    "primed_point_blank", "primed_target_cracker", "primed_pistol_gambit", "primed_ravage",
    "primed_heavy_trauma", "primed_pressure_point", "primed_bane_of_corpus", "primed_bane_of_grineer",
    "primed_bane_of_infested", "primed_bane_of_corrupted", "primed_charged_shell", "primed_cryo_rounds",
    "primed_fast_hands", "primed_pistol_ammo_mutation", "primed_rifle_ammo_mutation", "primed_shotgun_ammo_mutation",
    "primed_sniper_ammo_mutation", "primed_tactical_pump", "primed_vigor", "primed_shred",
    "primed_sure_footed", "primed_pack_leader"
]


def get_orders(item_url_name):
    url = f"https://api.warframe.market/v1/items/{item_url_name}/orders"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch orders for {item_url_name}. HTTP Status code: {response.status_code}")
        return []

    data = response.json()
    orders = data.get('payload', {}).get('orders', [])
    return orders


def find_biggest_difference():
    differences = []

    for item_url_name in most_expensive_items:
        orders = get_orders(item_url_name)

        buy_orders = [order for order in orders if order['order_type'] == 'buy' and order['user']['status'] == 'ingame']
        sell_orders = [order for order in orders if
                       order['order_type'] == 'sell' and order['user']['status'] == 'ingame']

        if not buy_orders or not sell_orders:
            continue

        highest_buy_order = max(buy_orders, key=lambda x: x['platinum'])
        lowest_sell_order = min(sell_orders, key=lambda x: x['platinum'])

        difference = highest_buy_order['platinum'] - lowest_sell_order['platinum']

        differences.append((difference, item_url_name, highest_buy_order, lowest_sell_order))

        # Introduce a delay between requests
        time.sleep(1)

    # Sort by difference and get the top 3
    differences.sort(reverse=True, key=lambda x: x[0])
    top_3 = differences[:3]

    for diff, item_url_name, buy_order, sell_order in top_3:
        print(f"Item: {item_url_name}")
        print(f"Highest buy order: {buy_order['platinum']} platinum by {buy_order['user']['ingame_name']}")
        print(f"Lowest sell order: {sell_order['platinum']} platinum by {sell_order['user']['ingame_name']}")
        print(f"Difference: {diff} platinum\n")


if __name__ == "__main__":
    find_biggest_difference()
