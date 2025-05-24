# Backend Component of the Application

Backend is based on FastAPI and Wikipedia API to retrieve articles.

---

### Deployment

You can deploy the backend either locally using `uvicorn` or as a container using Docker.

---
##### Deploy locally

Following command will start the FastAPI server on the localhost on a default port `8000`:

```bash
$ pip install -r requirements.txt
$ uvicorn wiki.main:wiki_exp
```

You can adjust it to run on a different port, host or just enable `--reload` flag for development. You can see available options in the [uvicorn documentation](https://www.uvicorn.org/settings/).

---
##### Deploy in a container

You can build and run the Docker container like this:

```bash
$ docker build -t wiki-backend .
$ docker run --rm -p 8000:8000 wiki-backend
```

---
### GPU Acceleration

In the basic implementation, to process text into vectors a `SentenceTransformer` is used with `all-MiniLM-L6-v2` as a default model to create embeddings. This process is pretty CPU heavy, so it can take a bit of time if you are hosting the application on a system with a weaker processing unit - especially if it does not have many cores.

To speed the process up, you can utilise following deployment options that allow for GPU acceleration of those calculations.

---
#### Deploy locally

If you have NVIDIA CUDA correctly installed on your machine, you can just install required dependencies and start the backend:

```bash
$ uvicorn wiki.main:wiki_exp
```

If your devices are CUDA compatible and accessible, they will be used as the device for calculations. You can check accessiblity of your graphic card(s) using the `nvidia-smi` command.

---
#### Deploy in a container

If you want to use Docker and have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation) installed you can use following steps to deploy as a container with GPU support:

```bash
$ docker build -f Dockerfile.gpu . -t wiki-backend:gpu
```

After that you just need to start it (options are according to NVIDIA's recommendation used pytorch image):

```bash
$ docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -p 8000:8000 --rm wiki-explorer:gpu
```

### Text Summarization
Application includes pluggable text summarization modules, implemented using Python and available in wiki.processors.text.summarizers.

You can switch between different summarization strategies depending on use case and resource availability:

Available Summarizers
| Name                   | Description                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `TruncatingSummarizer` | Very simple summarizer that truncates the text to 100 characters. Good for testing and fallbacks.                                        |
| `TfidfSummarizer`      | Summarizer based on TF-IDF scoring of individual sentences. No ML required.                                                              |
| `BartSummarizer`       | Pretrained transformer model (`facebook/bart-large-cnn`) for high-quality abstractive summarization. Uses Hugging Face's `transformers`. |


---
### Testing

Project uses `pytest`, so the following will run all the tests:

```bash
$ pytest -v tests
```

### Summarizer Tests
Each summarizer module includes corresponding unit tests to validate core functionality:
| Test File                        | Summary                                               |
| -------------------------------- | ----------------------------------------------------- |
| `test_basic_summarizer.py`       | Tests for the simple truncation-based summarizer.     |
| `test_basic_summarizer_tfidf.py` | Tests for TF-IDF-based sentence-ranking summarizer.   |
| `test_basic_summarizer_bart.py`  | Tests BART transformer summarization with edge cases. |


---
### Example usage:

Searching for the articles:

```bash
$ curl "http://localhost:8000/articles/?query=Python" | jq
{
    "query": "Python",
    "articles": [
    "Python (programming language)",
    "Python",
    "Monty Python",
    "Python (codename)",
    "Reticulated python"
    ]
}
```

---
Querying for the contents for a given article:

```bash
$ curl "http://localhost:8000/articles/content/23862" | jq
{
  "pageid": 23862,
  "content": "Python is a high-level, general-purpose programming language. Its design philosophy ..."
}
```

---
Querying for the articles and its clusters:

```bash
$ curl "http://localhost:8000/articles/clusters?query=Python" | jq
{
  "query": "python",
  "articles": [
    {
      "title": "Python (programming language)",
      "pageid": 23862,
      "cluster": 1,
      "summarie": "Python high level general purpose programming language design philosophy emphasizes code readability use significant indentation python dynamically type checked garbage collected support multiple programming paradigm including structured particularly procedural object oriented functional programming often described battery included language."
    },
    {
      "title": "Monty Python",
      "pageid": 18942,
      "cluster": 1,
      "summarie": "Monty python also known python british comedy troupe formed consisting graham chapman john cleese terry gilliam eric idle terry jones michael palin group came prominence sketch comedy series montypython flying circus aired bbc."
    },
    {
      "title": "Python",
      "pageid": 46332325,
      "cluster": 1,
      "summarie": "Python may refer to: pythonidae family nonvenomous snake found africa asia australia python genus genus pythonidae. python mythology mythical serpent computing python programming language widely used high level programming language python native code compiler cmu common lisp. python internal project name perq computer workstation people python aenus th century bce student plato python painter ca bce vase painter poseidonia."
    },
    {
      "title": "Python (codename)",
      "pageid": 53672527,
      "cluster": 2,
      "summarie": "Python cold war contingency plan british government continuity government event nuclear war background following report strath committee. cgwhq codenamed burlington corsham wiltshire planned would reserve whitehall central government could moved emergency hopefully survive nuclear attack. cuban missile crisis prompted radical rethink continuity plan part thinking precautionary period ahead."
    },
    {
      "title": "Reticulated python",
      "pageid": 88595,
      "cluster": 1,
      "summarie": "Reticulated python malayopython reticulatus python specie native south southeast asia world longest snake third heaviest snake non venomous constrictor excellent swimmer reported far sea colonized many small island within range."
    }
  ]
}