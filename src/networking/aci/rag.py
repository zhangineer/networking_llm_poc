from pinecone import Pinecone, ServerlessSpec
import os
import time
from langchain.text_splitter import MarkdownHeaderTextSplitter
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import openai
from langchain_openai import OpenAIEmbeddings
from src.llm_api.utils.helper import register

load_dotenv((find_dotenv()))

openai.api_key = os.getenv('OPENAI_API_KEY')

# initialize pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY") or 'YOUR_API_KEY')

# pinecone.init(
#     api_key=os.getenv('PINECONE_API_KEY') or 'YOUR_API_KEY',
#     environment="asia-southeast1-gcp-free"
# )


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def embed_documents(text):
    response = openai.Embedding.create(input=text, engine="text-embedding-ada-002")
    return response['data'][0]['embedding']


def preprocess_document(file_path):
    # Read the markdown file, Langchain markdown loader did not work well for me
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    # Split the Markdown text into sections
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs = markdown_splitter.split_text(markdown_text)
    sections = [{"metadata": doc.metadata, "text": doc.page_content} for doc in docs]
    return sections

# Then we initialize the index.
# We will be using OpenAI's text-embedding-ada-002 model for creating the embeddings,
# so we set the dimension to 1536.
# when we are using the model, the embedding dimension needs to align the size of the vector that it outputs


def create_pinecone_index(index_name):
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=1536,
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            ),
            metric='cosine' # usually use cosine, there are instances where you might have to use euclidian or dot-product
        )
        # wait for index to finish initialization
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    return pc.Index(index_name)


def build_vector_db(index):
    documents = preprocess_document("chattynetworks/aci/example_docs/aci_standards.md")
    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    texts = [doc["text"] for doc in documents]
    metadata = [
        {
            "headers": '\n'.join(doc['metadata'].values()),
            "texts": doc["text"]
        }
        for doc in documents]
    ids = ['0', '1', '2', '3', '4']
    for _ in tqdm(range(0, len(documents))):
        embeds = embed_model.embed_documents(texts)
        index.upsert(vectors=zip(ids, embeds, metadata))


def query_vector_store(index, query):
    from langchain_pinecone import PineconeVectorStore

    text_field = "texts"  # the metadata field that contains our text
    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    # initialize the vector store object

    vectorstore = PineconeVectorStore(
        index, embed_model, text_field
    )

    # get top 3 results from knowledge base
    results = vectorstore.similarity_search(query, k=3)
    # get the text from the results
    source_knowledge = "\n".join([x.page_content for x in results])

    return source_knowledge


@register
def get_configuration_guideline(query):
    index = create_pinecone_index("aci-kb")
    context = query_vector_store(index, query)
    return f"""
    Think step by step when answering user query following the configuration guidelines
    If no guideline provided for a specific policy, do not proceed and let the user know a policy is missing
    
    
    Step 1. Follow system instruction
    Step 2. Follow additional instruction: \n{context}
    Step 3. Answer the query:\n \t{query}
    """


if __name__ == "__main__":
    index = create_pinecone_index("aci-kb")
    build_vector_db(index)