# Truffle SDK - Launch Day Preview
An early preview, and home for feedback, for the soon to be released SDK for the Truffle! 
This README and example app offer a taste of what creating agentic applications is like. 
We intend to let the voice of the community drive post-launch development

[Check out a sample app here!](https://github.com/deepshard/trufflesdk/blob/main/hisnameisyang.py)

### Overview

Apps for the Truffle are a 'toolbox in a sandbox', that is, they are a set of tools for our agentic models to use, running within an ephemeral Ubuntu ARM container. For the Python SDK, prequisite packages are automatically installed with the app.
When developing your app, you can run it locally on your computer, and the Truffle will call your local instance in the same fashion as it would if it was running on the device, making debugging and testing fairly simple and streamlined. 

The Python SDK works by parsing your tools into a gRPC server at runtime, generating a method handler, as well as Protobuf messages for each tool's arguments and return types respectively. 
This means that any language can be used to create a Truffle App, and we hope to listen to what early-users want for expanding the SDK's support outside of Python.

Inside your application you are free to use the full power of our inference engine, access a vector datastore, request user input in the UI, and more! That means tools that use inference, tools that create files, tools that can do anything you dream up!  


### Tool Definitions
- Tools must take arguments and return values that can be expressed through base types
  - That is, they must be serializable! Nested objects that are all serializable are okay, but you can't pass like an instance of a webserver as a function parameter!
  - Unfortunately, to make the magic happen, we need type annotations for parameters and return values as well, like `def MyTool(self, search_query: str, num_results: int) -> List[str]:` 
- Tools are marked by the `truffle.tool` decorator, which optionally can (and are highly encouraged to) have a description of the tool for the model, as well as a icon to display in the client, like `@truffle.tool("MyTool searches DuckDuckGo for relevant results")`
  - the additional decorator, `truffle.args` can be used to add additional descriptions to each parameter to aid the model in using the tool, `@truffle.args(search_query='keywords or subjects to search for', num_results='the maximum number of results to return')`

- Wrapping these tool definitions in a class is how you assemble your app as a whole
  - any member variables of your app's class will be automatically serialized and restored when an app is loaded or saved
  - This means you are safe to keep any state that persists between tools as a member variable, and can trust that it will be set as needed when you app is loaded back up after a reboot for example.
    - examples of persistant state include API keys, search history, etc.
  - One of the only hard requirements is that this class must also contain a member variable of the type, `truffle.AppMetadata`, with various information about the app

- Some built-in types, like `truffle.Code` or `truffle.TruffleFile` are available to use as return types, acting as a hint for the SDK for how to display the return value to the user
  - for example `TruffleFile` causes to find and attach the file at the specified path with the tool's response

### Available APIs To Use Within Your Tools
This is one part we definitely want to hear your feedback on!
If you need something to build what you are dreaming of, let us know how we can help provide!

- General LLM Inference 
  - Fully featured with structured JSON schema output, tuning things like temperature and sampling, and selecting from our range of models  
  - synchronous and streaming generations
- Vision Model Inference
  - Same features as above, with optimizations for image interpretation and OCR tasks!
- Text Embeddings
  - Access raw embeddings of text up to ~32 thousand characters long, or use our per-app key-value vector store
  - Per-app VecDB will be simplistic in query complexity, but still powerful
  - Let us know if further expansion on embeddings and semantic search/storage should be a priority!
- Respond to user
  - Need an API key for your tool? Directly send a message to the client from within a toolcall with this method!


### Feedback! 
- What do you need to build your Truffle app?
- Let us know in the issues page!
- 

      
      
