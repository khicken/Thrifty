from google_img_source_search import ReverseImageSearcher

'''
Performs a reverse image search on scanned items
'''

if __name__ == '__main__':
    # image_url = ''

    searcher = ReverseImageSearcher()
    res = searcher.search_by_file('./samples/waterbottle.png')

    for search_item in res:
        print(f'Title: {search_item.page_title}')
        print(f'Site: {search_item.page_url}')
        print(f'Img: {search_item.image_url}\n')