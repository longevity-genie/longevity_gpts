# longevity_gpts
restful backends for GPTs build with ChatGPTBuilder and also for huggingface UI

## Setting up python backend and library

```commandline
micromamba create -f environment.yaml
micromamba activate longevity_gpts
```

## Starting REST APIs
There is a package with its own REST API per each module as well as index.py where everything is connected together
```
python rest_endpoint.py
```
You should fill in .env file to parametrize your host, port and other configuration

## Strarting openai like API
You could use tools with openai like api. It is usefull when you use LLM chats like huggingface chatua or librechat.
```
python openai_api_endpoint.py
```
This endpoint uses its endpoint_options.yaml file for configurations. It takes the model as a key and then applies all the parameters in litellm call. 
The required parameters are model and system_prompt. system_prompt is the name of the file in the prompts folder with system prompt. key_getter is the file name for a list of keys.

## Installing packages locally

If it complains on non-finding local packages do:

```
pip install -e .
```

It will also dynamically react to all your code updates in submodules.


## Database download

gene_lookup will not work without disgenet_2020.sqlite database. You should download it from https://www.disgenet.org/downloads and put it in genetics/data folder.


