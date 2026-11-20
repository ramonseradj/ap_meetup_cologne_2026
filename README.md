# ap_meetup_cologne_2026

This repository contains a Jupyter notebook demo that reads encrypted chat traces from BigQuery, decrypts and analyzes them locally with Ollama, then writes the enriched results back to BigQuery.

The language-model inference runs on your machine. BigQuery is still used to store and transfer the input and result tables, so use only data you are authorized to process.

## Requirements

- Python 3.10 or later
- [Ollama](https://ollama.com/download) installed locally
- A Google Cloud project with the BigQuery API enabled
- A service account JSON key with the BigQuery permissions described below

## 1. Get the code and install Python packages

From a terminal, clone the repository and enter its directory:

```bash
git clone https://github.com/ramonseradj/ap_meetup_cologne_2026.git
cd ap_meetup_cologne_2026
```

Create and activate a virtual environment. The repository's `.gitignore` excludes a directory named `venv`.

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the requirements and start JupyterLab:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

Open `notebook.ipynb` in JupyterLab and select the Python kernel from this virtual environment. The notebook also has a package-install cell; when using the requirements file above, that cell is not needed.

## 2. Install Ollama and download a model

Install Ollama using the instructions for your operating system at [ollama.com/download](https://ollama.com/download). On Linux, the official installer is also available with:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Make sure the Ollama service is running. On systems where it does not start automatically, run this in a separate terminal and leave it running:

```bash
ollama serve
```

Download the model used by default in the notebook and check that Ollama can see it:

```bash
ollama pull llama3
ollama list
```

The notebook connects to `http://localhost:11434` by default and sets `MODEL_NAME` to `llama3`. If you choose another model, pull it first and set `MODEL_NAME` to the exact model tag shown by `ollama list`. Keep the Ollama service running while executing the notebook.

## 3. Configure Google Cloud and BigQuery

Use a Google Cloud project where you can enable BigQuery and create a service account. Enable the BigQuery API, for example with the Google Cloud CLI:

```bash
gcloud services enable bigquery.googleapis.com --project=YOUR_PROJECT_ID
```

Create a service account and grant it:

- **BigQuery Job User** on the project, so it can run queries.
- **BigQuery Data Editor** on the dataset used by this demo, so it can read and write the tables.

Create and download a JSON key for the service account, then place it at the repository root as `service_account.json`. Both the notebook and the upload helper expect that path by default. This file contains credentials: do not commit it, share it, or add its contents to the notebook. The repository's `.gitignore` excludes JSON files, but check `git status` before committing.

In BigQuery, create the dataset `ap_meetup_cologne` in the project and region you intend to use. The project ID and dataset location should match your configuration.

## 4. Set the project, table, and encryption values

In the configuration cell near the beginning of `notebook.ipynb`, set the following values:

| Notebook variable | What to set |
| --- | --- |
| `PROJECT_ID` | Your Google Cloud project ID (not the project display name). Replace the notebook's sample value, `analytics-cologne`, with your project ID. |
| `CREDENTIAL_PATH` | Path to your service-account JSON file; use `service_account.json` if it is in the repository root. |
| `DATASET` | BigQuery dataset name; the demo defaults to `ap_meetup_cologne`. |
| `DEMO_TABLE` | Input table name; the upload helper creates `ap_meetup_demo`. |
| `RESULT_TABLE` | Output table name; the notebook defaults to `sentiment_results`. |
| `OLLAMA_URL` | Ollama server URL; the local default is `http://localhost:11434`. |
| `MODEL_NAME` | A model tag installed in Ollama, such as `llama3`. |

### Encryption key

The notebook's `ENCRYPTION_KEY` must be the same Fernet key that was used to encrypt the input table's `encrypted_chat_body` values. If you use `demo/upload_demo_data.py` to prepare the demo table, its `SECRET_KEY` must match the notebook key exactly.

To generate a Fernet key locally:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the generated value as bytes in the notebook, for example:

```python
ENCRYPTION_KEY = b'<paste-your-generated-key-here>'
```

If you are uploading the CSV with the helper script, set its `SECRET_KEY` to the same bytes value before running the script. Keep the key somewhere safe and private; without it, encrypted rows cannot be decrypted. The `ENCRYPTION_KEY` in the notebook and `SECRET_KEY` in the upload helper are currently demo values. Replace both locally with your generated key; do not use the demo key or commit either key for real or confidential data.

## 5. (Optional) Upload the bundled demo data

If your BigQuery input table is not already populated, the repository includes a sample CSV and a helper that encrypts its `chat_body` values before upload. First configure `PROJECT_ID`, `CREDENTIAL_PARTH`, and `SECRET_KEY` in `demo/upload_demo_data.py`; the key must match `ENCRYPTION_KEY` in the notebook. From the repository root, with the virtual environment active, run:

```bash
python demo/upload_demo_data.py
```

The helper writes to `ap_meetup_cologne.ap_meetup_demo` in the configured project and uses `if_exists="replace"`, so it replaces that table if it already exists. Confirm the project and target table before running it. The bundled CSV is intended for this demo only.

## 6. Run the notebook

1. Start Ollama and confirm that the model appears in `ollama list`.
2. Start JupyterLab from the repository root, if it is not already running:
   ```bash
   jupyter lab
   ```
3. Open `notebook.ipynb`, select the virtual-environment kernel, and review the configuration cell.
4. Run the notebook cells in order. The notebook reads `PROJECT_ID.DATASET.DEMO_TABLE`, decrypts `encrypted_chat_body`, calls the local Ollama model, and writes results to `PROJECT_ID.DATASET.RESULT_TABLE`.

## Troubleshooting

- **BigQuery permission errors:** Confirm the API is enabled, the service-account key belongs to the project you configured, and the account has BigQuery Job User plus dataset-level Data Editor access.
- **File not found for credentials:** Start JupyterLab from the repository root, or set `CREDENTIAL_PARTH` to the correct path.
- **Ollama connection refused:** Start the Ollama app/service and verify `OLLAMA_URL`. For a custom model tag, check `ollama list` and update `MODEL_NAME`.
- **Fernet `InvalidToken` errors:** The notebook key does not match the key used to encrypt the table. Use the same key for the upload and notebook; do not generate a new key after the table is encrypted.
- **Missing BigQuery data types package:** Activate the virtual environment and reinstall with `python -m pip install -r requirements.txt`.
