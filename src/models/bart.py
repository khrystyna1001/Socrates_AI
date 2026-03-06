from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.documents import Document
import pandas as pd
from transformers import BartForConditionalGeneration, BartTokenizer
from bert_score import BERTScorer
import torch
import psycopg2
import os

class BARTRAGSystem:
    def __init__(self, pdf_path="../sources", embedding_model='sentence-transformers/all-MiniLM-L6-v2', 
                 llm_model="tinyllama", bart_model="facebook/bart-large-cnn"):
        self.pdf_path = pdf_path
        self.embedding_model_name = embedding_model
        self.llm_model_name = llm_model
        self.bart_model_name = bart_model
        self.db = None
        self.qa_chain = None
        self.bart_model = None
        self.bart_tokenizer = None
        self.bert_scorer = None

    def get_documents(self):
        """Fetch PDF content from PostgreSQL and convert to LangChain Documents."""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set.")

        documents = []
        try:
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            query = "SELECT filename, content_text, page_number FROM pdf_documents;"
            cur.execute(query)
            rows = cur.fetchall()

            documents = []
            for filename, content, page_num in rows:
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename, 
                        "page": page_num\
                    }
                )
                documents.append(doc)

            cur.close()
            conn.close()
            

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            return chunks

        except Exception as e:
            raise RuntimeError(f"Error fetching documents from database: {str(e)}")

    def create_embeddings_and_vector_db(self, chunks):
        """Create embeddings and build FAISS vector database."""
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.db = FAISS.from_documents(documents=chunks, embedding=embeddings)
        return self.db

    def setup_rag_chain(self):
        """Initialize the RAG conversation chain."""
        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        eval_llm = OllamaLLM(
            model=self.llm_model_name, 
            base_url=ollama_base_url if ollama_base_url else None
        )
        
        # NEW: Specific instructions for the response structure
        QA_PROMPT_TEMPLATE = """Use the following pieces of context to answer the user's question. 
        Your response MUST follow this structure:
        1. Start with a section titled "SUMMARY OF GROUND TRUTHS" which summarizes the key facts from the provided context.
        2. Follow with a section titled "ANSWER" that directly addresses the user's question based on those truths.

        Context: {context}
        Question: {question}
        
        Helpful Response:"""
        
        QA_PROMPT = PromptTemplate(
            template=QA_PROMPT_TEMPLATE, input_variables=["context", "question"]
        )

        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
            "Rephrase the follow-up question as a standalone question. History: {chat_history} Input: {question}"
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=eval_llm, 
            retriever=self.db.as_retriever(), 
            condense_question_prompt=CONDENSE_QUESTION_PROMPT, 
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True, 
            verbose=False
        )
        return self.qa_chain

    def initialize_evaluation_models(self):
        """Initialize BART model and BERT scorer for evaluation."""
        self.bart_model = BartForConditionalGeneration.from_pretrained(self.bart_model_name)
        self.bart_tokenizer = BartTokenizer.from_pretrained(self.bart_model_name)
        self.bert_scorer = BERTScorer(lang="en", rescale_with_baseline=True)

    def process_query(self, query):
        """Process a single query and return structured source objects."""
        chat_history = []
        result = self.qa_chain.invoke({"question": query, "chat_history": chat_history})
        
        source_docs = result.get("source_documents", [])
        
        formatted_sources = []
        seen = set()
        
        for doc in source_docs:
            fname = doc.metadata.get("source", "Unknown File")
            page = doc.metadata.get("page", "?")
            
            unique_id = f"{fname}-{page}"
            if unique_id not in seen:
                formatted_sources.append({
                    "filename": fname,
                    "page": page
                })
                seen.add(unique_id)
        
        return result["answer"], formatted_sources
        
    def evaluate_responses(self, results):
        """Evaluate responses using BART and BERT scores."""
        if not self.bart_model or not self.bert_tokenizer or not self.bert_scorer:
            self.initialize_evaluation_models()

        bert_scores = []
        bart_scores = []
        
        for item in results:
            inputs = self.bart_tokenizer(item["response"], truncation=True, padding=True, return_tensors="pt")
            with torch.no_grad():
                bart_score = self.bart_model(**inputs).logits
            bart_scores.append(bart_score.mean().item())

            P, R, F1 = self.bert_scorer.score([item["response"]], [item["reference"]])
            bert_scores.append(F1.numpy().mean())

        return bert_scores, bart_scores

    def run_evaluation(self, sample_queries):
        """Run complete RAG evaluation pipeline."""
        chunks = self.get_documents()
        self.create_embeddings_and_vector_db(chunks)
        self.setup_rag_chain()

        df = pd.DataFrame(sample_queries)
        results = []
        
        for _, row in df.iterrows():
            question = row['question']
            ground_truth = row['answer']
            
            answer, relevant_docs = self.process_query(question)
            
            results.append({
                "user_input": question,
                "reference": ground_truth,
                "response": answer,
                "retrieved_contexts": [relevant_docs[0].page_content]
            })

        bert_scores, bart_scores = self.evaluate_responses(results)
        
        print("BERT Scores:", bert_scores)
        print("BART Scores:", bart_scores)
        
        return results, bert_scores, bart_scores