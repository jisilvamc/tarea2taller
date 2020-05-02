# Revisar descripcion al retornar un json; está el json y el status, pero no la descripción


import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
application = app  # gunicorn
app.config["DEBUG"] = True
mi_path = "https://t2taller-jisilvamc.herokuapp.com"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect('my_database.db')  # ya está vacía
conn.row_factory = dict_factory
cur = conn.cursor()
#cur.execute('DROP TABLE IF EXISTS hamburguesa;')
#cur.execute('CREATE TABLE hamburguesa (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre varchar(255), precio int, '
#            'descripcion varchar(255), imagen varchar(255));')
#cur.execute('DROP TABLE IF EXISTS ingrediente;')
#cur.execute('CREATE TABLE ingrediente (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre varchar(255), '
#            'descripcion varchar(255));')
#cur.execute('DROP TABLE IF EXISTS hamburguesa_ingrediente;')
#cur.execute('CREATE TABLE hamburguesa_ingrediente (id INTEGER PRIMARY KEY AUTOINCREMENT, hamburguesa_id int, '
#            'ingrediente_id int, FOREIGN KEY(hamburguesa_id) REFERENCES hamburguesa(id), '
#            'FOREIGN KEY(ingrediente_id) REFERENCES ingrediente(id));')


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Bienvenido al restaurant</h1>
<p>Primera API :)</p>'''

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



@app.route('/ingrediente', methods=['GET'])
def get_ing():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_ing = cur.execute('SELECT * FROM ingrediente;').fetchall()
    return jsonify(all_ing), 200

@app.route('/ingrediente', methods=['POST'])
def post_ing():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        dic = request.json
        nombre, descripcion = dic.get("nombre"), dic.get("descripcion")
        if nombre == "" or descripcion == "":
        	return "Input invalido", 400
        cur.execute("INSERT INTO ingrediente(nombre, descripcion) VALUES ('{}', '{}');".format(nombre, descripcion))
        conn.commit()
        new_ing = cur.execute("SELECT * FROM ingrediente ORDER BY id DESC LIMIT 1;".format()).fetchall()[0]
        return jsonify(new_ing), 201
    except (KeyError):
        return "Input invalido", 400

@app.route('/ingrediente/<ingredienteid>', methods=['GET'])
def get_ing_id(ingredienteid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        if not ingredienteid.isdigit():
            return "id invalido", 400
        ing = cur.execute('SELECT * FROM ingrediente WHERE id = {};'.format(ingredienteid)).fetchall()[0]
        return jsonify(ing), 200
    except:
        return "ingrediente inexistente", 404

@app.route('/ingrediente/<int:ingredienteid>', methods=['DELETE'])
def delete_ing_id(ingredienteid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        hamburguesas = cur.execute('SELECT hamburguesa_id FROM hamburguesa_ingrediente '
                                   'WHERE ingrediente_id={}'.format(ingredienteid)).fetchall()
        if hamburguesas:
            for hamb in hamburguesas:
                if cur.execute('SELECT id FROM hamburguesa WHERE id={}'.format(hamb["hamburguesa_id"])).fetchall():
                    return "Ingrediente no se puede borrar, se encuentra presente en una hamburguesa", 409
        cur.execute('DELETE FROM ingrediente WHERE id = {};'.format(ingredienteid))
        conn.commit()
        return "ingrediente eliminado", 200
    except:
        return "ingrediente inexistente", 404



@app.route('/hamburguesa', methods=['GET'])
def get_ham():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_ham = cur.execute('SELECT * FROM hamburguesa;').fetchall()
    for hamburguesa in all_ham:
        hamburguesaid = hamburguesa["id"]
        ingredientes = cur.execute('SELECT ingrediente_id FROM hamburguesa_ingrediente WHERE '
                               'hamburguesa_id = {};'.format(hamburguesaid)).fetchall()
        hamburguesa["ingredientes"] = [{"path": mi_path + "/ingrediente/" + str(i["ingrediente_id"])} for i in ingredientes]
    return jsonify(all_ham), 200

@app.route('/hamburguesa', methods=['POST'])
def post_ham():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        dic = request.json
        nombre, precio, descripcion, imagen = dic.get("nombre"), dic.get("precio"), dic.get("descripcion"), dic.get("imagen")
        if nombre == "" or precio == "" or descripcion == "" or imagen == "":
        	retun "Input invalido", 400
        cur.execute("INSERT INTO hamburguesa(nombre, precio, descripcion, imagen) "
                    "VALUES ('{}', {}, '{}', '{}');".format(nombre, precio, descripcion, imagen))
        conn.commit()
        new_ham = cur.execute("SELECT * FROM hamburguesa ORDER BY id DESC LIMIT 1;".format()).fetchall()[0]
        new_ham["ingredientes"] = []
        return jsonify(new_ham), 201
    except (KeyError):
        return "Input invalido", 400

@app.route('/hamburguesa/<hamburguesaid>', methods=['GET'])
def get_ham_id(hamburguesaid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        if not hamburguesaid.isdigit():
            return "id invalido", 400
        ham = cur.execute('SELECT * FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall()[0]
        ingredientes = cur.execute('SELECT ingrediente_id FROM hamburguesa_ingrediente WHERE '
                                   'hamburguesa_id = {};'.format(hamburguesaid)).fetchall()
        ham["ingredientes"] = [{"path": mi_path+"/ingrediente/"+str(i["ingrediente_id"])} for i in ingredientes]
        return jsonify(ham), 200
    except :
        return "hamburguesa inexistente", 404

@app.route('/hamburguesa/<int:hamburguesaid>', methods=['DELETE'])
def delete_ham_id(hamburguesaid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if cur.execute('SELECT * FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall():
        cur.execute('DELETE FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall()
        conn.commit()
        return "hamburguesa eliminada", 200
    else:
        return "hamburguesa inexistente", 404

@app.route('/hamburguesa/<hamburguesaid>', methods=['PATCH'])
def patch_ham_id(hamburguesaid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    try:
        hamburguesa = cur.execute('SELECT * FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall()
        if not hamburguesa:
            return "Hamburguesa inexistente", 404
        dic = request.json
        nombre, precio, descripcion, imagen = hamburguesa[0]["nombre"], hamburguesa[0]["precio"], \
                                              hamburguesa[0]["descripcion"], hamburguesa[0]["imagen"]
        if "nombre" in dic.keys():
            nombre = dic.get("nombre")
        if "precio" in dic.keys():
            precio = dic.get("precio")
        if "descripcion" in dic.keys():
            descripcion = dic.get("descripcion")
        if "imagen" in dic.keys():
            imagen = dic.get("imagen")
        cur.execute("UPDATE hamburguesa SET nombre='{}', precio={}, descripcion='{}', imagen='{}' WHERE id={};"
                    .format(nombre, precio, descripcion, imagen, hamburguesaid))
        conn.commit()
        patch_ham = cur.execute("SELECT * FROM hamburguesa WHERE id={};".format(hamburguesaid)).fetchall()[0]
        ingredientes = cur.execute('SELECT ingrediente_id FROM hamburguesa_ingrediente WHERE '
                                   'hamburguesa_id = {};'.format(hamburguesaid)).fetchall()
        patch_ham["ingredientes"] = [{"path": mi_path + "/ingrediente/" + str(i["ingrediente_id"])} for i in ingredientes]
        return jsonify(patch_ham), 200
    except:
        return "Parámetros inválidos", 400



@app.route('/hamburguesa/<int:hamburguesaid>/ingrediente/<int:ingredienteid>', methods=['PUT'])
def put_ham_ing_id(hamburguesaid, ingredienteid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if not cur.execute('SELECT * FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall():
        return "Id de hamburguesa inválido", 400
    elif not cur.execute('SELECT * FROM ingrediente WHERE id = {};'.format(ingredienteid)).fetchall():
        return "Ingrediente inexistente", 404
    else:
        cur.execute("INSERT INTO hamburguesa_ingrediente(hamburguesa_id, ingrediente_id) "
                    "VALUES ({}, {});".format(hamburguesaid, ingredienteid))
        conn.commit()
        return "Ingrediente agregado", 201

@app.route('/hamburguesa/<int:hamburguesaid>/ingrediente/<int:ingredienteid>', methods=['DELETE'])
def delete_ham_ing_id(hamburguesaid, ingredienteid):
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if not cur.execute('SELECT * FROM hamburguesa WHERE id = {};'.format(hamburguesaid)).fetchall():
        return "Id de hamburguesa inválido", 400
    elif not cur.execute('SELECT * FROM hamburguesa_ingrediente WHERE '
                         'hamburguesa_id = {} and ingrediente_id={};'.format(hamburguesaid, ingredienteid)).fetchall():
        return "Ingrediente inexistente en la hamburguesa", 404
    else:
        cur.execute('DELETE FROM hamburguesa_ingrediente WHERE '
                    'hamburguesa_id = {} and ingrediente_id={};'.format(hamburguesaid, ingredienteid))
        conn.commit()
        return "Ingrediente retirado", 200


if __name__ == '__main__':
	app.run()
    # app.run(port=33507)
    # app.run(debug=True)

# app.run(debug=True)
