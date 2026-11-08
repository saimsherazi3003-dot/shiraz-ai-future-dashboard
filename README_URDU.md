# Shiraz AI Future Trading Dashboard

یہ موبائل اور کمپیوٹر دونوں پر چلنے والا ابتدائی ویب ڈیش بورڈ ہے۔

## خصوصیات
- Binance USDⓈ-M Futures کا عوامی لائیو مارکیٹ ڈیٹا
- BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK, AVAX اور PEPE
- 1m، 5m، 15m، 30m، 1h اور 4h ٹائم فریم
- کینڈل اسٹک چارٹ، EMA9، EMA21، RSI، ATR اور حجم
- ابتدائی LONG / SHORT / WAIT فلٹر
- کوائن اسکینر
- اردو میں انڈیکیٹر کی وضاحت
- رسک اور پوزیشن سائز کیلکولیٹر

## حفاظتی حد
یہ تعلیمی/تجزیاتی ورژن ہے۔ یہ Binance اکاؤنٹ میں لاگ اِن نہیں کرتا، API secret نہیں مانگتا اور خودکار آرڈر نہیں لگاتا۔ سگنل منافع کی ضمانت نہیں۔

## کمپیوٹر پر چلانے کا طریقہ
1. Python 3.10 یا نیا ورژن انسٹال کریں۔
2. اس فولڈر میں Terminal / Command Prompt کھولیں۔
3. یہ کمانڈ چلائیں:
   `pip install -r requirements.txt`
4. پھر:
   `streamlit run app.py`
5. براؤزر میں کھلنے والا مقامی لنک کھولیں۔

## GitHub اور موبائل پر آن لائن چلانے کا طریقہ
1. اس ZIP کو Extract کریں۔
2. اس کے اندر موجود `app.py`, `requirements.txt`, `README_URDU.md` کو GitHub repository میں اپ لوڈ کریں۔
3. Streamlit Community Cloud میں GitHub سے سائن اِن کریں۔
4. New app بنائیں، اپنی repository منتخب کریں، Main file path میں `app.py` لکھیں اور Deploy کریں۔
5. Deploy ہونے کے بعد ملنے والا ویب لنک موبائل اور کمپیوٹر دونوں پر کھلے گا۔

## اگر ڈیٹا نہ آئے
Binance کا public endpoint کبھی کبھار عارضی طور پر دستیاب نہیں ہوتا یا نیٹ ورک اسے بلاک کر سکتا ہے۔ کچھ دیر بعد Refresh کریں۔
