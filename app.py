import sys

from flask import render_template, request, jsonify, Flask
from sqlalchemy import text

from models import *

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1337@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/show/<table_choice>', methods=['GET', 'POST'])
def show_table(table_choice):
    user_table_choice = table_choice.capitalize()
    if user_table_choice:
        selected_table = getattr(sys.modules[__name__], user_table_choice)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        item_count = selected_table.query.count()

        paginated_data = selected_table.query.paginate(page=page, per_page=per_page)
        data = paginated_data.items
        data_list = [item.as_dict() for item in data]

        return render_template('selectAll.html', data=data_list, table_name=user_table_choice,
                               pagination=paginated_data, item_count = item_count)


@app.route('/show/diseases', methods=['GET', 'POST'])
def show_filter():
    value = request.form.get('filter')
    selected_table = Diseases
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if value:
        old_filter = value
        paginated_data = selected_table.query.filter(selected_table.name.like(f'%{value}%')).paginate(page=page, per_page=per_page)
    else:
        old_filter = ''
        paginated_data = selected_table.query.paginate(page=page, per_page=per_page)
    data = paginated_data.items
    data_list = [item.as_dict() for item in data]

    item_count = selected_table.query.count()

    return render_template('selectFilterDiseases.html', data=data_list, table_name='diseases',
                           pagination=paginated_data, old_filter=old_filter, item_count = item_count)


@app.route('/show/<table_choice>/edit/<value>', methods=['GET', 'POST'])
def show_edit_value(table_choice, value):
    match table_choice:
        case 'symptoms':
            return render_template('EditFormSymptoms.html', table_name=table_choice, symptom_name=value)
        case 'drugs':
            expire_date = db.session.query(Drugs.expiredate).filter_by(name=value).first()
            expire_date = expire_date[0].strftime("%Y-%m-%d")
            return render_template('EditFormDrugs.html', table_name=table_choice, disease_name=value,
                                   expire_date=expire_date)
        case 'diseases':
            return render_template('EditFormDiseases.html', table_name=table_choice, disease_name=value)
        case 'diseasesymptoms':
            old_symptom_id = db.session.query(Diseasesymptoms.symptomid).filter_by(connectionid=value).first()[0]
            old_disease_id = db.session.query(Diseasesymptoms.diseaseid).filter_by(connectionid=value).first()[0]
            return render_template('EditFormDiseasesSymptoms.html', table_name=table_choice,
                                   old_symptom_id=old_symptom_id, old_disease_id=old_disease_id, connection_id=value)
        case 'drugdiseases':
            old_drug_id = db.session.query(Drugdiseases.drugid).filter_by(connectionid=value).first()[0]
            old_disease_id = db.session.query(Drugdiseases.diseaseid).filter_by(connectionid=value).first()[0]
            return render_template('EditFormDrugsDiseases.html', table_name=table_choice, old_drug_id=old_drug_id,
                                   old_disease_id=old_disease_id, connection_id=value)
        case 'homemedicine':
            old_quantity = db.session.query(Homemedicine.quantity).filter_by(medicineid=value).first()[0]
            old_drug_id = db.session.query(Homemedicine.drugid).filter_by(medicineid=value).first()[0]
            return render_template('EditFormHomeMedicine.html', table_name=table_choice, old_quantity=old_quantity,
                                   old_drug_id=old_drug_id, medicine_id=value)


@app.route('/edit_value', methods=['GET', 'POST'])
def edit_value():
    table_choice = request.form['table_name']
    user_table_choice = table_choice.capitalize()
    # selected_table = getattr(sys.modules[__name__], user_table_choice)
    match table_choice:
        case 'symptoms':
            old_name = request.form['old_name']
            new_name = request.form['new_name']
            try:
                symptom = db.session.query(Symptoms).filter(Symptoms.name == old_name).first()
                if symptom:
                    symptom.name = new_name
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленный успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'drugs':
            old_name = request.form['old_name']
            new_name = request.form['new_name']
            new_expire_date = request.form['new_expire_date']
            try:
                drug = db.session.query(Drugs).filter(Drugs.name == old_name).first()
                if drug:
                    drug.name = new_name
                    drug.expiredate = new_expire_date
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленны успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'diseases':
            old_name = request.form['old_name']
            new_name = request.form['new_name']
            try:
                disease = db.session.query(Diseases).filter(Diseases.name == old_name).first()
                if disease:
                    disease.name = new_name
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленны успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'diseasesymptoms':
            new_symptom_id = request.form['new_symptom_id']
            new_disease_id = request.form['new_disease_id']
            connection_id = request.form['connection_id']
            try:
                disease_symptom = db.session.query(Diseasesymptoms).filter_by(connectionid=connection_id).first()
                if disease_symptom:
                    disease_symptom.symptomid = new_symptom_id
                    disease_symptom.diseaseid = new_disease_id
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленны успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'drugdiseases':
            new_drug_id = request.form['new_drug_id']
            new_disease_id = request.form['new_disease_id']
            connection_id = request.form['connection_id']
            try:
                drug_disease = db.session.query(Drugdiseases).filter_by(connectionid=connection_id).first()
                if drug_disease:
                    drug_disease.drugid = new_drug_id
                    drug_disease.diseaseid = new_disease_id
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленны успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'homemedicine':
            new_quantity = request.form['new_quantity']
            new_drug_id = request.form['new_drug_id']
            medicine_id = request.form['medicine_id']
            print(new_quantity, new_drug_id, medicine_id)
            try:
                home_medicine = db.session.query(Homemedicine).filter_by(medicineid=medicine_id).first()
                if home_medicine:
                    home_medicine.quantity = new_quantity
                    home_medicine.drugid = new_drug_id
                    db.session.commit()
                    return render_template('Result.html', result='Данные обновленны успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')


