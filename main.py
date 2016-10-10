from flask import Flask, request, url_for, render_template, redirect, send_from_directory
import string
import pdb
import os

from fontanalysis.db.font import Font
from fontanalysis.db.label import Label
from fontanalysis.db.fontlabel import FontLabel
from fontanalysis.db.dbsettings import Session

app = Flask(__name__, static_folder='static')
app.config['depotDirectory'] = '../depot/imgdepot'


@app.route('/')
def empty_root():
    return redirect(url_for('home', id_number=1))

@app.route('/table')
def table():
    return render_template('table.html', **content)

@app.route('/<int:id_number>/', methods=['GET', 'POST'])
def home(id_number):
    """
    TODO: check if id_number is valid
    """

    if request.method == "POST":
        label = request.form['label']
        session = Session()
        row = session.query(FontLabel).filter_by(font_id=id_number).first()
        if row:
            row.label_id = label
        else:
            fontlabel = FontLabel(font_id=id_number, label_id=label)
            session.add(fontlabel)
        
        session.commit()

        return label

    else:
        def id_link_gen(id_number):
            if id_number is None:
                return None

            return '/{}/'.format(id_number)

        max_dirs = len(os.listdir(app.config['depotDirectory']))

        prev_id = None if id_number == 1 else id_number - 1
        next_id = None if id_number == max_dirs else id_number + 1

        prev_id_link = id_link_gen(prev_id)
        next_id_link = id_link_gen(next_id)
        first_id_link = id_link_gen(1)
        last_id_link = id_link_gen(max_dirs)

        fnames = ["{}.png".format(i) for i in string.letters]
        fnames = [os.path.join(str(id_number), i) for i in fnames]
        fnames = [url_for('imgdepot', fpath=i) for i in fnames]

        session = Session()
        font_info = session.query(Font).filter_by(id=id_number).first()

        row  = session.query(FontLabel, Label)\
            .filter(FontLabel.label_id==Label.id)\
            .filter(FontLabel.font_id==id_number).one_or_none()
        font_label = row[1].name if row else None
        label_id = row[1].id if row else None

        label_values = session.query(Label.id, Label.name).all()

        content = dict()
        content['fnames'] = fnames
        content['font_label'] = font_label
        content['font_name'] = font_info.name
        content['next_page'] = next_id_link
        content['prev_page'] = prev_id_link
        content['first_page'] = first_id_link
        content['last_page'] = last_id_link
        content['current_url'] = request.path
        content['label_values'] = label_values
        content['current_label_id'] = label_id

        return render_template('main.html', **content)
    
@app.route('/imgdepot/<path:fpath>')
def imgdepot(fpath):
    return send_from_directory(app.config['depotDirectory'], fpath)

if __name__ == "__main__":
    app.run(debug=True)

