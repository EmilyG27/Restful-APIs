from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
ma = Marshmallow(app)

@app.route('/')
def home():
    return "Welcome"

def get_db_connection():
    db_name = "fitness_center_db"
    user = "root"
    password = "Luna2794"
    host = "localhost"

    try:
        conn = mysql.connector.connect(database = db_name, user = user, password = password, host = host)
        print("connected")
        return conn
    
    except Error as e:
        print(e)

class MemberSchema(ma.Schema):
    id = fields.Int(dump_only = True)
    name = fields.Str(required = True)
    age = fields.Int(required = True)

class SessionSchema(ma.Schema):
    id = fields.Int(dump_only = True)
    date = fields.Str(required = True)
    workout_duration = fields.Int(required = True)
    calories_burned =  fields.Int(required = True)

member_schema = MemberSchema()
members_schema = MemberSchema(many = True)
session_schema = SessionSchema()
sessions_schema = SessionSchema(many = True)

@app.route('/members', methods = ["POST"])
def add_member():
    try:
        member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error", "connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Members (name, age) VALUES (%s, %s)"
        cursor.execute(query, (member['name'], member['age']))
        return jsonify({"message": "Member added"}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route("/members/<int:id>", methods = ["PUT"])
def update_member(id):
    try:
        member = member_schema.load(request.json)
    except ValidationError as e:
        print(e)
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member["name"], member["age"], id)
        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s"
        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated"}), 201
    
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()



@app.route("/members", methods = ["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members"
        cursor.execute(query)
        members = cursor.fetchall()

        return members_schema.jsonify(members)
    
    except Error as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route("/members<int:id>", methods = ["DELETE"])
def delete_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"message": "Member deleted"}), 200
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route("/sessions", methods = ["POST"])
def add_session():
    try:
        session = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error", "connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Sessions (date, workout_duration, calories_burned) VALUES (%s, %s, %s)"
        cursor.execute(query, (session['date'], session['workout_duration'], session['calories_burned']))
        conn.commit()
        return jsonify({"message": "Session added"}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route("/sessions/<int:id>", methods = ["PUT"])
def update_session(id):
    try:
        session = session_schema.load(request.json)
    except ValidationError as e:
        print(e)
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "connection failed"}), 500
        cursor = conn.cursor()

        updated_session = (session["date"], session["workout_duration"], session["calories_burned"], id)
        query = "UPDATE Sessions SET date = %s, workout_duration = %s, calories_burned = %s WHERE id = %s"
        cursor.execute(query, updated_session)
        conn.commit()

        return jsonify({"message": "Member updated"}), 201
    
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()



@app.route("/sessions", methods = ["GET"])
def get_sessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Sessions"
        cursor.execute(query)
        sessions = cursor.fetchall()

        return session_schema.jsonify(sessions)
    
    except Error as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
    
    finally:
        cursor.close()
        conn.close()



@app.route("/search_members", methods = ["GET"])
def search_members():
    members = request.json.get("members")
    members = members.split(", ")
    placeholders = ', '.join(['%s'] * len(members))
    print(members, placeholders)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"Select S.id, S.date, S.workout_duration, S.calories_burned, M.name AS MemberName From Sessions S, Members M Where S.id = M.id AND M.name in ({placeholders})", tuple(members))
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()