#A sample app for the Truffle^1 
#Please provide feedback in this repo! We are actively developing this and want it to be what you want!

from typing import List, Dict, Any
import os
from dotenv import load_dotenv

import pandas as pd
import requests
import json

import truffle

load_dotenv() 

class HisNameIsYang:
    def __init__(self):
        self.metadata = truffle.AppMetadata(
            fullname="His Name Is Yang", # the full, user facing name of your app! 
            description="That's my quant!", # user facing app description, also used to generate synthetic usage data for live classification in the UI
            name="yang", # the internal app name
            goal="Research, formulate, and execute quantitative strategies for trading cryptocurrencies.", # the goal, presented to the agentic model
            icon_url="https://raw.githubusercontent.com/deepshard/trufflesdk/refs/heads/main/assets/icon.png" # the primary icon for your app, a 512x512 PNG
        )
        self.max_losses = 300000.0 # member variables can be used to store state between tool calls, and are saved and loaded automatically by the Truffle SDK on app instantiation/reload


    # you may provide the tool description for the model and icon (right now Apple SF Symbol names) here, as well as indicate that this function should be treated as a tool
    @truffle.tool(
        description="Returns metadata given a path to a CSV file, such as column names, data types, and shape", 
        icon="tablecells.badge.ellipsis"
    )
    @truffle.args(path="The path to the CSV file to analyze") # we went back and forth with ways to provide these arg descriptions, definitely would love feedback
    def AnalyzeCSV(self, path: str) -> Dict[str,Any]:
        if not os.path.exists(path):
            return {"error": f"File '{path}' not found"}
        try:
            with open(path, 'r') as file:
                df = pd.read_csv(path)
                return {
                    "path": path,
                    "columns": df.columns.tolist(),
                    "shape": df.shape,
                    "dtypes": df.dtypes.apply(lambda x: x.name).to_dict()
                }
        except Exception as e:
            return truffle.ReportError(e) # returns detailed traceback and error info for the model to troubleshoot with
    

    # if a tool is fairly self explanatory, or you're feeling lazy, you can just use the decorator alone
    @truffle.tool()
    def BuildReport(self, title: str, abstract: str, data: Dict[str,Any]) -> truffle.TruffleFile:
        content = f"#{title}\n###Abstract:\n {abstract}\n\###Data: ```{data}```"

        # returning a TruffleFile directly allows us to find and display the file in the UI for the user
        # otherwise, the model can and will attach files in messages to the user directly
        return truffle.TruffleFile("report.md", content) 


    @truffle.tool("Uses the Perplexity AI search API to find relevant information", icon="magnifyingglass.circle.fill")
    def PerplexitySearch(self, search_query: str) -> str:
        PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")  # you could also add a step that automatically asks the user for it with truffle.RequestUserInput! 
        PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"
        PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": search_query}
        ]

        try:
            response = requests.post(
                PERPLEXITY_URL,
                json={ "model": PERPLEXITY_MODEL, "messages": messages},
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
                }
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return truffle.ReportError(e)


    @truffle.tool("Gathers the stance to take based on the inverse market sentiment from Cramer's Mad Money", icon="dollarsign.square.fill") 
    @truffle.args(subject="The subject of interest to gather sentiment for example: Ethereum")
    def GatherInverseCramerMarketSentiment(self, subject: str) -> str:
        search_query = f"Jim Cramer's most recent opinion on {subject}"
        sentiment = self.PerplexitySearch(search_query) # we can call other tools from within our tools, why the hell not?
        
        prompt = truffle.PromptBuilder(system="Analyze the sentiment and opinion of the following information, and return your insights in the given format. ").Add(sentiment)

        prompt.Add("What is the sentiment here? " + sentiment)

        # we can also provide a schema to force the model to return a specific format with structured output
        schema = """
        {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["Bullish", "Bearish", "Neutral"],
                    "description": "The overall sentiment of the prediction, with Bullish being generally positive, and Bearish being generally negative, avoid using neutral if possible"
                }
                "confidence": {
                    "type": "number",
                    "description": "The confidence of the sentiment prediction, 0-100%"
                }

            }
        }
        """

        request = truffle.GenerateRequest(id="cramer_sentiment", prompt=prompt, max_tokens=100, fmt=truffle.RESPONSE_JSON, schema=schema, temperature=0.75) 
        response = truffle.InferSync(request, model="yang") # many endpoints are available for you to use, harnessing the power of our models and inference stack! 

        data = json.loads(response) # no need to try/except here, we can trust the model to return the correct schema
        sentiment =  "Bearish" if data["sentiment"] == "Bullish" else "Bullish"  # invert the returned sentiment
        return f"Based on the inverse of Cramer's sentiment, it is {data['confidence'] }% probable that you should take a {sentiment} stance on {subject}." # and formulate it into a return value

    
    @truffle.tool("Gather current data on ETH flows as a CSV or Markdown table")
    @truffle.args(as_markdown="Return the data as a markdown table instead of a CSV")
    def ETHCashFlowData(self, as_markdown: bool) -> str:
        try:
            SOURCE_URL = 'https://farside.co.uk/eth/'
            from selenium import webdriver
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')  
            driver = webdriver.Chrome(options=options)
            driver.get(SOURCE_URL)
            WebDriverWait(driver, timeout=10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete' 
            )
            screenshot = driver.get_screenshot_as_base64() #once the page is loaded, we can take a screenshot with headless chrome
            conversion_format = "Markdown" if as_markdown else "CSV"
            as_table = truffle.Vision(f"Convert this data to a {conversion_format} table, ensure you preserve units and values", base64_image=screenshot) #using the vision model, we can convert the screenshot to a table
            return as_table
        except Exception as e:
            return truffle.ReportError(e)
    

    @truffle.tool
    def GetTradingStrategy(self, coin_name: str) -> str:
        prompt = truffle.PromptBuilder(system="Generate a trading strategy based on the current market conditions described in the context for the given cryptocurrency. ").Add(coin_name)
        prompt.Add("What is the best trading strategy for this coin?")

        schema = """
        {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "description": "The trading strategy to follow, for example: 'Buy high, sell low!'"
                }
            }
        }
        """

        request = truffle.GenerateRequest(id="trading_strategy", prompt=prompt, max_tokens=100, fmt=truffle.RESPONSE_JSON, schema=schema, temperature=0.75)
        response = truffle.InferSync(request, model="yang")

        data = json.loads(response)
        return f"The best trading strategy for {coin_name} is: {data['strategy']}"


    @truffle.tool("Get the current price of a cryptocurrency", icon="dollarsign.square.fill")
    @truffle.args(coin_name="The full name of the coin to get the price for, for example: Bitcoin")
    def GetCryptoPrice(self, coin_name: str) -> str:
        try:
            coin_ids = requests.get('https://api.coingecko.com/api/v3/coins/list').json()
            coin_id = next((coin['id'] for coin in coin_ids if coin['name'].lower() == coin_name.lower()), None)

            if not coin_id:
                return f"Could not find a coin with the name {coin_name}"
            
            response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd')
            price = response.json()[coin_name]['usd']
            return f"The current price of {coin_name} is ${price}"
        except Exception as e:
            return truffle.ReportError(e)
        
    @truffle.tool("Find recent ETH whale transactions")
    @truffle.args(max_results="The maximum number of latest transactions to return, limit is 5")
    def GetETHWhales(self, max_results: int) -> str:
        try:
            response = requests.get('https://api.clankapp.com/v2/blockchain/ethereum/whales-amount-average').json()
            avg_value_eth = response['avg_amount']['value'] # price in ETH

            max_results = min(max_results, 5)
            transactions_json = requests.get(f'https://api.clankapp.com/v2/explorer/tx?s_date=desc&t_blockchain=ethereum&size={max_results}').json()
            transactions = transactions_json['data'] 
            results = f"The average value of the latest Ethereum whale transactions is ${avg_value_eth} ETH\nThe latest {max_results} 'whale' transactions are: \n"

            for transaction in transactions:
                results += f"- Transaction from {transaction['from_owner']} to {transaction['to_owner']} for {transaction['format_amount']} ETH / {transaction['amount_usd']} \n"
            return results
        except Exception as e:
            return truffle.ReportError(e)    


    @truffle.tool("Open a long or short position on a cryptocurrency", icon="banknote")
    @truffle.args(ticker="The ticker of the coin to open a position for, for example: BTC", position="The position to take, either 'long' or 'short'")
    def OpenPosition(self, ticker: str, position: str) -> str:
        if position not in ["long", "short"]:
            return "Invalid position, must be either 'long' or 'short'"
        
        #todo: implement trading once i work up the courage to give the Truffle all my money
        return f"Opened a {position} position on {ticker}!"
