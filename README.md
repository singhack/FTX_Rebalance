# BOT_FTX_reblance
 Learning Project

### Install Requirement ###
ccxt  
pandas  
matplotlib  
simplejson  
requests  


  
### Setting ###   
  "LOGFILE":"Logs.log",             #### log file name   
  "apiKey":"apiKey",                ### your apikey  
  "secret":"secret",                ### your secretkey  
  "sub_account":"sub_accountname",                 ### your sub_account_name   
  "symbols": ["XRP","SOL","SRM","XRPBEAR"] ,                 ### basket symbol to trades 
  "fix_value": [80.0, 50.0,50.0,55] ,                 ### fixusdvalue of asset  
  "threshold_buy":[0.1,0.1,0.1,0.05],                 ### %diff from fix value to buy token   
  "threshold_sell":[0.1,0.1,0.1,0.05],                 ## %diff from fix value to sell token   
  "trigger_stop": [0.2,0.3,0.25,0.5],                 ## %diff from entry_price when starts bot     
  "gap":0.005,                                        ### Gap away from midprice to buy,sell order    
  "cd": 60 ,                                          ### cooldown to refresh bot   
  "entry_list": [1.2 ,  47.0 ,9.0 , 0.000020] ,       ## input entry_price if 0 bot refresh check pnl when starts bot
  "token_line": "token_line"                          ###  tokenID_Line to nortify trades   

# Start #
 1.Setting Config  
 2.Run bot.py  

