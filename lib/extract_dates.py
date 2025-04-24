import os
from bs4 import BeautifulSoup

class AvailableDate:
    def __init__(self, title, link):
        self.title = title
        self.link = link

    def __eq__(self, other):
        if not isinstance(other, AvailableDate):
            return False
        return self.title == other.title and self.link == other.link

    def __hash__(self):
        return hash((self.title, self.link))

    def __repr__(self):
        return f"AvailableDate(title='{self.title}', link='{self.link}')"

def extract_available_dates(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    available_dates = []
    for cell in soup.find_all('td', class_='buchbar'):
        link = cell.find('a')
        if link:
            title = link.get('title', '')
            href = link.get('href', '')
            if title and href:
                available_dates.append(AvailableDate(title, href))

    return available_dates

if __name__ == "__main__":
    html_folder = '/Users/dmitry.klekovkin/Workspace/source/einburgerung-check/html/'
    for filename in os.listdir(html_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(html_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            dates = extract_available_dates(html_content)
            print(f"Available dates for appointments in {filename}:")
            for date in dates:
                print(date)
