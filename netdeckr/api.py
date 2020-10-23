from os.path import join
from time import sleep  # used to wait 50ms to 100ms between scryfall requests
from html import escape
import requests

# This module uses the Scryfall API to look up information about magic cards
card_api = "https://api.scryfall.com/cards"


# Todo: Replace this with vformat and Formatter python built ins
def format_request(url, name, exact=True):
    command = "search?q="
    if exact:
        command += '!'
    command += "\"{}\"" .format(escape(name))

    # order by price
    command += "&order=usd"

    return join(url, command)


def is_card(name, exact=True):
    request = format_request(card_api, name, exact)
    response = requests.get(request)
    # Code 200 means result has been returned
    return response.status_code == 200


def get_card(name):
    card = None
    request = format_request(card_api, name)
    response = requests.get(request)

    if response.status_code == 200:
        card = response.json()['data']
        # cards are wrapped in a list so we unwrap it while returning
        return card[0]

    return card


def get_colors(api_card):
    colors = None
    if 'colors' in api_card:
        colors = api_card['colors']
    else:
        colors = api_card['color_identity']
    sorted(colors)

    if colors:
        colors = "".join(colors)
    # Artifacts are colorless but will use special colors
    elif "Artifact" in api_card['type_line']:
        colors = "artifact"
    # Lands are the colors of the mana they produce
    elif "Land" in api_card['type_line']:
        colors = "".join(api_card['produced_mana'])
    else:
        colors = "none"

    return colors


def extract_data(api_card):
    data = {}

    # extract image or images for the card
    if "image_uris" in api_card:
        data['front'] = api_card['image_uris']['large']
    else:
        data['front'] = api_card['card_faces'][0]['image_uris']['large']
        data['back'] = api_card['card_faces'][1]['image_uris']['large']

    # extract price information
    if api_card['prices']['usd']:
        data['price'] = api_card['prices']['usd']
    else:
        data['price'] = api_card['prices']['usd_foil']

    data['color'] = get_colors(api_card)

    return data


if __name__ == "__main__":
    card_name = "Bala Ged Recovery"

    card = get_card(card_name)
    print(extract_data(card))

