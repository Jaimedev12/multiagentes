from flask import Flask, jsonify, request, send_file, make_response

from visualization import visualization
from Simulation import Simulation

from response_format.serializers.AgentAction import serialize_agent_action_to_json

app = Flask(__name__)

GRID_SIZE = 20
NUMBER_ROBOTS = 1
IN_BOXES_PER_MINUTE = 1
OUT_BOXES_PER_MINUTE = 1
NUM_STEPS = 100
robot_positions = list()
simulation = None

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
    global simulation
    try:
        simulation = Simulation(_N=GRID_SIZE, 
                                _M=GRID_SIZE, 
                                _num_robots=NUMBER_ROBOTS, 
                                _modo_pos_inicial='Fija', 
                                _num_steps=NUM_STEPS, 
                                _in_boxes_per_minute=IN_BOXES_PER_MINUTE, 
                                _out_boxes_per_minute=OUT_BOXES_PER_MINUTE, 
                                _robot_positions=robot_positions)
        simulation.start_simulation()
        return "Simulation started!"
    except Exception as e:
        print(e)
        response = make_response(jsonify({"error": "Simulation could not be started!"}), 500)
        return response
    
@app.route('/simulation-step/<int:index>', methods=['GET'])
def get_simulation_step(index):
    try:
        current_index = len(simulation.simulation_actions)-1

        if index > current_index:
            simulation.do_next_step()

        response_object = {
            "agent_actions": list(map(serialize_agent_action_to_json, simulation.simulation_actions[index])),
            "out_boxes_needed": simulation.out_boxes_needed_in_steps[index]
        }

        return jsonify(response_object)
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
    
@app.route('/change_params', methods=['POST'])
def change_params():
    global IN_BOXES_PER_MINUTE, OUT_BOXES_PER_MINUTE, NUM_STEPS
    try:
        data = request.get_json()
        IN_BOXES_PER_MINUTE = data["in_boxes"]
        OUT_BOXES_PER_MINUTE = data["out_boxes"]
        NUM_STEPS = data["num_steps"]
        return "Params received and processed successfully!"
    except Exception as e:
        print(e)
        response = make_response(jsonify({"error": "Failed to process params"}), 500)
        return response


if __name__ == '__main__':
    app.run(debug=True, port=8000)