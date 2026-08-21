# VentureLens AI — Deployable Prototype

This package is ready to place in a GitHub repository and deploy on Streamlit Community Cloud.

## Files
- `streamlit_app.py` — application
- `requirements.txt` — Python dependencies
- `.gitignore` — prevents local secrets from being committed
- `.streamlit/secrets.toml.example` — example secret configuration

## Deploy
1. Create a GitHub repository.
2. Upload the contents of this folder to the repository root.
3. Open Streamlit Community Cloud and create a new app from the repository.
4. Set the entrypoint to `streamlit_app.py`.
5. In Advanced settings / Secrets, add:

   OPENAI_API_KEY = "your-key-here"

6. Deploy.
7. Share the resulting `*.streamlit.app` URL.

Do NOT commit your real API key to GitHub.

## Local run
    pip install -r requirements.txt
    streamlit run streamlit_app.py

If no deployed secret exists, the local app allows an API key to be entered in the sidebar.

## What is live
The application calls an OpenAI model and enables the web-search tool. It generates market sizing hypotheses, ICPs, real target accounts, lookalikes, key roles, pain hypotheses, competitors, partners, outreach, risks, experiments, sources, and an INVEST / TEST / PIVOT / PASS recommendation.

## Prototype limitations
This is decision-support, not audited market research. TAM/SAM/SOM estimates depend on public evidence and model assumptions. Pain points are hypotheses unless supported by public evidence. A production system should add persistent storage, authentication, CRM/contact-data integrations, source verification, rate limits, usage controls, and feedback from actual wins/losses.
