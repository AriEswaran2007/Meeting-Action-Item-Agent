# Meeting Action Item Agent

## About the Project

Meeting Action Item Agent is a Python-based application that uses a local Large Language Model (LLM) to analyze meeting transcripts.

The application identifies tasks, responsible persons, deadlines, important decisions, and a short meeting summary.

The main aim of this project is to make meeting follow-ups easier and reduce the time spent on taking notes manually.

## Features

- Accepts meeting transcripts as input.
- Extracts action items from meetings.
- Identifies responsible persons.
- Extracts deadlines when available.
- Identifies important decisions.
- Generates a short meeting summary.
- Allows action items to be downloaded as a CSV file.

## Technologies Used

- Python
- Streamlit
- Ollama
- Large Language Models
- Pandas

## How to Run

1. Install Python.
2. Install Ollama.
3. Download a compatible Ollama model.
4. Install the required Python libraries.
5. Run the Streamlit application.

## Run Command

```bash
streamlit run app.py