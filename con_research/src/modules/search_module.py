from con_research.src.modules.imports import *
class SerperDevToolSchema(BaseModel):
    """Input for TXTSearchTool."""
    search_query: str = Field(..., description="Mandatory search query you want to use to search the internet")

class SerperDevTool():
    name: str = "Search the internet"
    description: str = "A tool that can be used to semantic search a query from a txt's content."
    args_schema: Type[BaseModel] = SerperDevToolSchema
    search_url: str = "https://google.serper.dev/search"
    n_results: int = None

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        payload = json.dumps({"q": search_query})
        headers = {
            'X-API-KEY': os.environ["SERPER_API_KEY"],
            'content-type': 'application/json'
        }
        response = requests.request("POST", self.search_url, headers=headers, data=payload)
        results = response.json()
        if 'organic' in results:
            results = results['organic']
            urls = []
            for result in results:
                try:
                    urls.append(result['link'])  # Only extract the URL
                except KeyError:
                    pass

            # Limit to only the first two URLs
            urls = urls[:1]

            return urls
        else:
            return results
