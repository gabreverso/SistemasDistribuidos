from config import HOST, PORTA_TCP, PORTA_UDP
import socket
import json
import threading
from datetime import datetime

class ServidorDisciplinas:
    def __init__(self):
        self.disciplinas = {}
        self.executando = True
        
    def iniciar(self):
        print("Servidor iniciando...")
        
        thread_tcp = threading.Thread(target=self._iniciar_servidor_tcp)
        thread_udp = threading.Thread(target=self._iniciar_servidor_udp)
        thread_tcp.daemon = True
        thread_udp.daemon = True
        thread_tcp.start()
        thread_udp.start()
        

    def _iniciar_servidor_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORTA_TCP))
            s.listen()
            
            while self.executando:
                try:
                    conexao, endereco = s.accept()
                    threading.Thread(target=self._lidar_com_cliente_tcp, args=(conexao, endereco)).start()
                except:
                    break

    def _lidar_com_cliente_tcp(self, conexao, endereco):
        with conexao:
            print(f"\nNova conexão TCP de {endereco}")
            while True:
                try:
                    dados = conexao.recv(1024)
                    if not dados:
                        break
                    
                    try:
                        mensagem = json.loads(dados.decode('utf-8'))
                        print(f"Mensagem recebida: {mensagem}")
                        
                        resposta = self._processar_mensagem_tcp(mensagem)
                        conexao.sendall(json.dumps(resposta).encode('utf-8'))
                        print(f"Resposta enviada: {resposta}")
                        
                    except json.JSONDecodeError:
                        msg_erro = {'status': 'erro', 'mensagem': 'JSON inválido'}
                        conexao.sendall(json.dumps(msg_erro).encode('utf-8'))
                except:
                    break

    def _processar_mensagem_tcp(self, mensagem):
        try:
            acao = mensagem.get('acao')
            
            if acao == 'registrar':
                disciplina = mensagem['disciplina']
                if disciplina not in self.disciplinas:
                    self.disciplinas[disciplina] = {
                        'info': mensagem.get('info', {}),
                        'alunos': set()
                    }
                if 'id_usuario' in mensagem:
                    self.disciplinas[disciplina]['alunos'].add(mensagem['id_usuario'])
                return {
                    'status': 'sucesso',
                    'mensagem': 'Disciplina registrada',
                    'quantidade': len(self.disciplinas[disciplina]['alunos'])
                }
            
            elif acao == 'obter_info':
                disciplina = mensagem['disciplina']
                if disciplina in self.disciplinas:
                    return {
                        'status': 'sucesso',
                        'dados': self.disciplinas[disciplina]
                    }
                return {
                    'status': 'erro',
                    'mensagem': 'Disciplina não encontrada'
                }
            
            return {
                'status': 'erro',
                'mensagem': 'Ação desconhecida'
            }
            
        except KeyError as e:
            return {
                'status': 'erro',
                'mensagem': f'Campo obrigatório faltando: {str(e)}'
            }

    def _iniciar_servidor_udp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORTA_UDP))
            
            while self.executando:
                try:
                    dados, endereco = s.recvfrom(1024)
                    try:
                        mensagem = json.loads(dados.decode('utf-8'))
                        print(f"\nNotificação UDP de {endereco}: {mensagem.get('mensagem')}")
                    except:
                        print(f"\nNotificação UDP inválida de {endereco}")
                except:
                    break

if __name__ == '__main__':
    servidor = ServidorDisciplinas()
    servidor.iniciar()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor encerrado.")