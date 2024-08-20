from google_img_source_search import ReverseImageSearcher
import scraper

'''
Performs a reverse image search on scanned items.

Employs an unofficial ReverseImageSearcher to find sites and scrape pricing.
If no results are found, we employ Google's custom reverse search.
'''



if __name__ == '__main__':
    searcher = ReverseImageSearcher()
    res = searcher.search_by_file('./samples/waterbottle2-more.png')

    for search_item in res:
        print(f'Title: {search_item.page_title}')
        print(f'Site: {search_item.page_url}')
        print(f'Img: {search_item.image_url}\n')
    