from flask import Flask, render_template, redirect, url_for, flash
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Logged in successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
