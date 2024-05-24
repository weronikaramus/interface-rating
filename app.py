from flask import Flask, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study.db'

db = SQLAlchemy(app)



class SiteForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    url = StringField("URL: ", validators=[DataRequired()])
    category = StringField("Category: ", validators=[DataRequired()])
    type = StringField("Type: ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    our_sites = Site.query.all()
    session['current_site'] = session.get('current_site', 0) + 1
    current_site = our_sites[session['current_site']]
    # current_site = random.choice(Site.query.all())
    return render_template('survey.html', current_site=current_site)

@app.route('/site/add', methods=['GET', 'POST'])
def add_site():
    form = SiteForm()
    if form.validate_on_submit():
        site = Site.query.filter_by(url=form.url.data).first()
        if site is None:
            site = Site(name=form.name.data, url=form.url.data, category=form.category.data, type=form.type.data)
            db.session.add(site)
            db.session.commit()
            flash("Site added to survey!")
        else:
            flash("Site already exists!")

        return redirect(url_for('add_site'))

    our_sites = Site.query.order_by(Site.id)

    return render_template("add_site.html", form=form, our_sites=our_sites)

# Sample data
@app.before_first_request
def populate_db():
    site1 = Site(name="TechCrunch", url="https://techcrunch.com", category="News", type="main")
    site2 = Site(name="CNN", url="https://www.cnn.com", category="News", type="main")

    db.session.add_all([site1, site2])
    db.session.commit()


if __name__ == "__main__":
    app.run()
