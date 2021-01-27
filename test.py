from flask import Blueprint, jsonify
from . import mysql

from project.mysqlHandler import accountNumToAccountID, hasMoney
testblueprint = Blueprint('testblueprint', __name__)

@testblueprint.route('/test')
def test():

    return jsonify(hasMoney(1,10))
    

   
    
