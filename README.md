# Job Market Analytics Dashboard

A comprehensive web application for analyzing job market trends, salaries, and skills in the tech industry. This project aggregates data from multiple sources to provide real-time insights and a personalized resume matching feature.

## Features

-   **💰 Salary Analysis**: Visualize salary distributions by location and job title.
-   **🛠️ Skills Tracker**: Identify the most in-demand technical skills for various roles.
-   **📈 Market Trends**: Track job posting volumes over time to spot emerging opportunities.
-   **📄 Resume Match**: A content-based recommendation engine that matches your resume to the best-fitting job postings using TF-IDF and cosine similarity.

## Tech Stack

-   **Frontend**: HTML5, CSS3, Bootstrap 5, Plotly.js
-   **Backend**: Flask (Python)
-   **Data Processing**: Pandas, NumPy
-   **NLP & ML**: spaCy, scikit-learn (TF-IDF, Cosine Similarity)
-   **Data Collection**: JobSpy, Selenium

## Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd Sta160-Group-Project
    ```

2.  **Set up a virtual environment** (Recommended)
    ```bash
    # Windows
    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1

    # Mac/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    # If requirements.txt is missing, install manually:
    # pip install flask pandas plotly spacy scikit-learn python-jobspy selenium
    ```

4.  **Download NLP models**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Run the application**
    ```bash
    python src/website/app.py
    ```
    The app will be available at `http://127.0.0.1:5000/`.

## Project Structure

-   `src/website/`: Flask application and templates.
-   `src/analysis/`: Recommendation model and data analysis scripts.
-   `src/scraping/`: Scripts for data collection (JobSpy, Selenium).
-   `data/`: Processed and raw data files.
-   `api/`: Data loading and API utility functions.