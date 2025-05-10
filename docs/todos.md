Steps:
1. List of exchanges to be added:
   - Binance
   - Kraken
   - Bitfinex
   - Bittrex
   - KuCoin
   - Huobi
   - OKEx
   - Gate.io
   - Poloniex
2. List of tokens with USDT pairs to be added:
   - find all tokens with USDT pairs on the exchanges listed above
   - For MVP use next:
     - AR
     - TIA
     - CRV
     - CHZ
     - ATOM
     - ETC
3. Get trade info from all exchanges for all tokens with USDT pairs
4. Filter tokens between a pair of exchanges with different prices by specified percentage
5. Order by decreasing price difference 
    - amount of available tokens on exchange A
6. Investigate API to place orders on exchanges
7. Create module to handle orders on exchanges
8. Create module to store orders in database
9. Create module to handle wallets (balance in USDT)

Arbitrage algorithm:
1. Create order to buy token on exchange A (lower price) OrderType - MARKET
2. Verify if order is possible to fill ???
3. Transfer token (all amount) to exchange B (higher price)
4. Sell token on exchange B (higher price) OrderType - MARKET