import requests
import pandas as pd
from tqdm import tqdm
import wikipediaapi
import re
import time

API_KEY = ''  # Replace with your TMDb API key
BASE_URL = 'https://api.themoviedb.org/3'

# Initialize an empty list to store movie data
movies_data = []

# Configure Wikipedia API client with custom user agent
user_agent = 'MyCrossRecommenderSystem (https://github.com/Forest904/RecommenderSystem; )'
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent=user_agent
)

# Possible section titles for plot summaries
plot_section_titles = ['Plot', 'Plot summary', 'Synopsis', 'Premise', 'Story']

def get_wikipedia_plot(title, release_year=None):
    plot = None
    # Try different variations of the title
    search_titles = [title]
    if release_year:
        search_titles.append(f"{title} ({release_year} film)")
        search_titles.append(f"{title} ({release_year})")
    search_titles.append(f"{title} (film)")
    search_titles.append(f"{title} (movie)")

    for search_title in search_titles:
        page_py = wiki_wiki.page(search_title)
        if page_py.exists():
            # Function to recursively search for plot section
            def find_plot_section(sections):
                for section in sections:
                    if section.title.strip().lower() in [s.lower() for s in plot_section_titles]:
                        return section.text.strip()
                    else:
                        result = find_plot_section(section.sections)
                        if result:
                            return result
                return None

            plot = find_plot_section(page_py.sections)
            if plot:
                # Clean the plot text
                plot = re.sub(r'\[\d+\]', '', plot)  # Remove citation numbers like [1], [2], etc.
                plot = plot.replace('[citation needed]', '').strip()
                return plot
        # Sleep briefly to be polite to Wikipedia servers
        time.sleep(0.1)
    return None

# First pass: Collect data
for page in tqdm(range(1, 2)):
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}")
        continue
    data = response.json()
    for movie in data['results']:
        movie_id = movie['id']
        title = movie['title']
        release_date = movie.get('release_date', '')
        release_year = release_date[:4] if release_date else None
        
        # Fetch detailed info for each movie
        detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        detail_response = requests.get(detail_url)
        if detail_response.status_code != 200:
            print(f"Failed to fetch details for movie ID {movie_id}")
            continue
        details = detail_response.json()
        
        # Director is part of credits, fetch them
        credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US"
        credits_response = requests.get(credits_url)
        if credits_response.status_code != 200:
            print(f"Failed to fetch credits for movie ID {movie_id}")
            continue
        credits = credits_response.json()
        
        # Get director's name
        director = None
        for crew_member in credits['crew']:
            if crew_member['job'] == 'Director':
                director = crew_member['name']
                break
        
        # Get genres
        genres = [genre['name'] for genre in details.get('genres', [])]

        # Fetch 'Plot' section from Wikipedia
        plot = None
        try:
            plot = get_wikipedia_plot(title, release_year)
        except Exception as e:
            print(f"Error fetching Wikipedia page for '{title}': {e}")
            plot = None
        
        movies_data.append({
            'Title': title,
            'Director': director,
            'Genres': ', '.join(genres),
            'Plot': plot,
            'Original Title': details.get('original_title', ''),
            'Release Year': release_year,
            'Movie ID': movie_id  # Save for later use
        })

# Second pass: Revisit entries with missing plots
print("\nStarting second pass to fill in missing plots...\n")
for movie in tqdm(movies_data):
    if not movie['Plot']:
        title = movie['Title']
        release_year = movie['Release Year']
        original_title = movie['Original Title']
        movie_id = movie['Movie ID']
        # Try alternative methods to get the plot
        try:
            # Try with original title if different
            if original_title and original_title != title:
                plot = get_wikipedia_plot(original_title, release_year)
                if plot:
                    movie['Plot'] = plot
                    continue
            # Try searching without the release year
            plot = get_wikipedia_plot(title)
            if plot:
                movie['Plot'] = plot
                continue
            # As a last resort, use TMDb overview
            detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
            detail_response = requests.get(detail_url)
            if detail_response.status_code == 200:
                details = detail_response.json()
                plot = details.get('overview', None)
                if plot:
                    movie['Plot'] = plot
            # Sleep briefly to be polite to the API servers
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching alternative plot for '{title}': {e}")
            continue

# Create a DataFrame and save to CSV
df = pd.DataFrame(movies_data)

# Add attribution note
attribution_note = "Plot summaries sourced from Wikipedia and TMDb. Wikipedia content is licensed under the Creative Commons Attribution-ShareAlike License."

# Save to CSV with the attribution note
df.to_csv('top_k_movies.csv', index=False)
print("Dataset saved to 'top_10000_movies_with_plots.csv'")
print("\nPlease remember to include the following attribution when using this dataset:")
print(attribution_note)
