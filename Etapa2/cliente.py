from config import HOST, PORTA_TCP, PORTA_UDP
import socket
import json
from datetime import datetime
import argparse

class ClienteUsuario:
    def __init__(self, id_usuario):
        self.id_usuario = id_usuario
    
    def _enviar_tcp(self, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((HOST, PORTA_TCP))
                s.sendall(json.dumps(mensagem).encode('utf-8'))
                
                resposta = s.recv(1024)
                if resposta:
                    return json.loads(resposta.decode('utf-8'))
                return {'status': 'erro', 'mensagem': 'Resposta vazia'}
                
        except json.JSONDecodeError:
            return {'status': 'erro', 'mensagem': 'Resposta inválida'}
        except socket.timeout:
            return {'status': 'erro', 'mensagem': 'Timeout'}
        except Exception as e:
            return {'status': 'erro', 'mensagem': f'Erro: {str(e)}'}
    
    def registrar_disciplina(self, disciplina, info):
        print(f"\nUsuário {self.id_usuario} registrando em {disciplina}...")
        resposta = self._enviar_tcp({
            'acao': 'registrar',
            'disciplina': disciplina,
            'info': info,
            'id_usuario': self.id_usuario
        })
        print(f"Resposta: {resposta}")
        return resposta
    
    def obter_info_disciplina(self, disciplina):
        print(f"\nUsuário {self.id_usuario} consultando {disciplina}...")
        resposta = self._enviar_tcp({
            'acao': 'obter_info',
            'disciplina': disciplina
        })
        print(f"Resposta: {resposta}")
        return resposta
    
    def enviar_alerta(self, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(json.dumps({
                    'id_usuario': self.id_usuario,
                    'mensagem': mensagem,
                    'timestamp': datetime.now().isoformat()
                }).encode('utf-8'), (HOST, PORTA_UDP))
            print(f"\nUsuário {self.id_usuario} enviou alerta: {mensagem}")
            return True
        except Exception as e:
            print(f"\nErro ao enviar alerta: {str(e)}")
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cliente para sistema de disciplinas')
    parser.add_argument('--id', type=int, required=True, help='ID do usuário')
    parser.add_argument('--acao', choices=['registrar', 'consultar', 'notificar'], required=True)
    parser.add_argument('--disciplina', help='Nome da disciplina')
    parser.add_argument('--mensagem', help='Mensagem para notificação')
    
    args = parser.parse_args()
    
    cliente = ClienteUsuario(args.id)
    
    if args.acao == 'registrar':
        if not args.disciplina:
            print("Erro: --disciplina é obrigatório para registrar")
            exit(1)
        cliente.registrar_disciplina(args.disciplina, {})
    elif args.acao == 'consultar':
        if not args.disciplina:
            print("Erro: --disciplina é obrigatório para consultar")
            exit(1)
        cliente.obter_info_disciplina(args.disciplina)
    elif args.acao == 'notificar':
        if not args.mensagem:
            print("Erro: --mensagem é obrigatória para notificar")
            exit(1)
        cliente.enviar_alerta(args.mensagem)