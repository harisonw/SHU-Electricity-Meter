import time
from uuid import uuid4
import random 
from parameters import ACCOUNTS_DATA, BLOCKCHAIN_URL, CONTRACT_ABI, CONTRACT_ADDRESS
from web3 import Web3

grid_alerts = [
    "High power usage detected in your area. Please reduce consumption if possible.",
    "Scheduled maintenance: Expect power interruptions from 2:00 PM to 4:00 PM.",
    "Unusual voltage fluctuation detected. Your smart meter is monitoring the situation.",
    "Demand response event: Please conserve energy during peak hours (4:00 PM - 8:00 PM).",
    "Grid overload warning: Immediate reduction in power usage is requested.",
    "Emergency alert: Power outage detected in your vicinity. Restoration is underway.",
    "Your current energy usage has exceeded the set threshold. Consider adjusting usage.",
    "Critical grid event: Temporary load-shedding may occur to stabilize supply.",
    "Renewable energy surplus detected. You may benefit from shifting usage now.",
    "Safety alert: Your smart meter has detected a potential electrical hazard. Please contact support."
]

def select_random_alert():
    index = random.randint(0, len(grid_alerts)-1)
    return grid_alerts[index]


def send_alert(contract):
    select_random_alert_text = select_random_alert()
    print(f"Alert: {select_random_alert_text}")
    contract_instance.functions.sendGridAlert(
        select_random_alert_text
    ).transact({"from": example_address})


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    example_address = Web3.to_checksum_address(list(ACCOUNTS_DATA["addresses"])[1])
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    while True:
        random_sleep_interval = random.randint(10,60)
        send_alert(contract_instance)
        time.sleep(random_sleep_interval)
