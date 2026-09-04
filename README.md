# Vectra AI ChatBot
 
Vectra AI ChatBot is a full-stack AI chatbot web application with a React/Vite frontend and a FastAPI backend. It supports multiple conversation threads, live streaming assistant replies, automatic chat title generation, document upload with retrieval-augmented question answering, and tool-based assistant actions such as web search, calculations, and stock price lookups.
 
## 📸 Screenshots
 
<img width="1309" height="636" alt="Screenshot 2026-07-24 004856" src="https://github.com/user-attachments/assets/f3764e90-c19c-4d18-923c-3044881f038a" />
<img width="1354" height="680" alt="Screenshot 2026-09-04 223423" src="https://github.com/user-attachments/assets/ba415063-fe2b-4a70-a107-b90a043a4e67" />
<img width="1362" height="671" alt="Screenshot 2026-09-04 223553" src="https://github.com/user-attachments/assets/71b27122-2449-4259-a665-bd6baddbb6dc" />
<img width="1349" height="660" alt="Screenshot 2026-09-04 223636" src="https://github.com/user-attachments/assets/0a8971a8-3bda-4b70-a2ce-1ec86761bf44" />



 
## ✨ Features
 
**Chat & Threads**
- Create, switch between, rename, and delete multiple chat threads
- Auto-generate a chat title from the first user message
- View saved chat history per thread
- Download a chat as a text file
- Change the chat background image from the thread menu
**Streaming & Assistant Behavior**
- Stream assistant responses live, token by token, over Server-Sent Events (SSE)
- Visual tool-status indicator while the assistant is calling a tool
- System prompt drives the assistant to pick the right tool automatically (search, stock lookup, calculator, or document retrieval)
**Document Upload & RAG**
- Upload documents to a specific chat thread
- Ask questions about the uploaded document using retrieval-augmented generation (RAG)
- Each thread keeps its own isolated document context/vector store — uploads in one thread don't leak into another
**Tool-Based Actions**
- 🔎 Web search (DuckDuckGo)
- 🧮 Calculator for arithmetic
- 📈 Stock price lookup (Finnhub)
- 📄 Document retrieval tool for uploaded files
**UI**
- Responsive sidebar and chat interface
- Sidebar with thread list and active thread selection
- Thread menu: rename, change background, download chat, delete chat
- Auto-scroll to the latest message
## 🏗️ Architecture
 
```
React (Vite) frontend  ──HTTP/SSE──▶  FastAPI backend  ──▶  LangGraph Agent
                                            │                     │
                                            │                     ├─ Groq LLM
                                            ▼                     └─ Tools (search, calculator, stock, RAG)
                                     SQLite (thread state & checkpointing)
                                     ChromaDB (per-thread document embeddings)
```
 
- LangGraph handles agent state and checkpointing so conversation state persists across turns.
- A thread-aware tool node ensures the document retrieval tool always operates on the correct thread's uploaded content.
- Each thread has its own Chroma collection, keeping documents and retrieval scoped per conversation.
## 🛠️ Tech Stack
 
**Frontend**
- React 18
- Vite
- JavaScript
- CSS
- Key components: Sidebar, ChatWindow, ThreadItem, ThreadMenu, MessageBubble, delete-confirmation modal
**Backend**
- Python
- FastAPI
- LangGraph
- LangChain
- SQLite (thread/checkpoint persistence)
- ChromaDB (per-thread vector storage)
- HuggingFace embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- Groq (LLM inference)
**Tools**
- DuckDuckGo search tool
- Calculator tool
- Finnhub stock price tool
- RAG tool for uploaded documents
## 📁 Project Structure
 
```
CHAT_BOT/
├── backend/
│   ├── main.py                # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── agent/                 # LangGraph agent, state, tool node
│   ├── database/               # SQLite checkpointer
│   ├── services/               # Chat + RAG services
│   └── tools/                  # Search, calculator, stock, RAG tools
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/chatApi.js      # API client
│   │   ├── components/         # Sidebar, ChatWindow, ThreadItem, ThreadMenu, MessageBubble
│   │   ├── styles/
│   │   └── utils/
```
 
## 🔌 API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/threads` | Create a new conversation thread |
| GET | `/threads` | List all threads |
| GET | `/threads/{thread_id}/messages` | Get message history for a thread |
| DELETE | `/threads/{thread_id}` | Delete a thread |
| POST | `/threads/{thread_id}/upload` | Upload and index a file for RAG (multipart/form-data) |
| POST | `/chat/stream` | Stream assistant responses (SSE) |
 
## 🗺️ Roadmap
 
- [ ] Add authentication / multi-user support
- [ ] Broaden supported file types for upload beyond current formats
- [ ] Add unit/integration tests
- [ ] Improve error handling on the frontend for dropped SSE connections
