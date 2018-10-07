import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def collect_data_command():
    """collect data."""
    db = get_db()
    db.execute(
        'INSERT INTO user (username, password)'
        ' VALUES (?, ?)',
        ('123', '123')
    )
    db.commit()

    user = db.execute(
        'SELECT id FROM user'
    ).fetchone()

    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'GAN')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'image style transfer')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'reinforcement learning')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'object detection')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'denoising')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'deblurring')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'super resolution')
    )
    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (?, ?)',
        (user['id'], 'deraining')
    )


    classes = db.execute(
        'SELECT id FROM class WHERE user_id=?',
        (user['id'],)
    )
    classes_list = []
    for category in classes:
        classes_list += [category['id']]

    import urllib.request
    from random import randint

    fp = urllib.request.urlopen("http://openaccess.thecvf.com/CVPR2018.py")
    mybytes = fp.read()
    fp.close()

    fp = urllib.request.urlopen("http://openaccess.thecvf.com/ICCV2017.py")
    mybytes += fp.read()
    mystr = mybytes.decode("utf8").splitlines()
    fp.close()

    import re

    i = 0
    flag = True
    for line in mystr:
        i += 1
        if i > 40000:
            break
        if flag:
            paper_name = re.search(r"^<dt class=\"ptitle\"><br><a href=\".*\">(.*)</a></dt>$", line)
            if paper_name is not None:
                print(paper_name.group(1))
                flag = False
        else:
            paper_link = re.search(r'<a href="(.*)">pdf</a>', line)
            if paper_link is not None:
                print("http://openaccess.thecvf.com/" + paper_link.group(1))
                flag = True
                db.execute(
                    'INSERT INTO paper (title, abstract, link, user_id, class_id)'
                    ' VALUES (?, ?, ?, ?, ?)',
                    (paper_name.group(1), '', "http://openaccess.thecvf.com/" + paper_link.group(1), user['id'], classes_list[randint(0, len(classes_list)-1)])
                )
                db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    collect_data_command()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

