from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import ConversationalRetrievalChain
import pandas as pd
from transformers import BartForConditionalGeneration, BartTokenizer
from bert_score import BERTScorer
import torch


def main():
    # Read the file and split the document into chunks
    pdf_reader = PyPDFLoader("./18642.pdf")
    documents = pdf_reader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,)
    chunks = text_splitter.split_documents(documents)

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2')
    db = FAISS.from_documents(documents=chunks, embedding=embeddings)

    # Calling the model
    eval_llm = Ollama(model="tinyllama")

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
        """ Given the following conversation and a follow up question, rephrase 
        the follow up question to be a standalone question.
        Chat History: {chat_history}
        Follow Up Input: {question}
        Standalone question: """
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm=eval_llm, 
        retriever=db.as_retriever(), 
        condense_question_prompt=CONDENSE_QUESTION_PROMPT, 
        return_source_documents=True, 
        verbose=False
    )

    # RAG Evaluation
    sample_queries = [
        {
            "question": "What are the three primary indicators used to measure a country's economic health?",
            "answer": "The three primary indicators are Gross Domestic Product (GDP), the inflation rate, and the unemployment rate.",
            "reference": "Economists typically monitor three key metrics: GDP (output), the Consumer Price Index or inflation (price stability), and the unemployment rate (labor market health)."
        },
        {
            "question": "How does a central bank use monetary policy to combat high inflation?",
            "answer": "Central banks typically increase interest rates to reduce the money supply and discourage spending, which helps lower inflation.",
            "reference": "To curb inflation, central banks employ contractionary monetary policy, primarily by raising the federal funds rate to increase the cost of borrowing."
        },
        {
            "question": "What is the difference between fiscal policy and monetary policy?",
            "answer": "Fiscal policy involves government spending and taxation, while monetary policy involves managing interest rates and the money supply by a central bank.",
            "reference": "Fiscal policy is determined by the government (taxing and spending), whereas monetary policy is the domain of the central bank (interest rates and money circulation)."
        },
        {
            "question": "Explain the concept of 'Comparative Advantage' in international trade.",
            "answer": "Comparative advantage is the ability of an economy to produce a particular good or service at a lower opportunity cost than its trading partners.",
            "reference": "The theory of comparative advantage suggests that countries should specialize in producing goods where they have the lowest opportunity cost, even if they lack an absolute advantage."
        },
        {
            "question": "What occurs during the 'contraction' phase of a business cycle?",
            "answer": "During a contraction, economic activity slows down, GDP declines, and unemployment typically rises, often leading to a recession.",
            "reference": "A contraction is a phase of the business cycle where the economy as a whole is in decline, characterized by falling real GDP and tightening credit conditions."
        }
    ]

    df = pd.DataFrame(sample_queries)

    retriever = db.as_retriever()

    def process_query(query):
        chat_history = []
        result = qa({"question": query, "chat_history": chat_history})
        relevant_docs = retriever.invoke(query)
        print(result['answer'])
        return result['answer'], relevant_docs

    # RAGAS Framework
    results = []
    for _, row in df.iterrows():
        question = row['question']
        ground_truth = row['answer']

        answer, relevant_docs = process_query(question)

        results.append({
            "user_input": question,
            "reference": ground_truth,
            "response": answer,
            "retrieved_contexts": [relevant_docs[0].page_content]
        })

    # Intialize the BART model and tokenizer
    bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

    # Intialize the BERTScorer
    bert_scorer = BERTScorer(lang="en", rescale_with_baseline=True)

    bert_scores = []
    bart_scores = []
    
    for item in results:
        inputs = bart_tokenizer(item["response"], truncation=True, padding=True, return_tensors="pt")
        with torch.no_grad():
            bart_score = bart_model(**inputs).logits
        bart_scores.append(bart_score.mean().item())

        P, R, F1 = bert_scorer.score([item["response"]], [item["reference"]])
        bert_scores.append(F1.numpy().mean())

    print("BERT Scores:", bert_scores)
    print("BART Scores:", bart_scores)

if __name__ == "__main__":
    main()