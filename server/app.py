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

# Assuming your Message model has a 'created_at' attribute, add 'created_at' to the to_dict method if it's not there already.
class Message(db.Model):
    # ... other attributes ...
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'username': self.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp as needed
            # ... other fields ...
        }

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        try:
            # Fetch all messages, order them by created_at in ascending order
            messages_lc = [message.to_dict() for message in Message.query.order_by(Message.created_at).all()]
            return jsonify(messages_lc), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()

        if "body" not in data or "username" not in data:
            return jsonify({"error": "Missing 'body' or 'username' in request data"}), 400

        try:
            new_message = Message(
                body=data["body"],
                username=data["username"]
            )

            db.session.add(new_message)
            db.session.commit()

            new_message_dict = new_message.to_dict()

            return jsonify(new_message_dict), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return jsonify({"error": "Message not found"}), 404

    if request.method == "PATCH":
        try:
            updated_message_data = request.get_json()
            message.body = updated_message_data.get("body", message.body)

            db.session.commit()

            updated_message_dict = message.to_dict()

            return jsonify(updated_message_dict), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "DELETE":
        try:
            db.session.delete(message)
            db.session.commit()

            return jsonify({"success": True, "message": "Message deleted"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
