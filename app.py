from flask import Flask, render_template, flash, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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

PASSWORD = "BadanieUI2024"

class SiteForm(FlaskForm):
    name = StringField("Nazwa: ", validators=[DataRequired()])
    url = StringField("URL: ", validators=[DataRequired()])
    type = StringField("Typ: ", validators=[DataRequired()])
    picture = FileField("Interfejs: ")
    submit = SubmitField("DODAJ")

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(200), nullable=False)
    picture = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<Name %r>' % self.name

class QuestionForm(FlaskForm):
    type = StringField("Typ: ", validators=[DataRequired()])
    q1 = StringField("1 pytanie: ", validators=[DataRequired()])
    q2 = StringField("2 pytanie: ", validators=[DataRequired()])
    q3 = StringField("3 pytanie: ", validators=[DataRequired()])
    submit = SubmitField("DODAJ")

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
    submit = SubmitField("Dalej")

class Responder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(200), nullable=False)
    age = db.Column(db.String(200), nullable=False)
    residence = db.Column(db.String(200), nullable=False)
    education = db.Column(db.String(200), nullable=False)
    occupation = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<ID %r>' % self.id

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('responder.id'), nullable=False)
    star1 = db.Column(db.Integer, nullable=False)
    star2 = db.Column(db.Integer, nullable=False)
    star3 = db.Column(db.Integer, nullable=False)
    site = db.relationship('Site', back_populates='ratings')
    responder = db.relationship('Responder', back_populates='ratings')

Site.ratings = db.relationship('Rating', back_populates='site')
Responder.ratings = db.relationship('Rating', back_populates='responder')

Site.ratings = db.relationship('Rating', back_populates='site')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    home = "active"
    return render_template('index.html', home=home)

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    subquery = db.session.query(Question.type).distinct().subquery()
    our_sites = Site.query.filter(Site.type.in_(subquery)).all()

    if not our_sites:
        flash('Badanie jest obecnie niedostępne')
        return redirect(url_for('index'))

    # Initialize session index if not present
    if 'current_site_index' not in session:
        session['current_site_index'] = 0

    # Ensure responder_id is in session
    if 'responder_id' not in session:
        flash('Najpierw uzupełnij ankietę osobową')
        return redirect(url_for('particular'))

    current_site_index = session['current_site_index']

    # Check if the survey is completed
    if current_site_index >= len(our_sites):
        flash('Dziękujemy za udział!')
        return redirect(url_for('index'))

    current_site = our_sites[current_site_index]

    if request.method == 'POST':
        try:
            # Get ratings from the form
            star1 = int(request.form.get('star1'))
            star2 = int(request.form.get('star2'))
            star3 = int(request.form.get('star3'))

            # Create and save the rating
            rating = Rating(
                site_id=current_site.id,
                responder_id=session['responder_id'],
                star1=star1,
                star2=star2,
                star3=star3
            )
            db.session.add(rating)
            db.session.commit()

            # Update the current site index
            session['current_site_index'] += 1

            # Redirect to the next site or completion page if done
            if session['current_site_index'] >= len(our_sites):
                flash('Dziękujemy za wypełnienie ankiety!')
                return redirect(url_for('index'))

            # Reload current site after updating index
            current_site = our_sites[session['current_site_index']]
        except Exception as e:
            db.session.rollback()
            flash('Wystąpił błąd podczas zapisywania ocen. Spróbuj ponownie.')
            return redirect(url_for('survey'))

    # Fetch the relevant question
    question = Question.query.filter_by(type=current_site.type).first()

    # Calculate average ratings for the current site
    avg_star1 = db.session.query(func.avg(Rating.star1)).filter_by(site_id=current_site.id).scalar()
    avg_star2 = db.session.query(func.avg(Rating.star2)).filter_by(site_id=current_site.id).scalar()
    avg_star3 = db.session.query(func.avg(Rating.star3)).filter_by(site_id=current_site.id).scalar()

    return render_template('survey.html', current_site=current_site, question=question, avg_star1=avg_star1, avg_star2=avg_star2, avg_star3=avg_star3, current_site_index=current_site_index)


@app.route('/site/add', methods=['GET', 'POST'])
def add_site():
    if is_not_logged():
        return redirect(url_for('index'))

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

