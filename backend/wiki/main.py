from fastapi import FastAPI
from wiki.routes import articles

wiki_exp = FastAPI()

wiki_exp.include_router(articles.router)


@wiki_exp.get("/")
def read_root():
    return {"message": "Wikipedia Knowledge Explorer API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(wiki_exp)
