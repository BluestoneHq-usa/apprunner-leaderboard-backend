from fastapi import FastAPI, HTTPException
import logging
import os
import redis
import json
import random

# Initialize FastAPI app
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("fastapi_app")

# Load Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "localhost")  # Default to localhost if not set

# Initialize Redis client
try:
    redis_client = redis.Redis(host=REDIS_URL, port=9000, db=0)
    redis_client.ping()  # Test connection
    logger.info("Connected to Redis successfully.")
except redis.ConnectionError as e:
    logger.error("Failed to connect to Redis. Ensure REDIS_URL is correct and Redis is running.")
    raise e


@app.get("/getdata")
async def get_data():
    try:
        # Fetch leaderboard data from Redis
        leaderboard_data = redis_client.get("leaderboard_data")
        if not leaderboard_data:
            logger.error("No leaderboard data found in Redis.")
            raise HTTPException(status_code=404, detail="Leaderboard data not found.")

        # Deserialize JSON data
        random_json = json.loads(leaderboard_data)

        # Randomly change player scores and sort
        for val in random_json:
            val["score"] = random.randint(1000, 3000)
        random_json.sort(key=lambda x: x["score"], reverse=True)

        # Assign ranks
        for rank, val in enumerate(random_json, start=1):
            val["id"] = rank

        logger.info(f"Response: {random_json}")
        return random_json

    except redis.RedisError as redis_err:
        logger.error(f"Redis error: {redis_err}")
        raise HTTPException(status_code=500, detail="Redis error occurred.")
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decoding error: {json_err}")
        raise HTTPException(status_code=500, detail="Invalid JSON format in leaderboard data.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
