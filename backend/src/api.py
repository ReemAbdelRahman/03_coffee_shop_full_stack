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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

'''
get_drinks(format) to be used by both get_all_drinks() and get_aa_detailed_drinks()
'''
def get_drinks(format):
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    formatted_drinks = []
    for drink in drinks:
        if format == "short":
            formatted_drinks.append(drink.short())
        else:
            formatted_drinks.append(drink.long())


    return jsonify({
      'drinks': formatted_drinks,
      'success': True
    })    

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_all_drinks():

    formatted_drinks = get_drinks('short')

    return jsonify({
      'drinks': formatted_drinks,
      'success': True
    })    

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth(permission='get:drinks-detail')
def get_all_detailed_drinks(jwt):
    formatted_drinks = get_drinks('long')

    return jsonify({
      'drinks': formatted_drinks,
      'success': True
    })   


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth(permission='post:drinks')
def create_drink(jwt):
    
    body = request.json

    new_title   = body.get('title', None)
    new_recipe     = body.get('recipe', None)

    try:
      drink = Drink(title = new_title,
                    recipe = new_recipe)
      drink.insert()

      return jsonify({
        'success': True,
        'drinks': drink.long(),
        })

    except Exception as e:
      abort(405)    

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='patch:drinks')
@app.route('/drinks/<int:drink_id>', methods = ['PATCH'])
def update_category(jwt,drink_id):
    body = request.json

    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        if 'title' in body:
            drink.title = body.get('title')

        if 'recipe' in body:
            drink.recipe = body.get('recipe')      

        drink.update()

        return jsonify({
            'success': True,
            "drinks": drink.long()
        })
    except Exception as e:
        print(e)
        abort(400)  

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='delete:drinks')
@app.route('/drinks/<int:drink_id>', methods = ['DELETE'])
def delete_drink(jwt,drink_id):
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        Drink.query.filter_by(id=drink_id).delete()
        drink.delete()



        return jsonify({
            'success': True,
            'deleted':drink_id
        })

    except Exception as e:
      print(e)
      abort(422)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found!"
                    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
                    "success": False, 
                    "error": 405,
                    "message": "Method not allowed!"
                    }), 405

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

# def get_token_auth_header():
#  if 'Authorization' not in request.headers:
#         abort(401)

#     auth_header = request.headers['Authorization']
#     header_parts = auth_header.split(' ')

#     if len(header_parts) !=2:
#         abort(401)    #malformed header
#     elif header_parts[0].lower()=='bearer':
#         abort(401)    
#     return 'not implemented'    


# app = Flask(__name__)

# @app.route('/headers')
# def headers():
#    