# About
This repo contains the utils for nlmatics projects. Any modules/funcs used across two repos should be listed here.

## model_client
This module provides clients to access nlp models from model server.

### EncoderClient with DPR
```
from nlm_utils.model_client import EncoderClient
model_server_url = <suppy model server url>
encoder = EncoderClient(
    model="dpr-context",
    url=model_server_url,
)
encoder(["sales was 20 million dollars"])

from nlm_utils.model_client import EncoderClient
model_server_url = <suppy model server url>
encoder = EncoderClient(
    model="dpr-question",
    url=model_server_url,
)
encoder(["how much was sales"])
```
### EncoderClient with SIF
```
from nlm_utils.model_client import EncoderClient
model_server_url = <suppy model server url>
encoder = EncoderClient(
    model="sif",
    url=model_server_url,
)
encoder(["sales was 20 million dollars"])
```

### ClassificationClient used to get possible answer type of a qa
```
from nlm_utils.model_client.classification import ClassificationClient
model_server_url = <suppy model server url>
qa_type_client = ClassificationClient(
    model="roberta",
    task="qa_type",
    url=serverUrl,
    retry=1,
)
qa_type_client(["What is the name of the company"])
```
returns
```
{'predictions': ['HUM:gr']}
```


### ClassificationClient used for QA
```
from nlm_utils.model_client.classification import ClassificationClient
model_server_url = <suppy model server url>
qa_client = ClassificationClient(
    model='roberta',
    task="roberta-qa",
    host=model_server_url,
    port=80,
)
qa_client(["wht is the listing symbol of common stock or shares"], ["Our common stock is listed on the NYSE under the symbol 'MSFT'."])
```
returns
```
{'answers': [{'0': {'end_byte': 60,
    'end_logit': 16,
    'probability': 0.9999986487212269,
    'start_byte': 57,
    'start_logit': 14,
    'text': 'MSFT'}},
  {}]}
```

### ClassificationClient used for boolean (yes/no) question answering
```
from nlm_utils.model_client.classification import ClassificationClient
model_server_url = <suppy model server url>
boolq_client = ClassificationClient(
    model="roberta",
    task="boolq",
    url=model_server_url,
    retry=1,
)
sentences = ["it is snowing outside"]
question = ["is it snowing"]
boolq_client(question, sentences)
```
returns
```
{'predictions': ['True']}
```

## lazy cache
This module provides lazy cache for different types of data.
Cache can be configured to saved to different stroage
- Files
- Memory
- Redis
- MongoDB
- Google Cloud (planning)

Usage
```
# import Cache module
from nlm_utils.cache import Cache

# init cache with FileAgent
cache = Cache("FileAgent")

# apply cache on function
@cache
def func1(args):
    pass

# specify cache_key
func1(args, cache_key="cache_key")
# force_overwrite_cache
func1(args, overwrite=True)
# do not read and write cache
func1(args, no_cache=True)
```
### cache agent
Currently, cache support following agents
```
# file
cache = Cache("FileAgent", path=".cache", collection="collection")

# memory
cache = Cache("MemoryAgent", prefix="prefix")

# Mongodb
cache = Cache("MongodbAgent", db="cache", collection="cache")

# Redis
cache = Cache("RedisAgent", prefix="collection")
```

### Key for the cache
By default, cache layer will detect the arguments and generate the cache automaticly.
You can also specify the `cache_key` or include `uid` as a attribute in the argument.
The cache can be force overwrite by passing in `overwrite` argument.

Cache will also block the I/O if writing cache is happening (lock) -- planning



## utils (planning)
Functions can be shared across multiple repos.
- read_config(config_file)

## Credits 2020-2024
The code was written by the following while working at Nlmatics Corp.
- The initial skeleton and model clients were written by Suhail Kandanur.
- Reshav Abraham wrote the nlp_client.
- Yi Zhang refactored the code and created the core framework.
- Ambika Sukla wrote the value parser added code and prompts for flan-t5, encoder and openai models. 
- Tom Liu wrote yolo client and made several bug fixes.
- Kiran Panicker wrote the location parser, search summarization prompts for openai and made several bug fixes.
