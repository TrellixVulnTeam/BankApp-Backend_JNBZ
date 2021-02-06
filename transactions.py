from flask import Blueprint, jsonify, request
from project.mysqlHandler import mysql, isOwner, get_active_idAccounts_Of_Customer, getIdsTransferOfAccount, get_all_idAccounts_of_Customer
from flask_jwt_extended import jwt_required, get_jwt_identity

transactionsblueprint = Blueprint('transactionsblueprint', __name__)


# wyświetla wszystkie transakcje danego użytkownika
@transactionsblueprint.route('/transactions')
@jwt_required
def transactions():

    idAccounts = get_all_idAccounts_of_Customer(get_jwt_identity())

    transactionsId = []
    for id in idAccounts:
        transactionsId = transactionsId + getIdsTransferOfAccount(id)

    return getInfoAboutTranscation(transactionsId, 'JSON')


# wyświetla wszystkie transakcje na koncie o podanym idAccount
# TODO sprawdzić, czy potrzebne, jeśli tak to zmienić pobieranie danych z tablicy owners na allOwners
@transactionsblueprint.route('/transactions/<int:idAccount>', methods=['GET'])
@jwt_required
def transactionsOfAccount(idAccount):
    if isOwner(get_jwt_identity(), idAccount):
        idTransactions = getIdsTransferOfAccount(idAccount)
        return getInfoAboutTranscation(idTransactions, 'JSON')
    else:
        return jsonify({"msg": "Brak dostępu"}), 401


# generowanie PDFa
@transactionsblueprint.route('/transactions/pdf', methods=['POST'])
@jwt_required
def generatePDF():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        if not isinstance(request.json['idTransactions'], int):
            return jsonify({"msg": "IdTransactions musi być typu int"}), 400

        idTrans = request.json['idTransactions']

        # sprawdzanie czy transakcja należy do konta zalogowanego użytkownika
        if not isAccountOfTransaction(idTrans):
            return jsonify({"msg": "Brak dostępu do tej transakcji"}), 400

        infoTrans = getInfoAboutTranscation(idTrans, '')

        # TODO dodać samo generowanie pdfa, najlepiej używając pakietu z flaska
        # TODO wszystko jest w infoTrans, w takiej kolejności jak dodawane są dane
        # TODO do JSONa z userData w linijce 95 tego programu

        return ''


def isAccountOfTransaction(idTransaction):

    accountsList = get_active_idAccounts_Of_Customer(get_jwt_identity())
    for idAcc in accountsList:
        for idTran in getIdsTransferOfAccount(idAcc):
            if idTran == idTransaction:
                return True
    return False


# funkcja zwraca informacje o podanej transakcji lub liście transakcji
# type = 0 oznacza że wrócony typ danych to JSON, a 1, że lista
def getInfoAboutTranscation(idTransactions, type):
    conn = mysql.connect()
    cursor = conn.cursor()

    # spradzanie czy na wejściu jest int czy lista
    idTrans = idTransactions
    if isinstance(idTrans,int):
        idTransactions = []
        idTransactions.append(idTrans)

    myJson = []
    simpleData = []
    for id in idTransactions:
        sql = """select idAccounts, idAccountsOfRecipient, amountOfTransaction, date, old_balance, new_balance,
        message from transactions where idTransactions = %s """
        cursor.execute(sql, [id])
        data = cursor.fetchone()

        userData = []
        for row in data:
            userData.append(row)
            simpleData.append(row)

        myJson.append({
            'idTransactions ': id,
            'idAccounts': userData[0],
            'idAccountsOfRecipient': userData[1],
            'amountOfTransaction': userData[2],
            'idCreditCards': userData[3],
            'old_balance': userData[4],
            'new_balance': userData[5],
            'message': userData[6]
        })
    if type == 'JSON':
        return jsonify(myJson)
    else:
        return simpleData