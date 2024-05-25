import requests
import json
import uuid
import datetime

import discord



intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)
discord_key = None


messages= []

def save_assistant_response(response):
    message = {
            "id": response['id'],
            "content": response['finalContent'],
            "role": "assistant",
            "created": response['created']
            }
    messages.append(message)

def  save_user_response(content):
    now = datetime.datetime.utcnow()
    formatted_time = now.isoformat(sep='T', timespec='microseconds') + 'Z'
    message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "role": "user",
            "created": formatted_time, 
            }
    messages.append(message)



def process_streaming_response(response,debug):
    accumulated_content = ""
    for line in response.iter_content(1024):  # Adjust chunk size as needed
        if not line:  # Check for end of stream
            break
        decoded_line = line.decode('utf-8')  # Decode bytes to string
        accumulated_content += decoded_line 
    accumulated_content = [s.replace("data: ", "") for s in accumulated_content.split("\n") if s.strip()]
    

    if debug:
        return accumulated_content
    json_data = [json.loads(s) for s in accumulated_content][-1]

    if "Izzy:" in json_data["finalContent"]:
        json_data["finalContent"] = json_data["finalContent"].split("Izzy:")[1]

    return json_data 

def make_request(debug=False):
    url = 'https://api.figgs.ai/chat_completion'
    cookie = None
    headers = {
        'User-Agent': None,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.figgs.ai/',
        'Content-Type': 'application/json',
        'Origin': 'https://www.figgs.ai',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'TE': 'trailers'
        }
    data = {
            "messages": messages,
            "personality": None,
            "personaId":None,
            "scenario": None,
            "firstMessage": None,
            "description": None,
            "name": None,
            "exampleDialogs": None,
            "previousMessagesVersion": [],
            "botId": None,
            "roomId":None 
            }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return process_streaming_response(response,debug)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('$'):
        return

    elif message.content.startswith('/reboot'):
        messages.clear()
        await message.channel.send('Conversation history is cleared!!! :sunglasses:')
        return

    elif message.content.startswith('/debug'):
        content = message.content.split("/debug")[-1]
        save_user_response(content)
        response = make_request(debug=True)
        await message.channel.send(response)

    else:
        content = message.content
        save_user_response(content)
        response = make_request()
        save_assistant_response(response)
        await message.channel.send(response['finalContent'])
        return

client.run(discord_key)

