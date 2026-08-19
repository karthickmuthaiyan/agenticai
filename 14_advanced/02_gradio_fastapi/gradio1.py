import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

def file_upload(file):
   return f"File {file.name} uploaded successfully!"
# return file content as text
   # return file.read().decode("utf-8")


demo = gr.Interface(fn=file_upload, inputs="file", outputs="text")
demo.launch()