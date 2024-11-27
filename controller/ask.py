from flask import request, Response, Blueprint
from service.issue import ask_about_issue
from flasgger import swag_from

ask_controller = Blueprint('ask', __name__)

@ask_controller.route("/ask", methods=['GET'])
@swag_from("../docs/ask.yml")
def ask():
    question = request.args.get("question")

    if question == None:
        return Response(response="No question", status=400)
    
    try:
        response = ask_about_issue(question)

        return Response(response=f"{response}\n" if response else "No response", status=200)
    except Exception as e:
        print(e)
        return Response(response="Error occured", status=200)
    


