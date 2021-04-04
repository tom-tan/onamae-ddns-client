#!/usr/bin/env python2
import os
import socket
import ssl
import urllib2

from collections import defaultdict
from textwrap import dedent

class OnamaeDDNSError(Exception):
    """Error in the interaction with DDNS server.
    
    Note that the server may response with error due to the previous command.
    This class shows the reason of the error based on its error code rather than
    the command for which the server returns the error.

    If it cannot guess the reason from the error code,
    it uses user-specified error message.
    """
    def __init__(self, response, message):
        code = response.split("\n")[0]
        reason = None
        if code == '002 LOGIN ERROR':
            reason = 'Failed to login'
        elif code == '003 DBERROR':
            reason = 'Failed to modify IP address'
        else:
            reason = message
        super(OnamaeDDNSError, self).__init__("%s: %s" % (reason, code))

def get_global_ip():
    url = 'https://ifconfig.me'
    try:
        res = urllib2.urlopen(url, timeout = 5)
        return res.read()
    except urllib2.URLError as e:
        print(e)
        raise Exception("%s: %s" % (e.reason, url))

def read_env(file):
    ret = defaultdict(str)
    with open(file) as f:
        for l in f.readlines():
            k, v = l.rstrip().split('=')
            if len(v):
                ret[k] = v
    return ret

def connect(sock, server, port):
    sock.connect((server, port))
    return sock.recv(1024)

def send_command(sock, cmd):
    sock.sendall(dedent(cmd)[1:])
    return sock.recv(1024)

def login(sock, env):
    cmd = '''
        LOGIN
        USERID:%s
        PASSWORD:%s
        .
        ''' % (env['USERID'], env['PASSWORD'])
    return send_command(sock, cmd)

def modip(sock, env, ip):
    cmd = '''
        MODIP
        HOSTNAME:%s
        DOMNAME:%s
        IPV4:%s
        .
        ''' % (env['HOSTNAME'], env['DOMNAME'], ip)
    return send_command(sock, cmd)

def logout(sock):
    cmd = '''
        LOGOUT
        .
        '''
    return send_command(sock, cmd)

def enforce_success_response(res, msg):
    r = res.decode()
    if '000 COMMAND SUCCESSFUL' not in r:
        raise OnamaeDDNSError(r[:-3], msg)

def update_domain_ip(env, ip):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(5)
        sslsock = ssl.wrap_socket(sock)

        server, port = "ddnsclient.onamae.com", 65010
        res = connect(sslsock, server, port)
        enforce_success_response(res, "Failed to connect")

        res = login(sslsock, env)
        enforce_success_response(res, "Failed to login")

        res = modip(sslsock, env, ip)
        enforce_success_response(res, "Failed to modify IP address")
        
        res = logout(sslsock)
        enforce_success_response(res, "Failed to logout")
    finally:
        if sock is not None:
            sock.close()

if __name__ == '__main__':
    try:
        env_file = '.env'
        if not os.path.exists(env_file):
            print('File not found: %s' % env_file)
            exit(1)

        env = read_env(env_file)
        ip = get_global_ip()
        update_domain_ip(env, ip)
    except Exception as e:
        print(e)
        exit(1)
