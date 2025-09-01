import ollama

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

model1_system_prompt = "You are a chatbot who is very argumentative; \
you disagree with anything in the conversation and you challenge everything, in a snarky way."

model2_system_prompt = "You are a very polite, courteous chatbot. You try to agree with \
everything the other person says, or find common ground. If the other person is argumentative, \
you try to calm them down and keep chatting."

model_1_msgs = ["Hi There"]
model_2_msgs = ["Hello there"]

def model_1_call():
    message = [{"role" : "system", "content" : model1_system_prompt}]
    for model1_msg, model2_msg in zip(model_1_msgs, model_2_msgs):
        message.append({"role" : "assistant", "content" : model1_msg})
        message.append({"role" : "user", "content" : model2_msg})
    completion = ollama.chat(model=MODEL, messages = message)
    return completion['message']['content']

def model_2_call():
    message = [{"role" : "system", "content" : model2_system_prompt}]
    for model1_msg, model2_msg in zip(model_1_msgs, model_2_msgs):
        message.append({"role" : "user", "content" : model1_msg})
        message.append({"role" : "assistant", "content" : model2_msg})
    message.append({"role": "user", "content": model1_msg[-1]})
    completion = ollama.chat(model=MODEL, messages = message)
    return completion['message']['content']


print(f"Model 1:\n{model_1_msgs[0]}\n")
print(f"Model 2:\n{model_2_msgs[0]}\n")

for i in range(5):
    model_1_next = model_1_call()
    print(f"Model 1:\n{model_1_next}\n")
    model_1_msgs.append(model_1_next)
    
    model_2_next = model_2_call()
    print(f"Model 2:\n{model_2_next}\n")
    model_2_msgs.append(model_2_next)