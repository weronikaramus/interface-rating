from flask import Flask, render_template, session, request, redirect, url_for
import random
from Site import Site

app = Flask(__name__)
app.secret_key = 'your_secret_key'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    current_site = random.choice(sites)
    return render_template('survey.html', current_site=current_site)



site1 = Site("TechCrunch", "https://techcrunch.com", "News", "main")
site2 = Site("CNN", "https://www.cnn.com", "News", "main")
site3 = Site("GitHub", "https://github.com", "Development", "settings")
site4 = Site("Medium", "https://medium.com", "Blogging", "create post")

sites = [site1, site2, site3, site4]


if __name__ == "__main__":
    app.run()