@app.route('/delete_value/<table_choice>/<value>', methods=['GET', 'POST'])
def delete_value(table_choice, value):
    match table_choice:
        case 'diseasesymptoms':
            try:
                disease_symptom = db.session.query(Diseasesymptoms).filter_by(connectionid=value).first()
                if disease_symptom:
                    db.session.delete(disease_symptom)
                    db.session.commit()
                    return render_template('Result.html', result='Данные удалены успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'drugdiseases':
            try:
                drug_disease = db.session.query(Drugdiseases).filter_by(connectionid=value).first()
                if drug_disease:
                    db.session.delete(drug_disease)
                    db.session.commit()
                    return render_template('Result.html', result='Данные удалены успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'homemedicine':
            try:
                home_medicine = db.session.query(Homemedicine).filter_by(medicineid=value).first()
                if home_medicine:
                    db.session.delete(home_medicine)
                    db.session.commit()
                    return render_template('Result.html', result='Данные удалены успешно!')
            except Exception as e:
                return render_template('Result.html', result=f'Error: {str(e)}')


@app.route('/insertForm/<table_choice>')
def add_data_form(table_choice):
    match table_choice:
        case 'symptoms':
            return render_template('InsertFormSymptoms.html', table_name=table_choice)
        case 'drugs':
            return render_template('InsertFormDrugs.html', table_name=table_choice)
        case 'diseases':
            return render_template('InsertFormDiseases.html', table_name=table_choice)
        case 'diseasesymptoms':
            return render_template('InsertFormDiseasesymptoms.html', table_name=table_choice)
        case 'drugdiseases':
            return render_template('InsertFormDrugdiseases.html', table_name=table_choice)
        case 'homemedicine':
            return render_template('InsertFormHomemedicine.html', table_name=table_choice)
    # return render_template('InsertForm.html', table_name=table_choice)


@app.route('/database/insert', methods=['GET', 'POST'])
def add_data():
    table_name = request.form['table_name']

    match table_name:
        case 'symptoms':
            try:
                data = request.form['data']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO symptoms (name) VALUES ('{data}');")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'drugs':
            try:
                data = request.form['data']
                expiredate = request.form['date']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO drugs (name, expiredate) VALUES ('{data}', '{expiredate}');")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'diseases':
            try:
                data = request.form['data']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO diseases (name) VALUES ('{data}');")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'diseasesymptoms':
            try:
                diseaseid = request.form['diseaseid']
                symptomid = request.form['symptomid']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO diseasesymptoms (diseaseid, symptomid) VALUES ({diseaseid}, {symptomid});")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'drugdiseases':
            try:
                drugid = request.form['drugid']
                diseaseid = request.form['diseaseid']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO drugdiseases (drugid, diseaseid) VALUES ({drugid}, {diseaseid});")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')
        case 'homemedicine':
            try:
                drugid = request.form['drugid']
                quantity = request.form['quantity']
                # Формирование и выполнение SQL-запроса
                query = text(f"INSERT INTO homemedicine (drugid, quantity) VALUES ({drugid}, {quantity});")
                db.session.execute(query)
                db.session.commit()

                return render_template('Result.html', result='Данные добавленны успешно!')
            except Exception as e:
                # Обработка ошибок
                return render_template('Result.html', result=f'Error: {str(e)}')

    # try:
    #     # Формирование и выполнение SQL-запроса
    #     query = text(f"INSERT INTO {table_name} VALUES ({data});")
    #     db.session.execute(query)
    #     db.session.commit()
    #
    #     return 'Data added successfully!'
    # except Exception as e:
    #     # Обработка ошибок
    #     return f'Error: {str(e)}', 500


# @app.route('/delete_data', methods=['GET', 'POST'])
# def delete_data():
#     table_name = request.form['table_name']
#     condition = request.form['condition']
#
#     if table_name not in available_tables:
#         return 'Invalid table name', 400
#
#     if ';' in condition or 'DROP' in condition.upper():
#         return 'Invalid condition', 400
#
#     try:
#         # Формирование и выполнение SQL-запроса
#         query = text(f"DELETE FROM {table_name} WHERE {condition};")
#         db.session.execute(query)
#         db.session.commit()
#
#         return 'Data deleted successfully!'
#     except Exception as e:
#         # Обработка ошибок
#         return f'Error: {str(e)}', 500


# @app.route('/update_data', methods=['POST'])
# def update_data():
#     table_name = request.form['table_name']
#     condition_column = request.form['condition_column']
#     condition_value = request.form['condition_value']
#     update_column = request.form['update_column']
#     update_value = request.form['update_value']
#
#     # Предотвращение SQL-инъекций
#     if (';' in condition_value or ';' in update_value or
#             'DROP' in condition_value.upper() or 'DROP' in update_value.upper()):
#         return 'Invalid data', 400
#
#     try:
#         # Явное указание SQL-выражения как текста
#         query = text(f"UPDATE {table_name} SET {update_column} = :update_value "
#                      f"WHERE {condition_column} = :condition_value")
#         db.session.execute(query, {'update_value': update_value, 'condition_value': condition_value})
#         db.session.commit()
#
#         return 'Data updated successfully!'
#     except Exception as e:
#         # Обработка ошибок
#         return f'Error: {str(e)}', 500


if __name__ == "__main__":
    app.run(debug=True)
