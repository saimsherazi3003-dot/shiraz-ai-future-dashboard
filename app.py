import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime, timezone

st.set_page_config(page_title="Shiraz AI Future", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

BG = "#0b1020"
st.markdown("""
<style>
.stApp {background: #0b1020; color: #edf2ff;}
[data-testid="stSidebar"] {background: #111a2e;}
div[data-testid="stMetric"] {background:#141f35; border:1px solid #273653; padding:12px; border-radius:12px;}
.stTabs [data-baseweb="tab"] {font-size:16px;}
.small-note {color:#aebbd3;font-size:13px;}
.signal {padding:14px;border-radius:12px;background:#14233a;border:1px solid #2b4265;}
</style>
""", unsafe_allow_html=True)

API = "https://fapi.binance.com"

@st.cache_data(ttl=15, show_spinner=False)
def get_ticker():
    r = requests.get(f"{API}/fapi/v1/ticker/24hr", timeout=12)
    r.raise_for_status()
    return pd.DataFrame(r.json())

@st.cache_data(ttl=20, show_spinner=False)
def get_klines(symbol, interval, limit=180):
    r = requests.get(f"{API}/fapi/v1/klines", params={"symbol":symbol,"interval":interval,"limit":limit}, timeout=12)
    r.raise_for_status()
    cols = ["time","open","high","low","close","volume","close_time","quote_volume","trades","taker_buy_base","taker_buy_quote","ignore"]
    df = pd.DataFrame(r.json(), columns=cols)
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

def indicators(df):
    d = df.copy()
    d["ema9"] = d.close.ewm(span=9, adjust=False).mean()
    d["ema21"] = d.close.ewm(span=21, adjust=False).mean()
    delta = d.close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["rsi"] = 100 - (100/(1+rs))
    tr = pd.concat([(d.high-d.low), (d.high-d.close.shift()).abs(), (d.low-d.close.shift()).abs()], axis=1).max(axis=1)
    d["atr"] = tr.rolling(14).mean()
    d["vol_avg"] = d.volume.rolling(20).mean()
    return d

def analyze(d):
    last = d.iloc[-1]
    prev = d.iloc[-2]
    bull = last.ema9 > last.ema21
    bear = last.ema9 < last.ema21
    rsi = float(last.rsi) if pd.notna(last.rsi) else 50
    vol_ratio = float(last.volume / last.vol_avg) if pd.notna(last.vol_avg) and last.vol_avg else 1
    score = 0
    score += 1 if bull else -1
    score += 1 if last.close > last.ema9 else -1
    score += 1 if 50 <= rsi <= 68 else (-1 if rsi < 42 or rsi > 75 else 0)
    score += 1 if vol_ratio >= 1.2 else 0
    if score >= 2:
        signal = "LONG کا امکان"
        bias = "LONG"
    elif score <= -2:
        signal = "SHORT کا امکان"
        bias = "SHORT"
    else:
        signal = "انتظار / NO TRADE"
        bias = "WAIT"
    return {"signal":signal,"bias":bias,"rsi":rsi,"vol_ratio":vol_ratio,"score":score,
            "price":float(last.close),"ema9":float(last.ema9),"ema21":float(last.ema21),
            "atr":float(last.atr) if pd.notna(last.atr) else 0,
            "high":float(d.high.tail(20).max()),"low":float(d.low.tail(20).min())}

def explain(a):
    lines = []
    lines.append(f"موجودہ تجزیاتی اشارہ: **{a['signal']}**۔ یہ یقینی پیش گوئی نہیں، صرف انڈیکیٹرز پر مبنی اندازہ ہے۔")
    lines.append(f"EMA9: {a['ema9']:.6g} اور EMA21: {a['ema21']:.6g}۔")
    lines.append(f"RSI: {a['rsi']:.1f} — 70 سے اوپر مارکیٹ زیادہ خریدی ہوئی اور 30 سے نیچے زیادہ فروخت شدہ ہو سکتی ہے۔")
    lines.append(f"حالیہ حجم اوسط کے مقابلے میں {a['vol_ratio']:.2f} گنا ہے۔")
    lines.append(f"گزشتہ 20 کینڈلز کی بلند سطح تقریباً {a['high']:.6g} اور کم سطح {a['low']:.6g} ہے۔")
    lines.append("صرف اس اشارے پر ٹریڈ نہ کھولیں؛ سپورٹ/ریزسٹنس، کینڈل کلوز، فیس اور اسٹاپ لاس ضرور دیکھیں۔")
    return "\n\n".join(lines)

st.title("📈 Shiraz AI Future")
st.caption("Crypto Futures Dashboard | اردو تجزیہ | موبائل اور کمپیوٹر دونوں کے لیے")
st.warning("تعلیمی/تجزیاتی ٹول — منافع کی ضمانت نہیں۔ یہ ورژن خودکار خرید و فروخت یا آپ کے Binance اکاؤنٹ میں آرڈر نہیں لگاتا۔")

with st.sidebar:
    st.header("⚙️ سیٹنگز")
    symbol = st.selectbox("کوائن منتخب کریں", ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","LINKUSDT","AVAXUSDT","PEPEUSDT"])
    interval = st.selectbox("ٹائم فریم", ["1m","5m","15m","30m","1h","4h"], index=1)
    st.caption("ڈیٹا: Binance USDⓈ-M Futures کا عوامی مارکیٹ ڈیٹا")
    if st.button("🔄 تازہ ڈیٹا لوڈ کریں", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

try:
    tickers = get_ticker()
    row = tickers[tickers.symbol == symbol]
    df = indicators(get_klines(symbol, interval))
    a = analyze(df)
    t = row.iloc[0] if not row.empty else None
    change = float(t.priceChangePercent) if t is not None else 0
    last_price = float(t.lastPrice) if t is not None else a["price"]
    quote_vol = float(t.quoteVolume) if t is not None else 0

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("موجودہ قیمت", f"{last_price:,.6g} USDT", f"{change:+.2f}% (24h)")
    m2.metric("24 گھنٹے کا حجم", f"${quote_vol:,.0f}")
    m3.metric("RSI (14)", f"{a['rsi']:.1f}")
    m4.metric("تجزیاتی اسکور", f"{a['score']:+d}/4")

    tabs = st.tabs(["📊 لائیو چارٹ","🔎 کوائن اسکینر","🧠 اردو AI تجزیہ","🧮 رسک کیلکولیٹر","📘 رہنمائی"])
    with tabs[0]:
        st.subheader(f"{symbol} — {interval}")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.time, open=df.open, high=df.high, low=df.low, close=df.close, name="Candles"))
        fig.add_trace(go.Scatter(x=df.time, y=df.ema9, name="EMA 9", line=dict(width=1.5)))
        fig.add_trace(go.Scatter(x=df.time, y=df.ema21, name="EMA 21", line=dict(width=1.5)))
        fig.update_layout(template="plotly_dark", height=520, xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div class='signal'><b>اشارہ:</b> {a['signal']}<br><span class='small-note'>یہ صرف انڈیکیٹر پر مبنی ابتدائی فلٹر ہے۔</span></div>", unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("مارکیٹ اسکینر — ممکنہ حرکت والے کوائنز")
        st.caption("24h تبدیلی اور حجم کے مطابق ترتیب؛ ہر کوائن کا سگنل منتخب ٹائم فریم پر الگ حساب ہوتا ہے۔")
        candidates = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","LINKUSDT","AVAXUSDT","PEPEUSDT"]
        scan_rows = []
        progress = st.progress(0)
        for i, sym in enumerate(candidates):
            try:
                tr = tickers[tickers.symbol == sym]
                kd = indicators(get_klines(sym, interval, 100))
                aa = analyze(kd)
                rr = tr.iloc[0] if not tr.empty else None
                scan_rows.append({"کوائن":sym,"قیمت":aa["price"],"24h تبدیلی %":float(rr.priceChangePercent) if rr is not None else 0,
                                  "حجم کا تناسب":round(aa["vol_ratio"],2),"RSI":round(aa["rsi"],1),"اشارہ":aa["signal"]})
            except Exception:
                scan_rows.append({"کوائن":sym,"قیمت":None,"24h تبدیلی %":None,"حجم کا تناسب":None,"RSI":None,"اشارہ":"ڈیٹا دستیاب نہیں"})
            progress.progress((i+1)/len(candidates))
        scan = pd.DataFrame(scan_rows).sort_values("24h تبدیلی %", ascending=False, na_position="last")
        st.dataframe(scan, use_container_width=True, hide_index=True)
        st.caption("زیادہ 24h اضافہ لازماً مزید پمپ کی ضمانت نہیں؛ اچانک الٹ حرکت اور لیکویڈیشن کا خطرہ ہوتا ہے۔")

    with tabs[2]:
        st.subheader("🧠 Shiraz AI — اردو مارکیٹ وضاحت")
        st.markdown(explain(a))
        question = st.text_input("مارکیٹ کے بارے میں سوال لکھیں", placeholder="مثلاً EMA9 اور EMA21 کیا بتا رہے ہیں؟")
        if st.button("جواب دکھائیں"):
            q = question.strip().lower()
            if not q:
                st.info("پہلے اپنا سوال لکھیں۔")
            elif any(x in q for x in ["ema","ای ایم اے"]):
                st.write("EMA9 تیز رفتار اوسط ہے اور EMA21 نسبتاً سست۔ EMA9 کا EMA21 سے اوپر ہونا مثبت رجحان کی علامت ہو سکتا ہے، مگر کینڈل بند ہونے اور دوسرے اشاروں کی تصدیق ضروری ہے۔")
            elif "rsi" in q or "آر ایس آئی" in q:
                st.write("RSI رفتار ناپتا ہے۔ 70 سے اوپر زیادہ خریداری اور 30 سے نیچے زیادہ فروخت کی کیفیت ہو سکتی ہے؛ یہ اکیلا خرید یا فروخت کا حکم نہیں۔")
            elif any(x in q for x in ["long","لانگ","short","شارٹ"]):
                st.write(f"اس وقت منتخب کوائن {symbol} کا حسابی اشارہ: {a['signal']}۔ یہ یقینی سگنل نہیں؛ انٹری سے پہلے اسٹاپ لاس اور رسک دیکھیں۔")
            else:
                st.write("اس ابتدائی ورژن میں اردو وضاحت انڈیکیٹرز کے قواعد پر مبنی ہے، مکمل آزاد AI چیٹ نہیں۔ اپنا سوال EMA، RSI، حجم، لانگ/شارٹ یا رسک کے بارے میں کریں۔")

    with tabs[3]:
        st.subheader("🧮 رسک اور پوزیشن سائز کیلکولیٹر")
        c1,c2,c3 = st.columns(3)
        balance = c1.number_input("اکاؤنٹ بیلنس (USDT)", min_value=1.0, value=5.0, step=1.0)
        risk_pct = c2.number_input("فی ٹریڈ رسک %", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        stop_pct = c3.number_input("انٹری سے اسٹاپ لاس کا فاصلہ %", min_value=0.1, max_value=50.0, value=1.0, step=0.1)
        risk_usd = balance * risk_pct / 100
        position = risk_usd / (stop_pct/100)
        st.metric("زیادہ سے زیادہ منصوبہ بند نقصان", f"{risk_usd:.4f} USDT")
        st.metric("حسابی پوزیشن سائز (لیوریج سے پہلے)", f"{position:.2f} USDT")
        st.caption("فیس، سلپیج، فنڈنگ اور گیپ کی وجہ سے اصل نقصان مختلف ہو سکتا ہے۔ لیوریج پوزیشن کا خطرہ بڑھاتی ہے۔")

    with tabs[4]:
        st.subheader("اس ڈیش بورڈ کو کیسے استعمال کریں؟")
        st.markdown("""
1. کوائن اور ٹائم فریم منتخب کریں، ابتدا میں 5m یا 15m پر مشق کریں۔
2. چارٹ میں کینڈلز، EMA9 اور EMA21 دیکھیں۔
3. اردو تجزیے میں RSI اور حجم کی وضاحت پڑھیں۔
4. اسکینر کو صرف شارٹ لسٹ سمجھیں، فوری خریداری کا حکم نہیں۔
5. رسک کیلکولیٹر سے پہلے ممکنہ نقصان طے کریں۔
6. پہلے ڈیمو/پیپر ٹریڈنگ میں نتیجہ نوٹ کریں؛ حقیقی رقم لگانے میں جلدی نہ کریں۔

**اہم:** اس ورژن میں Binance API key یا secret درکار نہیں۔ کوئی رقم، والٹ یا اکاؤنٹ لاگ اِن یہاں درج نہ کریں۔
""")
    st.caption("آخری ڈیٹا ریفریش: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

except Exception as e:
    st.error("مارکیٹ ڈیٹا ابھی حاصل نہیں ہو سکا۔ انٹرنیٹ یا Binance عوامی API عارضی طور پر دستیاب نہ ہو سکتی ہے۔")
    st.caption(f"تفصیل: {str(e)[:250]}")
    st.info("کچھ دیر بعد 'تازہ ڈیٹا لوڈ کریں' دبائیں۔")

st.divider()
st.caption("Shiraz AI Future • ابتدائی محفوظ ورژن • خودکار ٹریڈنگ بند")
