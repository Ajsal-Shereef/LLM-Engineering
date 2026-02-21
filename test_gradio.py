import gradio as gr
def echo(message, history):
    print("message:", type(message), message)
    print("history:", type(history), len(history))
    if len(history) > 0:
        print("history[0]:", type(history[0]), history[0])
    return message
app = gr.ChatInterface(echo)
# We can't launch and test interactively easily, so let's just inspect the signature of ChatInterface in Gradio 5
