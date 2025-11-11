# Testing Guide: LibreChat Agentic Data Stack (Gemini + ClickHouse Edition)

## 1. Introduction

This document provides step-by-step guidance to test the core features of your LibreChat and ClickHouse Agentic Data Stack. This setup is currently configured to use **Google's Gemini** as the exclusive AI model provider.

**Your Stack:**
- **Frontend:** LibreChat UI (`http://localhost:3080`)
- **AI Model:** Google Gemini
- **Analytics Engine:** ClickHouse MCP Server (`http://localhost:8001`)
- **Backend:** Docker containers for all services.

---

## 2. Prerequisites

Before you begin testing, ensure that all services are running.
```bash
# Navigate to your LibreChat directory
cd /home/yuvaraj/Projects/LibreChat

# Check the status of all containers
docker compose ps
```
All services, including `api`, `mcp-clickhouse`, `rag_api`, and `vectordb`, should have a status of `Up`.

---

## 3. Feature Testing

### Test Case 1: Basic Chat Functionality (Gemini)

**Objective:** Verify that the chat interface is working correctly with the Gemini model.

**Steps:**
1.  Open your web browser and navigate to `http://localhost:3080`.
2.  Click on **"New conversation"**.
3.  Confirm that the model selection dropdown shows **"Gemini"** and its available models (e.g., `gemini-2.5-pro`).
4.  Enter a prompt in the chatbox.

**Sample Prompts:**
- `Explain the concept of zero-knowledge proofs in simple terms.`
- `Write a Python script that sends an email using the smtplib library.`
- `What are the best practices for building a scalable web application?`

**✅ Expected Outcome:**
The Gemini model should provide a coherent and relevant response to your prompt.

---

### Test Case 2: Agentic Analytics (ClickHouse Integration)

**Objective:** Verify that LibreChat can use the ClickHouse MCP server to query and analyze data using natural language.

**Steps:**
1.  Start a new conversation.
2.  Below the model selection, find the **MCP Server** dropdown.
3.  Select **`clickhouse-playground`**.
4.  Now, ask questions related to the datasets available in the ClickHouse playground.

**Sample Prompts:**
1.  **Discovering Data:**
    - `What datasets do you have access to?`
    - `Show me the table schema for the "uk_price_paid" dataset.`
2.  **Querying Data:**
    - `What are the 5 most expensive properties sold in London in 2023 from the uk_price_paid dataset?`
    - `From the taxi_tips dataset, what is the average trip duration and tip amount?`
    - `Count the number of flights in the ontime dataset.`

**✅ Expected Outcome:**
The AI should:
1.  Acknowledge that it is using the ClickHouse playground.
2.  Generate a SQL query based on your natural language prompt.
3.  Execute the query against the ClickHouse server.
4.  Return the results in a clear, human-readable format (often as a table or a summary).

---

### Test Case 3: File Upload and RAG (Retrieval-Augmented Generation)

**Objective:** Verify that you can upload documents and ask questions based on their content.

**Steps:**
1.  Create a simple text file named `test_document.txt` with the following content:
    > The quick brown fox jumps over the lazy dog. LibreChat is an open-source AI chat platform. The Agentic Data Stack combines chat with powerful analytics. The primary analytics engine used here is ClickHouse.

2.  In a new conversation, click the **paperclip icon** to attach a file.
3.  Upload `test_document.txt`.
4.  Once the file is uploaded, ask questions about its content.

**Sample Prompts:**
- `Summarize the attached document.`
- `According to the document, what is LibreChat?`
- `What is the primary analytics engine mentioned in the file?`

**✅ Expected Outcome:**
The AI should provide answers based *only* on the content of the `test_document.txt` file, demonstrating its ability to read and comprehend the uploaded data.

---

### Test Case 4: Conversation Management

**Objective:** Verify that you can manage your chat history effectively.

**Steps:**
1.  **Rename a Conversation:**
    - Hover over a conversation in the left sidebar.
    - Click the pencil icon and give it a new name (e.g., "ClickHouse Test").
2.  **Search Conversations:**
    - Use the search bar at the top of the sidebar to find your renamed conversation.
3.  **Delete a Conversation:**
    - Hover over a conversation, click the trash can icon, and confirm the deletion.

**✅ Expected Outcome:**
The UI should update immediately, reflecting the changes you made (renaming, searching, and deleting).

---

## 4. System Health Checks

**Objective:** Verify that the backend services are healthy.

1.  **Check ClickHouse MCP Server:**
    - Open a new terminal and run:
      ```bash
      curl http://localhost:8001/health
      ```
    - **✅ Expected Outcome:** You should see a message like `OK - Connected to ClickHouse...`

2.  **Check Docker Container Logs:**
    - To see the logs for a specific service (e.g., the `rag_api` for file processing):
      ```bash
      docker compose logs -f rag_api
      ```
    - **✅ Expected Outcome:** The logs should show normal operational messages without continuous errors. Press `Ctrl + C` to exit the log stream.
