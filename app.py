import sys

from flask import render_template, request, jsonify, Flask
from sqlalchemy import text

from models import *

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1337@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/database/selectAll', methods=['GET', 'POST'])
def database_select_all():
    if request.method == 'POST':
        user_table_choice = request.form.get('table_choice').capitalize()
        if user_table_choice:
            selected_table = getattr(sys.modules[__name__], user_table_choice)
            data = selected_table.query.all()
            # i need to convert data to json for request
            data = [item.as_dict() for item in data]
            return render_template('selectAll.html', data=jsonify(data).json)

    return render_template('SelectAllNone.html')


@app.route('/database/add_data_form')
def add_data_form():
    return render_template('InsertForm.html')


@app.route('/database/delete')
def delete_form():
    return render_template('DeleteForm.html')


@app.route('/database/update')
def update_data_form():
    return render_template('UpdateForm.html')


@app.route('/database/insert', methods=['GET', 'POST'])
def add_data():
    table_name = request.form['table_name']
    data = request.form['data']

    # Предотвращение SQL-инъекций
    if ';' in data or 'DROP' in data.upper():
        return 'Invalid data', 400

    if table_name not in available_tables:
        return 'Invalid table name', 400

    try:
        # Формирование и выполнение SQL-запроса
        query = text(f"INSERT INTO {table_name} VALUES ({data});")
        db.session.execute(query)
        db.session.commit()

        return 'Data added successfully!'
    except Exception as e:
        # Обработка ошибок
        return f'Error: {str(e)}', 500


@app.route('/delete_data', methods=['GET', 'POST'])
def delete_data():
    table_name = request.form['table_name']
    condition = request.form['condition']

    if table_name not in available_tables:
        return 'Invalid table name', 400

    if ';' in condition or 'DROP' in condition.upper():
        return 'Invalid condition', 400

    try:
        # Формирование и выполнение SQL-запроса
        query = text(f"DELETE FROM {table_name} WHERE {condition};")
        db.session.execute(query)
        db.session.commit()

        return 'Data deleted successfully!'
    except Exception as e:
        # Обработка ошибок
        return f'Error: {str(e)}', 500


@app.route('/update_data', methods=['POST'])
def update_data():
    table_name = request.form['table_name']
    condition_column = request.form['condition_column']
    condition_value = request.form['condition_value']
    update_column = request.form['update_column']
    update_value = request.form['update_value']

    # Предотвращение SQL-инъекций
    if (';' in condition_value or ';' in update_value or
            'DROP' in condition_value.upper() or 'DROP' in update_value.upper()):
        return 'Invalid data', 400

    try:
        # Явное указание SQL-выражения как текста
        query = text(f"UPDATE {table_name} SET {update_column} = :update_value "
                     f"WHERE {condition_column} = :condition_value")
        db.session.execute(query, {'update_value': update_value, 'condition_value': condition_value})
        db.session.commit()

        return 'Data updated successfully!'
    except Exception as e:
        # Обработка ошибок
        return f'Error: {str(e)}', 500


if __name__ == "__main__":
    app.run(debug=True)
