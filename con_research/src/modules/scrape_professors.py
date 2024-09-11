import requests
from bs4 import BeautifulSoup

# Scraping a professor's profile page and checking their research areas
def scrape_professor_profile(url, interest_keywords):
    """
    Scrapes a specific professor's profile page and checks if the professor
    has research interests matching the provided keywords.
    """
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to retrieve content from {url}. Status code: {response.status_code}"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the Research areas section by finding the appropriate <h2> tag
    research_section = soup.find('h2', class_='skim-top', text="Research areas")
    
    if research_section:
        # Assuming the research areas are stored in the <p> tag below the <h2> tag
        research_areas = research_section.find_next('p').get_text(strip=True).lower()

        # Check if any of the interest keywords match the research areas
        if any(interest.lower() in research_areas for interest in interest_keywords):
            name = soup.find('h1').get_text(strip=True)  # Assuming professor's name is in the <h1> tag
            return {'Name': name, 'Research Areas': research_areas}
    
    return None

# Function to scrape multiple professors' profiles
def scrape_professors_by_research_area(professor_names, interest_keywords):
    """
    Iterates through a list of professor names, scrapes their profile pages,
    and returns professors with matching research areas.
    """
    base_url = "https://www.ntu.ac.uk/staff-profiles/education/"
    matching_professors = []

    for name in professor_names:
        # Splitting professor's first and last name to create the URL
        first_name, last_name = name.split()  # Assume professor names are provided as 'FirstName LastName'
        profile_url = f"{base_url}{first_name}{last_name}"  # Construct the profile URL
        profile_data = scrape_professor_profile(profile_url, interest_keywords)

        if profile_data:
            matching_professors.append(profile_data)

    return matching_professors if matching_professors else "No matching profiles found."

# Example usage:
professor_names = ["John Doe", "Jane Smith", "Emily Johnson"]  # List of professor names to scrape
interest_keywords = ["child development", "lifespan development", "diversity"]  # Research areas to filter by

# Run the scraping and print results
result = scrape_professors_by_research_area(professor_names, interest_keywords)
print(result)
