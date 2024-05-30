from flask import Flask, render_template, flash, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
import uuid
from flask_wtf.file import FileField

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study.db'
app.config['UPLOAD_FOLDER'] = 'static/img'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class SiteForm(FlaskForm):
    name = StringField("Nazwa: ", validators=[DataRequired()])
    url = StringField("URL: ", validators=[DataRequired()])
    category = StringField("Kategoria: ", validators=[DataRequired()])
    type = StringField("Typ: ", validators=[DataRequired()])
    picture = FileField("Interfejs: ")
    submit = SubmitField("DODAJ")

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    picture = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<Name %r>' % self.name

class QuestionForm(FlaskForm):
    type = StringField("Type: ", validators=[DataRequired()])
    q1 = StringField("1 question: ", validators=[DataRequired()])
    q2 = StringField("2 question: ", validators=[DataRequired()])
    q3 = StringField("3 question: ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200), nullable=False, unique=True)
    q1 = db.Column(db.String(200), nullable=False)
    q2 = db.Column(db.String(200), nullable=False)
    q3 = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.type

class ResponderForm(FlaskForm):
    gender = RadioField(u'Płeć:', choices=[('female', 'Kobieta'), ('male','Mężczyzna'), ('nonbinary', 'Osoba niebinarna'), ('other', 'Inna/Wolę nie podawać')], validators=[DataRequired()])
    age = RadioField(u"Wiek:", choices=[("under 18", "poniej 18"), ("18-26","18-26"), ("27-35", "27-35"), ("over 36", "powyżej 36")], validators=[DataRequired()])
    residence = RadioField(u"Miejsce zamieszkania:", choices=[("village", "wieś"), ("under 50k","miasto do 50 tys."), ("50k - 150k", "miasto od 50 tys. do 150 tys."), ("150k - 500k", "miasto od 150 tys. do 500 tys."), ("over 500k", "miasto powyżej 500 tys.")], validators=[DataRequired()])
    education = RadioField(u"Wykształcenie: ", choices=[("primary", "podstawowe"), ("secondary", "średnie"), ("proffesional", "zawodowe"), ("higher", "wyższe")], validators=[DataRequired()])
    occupation = StringField("Zawód: ")
    submit = SubmitField("ZAPISZ")

class Responder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(200), nullable=False)
    age = db.Column(db.String(200), nullable=False)
    residence = db.Column(db.String(200), nullable=False)
    education = db.Column(db.String(200), nullable=False)
    occupation = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<ID %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    our_sites = Site.query.all()

    if 'current_site_index' not in session:
        session['current_site_index'] = 0

    current_site_index = session['current_site_index']
    if current_site_index >= len(our_sites):
        return redirect(url_for('particular'))  # Redirect if the index is out of range

    current_site = our_sites[current_site_index]
    question = Question.query.filter_by(type=current_site.type).first()

    # Increment the index for the next visit
    session['current_site_index'] += 1

    return render_template('survey.html', current_site=current_site, question=question)

@app.route('/site/add', methods=['GET', 'POST'])
def add_site():
    form = SiteForm()
    if form.validate_on_submit():
        site = Site.query.filter_by(url=form.url.data).first()
        if site is None:
            pic_filename = None
            if form.picture.data:
                file = form.picture.data
                pic_filename = secure_filename(file.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                pic_filename = pic_name

            site = Site(
                name=form.name.data,
                url=form.url.data,
                category=form.category.data,
                type=form.type.data,
                picture=pic_filename
            )
            db.session.add(site)
            db.session.commit()
            flash("Site added to survey!")
        else:
            flash("Site already exists!")
        return redirect(url_for('add_site'))

    our_sites = Site.query.order_by(Site.id)
    return render_template("add_site.html", form=form, our_sites=our_sites)

@app.route('/question/add', methods=['GET', 'POST'])
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question.query.filter_by(type=form.type.data).first()
        if question is None:
            question = Question(type=form.type.data, q1=form.q1.data, q2=form.q2.data, q3=form.q3.data)
            db.session.add(question)
            db.session.commit()
            flash("Questions added to survey!")
        else:
            flash("Questions already exists!")

        return redirect(url_for('add_question'))

    our_questions = Question.query.order_by(Question.id)
    return render_template("add_question.html", form=form, our_questions=our_questions)

@app.route('/particular', methods=['GET', 'POST'])
def particular():
    session['current_site_index'] = 0
    form = ResponderForm()
    if form.validate_on_submit():
        responder = Responder.query
        if responder is None:
            responder = Responder(gender=form.gender.data, age=form.age.data, residence=form.residence.data, education=form.education.data, occupation=form.occupation.data)
            db.session.add(responder)
            db.session.commit()
            flash("Thank you for your time!")
        else:
            flash("Oops, something went wrong!")

        return redirect(url_for('particular'))

    our_responders = Responder.query.order_by(Responder.id)
    return render_template("respondents_particulars.html", form=form, our_responders=our_responders)

@app.route('/for_researchers', methods=['GET', 'POST'])
def for_researchers():
    return render_template("for_researchers.html")

if __name__ == "__main__":
    app.run(debug=True)
