"""Ensemble retriever over PDF files, Wikipedia, and a SQLite database.

Install dependencies:
	pip install langchain langchain-community langchain-openai pypdf
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from typing import Iterable
from dotenv import load_dotenv


from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader, WikipediaLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

def load_sqlite_documents(db_path: str, tables: Iterable[str] | None = None) -> list[Document]:
	"""Convert SQLite rows into searchable documents."""
	connection = sqlite3.connect(db_path)
	connection.row_factory = sqlite3.Row
	try:
		available = [row[0] for row in connection.execute(
			"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
		)]
		selected = set(tables or available)
		documents: list[Document] = []
		for table in available:
			if table not in selected:
				continue
			# Table names come from sqlite_master, not user SQL input.
			safe_table = '"' + table.replace('"', '""') + '"'
			rows = connection.execute(f"SELECT * FROM {safe_table}").fetchall()
			for row in rows:
				text = "\n".join(f"{key}: {row[key]}" for key in row.keys())
				documents.append(Document(page_content=text, metadata={"source": f"sqlite:{table}"}))
		return documents
	finally:
		connection.close()


class EnsembleRetriever(BaseRetriever):
	"""Retrieve from each source and merge results using reciprocal rank fusion."""

	pdf_retriever: BaseRetriever | None = None
	wiki_retriever: BaseRetriever | None = None
	sqlite_retriever: BaseRetriever | None = None
	per_source_k: int = 4
	fusion_k: int = 60

	def _get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]:
		ranked_lists = [
			retriever.invoke(query)
			for retriever in (self.pdf_retriever, self.wiki_retriever, self.sqlite_retriever)
			if retriever is not None
		]
		scores: dict[str, float] = {}
		docs: dict[str, Document] = {}
		for results in ranked_lists:
			for rank, document in enumerate(results[: self.per_source_k]):
				key = f"{document.metadata.get('source', '')}:{document.page_content}"
				scores[key] = scores.get(key, 0.0) + 1 / (self.fusion_k + rank + 1)
				docs[key] = document
		return [docs[key] for key, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)]


def build_retriever(pdf_dir: str, db_path: str, wiki_topic: str, persist_dir: str) -> BaseRetriever:
	splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
	pdf_docs = splitter.split_documents(PyPDFDirectoryLoader(pdf_dir).load()) if pdf_dir else []
	if wiki_topic:
		try:
			wiki_docs = splitter.split_documents(
				WikipediaLoader(query=wiki_topic, load_max_docs=5).load()
			)
		except Exception as exc:
			# Wikipedia can return an HTML/error response instead of JSON when the
			# API is unavailable or blocked. Keep the other retrievers usable.
			print(f"Warning: Wikipedia could not be loaded: {exc}")
			wiki_docs = []
	else:
		wiki_docs = []
	sqlite_docs = splitter.split_documents(load_sqlite_documents(db_path)) if db_path else []
	print(f"Loaded {len(pdf_docs)} PDF chunk(s), {len(wiki_docs)} Wikipedia chunk(s), and {len(sqlite_docs)} SQLite chunk(s)")
	embeddings = OpenAIEmbeddings()

	def indexed(docs: list[Document], name: str):
		return Chroma.from_documents(docs or [Document("No data available.")], embeddings,
									 collection_name=name, persist_directory=f"{persist_dir}/{name}").as_retriever(search_kwargs={"k": 4})

	return EnsembleRetriever(
		pdf_retriever=indexed(pdf_docs, "pdfs") if pdf_dir else None,
		wiki_retriever=indexed(wiki_docs, "wikipedia") if wiki_topic else None,
		sqlite_retriever=indexed(sqlite_docs, "sqlite") if db_path else None,
	)


def answer(query: str, pdf_dir: str | None = None, db_path: str | None = None, wiki_topic: str | None = None) -> str:
	retriever = build_retriever(pdf_dir, db_path, wiki_topic, ".chroma")
	chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4o-mini", temperature=0), retriever=retriever)
	return chain.invoke({"query": query})["result"]


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("query")
	parser.add_argument("--pdf-dir")
	parser.add_argument("--db")
	parser.add_argument("--wiki-topic")
	args = parser.parse_args()
	if not any((args.pdf_dir, args.db, args.wiki_topic)):
		raise SystemExit("Provide at least one of --pdf-dir, --db, or --wiki-topic.")
	if not os.getenv("OPENAI_API_KEY"):
		raise SystemExit("Set OPENAI_API_KEY before running.")
	print(f"Query: {args.query}\nPDF dir: {args.pdf_dir}\nSQLite DB: {args.db}\nWikipedia topic: {args.wiki_topic}")
	print(answer(args.query, args.pdf_dir, args.db, args.wiki_topic))