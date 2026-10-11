from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os 

def get_llm():
    return ChatGoogleGenerativeAI(model = "gemini-2.5-flash", google_api_key = os.getenv("GOOGLE_API_KEY"),temperature=0.3)


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 3000,
        chunk_overlap = 200
    )

    return splitter.split_text(transcript)

def summarize(transcript : str) -> str:
    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}"),
    ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    # chunk_summaries = [map_chain.invoke({"text" : chunk}) for chunk in chunks]
    chunk_summaries = []

    for i, chunk in enumerate(chunks, start=1):
        try:
            print(f"Summarizing chunk {i}/{len(chunks)}...")
            summary = map_chain.invoke({"text": chunk})
            chunk_summaries.append(summary)

        except Exception as e:
            print(f"Warning: Could not summarize chunk {i}: {e}")
            chunk_summaries.append(
                chunk[:1000] + "\n[AI summary unavailable for this section]"
            )

    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            "You are an expert meeting summarizer. Combine these partial summaries "
            "into one final professional meeting summary in bullet points.",
        ),
        ("human", "{text}"),
    ]
    )

    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | combined_prompt | llm | StrOutputParser()
    )

    return combined_chain.invoke(combined)

# def generate_title(transcipt : str) -> str:

    llm = get_llm()

    

    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | 
        ChatPromptTemplate.from_messages([
             (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        |StrOutputParser()
    )

    return title_chain.invoke(transcipt[:2000])


def generate_title(transcript: str) -> str:
    # Fallback title if Mistral is unavailable
    fallback_title = "Meeting Summary"

    if not transcript or not transcript.strip():
        return fallback_title

    try:
        llm = get_llm()

        title_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Generate a short professional title based on the transcript. "
                "Use a maximum of 8 words. Return only the title."
            ),
            ("human", "{text}"),
        ])

        title_chain = title_prompt | llm | StrOutputParser()

        title = title_chain.invoke({
            "text": transcript[:2000]
        })

        return title.strip() or fallback_title

    except Exception as e:
        print(f"Warning: Could not generate AI title: {e}")
        print("Using fallback title instead.")
        return fallback_title


