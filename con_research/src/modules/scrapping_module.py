from con_research.src.modules.imports import *

class ContentScraper:
    @staticmethod
    def scrape_anything(url: str):
        """Determines the content type of the URL and scrapes it accordingly."""
        if url.lower().endswith('.pdf'):
            print('Reading pdf from the url...')
            return ContentScraper._extract_text_from_pdf_url(url)
        else:
            print('Extracting text from the url...')
            return ContentScraper._scrape_text_from_url(url)

    @staticmethod
    def _scrape_text_from_url(url: str):
        """Scrapes text from an HTML web page."""
        try:
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
            response = requests.get(url, headers={'User-Agent': user_agent})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text(separator=" ", strip=True)
                return page_text
            else:
                return f"Failed to retrieve the webpage: Status code {response.status_code}"
        except Exception as e:
            return f"Failed to retrieve the webpage: {e}"

    @staticmethod
    def _extract_text_from_pdf_url(url: str):
        """Extracts text from a PDF document."""
        try:
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
            request = urllib.request.Request(url, headers={'User-Agent': user_agent})
            response = urllib.request.urlopen(request).read()
            fb = BytesIO(response)

            resource_manager = PDFResourceManager()
            fake_file_handle = StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            for page in PDFPage.get_pages(fb, caching=True, check_extractable=True):
                page_interpreter.process_page(page)

            text = fake_file_handle.getvalue().replace(u'\xa0', u' ')
            fb.close()
            converter.close()
            fake_file_handle.close()
            return text
        except Exception as e:
            return f"Failed to retrieve the PDF document: {e}"
class FixedSeleniumScrapingSchema(BaseModel):
    """Input for SeleniumScrapingTool."""
    pass

class SeleniumScrapingSchema(FixedSeleniumScrapingSchema):
    """Input for SeleniumScrapingTool."""
    website_url: str = Field(..., description="Mandatory website url to read the file")
    css_element: str = Field(..., description="Mandatory css reference for element to scrape from the website")

class SeleniumScraping():
    name: str = "Read a website content"
    description: str = "Its used to read a website content."
    args_schema: Type[BaseModel] = SeleniumScrapingSchema
    website_url: Optional[str] = None
    driver: Optional[Any] = webdriver.Chrome
    cookie: Optional[dict] = None
    wait_time: Optional[int] = 10
    css_element: Optional[str] = None

    def __init__(self, website_url: Optional[str] = None, cookie: Optional[dict] = None, css_element: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if cookie is not None:
            self.cookie = cookie

        if css_element is not None:
            self.css_element = css_element

        if website_url is not None:
            self.website_url = website_url
            self.description = f"Its used to read {website_url}'s content."
            self.args_schema = FixedSeleniumScrapingSchema

    def _run(self, **kwargs: Any) -> str:
        website_url = kwargs.get('website_url', self.website_url)
        css_element = kwargs.get('css_element', self.css_element)

        # Check if the URL ends with .pdf
        if website_url.lower().endswith('.pdf'):
            print('Reading pdf from the url...')
            return ContentScraper._extract_text_from_pdf_url(website_url)
        else:
            try:
                print('Extracting text from the url...')
                driver = self._create_driver(website_url, self.cookie, self.wait_time)
                content = []
                if css_element is None or css_element.strip() == "":
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    content.append(body_text)
                else:
                    driver.find_elements(By.CSS_SELECTOR, css_element)
                    for element in driver.find_elements(By.CSS_SELECTOR, css_element):
                        content.append(element.text)
                driver.close()
                return "\n".join(content)
            except Exception as e:
                return f"Failed to extract content from the URL: {e}"

    def _create_driver(self, url, cookie, wait_time):
        options = Options()
        options.add_argument("--headless")
        driver = self.driver(options=options)
        driver.get(url)
        time.sleep(wait_time)
        if cookie:
            driver.add_cookie(cookie)
            time.sleep(wait_time)
            driver.get(url)
            time.sleep(wait_time)
        return driver

    def close(self):
        self.driver.close()


# New Function to Scrape Faculty Profiles Based on Interests
def scrape_faculty_page(url, interest_keywords):
    """
    Scrapes a university or conference page and returns information on faculty
    members who match the interest areas.
    """
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to retrieve content from {url}. Status code: {response.status_code}"

    soup = BeautifulSoup(response.content, 'html.parser')
    faculty_data = []

    # Adjust the selectors depending on the page's structure
    profiles = soup.find_all('div', class_='faculty-profile')

    for profile in profiles:
        name = profile.find('h3', class_='faculty-name').text.strip()
        description = profile.find('p', class_='faculty-description').text.strip().lower()
        
        # Check if the faculty member matches any of the provided interest keywords
        if any(interest in description for interest in interest_keywords):
            faculty_data.append({
                'Name': name,
                'Description': description
            })

    return faculty_data
