import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine

from werkzeug.security import check_password_hash, generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = create_engine(current_app.config['DATABASE'])

    return g.db


# def close_db(e=None):
#     db = g.pop('db', None)
#     #
#     # if db is not None:
#     #     db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8').replace('\n', ''))


def collect_data_command():
    """collect data."""
    db = get_db()
    db.execute(
        'INSERT INTO "user"(username, password) VALUES (%s, %s)',
        '123', generate_password_hash('123')
    )

    user = db.execute(
        'SELECT id FROM "user"'
    ).fetchone()
    print(user)

    db.execute(
        'INSERT INTO class (user_id, class_name)'
        ' VALUES (%s, %s)',
        (user['id'], 'GAN'),
        (user['id'], 'image style transfer'),
        (user['id'], 'reinforcement learning'),
        (user['id'], 'object detection'),
        (user['id'], 'denoising'),
        (user['id'], 'deblurring'),
        (user['id'], 'super resolution'),
        (user['id'], 'deraining')
    )

    classes = db.execute(
        'SELECT id FROM class WHERE user_id= %s',
        (user['id'],)
    ).fetchall()
    print(classes)
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
                    ' VALUES (%s, %s, %s, %s, %s)',
                    (paper_name.group(1), '', "http://openaccess.thecvf.com/" + paper_link.group(1), user['id'],
                     classes_list[randint(0, len(classes_list)-1)])
                )


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    collect_data_command()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)

