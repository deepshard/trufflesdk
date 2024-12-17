# Truffle SDK - Launch Day Preview
An early preview, and home for feedback, for the soon to be released SDK for the Truffle^1! 
This README and example app offer a taste of what creating agentic applications is like. 
We intend to let the voice of the community drive post-launch development

[Check out a sample app here!](https://github.com/deepshard/trufflesdk/blob/main/hisnameisyang.py)

### Overview

Apps for the Truffle are a 'toolbox in a sandbox', that is, they are a set of tools for our agentic models to use, running within an ephemeral Ubuntu ARM container. For the Python SDK, prequisite packages are automatically installed with the app.
When developing your app, you can run it locally on your computer, and the Truffle will call your local instance in the same fashion as it would if it was running on the device, making debugging and testing fairly simple and streamlined. 

The Python SDK works by parsing your tools into a gRPC server at runtime, generating a method handler, and Protobuf messages for each tool's arguments and return types respectively. 
While we're starting with Python, this approach means it's easy to extend the SDK such that any language can be used to create a Truffle App

Inside your application you are free to use the full power of our inference engine, access a vector datastore, request user input in the UI, and more! That means tools that use inference, tools that create files, tools that can do anything you dream up!  


### Tool Definitions
- Tools must take arguments and return values that can be expressed through base types
  - That is, they must be serializable! Nested objects that are all serializable are okay, but you can't pass an instance of a webserver as a function parameter for example!
  - Unfortunately, to make the magic happen, type annotations for parameters and return values are required, like `def MyTool(self, search_query: str, num_results: int) -> List[str]:` 
- Tools are marked by the `truffle.tool` decorator, which optionally can (and are highly encouraged to) have a description of the tool for the model, as well as an icon to display in the client, like `@truffle.tool("MyTool searches DuckDuckGo for relevant results")`
  - An additional decorator, `truffle.args`, can be used to add additional descriptions to each parameter to aid the model in using the tool, `@truffle.args(search_query='keywords or subjects to search for', num_results='the maximum number of results to return')`

- To assemble an app, you simply wrap these tools in a class
  - Any member variables of your app's class are automatically serialized and restored when an app is loaded or saved. This means you are safe to keep any state that persists between tools as a member variable, and can trust that it will be set as needed when your app is loaded back up after a reboot or device crash
    - Examples of persistant state include API keys, search history, etc.
  - One of the only hard requirements is that this class must also contain a member variable of the type, `truffle.AppMetadata`, with information about the app, namely:
    - Full name: A user facing name for the app
    - Description: A user facing description of the app. This is also used to generate synthetic data for live classification
    - Name: Internal app name
    - Goal: The purpose of the app. It is presented to the core mixture-of-models almost as a system prompt
    - Icon URL: The primary icon for the app. Must be 512x512 PNG

- There are built-in types that can be used to display information in special ways in the UI
  - `truffle.Code`
  - `truffle.TruffleFile`
    - This finds and attaches the file at the specified path alongside the tool's response

### Available APIs To Use Within Your Tools
This is one part we definitely want to hear your feedback on!
If you need something to build what you are dreaming of, let us know!

- General LLM Inference 
  - Fully featured with structured JSON schema output, temperature and sampling adjustment, and selecting from our range of models  
  - Synchronous and streaming generations
- Vision Model Inference
  - Same features as above, with optimizations for image interpretation and OCR tasks!
- Text Embeddings
  - Access raw embeddings of text up to ~32 thousand characters long and use our per-app key-value vector store
  - Per-app VecDB will be simplistic in query complexity, but still powerful
- User Requests
  - Need an API key for your tool? Directly send a message to the client from within a toolcall with this method!


### Feedback! 
- What do you need to build your Truffle app?
- Let us know in the issues page!

      
      
