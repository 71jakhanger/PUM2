from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

from appwrite.query import Query

client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')
client.set_project('66d480b50014b63a691e')
client.set_key('e85c438bf4c78a0fbe624610a14466080516ee6326e048a6176b0c4813e66d0e13124e68f24b5244d63eb9a740744f34b38334eca877381cabf5e1c217211862a737e494071920f4f7b1c1c92323c0f5894140d0a5d59a4a7d32c9a6dfec83b0c3a23062a9cbb69386255ec3d3ef12f48860a06c1e6f074b6604058013e20383')


databases = Databases(client)

databaseID='66d484b90018dc2e460c'

collectionID='66d484c9003082e52a03'


from flask import Flask, render_template, request, redirect, make_response
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

    accounts = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )
    for account in accounts['documents']:
        total += account['number']
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
    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )
    case = "Oh"
    for user in users['documents']:
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
    names = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )
    access = 0
    for user in names['documents']:
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
        databases.create_document(
                database_id = databaseID,
                collection_id = collectionID,
                document_id = ID.unique(),
                data = new_user
            )
        resp = make_response(redirect('/home'))
        set_cookie(resp, name)
        return resp

@app.route('/home')
def home():
    mass = []
    global name1
    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )
    for user in users['documents']:
        if user['name'] == name1 and user['admin'] == True:
            return redirect('/admin')
    fix(users['documents'])
    users['documents'].reverse()
    for user in users['documents']:
        troll = f"{user['name']} : {user['number']}"
        mass.append(troll)
    return render_template('home.html', total=count_total(), names=mass, k = k())

@app.route("/add", methods=["POST"])
def add():
    form = request.form
    number = form['number']
    if number == "":
        number = 0
    number = int(number)
    username = request.cookies.get('username')
    if not username:
        return redirect('/')

    if number > 600:
        number = 600
    elif number < -600:
        number = -600

    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )

    for user in users['documents']:
        if user['name'] == username:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] += number
            print(user['$id'])
            print(user)
            data={'name': user['name'], 'password':user['password'],'number':user['number'],'admin':user['admin']}
            databases.update_document(
                database_id = databaseID,
                collection_id = collectionID,
                document_id = user['$id'],
                data = data,
            )

            break



    return redirect("/home")

@app.route("/AddAdmin", methods=["POST"])
def AddAdmin():
    form = request.form
    number = form['number']
    if number =="":
        number = 0
    number = int(number)
    username = request.cookies.get('username')
    if not username:
        return redirect('/')

    if number > 1200:
        number = 1200
    elif number < -1200:
        number = -1200

    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )

    for user in users['documents']:
        if user['name'] == username:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] += number
            data={'name': user['name'], 'password':user['password'],'number':user['number'],'admin':user['admin']}
            databases.update_document(
                database_id = databaseID,
                collection_id = collectionID,
                document_id = user['$id'],
                data = data
            )
            break
    return redirect("/admin")


@app.route('/logout', methods=["POST"])
def logout():
    resp = make_response(redirect('/'))  # Создаем объект ответа с перенаправлением
    resp.set_cookie('username', '', expires=0)  # Устанавливаем пустое значение и истекающий срок для удаления cookie
    return resp  # Возвращаем ответ

@app.route('/admin')
def admin():
    mass = []
    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )
    fix(users['documents'])
    users['documents'].reverse()
    for user in users['documents']:
        troll = f"{user['name']} - {user['number']}"
        mass.append(troll)
    return render_template('admin.html', total=count_total(), names=mass,  k = k())


@app.route('/delete_user', methods=["POST"])
def delete_user():
    name = request.form['name']
    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )

    name_id=databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID,
        queries = Query.equal('name',name)
    )
    print(name_id['documents'])
    name_id=name_id['documents'][0]['$id']

    databases.delete_document(
        database_id = databaseID,
        collection_id = collectionID,
        document_id = name_id
    )

    return redirect('/home')


@app.route('/update_number', methods=["POST"])
def update_number():
    name = request.form['name']
    number = int(request.form['number'])

    if number <0:
        number = 0

    users = databases.list_documents(
        database_id = databaseID,
        collection_id = collectionID
    )

    for user in users['documents']:
        if user['name'] == name:
            if user['number'] < 0:
                user['number'] = 0
            user['number'] = number
            data = {'name': user['name'], 'password': user['password'], 'number': user['number'],
                    'admin': user['admin']}
            databases.update_document(
        database_id = databaseID,
        collection_id = collectionID,
        document_id = user['$id'],
        data = data
    )
            break

    return redirect('/admin')

@app.route('/AboutUs')
def AboutUs():
    f = open('templates/AboutUs.html', 'r')
    return f.read()

if __name__ == '__main__':
    app.run(debug=True)