from flask import Flask, jsonify, request

def add_numbers(n1, n2):
    return n1 + n2

def create_app():
    app = Flask(__name__)
    
    @app.route('/add', methods=['POST'])
    def add_endpoint():
        data = request.get_json()
        result = add_numbers(data['num1'], data['num2'])
        return jsonify({'result': result})
        
    return app

def main():
    app = create_app()
    # Test the endpoint using requests library, not starting server here
    response = requests.post('http://localhost/add', json={'num1': 2, 'num2': 3})
    print(response.json())  # should print {'result': 5}