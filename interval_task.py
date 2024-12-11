 
from uagents import Agent, Context
import requests
 
# Create an agent named Alice
batching_agent = Agent(name="BatchingAgent", seed="Batching_model", port=8000, endpoint=["http://localhost:8000/submit"])
 
accumulated_data = []
 
source_url = "http://example.com/get-single-data"
target_url = "http://example.com/send-batch-data"

def get_data():
    try:
        response = requests.get(source_url)
        if response.status_code == 200:
            return response.json()  
        else:
            return {"Heart_rate": 0, "timestamp": "Unknown"}
    except Exception as e:
        return {"Heart_rate": 0, "timestamp": "Error fetching data"}

def send_accumulated_data(data):
    try:
        response = requests.post(target_url, json={"data": data})
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False
    
@batching_agent.on_interval(period=1.0)
async def accumulate_heart_rate_data(ctx: Context):
    accumulated_data = ctx.storage.get("accumulated") or []
    
    data = get_data()  # Example heart rate data
    
    # Accumulate data every second
    accumulated_data.append(data)
    ctx.storage.set("accumulated", accumulated_data)
    ctx.logger.info(f"Accumulated heart rate data: {data}")
    
    # If we've accumulated data for 60 seconds, process and reset
    if len(accumulated_data) >= 60:
        ctx.logger.info(f"Accumulated data for the past 60 seconds: {accumulated_data}")
        
        if send_accumulated_data(accumulated_data):
            ctx.logger.info(f"Successfully sent accumulated data to {target_url}")
        else:
            ctx.logger.error(f"Failed to send accumulated data to {target_url}")
        # Reset accumulated data after processing
        ctx.storage.set("accumulated", [])
        
# Run the agent
if __name__ == "__main__":
    batching_agent.run()
 
 
 