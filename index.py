from flask import Flask, jsonify, request, Response, abort
from acbrlib import AcbrLibNfe
from os import path
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue, Pool
from flask_expects_json import expects_json
import json
import os

app = Flask(__name__)

schemaStatus = {
    'type': 'object',
    'properties': {
        'certificado': {'type': 'string'}
    },
    'required': ['certificado']
}

BASE_DIR = path.dirname(path.abspath(__file__))

@app.route('/', methods=['GET'])
def hello_world():
    return { "teste": "Ok"}

@app.route('/status', methods=['POST'])
@expects_json(schemaStatus)
def StatusServico():
    try:
        body = json.loads(request.data)
        queue = Queue()
        process = Process(target=StatusServicoT, args=(queue,body['certificado']))
        process.start()
        ret = queue.get()
        process.join()
        if process.exitcode:
            process.join()
            
        response = Response()
        response.data = json.loads(ret)
        response.content_type = "application/json"
        return response
    except Exception as e:
        print(e)
        abort(503)
    
@app.route('/pdf', methods=['GET'])
def GerarPDF():
    try:
        queue = Queue()
        process = Process(target=GerarPDFT, args=(queue,))
        process.start()
        ret = queue.get()
        process.join()

        if process.exitcode:
            process.join()

        return json.loads(ret)
    except Exception as e:
        print(e)
        abort(503)


def StatusServicoT(q, certificado):
    print(certificado)
    print('StatusServico Inicio: ' , datetime.now())
    lib = AcbrLibNfe()
    lib.NFE_Inicializar('RS','20162013',path.join(BASE_DIR, path.join('arquivos', 'certificado - 20162013.pfx')))
    ret = lib.NFE_StatusServico()
    lib.NFE_Finalizar()
    print('StatusServico Fim: ' , datetime.now())
    return q.put(json.dumps(ret))

def GerarPDFT(q):
    print('GerarPDF Inicio: ' , datetime.now())
    lib = AcbrLibNfe()
    lib.NFE_Inicializar('RS','20162013',path.join(BASE_DIR, path.join('arquivos', 'certificado - 20162013.pfx')))
    xmlContent = Path(path.join(BASE_DIR, path.join('arquivos', 'NF.xml'))).read_text()
    lib.NFE_CarregarXML(xmlContent)
    ret = lib.NFE_SalvarPDF()
    lib.NFE_Finalizar()
    print('GerarPDF Fim: ' , datetime.now())
    return q.put(json.dumps({"base64": ret}))

if __name__ == '__main__':
    app.run(port=5000)