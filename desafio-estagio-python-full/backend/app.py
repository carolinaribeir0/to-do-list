from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1010"
app.config["MYSQL_DB"] = "desafio"

def db_connection():
    return pymysql.connect(
    host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        db=app.config["MYSQL_DB"],
        cursorclass=pymysql.cursors.DictCursor
) #Função para conectar ao mysql para evitar erro de database/table já existente


def create_table(): #adcionada clausula IF NOT EXISTS   
    try:
        print("Creating table")
        connection = db_connection()
        with connection.cursor() as cur:
            cur = connection.cursor()
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS`desafio`.`tasks` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `description` VARCHAR(255) NOT NULL,
    `status` ENUM('To-Do', 'Doing', 'Done') NOT NULL,
    PRIMARY KEY (`id`));

                    """
            )
            connection.commit()
            connection.close()
            print("Table created successfully")
    except Exception as e:
        print("Error while create", e)


@app.route("/")
def hello_world():  # put application's code here
    return "Hello World!"


@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        connection= db_connection()
        with connection.cursor() as cur:
            cur = connection.cursor()
            cur.execute("SELECT * FROM tasks")
            tasks = cur.fetchall()
        connection.close()
        response = {
                "error": False,
                "data": tasks,
                "message": "Tasks fetched successfully",
            }
        return jsonify(response), 200
    except Exception as e:
        response = {"error": True, "message": f"Error Occurred: {e}", "data": None}
        return jsonify(response), 500
    
@app.route("/get_task/<int:task_id>", methods=["GET"]) #adcionado para consultar task por ID para carregar os dados na tela para editar
def get_task(task_id):
    try:
        connection= db_connection()
        with connection.cursor() as cur:
            cur = connection.cursor()
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id))
            task = cur.fetchone()
        connection.close()
        response = {
                "error": False,
                "data": task,
                "message": "Task fetched successfully",
            }
        return jsonify(response), 200
    except Exception as e:
        response = {"error": True, "message": f"Error Occurred: {e}", "data": None}
        return jsonify(response), 500


@app.route("/add_task", methods=["POST"])
def add_task():
    try:
        data = request.get_json()
        description = data["description"]
        status = data["status"]
        connection = db_connection()
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (description, status) VALUES (%s, %s)",
                (description, status),
            )
        connection.commit()
        connection.close()
        response = {"error": False, "message": "Task added successfully", "data": data}
        return jsonify(response), 201
    except Exception as e:
        response = {"error": True, "message": f"Error Occurred: {e}", "data": None}

        # Return a JSON response with HTTP status code 500 (Internal Server Error)
        return jsonify(response), 500


@app.route("/update_task/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json()
        description = data["description"]
        status = data["status"]
        connection= db_connection()
        with connection.cursor() as cur:
            cur.execute(
            "UPDATE tasks SET description = %s, status = %s WHERE id = %s", (description, status, task_id)
        )
        connection.commit()
        connection.close()
        response = {
            "error": False,
            "message": "Task updated successfully",
            "data": data,
        }
        return jsonify(response), 200
    except Exception as e:
        response = {"error": True, "message": f"Error Occurred: {e}", "data": None}
        return jsonify(response), 500
    
@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        connection = db_connection()
        with connection.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            affected_rows=cur.rowcount
        connection.commit()
        connection.close()
        
        if affected_rows == 0:
            response = {"error": True, "message": "Task not found", "data": None}
            return jsonify(response), 404

        response = {
            "error": False,
            "message": "Task deleted successfully",
            "data": None,
        }
        return jsonify(response), 200
    except Exception as e:
        response = {"error": True, "message": f"Error Occurred: {e}", "data": None}
        return jsonify(response), 500

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
#rotas estavam sem funcionar porque foram declaradas antes de iniciar o app run, movido para o final do codigo após a declaração das tasks