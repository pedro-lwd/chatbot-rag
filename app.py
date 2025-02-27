from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os 
from wtforms.validators import InputRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'saudadesdaminhaex123'
app.config['PASTA_UPLOAD'] = 'static'

class UploadFormArquivos(FlaskForm):
    arquivo = FileField("Arquivo", validators=[InputRequired()])
    submit = SubmitField("Fazer upload do arquivo")
    
@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    form = UploadFormArquivos()
    if form.validate_on_submit():
        arquivo = form.arquivo.data 
        arquivo.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['PASTA_UPLOAD'], secure_filename(arquivo.filename)))
        return "Arquivo foi salvo"
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)