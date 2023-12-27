from flask import Flask, jsonify
from acbrlib import AcbrLibNfe
from os import path
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue
import json

app = Flask(__name__)
app.config.from_envvar('TEMPLATES_AUTO_RELOAD', True)

BASE_DIR = path.dirname(path.abspath(__file__))

@app.route('/', methods=['GET'])
def hello_world():
    return { "teste": "Ok"}

@app.route('/status', methods=['GET'])
def StatusServico():
    q = Queue()
    p = Process(target=StatusServicoT, args=(q,))
    p.start()
    ret = q.get()
    p.join()
    return json.loads(ret)

    # thread = Process(target=StatusServicoT, args=({},))
    # thread.start()
    # thread.join()
    # thread.close()
    # return {}

@app.route('/pdf', methods=['GET'])
def GerarPDF():
    thread = Process(target=GerarPDFT)
    thread.start()
    thread.join()
    thread.close()
    return {}


def StatusServicoT(q):
    print(q)
    print('StatusServico Inicio: ' , datetime.now())
    lib = AcbrLibNfe()
    lib.NFE_Inicializar('RS','20162013',path.join(BASE_DIR, path.join('arquivos', 'certificado - 20162013.pfx')))
    ret = lib.NFE_StatusServico()
    lib.NFE_Finalizar()
    print('StatusServico Fim: ' , datetime.now())
    q.put(json.dumps(ret))

def GerarPDFT():
    print('GerarPDF Inicio: ' , datetime.now())
    lib = AcbrLibNfe()
    lib.NFE_Inicializar('RS','20162013',path.join(BASE_DIR, path.join('arquivos', 'certificado - 20162013.pfx')))
    xmlContent = Path(path.join(BASE_DIR, path.join('arquivos', 'NF.xml'))).read_text()
    lib.NFE_CarregarXML(xmlContent)
    ret = lib.NFE_SalvarPDF()
    lib.NFE_Finalizar()
    print('GerarPDF Fim: ' , datetime.now())
    return {"base64": ret}