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

print('Inicio da aplicação')
Queue().close()

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

@app.route('/status', methods=['GET'])
# @expects_json(schemaStatus)
def StatusServico():
    # body = json.loads(request.data)
    try:
        print('def StatusServico()')
        queue = Queue()
        process = Process(target=StatusServicoT, args=(queue,))
        process.start()
        ret = queue.get()
        process.join()
        if process.exitcode:
            process.join()      

        print(ret['result_code'])
        print(jsonify(ret['message']), 200)
        
        return Response(ret['message'], 200 if not ret['result_code'] else 400)
    except Exception as e:
        print('except')
        print(e)
        return Response({"error": str(e)},400)
    
@app.route('/pdf', methods=['GET'])
def GerarPDF():
    queue = Queue()
    process = Process(target=GerarPDFT, args=(queue,))
    process.start()
    ret = queue.get()
    print(ret)
    process.join()

    if process.exitcode:
        process.join()

    return json.loads(ret)

def StatusServicoT(q):
    try:
        print('StatusServico Inicio: ' , datetime.now())
        lib = AcbrLibNfe()
        lib.NFE_Inicializar('RS','20162013',path.join(BASE_DIR, path.join('arquivos', 'certificado - 20162013.pfx')))
        ret = lib.NFE_StatusServico()
        print(type(ret))
        lib.NFE_Finalizar()
        print('StatusServico Fim: ' , datetime.now())
        return q.put(ret)
    except Exception as e: 
        ret = { "error": e.message, "status": 400}
        return q.put(ret)

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