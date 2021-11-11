#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import argparse

class DanScraper:
    def __init__(self,url,number_of_urls,extensions,mailserver,domain):
        self.url = url
        self.urls = deque([self.url])
        self.number_of_urls = number_of_urls
        self.extensions = extensions
        self.mailserver = mailserver
        self.domain = domain

        self.scraped_urls = set()
        self.emails = set()
        self.pdf_links = set()


        self.count = 0

    def save_pdfs(self):
        
        for pdf_url in self.pdf_links:
            r = requests.get(pdf_url, allow_redirects=True)
            file_name = pdf_url.split("/")[-1]
            name =file_name[0:11] + ".pdf"
            open(name, 'wb').write(r.content)
    
    def save_emails(self):
        with open("emails.txt", "w") as file:
            for mail in self.emails:
                file.write(f"{mail}\n")
    def start(self):
        
        try:
            while len(self.urls):
                self.count += 1
                if self.count == self.number_of_urls:
                    break
                url = self.urls.popleft()
                self.scraped_urls.add(url)

                parts = urllib.parse.urlsplit(url)
                base_url = '{0.scheme}://{0.netloc}'.format(parts)

                path = url[:url.rfind('/')+1] if '/' in parts.path else url
                if parts.hostname not in url:
                    continue
                print('[%d] Processing %s' % (self.count, url))

                try:
                    response = requests.get(url)
                    if 'pdf' in url:
                        self.pdf_links.add(url)
                except:
                    continue
                    
                emails_update = set(re.findall(rf"[a-z0-9\.\-+_]+@{self.mailserver}\.{self.domain}", response.text, re.I))
            
                self.emails.update(emails_update)


                soup = BeautifulSoup(response.text, features="lxml")

                for anchor in soup.find_all("a"):
                    link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                    if link.startswith('/'):
                        link = base_url + link
                    elif not link.startswith('http'):
                        link = path + link
                    if not link in self.urls and not link in self.scraped_urls:
                        self.urls.append(link)



            self.save_pdfs()
            self.save_emails()
        except KeyboardInterrupt:
            print('[-] Closing!')



if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="DanScraper.py", epilog=" == Nothing Can Be Hide from Dan's Scraper ==", usage="DanScraper.py  -u https://SomeWebSite.com -m gmail -d com -x pdf -n 3000", prefix_chars='-', add_help=True)

    parser.add_argument('-u', action='store', metavar='URL', type=str, help='Target URL.\tExample: https://site.com', required=True)
    parser.add_argument('-m', action='store', metavar='MailServer', type=str, help='Mail Server \tExample: [gmail|yahoo]', required=True)
    parser.add_argument('-d', action='store', metavar='Domain', type=str, help='Domain \tExample: [bg|com]', required=True)
    parser.add_argument('-x', action='store', metavar='Extensions', type=str, help='Extensions separated by a comma.\tExample: pdf,txt,doc')

    parser.add_argument('-n', action='store', metavar='NumberOfUrl', type=int, default=1000)
    parser.add_argument('-v', action='version', version='DanScraper - v1.0', help='Prints the version of DanScraper.py')

    args = parser.parse_args()

    if not args.u or not args.m or not args.d:
        print('[!] You must specify target Domain.\n')
        print(parser.print_help())
        exit()
  
    scraper = DanScraper(args.u,args.n,args.x,args.m,args.d)
    scraper.start()


