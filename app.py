from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# creates data path, add more data files/paths later if needed
DATA_PATH = os.path.join('data', 'FAOSTAT_data_en_10-14-2025.csv')
IMF_PATH = os.path.join('data', 'IMF_cleaned.csv')

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

# load data from csv and returns it as panda df
def load_imf_data():
    df = pd.read_csv(IMF_PATH)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Year', 'Value'])
    # sort for consistency (nice and stable output order)
    df = df.sort_values(['Indicator', 'Country', 'Year'])
    return df

def _reshape_indicator(df, indicator_name):
    sub = df[df['Indicator'] == indicator_name].copy()
    years = sorted(sub['Year'].unique().tolist())
    countries = sorted(sub['Country'].unique().tolist())
    values_dict = {}
    for c in countries:
        series_for_country = []
        for y in years:
            row = sub[(sub['Country'] == c) & (sub['Year'] == y)]
            if len(row) == 0:
                series_for_country.append(None)  # no data this year
            else:
                series_for_country.append(float(row['Value'].iloc[0]))
        values_dict[c] = series_for_country
    out = {
        "years": years,
        "countries": countries,
        "values": values_dict
    }
    return out


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

@app.route('/api/imf_inflation')
def api_imf_inflation():
    df = load_imf_data()
    data = _reshape_indicator(df, "CPI inflation (% change)")
    return jsonify(data)


@app.route('/api/imf_gdp_growth')
def api_imf_gdp_growth():
    df = load_imf_data()
    data = _reshape_indicator(df, "GDP (constant prices, % change)")
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
