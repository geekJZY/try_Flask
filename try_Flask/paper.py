from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('paper', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    classes = db.execute(
        'SELECT c.id, user_id, class_name'
        ' FROM class c'
        ' WHERE user_id=%s'
        ' ORDER BY c.id ASC',
        (g.user['id'],)
    ).fetchall()

    if request.method == 'POST':
        print(request.form['category'])
        if request.form['category'] == "NULL":
            papers = db.execute(
                'SELECT p.id, title, abstract, link, created, class_name'
                ' FROM paper p JOIN class c ON p.class_id = c.id'
                ' WHERE p.user_id=%s'
                ' ORDER BY created DESC',
                (g.user['id'],)
            ).fetchall()
        else:
            papers = db.execute(
                'SELECT p.id, title, abstract, link, created, class_name'
                ' FROM paper p JOIN class c ON p.class_id = c.id'
                ' WHERE p.user_id=%s AND c.id=%s'
                ' ORDER BY created DESC',
                (g.user['id'], request.form['category'])
            ).fetchall()
        search_item = request.form['search_title']
        return render_template('paper/index.html', papers=papers, search_item=search_item, categories=classes)

    papers = db.execute(
        'SELECT p.id, title, abstract, link, created, class_name'
        ' FROM paper p JOIN class c ON p.class_id = c.id'
        ' WHERE p.user_id=%s'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('paper/index.html', papers=papers, search_item='', categories=classes)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        link = request.form['link']
        class_id = request.form['category']
        error = None

        if not title or not link or not class_id:
            error = 'Title and Link and class_id is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO paper (title, abstract, link, user_id, class_id)'
                ' VALUES (%s, %s, %s, %s, %s)',
                (title, abstract, link, g.user['id'], class_id)
            )
            return redirect(url_for('paper.index'))

    db = get_db()
    classes = db.execute(
        'SELECT c.id, user_id, class_name'
        ' FROM class c'
        ' WHERE user_id=%s'
        ' ORDER BY c.id ASC',
        (g.user['id'],)
    ).fetchall()

    return render_template('paper/create.html', categories=classes)

def get_paper(id):
    paper = get_db().execute(
        'SELECT id, title, abstract, link, class_id, created, user_id'
        ' FROM paper p '
        ' WHERE p.id = %s AND p.user_id = %s',
        (id, g.user['id'])
    ).fetchone()

    if paper is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return paper

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    paper = get_paper(id)

    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        link = request.form['link']
        class_id = request.form['category']
        error = None

        if not title or not link or not class_id:
            error = 'Title and Link and class_id is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE paper SET title=%s, abstract=%s, link=%s, class_id=%s'
                ' WHERE id=%s',
                (title, abstract, link, class_id, id)
            )
            return redirect(url_for('paper.index'))

    db = get_db()
    classes = db.execute(
        'SELECT c.id, user_id, class_name'
        ' FROM class c'
        ' WHERE user_id=%s'
        ' ORDER BY c.id ASC',
        (g.user['id'],)
    ).fetchall()

    return render_template('paper/update.html', categories=classes, paper=paper)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_paper(id)
    db = get_db()
    db.execute('DELETE FROM paper WHERE id = %s', (id,))
    return redirect(url_for('paper.index'))