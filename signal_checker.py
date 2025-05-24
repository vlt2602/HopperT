from indicator_helper import calculate_rsi

def check_rsi_signal(df):
  try:
      close_prices = df['close'].tolist()
      rsi = calculate_rsi(close_prices)
      return rsi < 35  # Tín hiệu mua khi quá bán
  except:
      return False