@app.route('/site/delete/<string:site_url>', methods=['POST'])
def delete_site(site_url):
    if is_not_logged():
        return redirect(url_for('index'))

    # Znajdź stronę na podstawie adresu URL
    site = Site.query.filter_by(url=site_url).first()

    if site is None:
        flash('Strona nie została znaleziona.')
        return redirect(url_for('add_site'))

    # Usuń powiązane oceny
    ratings = Rating.query.filter_by(site_id=site.id).all()
    for rating in ratings:
        db.session.delete(rating)

    # Usuń powiązane obrazy, jeśli istnieją
    if site.picture:
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], site.picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    # Usuń stronę z bazy danych
    db.session.delete(site)
    db.session.commit()

    flash('Strona oraz powiązane oceny zostały usunięte.')
    return redirect(url_for('add_site'))


@app.route('/question/add', methods=['GET', 'POST'])
def add_question():
    if is_not_logged():
        return redirect(url_for('index'))

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question.query.filter_by(type=form.type.data).first()
        if question is None:
            question = Question(type=form.type.data, q1=form.q1.data, q2=form.q2.data, q3=form.q3.data)
            db.session.add(question)
            db.session.commit()
            flash("Dodano kryteria!")
        else:
            flash("Kryteria do tego tyou już istnieją")

        return redirect(url_for('add_question'))

    our_questions = Question.query.order_by(Question.id)

    persons = Responder.query.order_by(Responder.id)

    return render_template("add_question.html", form=form, our_questions=our_questions, persons=persons)

@app.route('/question/delete/<string:question_type>', methods=['POST'])
def delete_question(question_type):
    if is_not_logged():
        return redirect(url_for('index'))

    # Znajdź pytanie na podstawie typu
    question = Question.query.filter_by(type=question_type).first()

    if question is None:
        flash('Pytanie o podanym typie nie zostało znalezione.')
        return redirect(url_for('add_question'))

    # Usuń pytanie z bazy danych
    db.session.delete(question)
    db.session.commit()

    flash('Pytanie zostało usunięte.')
    return redirect(url_for('add_question'))



@app.route('/particular', methods=['GET', 'POST'])
def particular():
    # Reset session index
    session['current_site_index'] = 0
    form = ResponderForm()

    if form.validate_on_submit():
        responder = Responder.query.filter_by(
            gender=form.gender.data,
            age=form.age.data,
            residence=form.residence.data,
            education=form.education.data,
            occupation=form.occupation.data
        ).first()

        if responder is None:
            # Create a new responder if not found
            new_responder = Responder(
                gender=form.gender.data,
                age=form.age.data,
                residence=form.residence.data,
                education=form.education.data,
                occupation=form.occupation.data
            )
            try:
                db.session.add(new_responder)
                db.session.commit()
                session['responder_id'] = new_responder.id  # Store responder ID in session
            except Exception as e:
                db.session.rollback()
                flash("Oops, something went wrong while saving your information. Please try again.", 'error')
        else:
            session['responder_id'] = responder.id  # Store responder ID in session
            # flash("This responder already exists.", 'info')

        return redirect(url_for('survey'))

    our_responders = Responder.query.order_by(Responder.id).all()
    return render_template("respondents_particulars.html", form=form, our_responders=our_responders)

@app.route('/for_researchers', methods=['GET', 'POST'])
def for_researchers():
    if 'logged' not in session:
        session['logged'] = False
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged'] = True
    logged = session['logged']
    for_researchers = "active"
    return render_template("for_researchers.html", logged=logged, for_researchers=for_researchers)

@app.route('/responses', methods=['GET', 'POST'])
def responses():
    if is_not_logged():
        return redirect(url_for('index'))

    ratings = Rating.query.all()
    responders = Responder.query.all()
    sites = Site.query.all()
    questions = Question.query.all()

    return render_template("responses.html", ratings=ratings, responders=responders, sites=sites, questions=questions)

@app.route('/about', methods=['GET', 'POST'])
def about():
    about = "active"
    return render_template("about.html", about=about)


def is_not_logged():
    if 'logged' not in session or session['logged']==False:
        flash('Nie masz dostępu do tej strony')

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s') % table
        session.execute(table.delete())
    session.commit()

if __name__ == "__main__":
    app.run(debug=True)
