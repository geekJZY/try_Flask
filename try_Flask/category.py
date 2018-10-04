from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('category', __name__, url_prefix='/category')


@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    classes = db.execute(
        'SELECT c.id, user_id, class_name'
        ' FROM class c'
        ' WHERE user_id=?'
        ' ORDER BY c.id ASC',
        (g.user['id'],)
    ).fetchall()
    if request.method == 'POST':
        class_name = request.form['class_name']
        error = None

        if not class_name or class_name=='':
            error = 'Category name is required.'
        for category in classes:
            if category['class_name']==class_name:
                error = 'Category name exist'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO class (user_id, class_name)'
                ' VALUES ( ?, ?)',
                (g.user['id'], class_name)
            )
            db.commit()

            return redirect(url_for('category.index'))

    return render_template('category/index.html', categories=classes)

def get_class(id):
    category = get_db().execute(
        'SELECT id, user_id, class_name'
        ' FROM class p '
        ' WHERE p.id = ? AND p.user_id = ?',
        (id, g.user['id'])
    ).fetchone()

    if category is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return category


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_class(id)
    db = get_db()
    db.execute(
        'DELETE FROM paper '
        ' WHERE class_id=?',
        (id,)
    )
    db.execute('DELETE FROM class WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('category.index'))