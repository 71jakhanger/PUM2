from flask import Flask, render_template, request, redirect, make_response, json
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = 'supersecretkey'
name1 = ""
def set_cookie(resp, name):
    resp.set_cookie('username', name, max_age=60*60*24*40)
def fix(users):
    l = len(users)
    for i in range(l):
        for j in range(1, l):
            if users[j]['number'] < users[j-1]['number']:
                users[j],users[j-1] = users[j-1],users[j]
def count_total():
    total = 0
    with open("names.json", 'r') as file:
        names = json.load(file)
    for name in names:
        total += name['number']
    return total


from datetime import datetime


def k():
    try:
        today = datetime.now()
    except Exception as e:
        return f"Ошибка при получении текущей даты: {e}"

    try:
        year = today.year
        end_of_september = datetime(year, 9, 30)

        if today > end_of_september:
            return "Сентябрь уже закончился. Пожалуйста, обновите данные."

        days_remaining = (end_of_september - today).days

        if days_remaining <= 0:
            return "Сентябрь уже закончился. Пожалуйста, обновите данные."

        pushups_remaining = 100000 - count_total()
        daily_pace = pushups_remaining / days_remaining

        return float(daily_pace / 3226)
    except Exception as e:
        return f"Ошибка при расчете коэффициента: {e}"


@app.route("/")
def index():
    username = request.cookies.get('username')
    global name1
    name1 = username
    with open("names.json", 'r') as file:
        users = json.load(file)
    case = "Oh"
    for user in users:
        if username == user['name'] and user['admin']==True:
            case = "admin"
            break
        elif username == user['name'] and user['admin']==False:
            case = "user"
            break
    if case == "admin":
        return redirect('/admin')
    elif case == "user":
        return redirect('/home')
    else:
        with open('templates/login.html', 'r') as f:
            return f.read()

@app.route("/login", methods=["POST"])
def login():
    form = request.form
    name = form['name']
    password = form['password']
    global name1
    name1 = name
    with open('names.json', 'r') as file:
        names = json.load(file)
    access = 0
    for user in names:
        if user['name'] == name and user['password'] == password:
            access = 1
            break
        elif user['name'] == name and user['password'] != password:
            access = 2
            break
    if access == 1:
        resp = make_response(redirect('/home'))
        set_cookie(resp, name)
        return resp
    elif access == 2:
        return redirect('/login')
    else:
        new_user = {
            "name": name,
            "password": password,
            "number": 0,
            "admin": False
        }
        names.append(new_user)
        with open('names.json', 'w') as file:
            json.dump(names, file, indent=4)
        resp = make_response(redirect('/home'))
        set_cookie(resp, name)
        return resp

@app.route('/home')
def home():
    mass = []
    global name1
    with open('names.json', 'r') as file:
        users = json.load(file)
    for user in users:
        if user['name'] == name1 and user['admin'] == True:
            return redirect('/admin')
    fix(users)
    users.reverse()
    for user in users:
        troll = f"{user['name']} : {user['number']}"
        mass.append(troll)
    return render_template('home.html', total=count_total(), names=mass, k = k())

@app.route("/add", methods=["POST"])
def add():
    form = request.form
    number = int(form['number'])
    username = request.cookies.get('username')
    if not username:
        return redirect('/')

    if number > 600:
        number = 600
    elif number < -600:
        number = -600

    with open('names.json', 'r') as file:
        users = json.load(file)

    for user in users:
        if user['name'] == username:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] += number
            break

    with open('names.json', 'w') as file:
        json.dump(users, file, indent=4)

    return redirect("/home")

@app.route("/AddAdmin", methods=["POST"])
def AddAdmin():
    form = request.form
    number = int(form['number'])
    username = request.cookies.get('username')
    if not username:
        return redirect('/')

    if number > 600:
        number = 600
    elif number < -600:
        number = -600

    with open('names.json', 'r') as file:
        users = json.load(file)

    for user in users:
        if user['name'] == username:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] += number
            break

    with open('names.json', 'w') as file:
        json.dump(users, file, indent=4)

    return redirect("/admin")


@app.route('/logout', methods=["POST"])
def logout():
    resp = make_response(redirect('/'))  # Создаем объект ответа с перенаправлением
    resp.set_cookie('username', '', expires=0)  # Устанавливаем пустое значение и истекающий срок для удаления cookie
    return resp  # Возвращаем ответ

@app.route('/admin')
def admin():
    mass = []
    with open('names.json', 'r') as file:
        users = json.load(file)
    fix(users)
    users.reverse()
    for user in users:
        troll = f"{user['name']} - {user['number']}"
        mass.append(troll)
    return render_template('admin.html', total=count_total(), names=mass)


@app.route('/delete_user', methods=["POST"])
def delete_user():
    name = request.form['name']
    with open('names.json', 'r') as file:
        users = json.load(file)

    users = [user for user in users if user['name'] != name]

    with open('names.json', 'w') as file:
        json.dump(users, file, indent=4)

    return redirect('/home')


@app.route('/update_number', methods=["POST"])
def update_number():
    name = request.form['name']
    number = int(request.form['number'])

    if number <0:
        number = 0

    with open('names.json', 'r') as file:
        users = json.load(file)

    for user in users:
        if user['name'] == name:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] = number
            break

    with open('names.json', 'w') as file:
        json.dump(users, file, indent=4)

    return redirect('/admin')

@app.route('/AboutUs')
def AboutUs():
    f = open('templates/AboutUs.html', 'r')
    return f.read()

if __name__ == '__main__':
    app.run(debug=True)