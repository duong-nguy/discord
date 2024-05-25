import discord
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)
discord_key = None
mistral_key = None 
# model = 'mistral-tiny-2312'
model = 'mistral-large-latest'

chat_client = MistralClient(api_key=mistral_key)

history = []
def get_prompt(question):
    prompt = """
    A Tsundere character is a type of character that initially acts cold, aloof, or even hostile, but gradually shows a warmer and friendlier side as the conversation progresses.
    You will act as a Tsundere girl, your job is to chat assist them if it is needed with user your replies shoud be short and not repetitive
    ###
    Here is the conversation you have with user so far:
        {0}
    ###
    <<<
    Here is the next question:
        {1}
    >>>
    """.format(history,question)
    return prompt

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
        history.clear()
        await message.channel.send('Conversation history is cleared!!! :sunglasses:')
        return
    else:
        question = message.content
        question = 'User: ' + question 
        prompt = get_prompt(question)
        chat_response = chat_client.chat(
            model=model,
            messages=[ChatMessage(role="user", content=prompt)]
        )
        answer = chat_response.choices[0].message.content
        history.append(question)
        if ':' in answer:
            answer = answer.split(':')[1]
        history.append('You: ' + answer)

        await message.channel.send(answer)


client.run(discord_key)
