from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import os
from typing import Dict, List, TypedDict

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
SENTIMENT_THRESHOLD = float(os.getenv("SENTIMENT_THRESHOLD", -0.2))

class SentimentData(TypedDict):
    sentiment: str
    score: float
    reason: str

class SuggestionData(TypedDict):
    suggestions: List[str]

class SentimentAnalyzer:
    """
    SentimentAnalyzer class to analyze sentiment and provide suggestions for customer support conversations.
    """
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.llm = Ollama(model=model_name, base_url=OLLAMA_BASE_URL)
        
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
        """
        Analyze sentiment of a customer support conversation.
        """
        try:
            sentiment_result: Dict = self.sentiment_chain.invoke({"conversation": conversation})
            sentiment_data: SentimentData = json.loads(sentiment_result.get('text'))
            return sentiment_data
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0, "reason": "Error in analysis"}
    
    def get_suggestions(self, conversation: str, sentiment_analysis: SentimentData) -> List[str]:
        """
        Get suggestions for a customer support conversation based on sentiment analysis.
        """
        if sentiment_analysis["score"] < SENTIMENT_THRESHOLD:  # Only get suggestions for negative sentiment
            try:
                suggestion_result: Dict = self.suggestion_chain.invoke({
                    "conversation": conversation,
                    "sentiment_analysis": json.dumps(sentiment_analysis)
                })
                suggestion_data: SuggestionData = json.loads(suggestion_result.get('text'))
                return suggestion_data.get("suggestions", [])
            except Exception as e:
                print(f"Error getting suggestions: {e}")
        return []
