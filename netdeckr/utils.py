

def format_text(text):
    uncapitalized = ["a", "an", "and", "at", "but", "by", "for", "in",
                     "nor", "of", "on", "or", "so", "the", "to", "up"]

    # set all words to lowercase
    text = text.lower()
    text = text.capitalize()

    words = text.split(" ")

    # capitalize ever other word that should not be left uncapitalized
    formatted = [w.capitalize() if w not in uncapitalized else w for w in words]

    return " ".join(formatted)


# Takes the database entries (which are dictionaries) and returns contents as a string
# Format: number owned followed by the name of the card line by line
def db_to_str(cards):
    card_string = ""

    for card in cards:
        # Avoid cards that have been removed
        if card['quantity'] > 0:
            card_string += str(card['quantity']) + " " + card['name'] + "\n"

    # Strip the last newline character before returning string
    return card_string.strip("\n")
