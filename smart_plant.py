from app import create_app
from gevent import pywsgi, monkey
from config import Config

app = create_app()
 
if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    monkey.patch_all()
    http_server = pywsgi.WSGIServer((Config.WSGI_HOST, Config.WSGI_PORT), app)
    http_server.serve_forever()
