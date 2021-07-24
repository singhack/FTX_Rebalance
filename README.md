# BOT_FTX_reblance
 Learning Project

### Install Requirement ###
ccxt  
pandas  
matplotlib  
seaborn
simplejson  
ta-libs
requests  
######################
  
### Setting ###   
  "LOGFILE":"Logs.log",             #### log file name   <br>
  "apiKey":"apiKey",                ### your apikey   <br>
  "secret":"secret",                ### your secretkey   <br>
  "sub_account":"sub_accountname",                 ### your sub_account_name    <br>
  "symbols": ["XRP","SOL","SRM","XRPBEAR"] ,                 ### basket symbol to trades  <br>
  "fix_value": [80.0, 50.0,50.0,55] ,                 ### fixusdvalue of asset   <br>
  "threshold_buy":[0.1,0.1,0.1,0.05],                 ### %diff from fix value to buy token    <br>
  "threshold_sell":[0.1,0.1,0.1,0.05],                ###%diff from fix value to sell token    <br>
  "trigger_stop": [0.2,0.3,0.25,0.5],                 ### %diff from entry_price when starts bot      <br>
  "gap":0.002,                                        ### Gap away from midprice to buy,sell order  !not change!   <br>
  "cd": 60 ,                                          ### cooldown to refresh bot ทำงานทุก 1 นาที <br>
  "entry_list": [1.2 ,  47.0 ,9.0 , 0.000020] ,       ### ตั้งบันทึกค่า entry price ถ้าไม่จะเอาราคาปัจจุบันเมือเปิดบอท  <br>
  "token_line": "token_line"                          ###  tokenID_Line to nortify trades  ถ้าจะแจ้งเตือนใส่ Token Line ตรงนี้  <br>

# Start #
 1.Setting Config  
 2.Run bot.py  

