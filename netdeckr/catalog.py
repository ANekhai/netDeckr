import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from mtgsdk import Card

from netdeckr.db import get_db

bp = Blueprint('catalog', __name__)


@bp.route('/index')
def index():
    db = get_db()
    cards = db.execute(
        'SELECT * FROM card'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('blog/index.html', cards=cards)


@bp.route('/', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        card_name = request.form['name']
        quantity = request.form['quantity']
        db = get_db()
        db_card = db.execute(
            'SELECT name, quantity FROM card WHERE name = ?', (card_name,)
            ).fetchone()
        error = None

        if not card_name:
            error = 'Card name is required.'
        elif not quantity:
            error = 'Quantity to add required.'

        known_cards = Card.where(name=card_name).all()

        if not Card.where(name=card_name).all():
            error = 'Could not find card named {}' .format(card_name)


        # TODO: Check if card already in database and add to quantity already in the database

        if error is not None:
            flash(error)
        # Add quantity of cards to extant entry
        elif db_card is not None:
            prev_quantity = db_card['quantity']
            db.execute(
                'UPDATE card'
                ' SET quantity = ?'
                ' WHERE name = ?', (quantity+prev_quantity, card_name)
            )
            db.commit()
            return redirect(url_for('catalog.index'))
        # create a new entry in database for this card
        else:
            db = get_db()
            db.execute(
                'INSERT INTO card (card_name, quantity)'
                ' VALUES (?, ?)',
                (card_name, quantity)
            )
            db.commit()
            return redirect(url_for('catalog.index'))

    return render_template('catalog/add.html')
