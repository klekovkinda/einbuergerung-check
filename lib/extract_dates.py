from bs4 import BeautifulSoup


def extract_available_dates(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    available_dates = []
    for cell in soup.find_all('td', class_='buchbar'):
        link = cell.find('a')
        if link:
            title = link.get('title', '')
            href = link.get('href', '')
            if title and href:
                available_dates.append(title.split(' ')[0])

    return available_dates
