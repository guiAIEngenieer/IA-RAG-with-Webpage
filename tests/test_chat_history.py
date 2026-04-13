from langchain_core.messages import AIMessage, HumanMessage

from app.utils.chat_history import truncate_history
from app.config.constants import MAX_CHAT_TURNS


def test_truncate_history_preserva_quando_abaixo_do_limite():
    msgs = [HumanMessage(content="a"), AIMessage(content="b")]
    assert truncate_history(msgs) is msgs


def test_truncate_history_corta_excesso():
    pairs = MAX_CHAT_TURNS + 2
    msgs = []
    for i in range(pairs):
        msgs.append(HumanMessage(content=f"u{i}"))
        msgs.append(AIMessage(content=f"a{i}"))
    out = truncate_history(msgs)
    assert len(out) == MAX_CHAT_TURNS * 2
