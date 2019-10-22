import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    print('getting drinks')
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    create_drink: creates a new drink
    Args:
        title (data type: str) ie "Matcha Latte"
        recipe (data type: str) ie
                "[{'color': string, 'name':string, 'parts':number}]"
    Returns:
        returns success if drink is updated
    """
    # TODO: Review please explain why below doesnt work
    # body = request.get_json()
    # title = body.get('title', None)
    # recipe = body.get('recipe', None)

    data = json.loads(request.data.decode('utf-8'))
    recipe = json.dumps(data['recipe'])
    title = data['title']

    if not title or not recipe:
        abort(400)

    try:
        drink = Drink(
            title=title,
            recipe=recipe,
        )
        drink.insert()
        return jsonify({
            "success": True,
            "drink": drink.long()
        }), 201
    except TypeError:
        abort(422)
    except exc.SQLAlchemyError:
        abort(500)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    """
    update_drink: updates a drink given id
    Args:
        drink_id (data type: int)
    Returns:
        returns success if drink is updated
    """
    # TODO: Review please explain why below doesnt work
    # body = request.get_json()
    # title = body.get('title', None)
    data = json.loads(request.data.decode('utf-8'))
    title = data['title']

    if not title:
        abort(400)

    drink = Drink.query.get_or_404(drink_id)

    try:
        if title:
            drink.title = title
        drink.update()
        return jsonify({
            "success": True,
            "drink": drink.long()
        }), 200
    except TypeError:
        abort(400)
    except exc.SQLAlchemyError:
        abort(500)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
    delete_drink: deletes a drink by id
    Args:
        drink_id (data type: int)
    Returns:
        returns success if drink is deleted
    """
    drink = Drink.query.get_or_404(drink_id)
    try:
        drink.delete()
        return jsonify({
            "success": True,
        })
    except exc.SQLAlchemyError:
        abort(500)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401


@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "forbidden"
                    }), 403


@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }), 404


@app.errorhandler(405)
def methodnotallowed(error):
    return jsonify({
                    "success": False,
                    "error": 405,
                    "message": "method not allowed"
                    }), 405


@app.errorhandler(400)
def badrequest(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(500)
def badrequest(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                    }), 500
