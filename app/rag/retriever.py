from app.config.constants import KWARGS

def build_retriever(vectorstore):
    return vectorstore.as_retriever(
        search_kwargs={"k": KWARGS}
    )

