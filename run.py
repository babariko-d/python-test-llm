from dotenv import load_dotenv
from flask import Flask
from controller.ask import ask_controller
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "Ask LLM API",
        "description": "Ask LLM API",
        "version": "1.0"
    }
}
app.config['SWAGGER'] = {
    'title': 'Ask LLM API',
    'uiversion': 2,
    'template': './resources/flasgger/swagger_ui.html'
}
Swagger(app, template=template)

if __name__ == '__main__':
    app.register_blueprint(ask_controller)
    app.run(host="0.0.0.0", threaded=True)