from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from typing import List 
import logging 
import time
from typing import Optional

logger = logging.getLogger(__name__)
# ===== TOOLS =====
@tool
def web_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query string
    """
    search = DuckDuckGoSearchRun(region="us-en")
    result = search.invoke(query)
    print(f"\n📡 Search Result Preview: {result[:200]}...\n")
    return result

from langchain.tools import tool
from langchain_google_community import GoogleSearchAPIWrapper
from dotenv import load_dotenv
load_dotenv()
search = GoogleSearchAPIWrapper()

@tool
def google_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query string
    """
    return search.run(query)

my_tools = [google_search]

class ResearchTools():
    """
    Research Tools Collection
    
    Provides reusable tools for agents:
    - Web search
    - Webpage scraping
    - Mathematical calculations
    """
    def __init__(self):
        """
        Initialize the research tools
        """
        self.search_engine = DuckDuckGoSearchRun()
        logger.info("Research tools initialized")

    def web_search(self,query: str)->str:
        """
        Search the web for current information
        
        Args:
            query: Search query string
            
        Returns:
            Search results as formatted string
        """
        try:
            logger.info(f"Web Search : {query}")
            results =  self.search_engine.invoke(query)
            return f"Search Results : \n{results}"
        except Exception as e:
            logger.error(f"Search error : {e}")
            return f"Search error : {e}"
        
    def web_scrape(self,url: str)->str:
        """
        Extract content from a webpage
        
        Args:
            url: Webpage URL
            
        Returns:
            Webpage content (first 1000 chars)
        """
        try:
            logger.info(f"Web Scrape : {url}")
            loader = WebBaseLoader(url)
            docs = loader.load()
            content = docs[0].page_content[:1000] if docs else "No content found"
            return f"Webpage Content : \n{content}"
        except Exception as e:
            logger.error(f"Scrape error : {e}")
            return f"Scrape error : {e}"
        
    def calculate(self,expression:str)->str:
        """
        Perform mathematical calculations
        
        Args:
            expression: Mathematical expression
            
        Returns:
            Calculation result
        """
        try:
            logger.info(f"Calculating: {expression}")
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return f"Calculation error: {str(e)}"
    def get_tools(self)->List[tool]:
        """
        Get all tools as LangChain tool objects
        
        Returns:
            List of tool objects for agent binding
        """
        return [
            tool(
                self.web_search,
                description="Search the web for current information. Input: search query string."
            ),
            tool(
                self.web_scrape,
                description="Extract content from a webpage. Input: valid URL."
            ),
            tool(
                self.calculate,
                description="Perform mathematical calculations. Input: math expression."
            )
        ]
    
if __name__ == "__main__":

    # Example usage
    research_tools = ResearchTools()
    query = "What is capital of pakistan?"
    print("Query:",query)
    print("Results of Web Search Tool :",research_tools.web_search(query))
   