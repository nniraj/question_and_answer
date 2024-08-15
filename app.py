from flask import Flask, g, render_template, request, session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_res = None
    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cur = db.execute('select id, name, password, admin, expert  from users where name=?', [user])
        user_res = user_cur.fetchone()
    return user_res

@app.route('/')
def index():
    user = get_current_user()
    db = get_db()

    questions_cur = db.execute('select questions.id, questions.question_text, askers.name as asker_name, experts.name as expert_name from questions join users as askers on askers.id=questions.asked_by_id join users as experts on experts.id=questions.expert_id where questions.answer_text is not null')
    questions = questions_cur.fetchall()
    return render_template('home.html', user=user, questions=questions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if request.method=="POST":
        db = get_db()
        name = request.form['name']

        existing_usr_cur = db.execute('select id from users where name=?', [name])
        existing_usr = existing_usr_cur.fetchone()

        if existing_usr:
            return render_template('register.html', user=user, error='User already exist.')
        
        hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        db.execute('insert into users (name, password, expert, admin) values (?,?,?,?)', [name, hashed_password, '0', '0'])
        db.commit()
        session['user'] = name
        return redirect(url_for('index'))
    return render_template('register.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if request.method=="POST":
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        user_cur = db.execute('select id, name, password from users where name=?', [name])
        user_res = user_cur.fetchone()

        if user_res and check_password_hash(user_res['password'], password):
            session['user'] = user_res['name']
            return redirect(url_for('index'))
        else:
            return "<h1>Please check username and password again</h1>"
    return render_template('login.html', user=user)

@app.route('/question/<question_id>')
def question(question_id):
    user = get_current_user()
    db = get_db()
    question_cur = db.execute('select  questions.question_text, questions.answer_text, askers.name as asker_name, experts.name as expert_name from questions join users as askers on askers.id=questions.asked_by_id join users as experts on experts.id=questions.expert_id where questions.id=?', [question_id])
    question = question_cur.fetchone()
    return render_template('question.html', user=user, question=question)

@app.route('/answer/<question_id>', methods=['POST', 'GET'])
def answer(question_id):
    db = get_db()
    user = get_current_user()
    if request.method=='POST':
        db.execute('update questions set answer_text=? where id=?', [request.form['answer'], question_id])
        db.commit()
        return redirect(url_for('index'))
    else:
        answer_cur = db.execute('SELECT id, QUESTION_TEXT FROM QUESTIONS WHERE ID=?', [question_id])
        answer = answer_cur.fetchone()
        return render_template('answer.html', user=user, answer=answer)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    db = get_db()
    if request.method == 'POST':
        question = request.form["question"]
        expert_id = request.form["expert"]
        db.execute('insert into questions (question_text, asked_by_id, expert_id) values (?,?,?)', [question, user['id'], expert_id])
        db.commit()
        return redirect(url_for('index'))
    
    exp_cur = db.execute('select id, name from users where expert=1')
    exp_results = exp_cur.fetchall()
    return render_template('ask.html', user=user, experts=exp_results)

@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    questions_cur = db. execute('select questions.id, questions.question_text, users.name from questions join users on users.id=questions.asked_by_id where questions.answer_text is null and questions.expert_id=?', [user['id']])
    questions = questions_cur.fetchall()
    return render_template('unanswered.html', user=user, questions=questions)

@app.route('/users')
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    users_cur = db.execute('select id, name, expert, admin from users')
    users_res = users_cur.fetchall()
    return render_template('users.html', user=user, users=users_res)


@app.route('/promote/<user_id>')
def promote(user_id):
    db = get_db()
    db.execute('update users set expert=1 where id=?', [user_id])
    db.commit()
    return redirect(url_for('users'))

@app.route('/logout')
def logout():
    user = get_current_user()
    session.pop('user')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)