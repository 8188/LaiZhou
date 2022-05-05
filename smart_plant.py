from app import create_app
from gevent import pywsgi

app = create_app()
    
if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    pywsgi.WSGIServer(('0.0.0.0', 8990), app).serve_forever()
