import platform
from os import path
from ctypes import cdll, POINTER, c_int, create_string_buffer, c_uint, byref
from multiprocessing import Process
from datetime import datetime

BASE_DIR = path.dirname(path.abspath(__file__))

class AcbrLibException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AcbrLib:
    dll = None
    dll_handler = None
    STR_BUFFER_LEN = 2000000

    def _check_result(self, result_code):
        if result_code == 0:
            return
        
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(self.STR_BUFFER_LEN)
        self.dll.NFE_UltimoRetorno(self.dll_handler, buffer, byref(size))

        buffer = create_string_buffer(size.value)
        self.dll.NFE_UltimoRetorno(self.dll_handler, buffer, byref(c_int(self.STR_BUFFER_LEN)))
        resposta = buffer.raw.decode('utf-8').replace('0x00', '').replace('\x00', '').rstrip(u"\u0000")
        raise AcbrLibException(resposta)

    def _process_result(self, result, size):
        if size.value <= self.STR_BUFFER_LEN:
            return result.raw.decode('utf-8').replace('0x00', '').replace('\x00', '')
        if size.value > self.STR_BUFFER_LEN:
            buffer = create_string_buffer(size.value)
            self.dll.NFE_UltimoRetorno(self.dll_handler, buffer, byref(c_int(self.STR_BUFFER_LEN)))
            return buffer.raw.decode('utf-8').replace('0x00', '').replace('\x00', '')
        

class AcbrLibNfe(AcbrLib):
    def __init__(self):
        name = None
        if platform.uname()[0] == "Windows":
            name = "ACBrNFe64.dll"
        if platform.uname()[0] == "Linux":
            name = "libacbrnfe64.so"

        dll_path = path.join(BASE_DIR, path.join('lib', name))
        self.dll = cdll.LoadLibrary(dll_path)
        self.dll_handler = POINTER(c_int)()

    def NFE_Inicializar(self, uf, senha, arquivo_pfx):
        ret = self.dll.NFE_Inicializar(byref(self.dll_handler), '[memory]'.encode('utf-8'), "")
        self._check_result(ret)

        config = {
            'Principal': {
                'TipoResposta': '2',
                'CodificacaoResposta': '0',
                'LogNivel': '4',
                'LogPath': BASE_DIR
            },
            'NFe': {
                'PathSchemas': path.join(BASE_DIR, path.join('arquivos','schemas', 'NFe')),
                'SalvarGer': '0',
                'SalvarArq': '0',
                'SalvarEvento': '0',
                'SSLType': '5'
            },
            'DFe': {
                'SSLCryptLib': '3' if platform.uname()[0] == "Windows" else '1',
                'SSLHttpLib': '3' if platform.uname()[0] == "Windows" else '1',
                'SSLXmlSignLib': '4',
                'UF': uf,
                'TimeZone.Modo': '0',
                'ArquivoPFX': arquivo_pfx,
                'Senha': senha,
                'VerificarValidade': '1',
            },
            'DANFE': {
                'PathPDF': path.join(BASE_DIR, 'danfe'),
                'MostraSetup': '0',
                'MostraPreview': '0',
                'MostraStatus': '0',
            }
        }

        for sessao_key, sessao_value in config.items():
            for key, value in sessao_value.items():
                ret = self.dll.NFE_ConfigGravarValor(self.dll_handler, sessao_key.encode('utf-8'), key.encode('utf-8'), value.encode('utf-8'))
                self._check_result(ret)

    def NFE_StatusServico(self):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(self.STR_BUFFER_LEN)
        ret = self.dll.NFE_StatusServico(self.dll_handler, buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_CarregarINI(self, eArquivoOuINI):
        ret = self.dll.NFE_CarregarINI(self.dll_handler, eArquivoOuINI.encode('utf-8'))
        self._check_result(ret)

    def NFE_Assinar(self):
        ret = self.dll.NFE_Assinar(self.dll_handler)
        self._check_result(ret)

    def NFE_Validar(self):
        ret = self.dll.NFE_Validar(self.dll_handler)
        self._check_result(ret)

    def NFE_ObterXml(self):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(len(buffer))
        ret = self.dll.NFE_ObterXml(self.dll_handler, 0, buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_Enviar(self, lote=0, imprimir=False, sincrono=True, zipado=False):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(len(buffer))
        ret = self.dll.NFE_Enviar(self.dll_handler, lote, imprimir, sincrono, zipado, buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_Cancelar(self, chave, justificativa, cnpj, lote=0):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(len(buffer))
        ret = self.dll.NFE_Cancelar(self.dll_handler, chave.encode('utf-8'), justificativa.encode('utf-8'), cnpj.encode('utf-8'), lote, buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_DistribuicaoDFePorChave(self, uf_autor, cnpj_cpf, chave):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(len(buffer))
        ret = self.dll.NFE_DistribuicaoDFePorChave(self.dll_handler, uf_autor, cnpj_cpf.encode('utf-8'), chave.encode('utf-8'), buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_LimparLista(self):
        ret = self.dll.NFE_LimparLista(self.dll_handler)
        self._check_result(ret)

    def NFE_CarregarXML(self, eArquivoOuXML):
        ret = self.dll.NFE_CarregarXML(self.dll_handler, eArquivoOuXML.encode('utf-8'))
        self._check_result(ret)

    def NFE_SalvarPDF(self):
        buffer = create_string_buffer(self.STR_BUFFER_LEN)
        size = c_uint(len(buffer))
        ret = self.dll.NFE_SalvarPDF(self.dll_handler, buffer, byref(size))
        self._check_result(ret)
        return self._process_result(buffer, size)

    def NFE_ImprimirPDF(self):
        ret = self.dll.NFE_ImprimirPDF(self.dll_handler)
        self._check_result(ret)

    def NFE_Finalizar(self):
        ret = self.dll.NFE_Finalizar(self.dll_handler)
        self._check_result(ret)