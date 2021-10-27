# crypto-efficient-frontier
 Developing an efficient frontier allocation for a crypto portfolio

The relevant functions developed thus far are:
 - Volatility minimizator: minimize_vol(desired_return,crypto_ticker_list)
   This functions returns the weights of the least risky portfolio given the desired cryptos and the desired return
 
The main tasks ahead are:
 - Add time considerations for the calculations, so only a certain timeframe can be used for returns and volatility estimations
 - Consider what happens for cryptos with different timeframe data availability
 - Add function to return optimal portfolio given risk-free rate
 - Add local database so the api only needs to be called once for every crypto when we need to do new analysis
