from app.main import bp
from flask.json import jsonify
from app.main.model_train import mscred_renew
from app.data.data_make import HOW_pred, redisTest


@bp.route("/health", methods=["GET", "POST"])
def health():
    return jsonify('Hydrogen oil water system diagnosis server check ok.')

@bp.route('/mscredTrain')
def mscred_run():
    print("MSCRED start running-------------")
    mscred_renew()
    return "Training is finished."

@bp.route('/HOW', methods=['GET', 'PUT', 'POST'])
def H2_oil_water():
    return jsonify(HOW_pred())

@bp.route('/generatorDiagnosis', methods=["PUT", "POST"])
def generatorDiagnosis():
    redisTest()
    return 
