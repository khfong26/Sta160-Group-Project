from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# creates data path, add more data files/paths later if needed
DATA_PATH = os.path.join('data', 'FAOSTAT_data_en_10-14-2025.csv')

#loads data from csv and returns it as a panda df
def load_data():
    df = pd.read_csv(DATA_PATH, dtype=str)
    mask = (df['Area'] == 'Canada') & df['Item'].str.contains('Food Indices', na=False)
    df = df.loc[mask].copy()
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['date'] = pd.to_datetime(df['Year'] + ' ' + df['Months'], format='%Y %B', errors='coerce')
    df = df.dropna(subset=['date', 'Value'])
    df = df.sort_values('date')
    df['year'] = df['date'].dt.year
    return df

# routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/cpi_data')
def api_cpi_data():
    df = load_data()
    data = {
        "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "values": df['Value'].tolist()
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
