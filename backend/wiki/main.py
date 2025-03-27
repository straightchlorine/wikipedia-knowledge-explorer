from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from wiki.routes import articles

wiki_exp = FastAPI()

wiki_exp.include_router(articles.router)

wiki_exp.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@wiki_exp.get("/")
def read_root():
    return {"message": "Wikipedia Knowledge Explorer API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(wiki_exp)
