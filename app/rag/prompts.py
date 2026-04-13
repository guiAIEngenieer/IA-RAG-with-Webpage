from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Respond according to the language used in the user's prompt and according to the provided context and chat history.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Context: {context}\nQuestion: {query}"),
    ]
)
