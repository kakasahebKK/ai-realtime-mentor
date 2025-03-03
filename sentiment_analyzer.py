from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from typing import Dict, List, Any, Optional, Union, TypedDict

class SentimentData(TypedDict):
    sentiment: str
    score: float
    reason: str

class SuggestionData(TypedDict):
    suggestions: List[str]

class SentimentAnalyzer:
    def __init__(self, model_name: str = "llama2") -> None:
        self.llm = Ollama(model=model_name)
        
        self.sentiment_template: str = """
        You are a sentiment analysis expert. Analyze the following customer support conversation.
        Return a JSON with: 
        1. "sentiment": overall sentiment (positive, neutral, negative)
        2. "score": sentiment score from -1.0 (very negative) to 1.0 (very positive)
        3. "reason": brief explanation for your analysis
        
        Conversation:
        {conversation}
        
        Return only valid JSON without any other text.
        """
        
        self.suggestion_template: str = """
        You are an expert customer support coach. The following conversation between a support agent and customer shows negative sentiment.
        
        Conversation:
        {conversation}
        
        Sentiment analysis: {sentiment_analysis}
        
        Provide 1-2 specific, tactful suggestions for the support agent to improve the customer's sentiment. 
        Be concise and practical. Format as JSON with one field: "suggestions" containing an array of suggestion strings.
        
        Return only valid JSON without any other text.
        """
        
        self.sentiment_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["conversation"],
                template=self.sentiment_template
            )
        )
        
        self.suggestion_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["conversation", "sentiment_analysis"],
                template=self.suggestion_template
            )
        )
    
    def analyze_sentiment(self, conversation: str) -> SentimentData:
        try:
            sentiment_result: str = self.sentiment_chain.invoke({"conversation": conversation})
            sentiment_data: SentimentData = json.loads(sentiment_result)
            return sentiment_data
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0, "reason": "Error in analysis"}
    
    def get_suggestions(self, conversation: str, sentiment_analysis: SentimentData) -> List[str]:
        if sentiment_analysis["score"] < -0.2:  # Only get suggestions for negative sentiment
            try:
                suggestion_result: str = self.suggestion_chain.invoke({
                    "conversation": conversation,
                    "sentiment_analysis": json.dumps(sentiment_analysis)
                })
                suggestion_data: SuggestionData = json.loads(suggestion_result)
                return suggestion_data.get("suggestions", [])
            except Exception as e:
                print(f"Error getting suggestions: {e}")
        return []
