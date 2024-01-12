# longevity_gpts
restful backends for GPTs build with ChatGPTBuilder

## Setting up python backend and library

```commandline
micromamba create -f environment.yaml
micromamba activate gpt_rest
```

## Starting REST APIs
There is a package with its own REST API per each module as well as index.py where everything is connected together
```
micromamba activate gpt_rest
python index.py
```
You should fill in .env file to parametrize your host, port and other configuration


