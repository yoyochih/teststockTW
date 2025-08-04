from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import datetime
import yfinance as yf
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import traceback

app = Flask(__name__)
CORS(app)

def fetch_data(ticker):
    df = yf.download(ticker, period='6mo', interval='1d')[['Close']]
    df = df.dropna()
    df['Return'] = df['Close'].pct_change()
    df['Lag1'] = df['Return'].shift(1)
    df['Lag2'] = df['Return'].shift(2)
    df.dropna(inplace=True)
    return df

def train_model(df):
    X = df[['Lag1', 'Lag2']]
    y = df['Return']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def generate_base64_charts(df, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    df['Return'].tail(60).plot(ax=ax1, title=f"{ticker} - 日報酬率 (近三個月)", color='purple')
    df['Close'].tail(60).plot(ax=ax2, title=f"{ticker} - 股價 (近三個月)", color='black')
    ax1.set_ylabel("報酬率")
    ax2.set_ylabel("價格")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

@app.route('/api/predict', methods=['GET'])
def predict():
    ticker = request.args.get('ticker', default='2330.TW')
    try:
        df = fetch_data(ticker)
        model = train_model(df)
        last = df.iloc[-1][['Lag1', 'Lag2']].values.reshape(1, -1)
        pred = model.predict(last)[0]
        predicted_percent = round(pred * 100, 2)

        comment = (
            f"預測明日報酬率為 {predicted_percent}%。"
            + ("✅ 屬於理想投資區間（5% ~ 10%）" if 5 <= predicted_percent <= 10 else "⚠️ 不建議短期投資")
        )

        chart_base64 = generate_base64_charts(df, ticker)

        return jsonify({
            'predicted_return': predicted_percent,
            'message': comment,
            'charts': {
                'return_chart': chart_base64,
                'price_chart': chart_base64
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
