from flask import Flask, jsonify, request, send_file, make_response
from visualization import visualization
from Simulation import Simulation

from response_format.serializers.AgentAction import serialize_agent_action_to_json

app = Flask(__name__)

GRID_SIZE = 20
NUMBER_ROBOTS = 1
simulation_array = list()
robot_positions = list()

@app.route('/hello-world', methods=['GET'])
def hello():
    return "Hello world!"

@app.route('/start-visualization', methods=['GET'])
def start_visualization():
    try:
        visualization.launch(open_browser=True)
        return "Visualization started!"
    except:
        response = make_response(jsonify({"error": "Visualization could not be started!"}), 500)
        return response
    
@app.route('/start-simulation', methods=['GET'])
def start_simulation():
    global simulation_array
    try:
        simulation = Simulation(GRID_SIZE, GRID_SIZE, NUMBER_ROBOTS, 'Fija', 50, robot_positions)
        simulation.execute_simulation()
        simulation_array = simulation.simulation_actions
        return "Simulation started!"
    except Exception as e:

        print(e)
        response = make_response(jsonify({"error": "Simulation could not be started!"}), 500)
        return response
    
@app.route('/simulation-step/<int:index>', methods=['GET'])
def get_simulation_step(index):
    try:
        return list(map(serialize_agent_action_to_json, simulation_array[index]))
    except Exception as e:
        print(e)
        response = make_response(jsonify({"msg": "Error when trying to get the simulation step"}), 500)
        return response
    
@app.route('/set_positions', methods=['POST'])
def set_positions():
    global robot_positions
    try:
        data = request.get_json()
        # print(data["positions"])
        robot_positions = data["positions"]
        return "Positions received and processed successfully!"
    except Exception as e:
        print(e)
        response = make_response(jsonify({"error": "Failed to process positions"}), 500)
        return response

if __name__ == '__main__':
    app.run(debug=True, port=8000)