import pytest
from langchain_core.documents import Document

from app.pipeline import chunker


def test_chunking_retorna_documentos():
    page = [
        Document(page_content="a" * 1200, metadata={"source": "https://x.com"}),
    ]
    out = chunker.chunking(page)
    assert len(out) >= 2
    assert all(isinstance(d, Document) for d in out)
    assert all(d.page_content for d in out)


def test_chunking_ignora_documento_vazio():
    page = [
        Document(page_content="   ", metadata={}),
        Document(page_content="hello world", metadata={}),
    ]
    out = chunker.chunking(page)
    assert len(out) >= 1


def test_chunking_sem_conteudo_util():
    page = [Document(page_content="   ", metadata={})]
    with pytest.raises(ValueError, match="No chunks"):
        chunker.chunking(page)
