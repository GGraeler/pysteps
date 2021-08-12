#Carter Humphreys (up to line 77)

import requests
import urllib.request
import gzip
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def get_http_files(url, ext=''):
    """
    Returns list file listing from HTTP/HTTPS directory
    """
    # Get HTML page
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    
    # Get file listing
    files = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext) and 'latest' not in node.get('href')]
    return files

def iastate_ingest(date, vars):
    """
    doc string
    """
    # Get available files
    if isinstance(vars, list):
        files = []
        for var in vars:
            url = f'https://mtarchive.geol.iastate.edu/{date:%Y}/{date:%m}/{date:%d}/mrms/ncep/{var}/'
            files += get_http_files(url=url, ext='gz')
    else:
        url = f'https://mtarchive.geol.iastate.edu/{date:%Y}/{date:%m}/{date:%d}/mrms/ncep/{vars}/'
        files = get_http_files(url=url, ext='gz')
    return files

start_date=datetime(2017, 6, 1)
end_date=datetime(2017, 6, 30)

for a in range((end_date-start_date).days+1):  

    download_date=start_date+timedelta(days=a)

    return_filenames=iastate_ingest(download_date, 'PrecipRate')

   

    for url in return_filenames:

        path = f'/usr1/home/nas-qnap/MRMS/{download_date:%Y}/{download_date:%m}/{download_date:%d}'
        #path=f'/run/user/1001/gvfs/afp-volume:host=b74-116-qnap.local,user=anonymous,volume=Public/MRMS/{download_date:%Y}/{download_date:%m}/{download_date:%d}'

        file=url[url.rfind('/')+1:]

        # Check if file exists
        if Path(f'{path}/{file}').exists() == False:
            print(file)
        
            # Ensure directories are built
            Path(path).mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, f'{path}/{file}')
            # Decompress Gzip file
            with gzip.open(f'{path}/{file}', 'rb') as f_in:
                #localfile=localfile.replace('.gz', '')
                with open(f'{path}/MRMS_{file.replace(".gz", "")}', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
       
            # Remove compressed file
            #os.remove(f'{path}/{file}')
