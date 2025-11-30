from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_community import GoogleSearchAPIWrapper
from dotenv import load_dotenv
load_dotenv()

search = DuckDuckGoSearchRun(region="us-en")
# ===== TOOLS =====
@tool
def duck_duck_web_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query string
    """
    
    result = search.invoke(query)
    print(f"\n📡 Search Result Preview: {result[:200]}...\n")
    return result


google_search = GoogleSearchAPIWrapper()

@tool
def google_web_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query string
    """
    return google_search.run(query)



@tool
def web_scrape(url: str)->str:
        """
        Extract content from a webpage
        
        Args:
            url: Webpage URL
            
        Returns:
            Webpage content (first 1000 chars)
        """
        try:
            print(f"Web Scrape : {url}")
            loader = WebBaseLoader(url)
            docs = loader.load()
            content = docs[0].page_content[:1000] if docs else "No content found"
            return f"Webpage Content : \n{content}"
        except Exception as e:
            print(f"Scrape error : {e}")
            return f"Scrape error : {e}"
@tool
def calculate(expression:str)->str:
        """
        Perform mathematical calculations
        
        Args:
            expression: Mathematical expression
            
        Returns:
            Calculation result
        """
        try:
            print(f"Calculating: {expression}")
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            print(f"Calculation error: {e}")
            return f"Calculation error: {str(e)}"

my_tools = [google_web_search, duck_duck_web_search, web_scrape, calculate]


if __name__ == "__main__":

    # Example usage
    research_tools = my_tools[0]
    query = "What is capital of pakistan?"
    print("Query:",query)
    print("Results of Web Search Tool :",research_tools.invoke(query))
   