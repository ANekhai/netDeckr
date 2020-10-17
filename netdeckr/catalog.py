import functools
from os import path

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, Response, send_from_directory, url_for
)
from werkzeug.exceptions import abort

from mtgsdk import Card

from netdeckr.db import get_db

from .utils import format_text, db_to_str

bp = Blueprint('catalog', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    cards = db.execute(
        'SELECT * FROM card'
        ' ORDER BY updated DESC'
    ).fetchall()
    return render_template('catalog/index.html', cards=cards)


@bp.route('/add', methods=('POST',))
def add():
    # format the card's name as a title
    card_name = format_text(request.form['name'])

    quantity = int(request.form['quantity'])
    db = get_db()
    db_card = db.execute(
        'SELECT name, quantity FROM card WHERE name = ?', (card_name,)
        ).fetchone()
    image_url = None
    error = None

    if not card_name:
        error = 'Card name is required.'
    elif not quantity:
        error = 'Quantity to add required.'
    elif quantity < 1:
        error = 'Can only add a positive number of cards.'
    # Check if card is contained in the mtg card database using mtgsdk
    elif not db_card and not Card.where(name='"{}"'.format(card_name)).all():
        error = 'Could not find card named {}' .format(card_name)

    if not db_card and not error:
        # Get URL for image of card to store in database
        # Must collect all image_urls, as not every card entry fetched will have an image_url
        urls = [c.image_url for c in Card.where(name='"{}"' .format(card_name)).all()
                if c.image_url]
        image_url = urls[-1]

    if error is not None:
        flash(error)
    # Add quantity of cards to extant entry
    elif db_card is not None:
        prev_quantity = int(db_card['quantity'])
        db.execute(
            'UPDATE card'
            ' SET quantity = ?, updated = CURRENT_TIMESTAMP'
            ' WHERE name = ?', (quantity+prev_quantity, card_name)
        )
        db.commit()
    # create a new entry in database for this card
    else:
        db = get_db()
        db.execute(
            'INSERT INTO card (name, quantity, image)'
            ' VALUES (?, ?, ?)',
            (card_name, quantity, image_url)
        )
        db.commit()

    return redirect(url_for('catalog.index'))


# Helper function to get a card based on it's ID in the database
def get_card(id):
    card = get_db().execute(
        'SELECT * FROM card'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if card is None:
        abort(404, "Card id {0} doesn't exist".format(id))

    return card


@bp.route('/<int:id>/info', methods=('GET',))
def info(id):
    card = get_card(id)
    return render_template('catalog/info.html', card=card)


@bp.route('/<int:id>/remove', methods=('POST',))
def remove(id):
    card = get_card(id)
    to_remove = int(request.form['quantity'])
    error = None

    if not to_remove:
        error = "Quantity of cards to remove is required."
    elif to_remove < 1:
        error = "Can only remove a positive number of cards."

    if error:
        flash(error)
    else:
        remaining = max(card['quantity'] - to_remove, 0)

        db = get_db()
        db.execute('UPDATE card'
                   ' SET quantity = ?, updated = CURRENT_TIMESTAMP'
                   ' WHERE id = ?', (remaining, id))
        db.commit()

    return redirect(url_for('catalog.index'))


@bp.route('/search', methods=('POST',))
def search():
    query_name = format_text(request.form['query'])
    db = get_db()
    error = None

    card = db.execute(
        'SELECT * FROM card'
        ' WHERE name = ?', (query_name,)
    ).fetchone()

    if not card or int(card['quantity']) == 0:
        error = "{} not owned." .format(query_name)

    if error:
        flash(error)
    else:
        return redirect(url_for('catalog.info', id=card['id']))

    return redirect(url_for('catalog.index'))


@bp.route('/download', methods=('GET',))
def download():
    db = get_db()
    cards = db.execute(
        'SELECT name, quantity FROM card'
        ' ORDER BY name'
    ).fetchall()
    cards_str = db_to_str(cards)

    return Response(
        cards_str,
        mimetype='text/plain'
    )


# TODO: add a function to allow for mass uploading of a file into the database
