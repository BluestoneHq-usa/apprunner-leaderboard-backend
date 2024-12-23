from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)

# Update the Redis connection parameters
r = redis.Redis(host=os.getenv('REDIS_URL'), port=6379, db=0) # type: ignore

@app.route('/getdata')
def get_data():
    try:
        leaderboard_data = r.get('leaderboard_data')
        if leaderboard_data:
            return leaderboard_data.decode('utf-8'), 200  # Decode bytes to string
        else:
            return "No data found", 404
    except redis.ConnectionError as e:
        return str(e), 500

@app.route('/setdata', methods=['POST'])
def set_data():
    try:
        # Get JSON data from the request
        data = request.json
        if 'leaderboard_data' not in data:
            return jsonify({"error": "No 'leaderboard_data' key provided"}), 400

        # Set the data in Redis
        r.set('leaderboard_data', data['leaderboard_data'])
        return jsonify({"message": "Data set successfully"}), 200
    except redis.ConnectionError as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
