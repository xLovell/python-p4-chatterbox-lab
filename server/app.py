from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc())

        messages_dict = [message.to_dict() for message in messages]
        response = make_response(
            messages_dict,
            200
        )
        response.headers["Content-Type"] = "application/json"

        return response
    elif request.method == 'POST':
        new_message = Message(
            body = request.get_json()["body"],
            username = request.get_json()["username"]
        )
        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            message_dict,
            201
        )

        return response

@app.route('/messages/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()

    if message == None:
        response_body = {
            "message": "This message does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)

        return response
    else:
        if request.method == 'GET':
            message_dict = message.to_dict()

            response = make_response(
                message_dict,
                200
            )

            return response
        elif request.method == 'PATCH':
            message.body = request.get_json()["body"]

            db.session.add(message)
            db.session.commit()

            message_dict = message.to_dict()

            response = make_response(message_dict, 200)
            return response
        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }
            response = make_response(response_body, 200)
            return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)
