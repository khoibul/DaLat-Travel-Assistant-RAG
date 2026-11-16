# Da Lat Travel Assistant with RAG

## 1. Project Overview

**Student ID:** 25127203  
**Project:** SIGN-IN TRAVEL ASSISTANT WITH RAG CHAT  
**Destination:** Da Lat, Vietnam

Da Lat Travel Assistant is a Streamlit-based chatbot that helps users discover attractions, local food, and travel experiences in Da Lat.

The application integrates Firebase Authentication with Retrieval-Augmented Generation (RAG). Users must sign in before accessing the chatbot.

The chatbot retrieves relevant information from a predefined knowledge base and generates answers using locally hosted open-source AI models through Ollama.

## 2. Technologies

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Authentication | Firebase Authentication |
| AI Backend | Ollama |
| Embedding Model | embeddinggemma |
| Language Model | qwen3:4b |
| Retrieval Algorithm | Cosine Similarity, Top-3 |
| Knowledge Base | JSON |
| Remote Model Hosting | Google Colab (Tesla T4 GPU) |
| API Tunnel | Pinggy |
| Chat History | Streamlit Session State |

## 3. System Architecture

The application consists of three main components:

**Authentication**

Firebase Authentication provides email/password registration and login. Only authenticated users can access the travel assistant.

**Retrieval-Augmented Generation**

1. Load 15 travel guide entries from `knowledge_base.json`.
2. Generate embeddings using `embeddinggemma`.
3. Cache knowledge base embeddings.
4. Convert the user's question into an embedding.
5. Calculate cosine similarity.
6. Retrieve the top three most relevant entries.
7. Send the retrieved context and question to `qwen3:4b`.
8. Generate an answer with source citations such as `[G09]`.

**Chat Interface**

Streamlit displays user questions, generated answers, retrieved knowledge entries, and similarity scores. Chat history is maintained using `st.session_state` and cleared when users sign out.

## 4. Installation and Setup

### Requirements

- Python
- Firebase project with Email/Password Authentication enabled
- Ollama with `embeddinggemma` and `qwen3:4b`
- Internet connection when using a remote Ollama server

### Installation

Clone the repository:

```bash
git clone https://github.com/khoibul/DaLat-Travel-Assistant-RAG.git
cd DaLat-Travel-Assistant-RAG
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file based on `.env.example`:

```dotenv
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
FIREBASE_PROJECT_ID=your_firebase_project_id
OLLAMA_BASE_URL=http://localhost:11434
```

When using Google Colab and Pinggy, replace `OLLAMA_BASE_URL` with the current HTTPS tunnel URL.

### Ollama Models

Install and start Ollama, then download the required models:

```bash
ollama pull embeddinggemma
ollama pull qwen3:4b
```

### Run the Application

```bash
streamlit run app.py
```

Open the Streamlit application, create an account or sign in, and start asking questions about Da Lat.

## 5. Testing Results

The following test cases were performed to evaluate retrieval and answer generation.

| # | Test Question | Expected Source | Retrieved IDs | Result |
|---|---|---|---|---|
| 1 | Where can I go hiking in Da Lat? | G09 | G08, G09, G01 | Pass |
| 2 | Where can I see flowers in Da Lat? | G04 | G04, G06, G02 | Pass |
| 3 | What local food should I try in Da Lat? | G13, G14 | G03, G13, G14 | Pass |
| 4 | Which mountain is suitable for trekking in Da Lat? | G09 | G08, G09, G01 | Pass – Paraphrase |
| 5 | What is the population of Da Lat? | None | G08, G12, G05 | Pass – I don't know |
| 6 | What is the population of each district in Da Lat? | None | G15, G08, G05 | Pass – I don't know |

**Test Summary:** 6/6 test cases passed in the independent RAG tests.

The Streamlit application was also tested for account registration, login, multiple chat messages, source citations, similarity scores, and clearing chat history after sign-out.

### Observed Failure and Resolution

During remote deployment, the chatbot experienced a request timeout of 180 seconds.

Investigation showed that Ollama was previously running the language model on the CPU rather than the available GPU.

After reinstalling and restarting Ollama in Google Colab, both `embeddinggemma` and `qwen3:4b` were verified to run with 100% GPU processing on an NVIDIA Tesla T4.

The Pinggy connection was re-established, and a subsequent Streamlit RAG query returned the expected answer with source citations.

## 6. Computational Thinking Analysis

### Abstraction

The system focuses on the essential information required to answer travel-related questions: the user's question, relevant guide entries, and generated answers.

Unnecessary details outside the travel knowledge base are excluded from answer generation.

### Decomposition

The problem is divided into smaller modules:

- Authentication using Firebase
- Knowledge base management
- Text embedding
- Similarity calculation and retrieval
- Answer generation
- Streamlit interface and session management

### Pattern Recognition

Travel questions often contain different expressions with similar meanings. For example, questions about hiking and trekking may refer to related activities.

Semantic embeddings help identify these similarities even when users do not use identical words.

### Algorithm Design

```text
INPUT: User question Q, knowledge base K

1. Verify that the user is signed in.
2. Load cached embeddings for K.
3. Generate embedding E(Q).
4. FOR each entry in K:
       Calculate cosine similarity.
5. Sort entries by similarity score.
6. Select the top 3 entries.
7. Construct a prompt with Q and retrieved context.
8. Generate an answer using qwen3:4b.
9. Include relevant source IDs.
10. If the context is insufficient:
        Return "I don't know."

OUTPUT: Answer and retrieved sources
```

## 7. Limitations

- The chatbot only has access to 15 predefined knowledge base entries.
- It cannot provide reliable information about topics missing from the guide.
- Retrieval accuracy depends on embedding similarity and the quality of the knowledge base.
- The language model may occasionally produce incomplete or inaccurate answers.
- Remote inference depends on Google Colab availability and the Pinggy tunnel.
- Free Pinggy tunnel URLs are temporary.
- Chat history is session-based and is not permanently stored.

## 8. AI Tools Used

**ChatGPT (OpenAI)** was the only AI assistant used during the development of this project.

ChatGPT was used to support:

- Understanding assignment requirements
- Learning Firebase Authentication and Streamlit
- Designing the RAG pipeline
- Debugging Python code and API connections
- Planning test cases
- Preparing documentation

## 9. Demo Video

**Video Link:** [Watch Demo Video](https://drive.google.com/file/d/1RydabEKzVSUZzbbBWsv4d8XcgwdNRCfd/view?usp=sharing)

The demonstration includes authentication, RAG question answering, retrieved source inspection, Computational Thinking analysis, and testing results.