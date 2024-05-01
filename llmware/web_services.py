
# Copyright 2023 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.


""" The web_services module implements classes to enable integrated access to popular web services within
LLMWare pipelines. """


import logging
import os
import shutil


from llmware.exceptions import LLMWareException
from llmware.configs import LLMWareConfig


class WikiKnowledgeBase:

    """ WikiKnowledgeBase implements Wikipedia API """

    def __init__(self):

        # importing here to suppress log warnings produced by urllib3
        import urllib3
        urllib3.disable_warnings()

        self.user_agent = "Examples/3.0"

        try:
            from wikipediaapi import Wikipedia, ExtractFormat
        except ImportError:
            raise LLMWareException(message="Exception: pip install `wikipediaapi` required.")

        self.wiki = Wikipedia(user_agent=self.user_agent, extract_format=ExtractFormat.WIKI, verify=False)
        self.wiki_search_api_url = 'http://en.wikipedia.org/w/api.php'

    def get_article(self, article_name):

        article_response = {"title": "", "summary": "", "text": ""}

        try:
            page_py = self.wiki.page(article_name)

            if page_py.exists():

                logging.info("update: page_py - %s - %s", page_py.title, page_py.summary)
                logging.info("update: text - %s ", page_py.text)

                article_response = {"title": page_py.title, "summary": page_py.summary, "text": page_py.text}

            else:
                logging.info("update: connected with Wikipedia - selected article does not exist - %s ", article_name)

        except:
            logging.error("error: could not retrieve wikipedia article - please try again")

        return article_response

    def search_wikipedia(self, query, result_count=10, suggestion=False):

        # output result
        output = []

        # search params passed to the wikipedia api
        search_params = {'list': 'search', 'srprop': '', 'srlimit': result_count, 'srsearch': query,
                         'format': 'json', 'action': 'query'}

        if suggestion: search_params['srinfo'] = 'suggestion'

        headers = {'User-Agent': self.user_agent}

        try:
            import requests
            r = requests.get(self.wiki_search_api_url, params=search_params, headers=headers, verify=False)

            for i, title in enumerate(r.json()["query"]["search"]):

                logging.info("update:  wiki results - %s - %s", i, title)

                new_entry = {"num": i, "title": title["title"], "pageid": title["pageid"]}
                output.append(new_entry)

        except:
            logging.error("error: could not connect with Wikipedia to retrieve search results")

        return output


class YFinance:

    """ YFinance class implements the Yahoo Finance API. """

    def __init__(self, ticker=None):

        """
        Widely used Yahoo Finance API - key object = "
        TickerObj = yahooFinance.Ticker("META")
        print("All Info : ", TickerObj.info)
        for keys, values in TickerObj.info.items():
            print("keys: ", keys, values)

        # display Company Sector
        print("Company Sector : ", TickerObj.info['sector'])

        # display Price Earnings Ratio
        print("Price Earnings Ratio : ", TickerObj.info['trailingPE'])

        # display Company Beta
        print(" Company Beta : ", TickerObj.info['beta'])
        print(" Financials : ", TickerObj.get_financials())
        """

        self.company_info = None

        self.financial_summary_keys = ["shortName", "symbol","marketCap", "totalRevenue", "ebitda", "revenueGrowth", "grossMargins",
                                   "freeCashflow", "priceToSalesTrailing12Months", "grossMargins","currency"]

        self.stock_summary_keys = ["shortName", "symbol", "exchange","bid", "ask", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "symbol",
                                   "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice",
                                   "returnOnAssets", "returnOnEquity", "trailingPE", "forwardPE", "volume",
                                   "forwardEps", "pegRatio", "currency"]

        self.risk_summary_keys = ["shortName","symbol", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
                                  "shortName", "longBusinessSummary"]

        self.company_summary_keys = ["shortName", "longName", "symbol", "marketCap", "companyOfficers", "website",
                                     "industry", "sector", "longBusinessSummary", "fullTimeEmployees"]

        self.keys = ["address1", "city", "state", "zip", "country", "phone","website","industry",
                     "industryDisp", "sector", "sectorDisp", "longBusinessSummary", "fullTimeEmployees",
                     "companyOfficers", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk",
                     "overallRisk", "previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose",
                     "regularMarketOpen", "regularMarketDayLow", "regularMarketDayHigh", "payoutRatio", "beta",
                     "trailingPE", "forwardPE", "volume", "regularMarketVolume", "averageVolume",
                     "averageVolume10days", "bid", "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow",
                     "fiftyTwoWeekHigh", "priceToSalesTrailing12Months", "fiftyDayAverage", "twoHundredDayAverage",
                     "trailingAnnualDividendRate", "trailingAnnualDividendYield", "currency", "enterpriseValue",
                     "profitMargins", "floatShares", "sharesOutstanding", "sharesShort", "sharesShortPriorMonth",
                     "sharesShortPreviousMonthDate", "dateShortInterest", "sharesPercentSharesOut",
                     "heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat",
                     "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd",
                     "nextFiscalYearEnd", "mostRecentQuarter", "earningsPerQuarterlyGrowth", "netIncomeToCommon",
                     "trailingEps", "forwardEps", "pegRatio", "enterpriseToRevenue", "enterpriseToEbitda",
                     "52WeekChange", "SandP52WeekChange", "exchange", "quoteType", "symbol", "underlyingSymbol",
                     "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                     "targetMedianPrice", "recommendationMean", "recommendationKey", "numberOfAnalystOpinions",
                     "totalCash", "totalCashPerShare", "ebitda", "totalDebt", "quickRatio", "currentRatio",
                     "totalRevenue", "debtToEquity", "revenuePerShare", "returnOnAssets" "returnOnEquity", "grossProfits",
                     "freeCashflow", "operatingCashflow", "earningsGrowth", "revenueGrowth", "grossMargins",
                     "ebitdaMargins", "operatingMargins", "financialCurrency", "trailingPegRatio"]

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        if ticker:
            self.company_info = yfinance.Ticker(ticker)
        else:
            self.company_info = None

    def ticker(self, company_ticker):

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        company_info = yfinance.Ticker(company_ticker)
        return company_info

    def get_company_summary(self, ticker=None):

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.company_summary_keys:
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info

    def get_financial_summary(self, ticker=None):

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.financial_summary_keys:
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info

    def get_stock_summary(self, ticker=None):

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        output_info = {}
        company_info = yfinance.Ticker(ticker).info
        for targets in self.stock_summary_keys:
            for keys,values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
        return output_info


class WebSiteParser:

    """ WebSiteParser implements a website-scraping parser.   It can be accessed directly, or in many cases, will
    be accessed through Parser or Library classes indirectly. """

    def __init__(self, url_or_fp, link="/", save_images=True, reset_img_folder=False, local_file_path=None,
                 from_file=False, text_only=False, unverified_context=False):

        try:
            from bs4 import BeautifulSoup
            import requests
            from urllib.request import urlopen, Request
        except ImportError:
            raise LLMWareException(message="Exception: to use WebSiteParser requires three additional Python "
                                           "dependencies via pip install:  bs4 (BeautifulSoup), requests, and "
                                           "urllib.request")

        #   note: for webscraping, unverified ssl are a common error
        #   to debug, if the risk environment is relatively low, set `unverified_context` = True
        self.unverified_context=unverified_context

        # by default, assume that url_or_fp is a url path
        self.url_main = url_or_fp

        # by default, will get images and links
        self.text_only = text_only

        # by passing link - provides option for recursive calls to website for internal links
        if link == "/":
            self.url_link = ""
        else:
            self.url_link = link

        self.url_base = self.url_main + self.url_link

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        if not local_file_path:
            # need to update this path
            self.local_dir = os.path.join(LLMWareConfig.get_llmware_path(), "process_website/")
        else:
            self.local_dir = local_file_path

        if reset_img_folder:
            if os.path.exists(self.local_dir):
                # important step to remove & clean out any old artifacts in the /tmp/ directory
                shutil.rmtree(self.local_dir)
            os.makedirs(self.local_dir, exist_ok=True)

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir, exist_ok=True)

        if from_file:
            # interpret url as file_path and file_name
            try:
                html = open(url_or_fp, encoding='utf-8-sig', errors='ignore').read()
                bs = BeautifulSoup(html, features="lxml")
                self.html = bs.findAll()
                success_code = 1
                self.text_only = True
            except:
                logging.error("error: WebSite parser- could not find html file to parse at %s ", url_or_fp)
                success_code = -1
                self.text_only = True
        else:
            # this is the most likely default case -interpret url_or_fp as url
            try:
                req = Request(self.url_base, headers={'User-Agent': 'Mozilla/5.0'},unverifiable=True)

                if self.unverified_context:
                    import ssl
                    ssl._create_default_https_context = ssl._create_unverified_context
                    html = urlopen(req).read()
                else:
                    html = urlopen(req).read()

                bs = BeautifulSoup(html, features="lxml")

                self.bs = bs
                self.html = bs.findAll()

                out_str = ""
                for x in self.html:
                    out_str += str(x) + " "

                with open(os.path.join(self.local_dir, "my_website.html"), "w", encoding='utf-8') as f:
                    f.write(out_str)
                f.close()

                success_code = 1

            except Exception as e:
                success_code = -1
                raise LLMWareException(message=f"Exception: website_parser could not connect to website - "
                                               f"caught error - {e}.  Two suggested fixes: \n"
                                               f"1.  Update your certificates in the Python path, e.g., "
                                               f"'Install Certificates.command'\n"
                                               f"2.  Set unverified_context=True in the constructor for "
                                               f"WebSiteParser.\n"
                                               f"Note: it is also possible that the website does not exist, "
                                               f"or that it is restricted and rejecting your request for any "
                                               f"number of reasons.")

        self.save_images = save_images
        self.image_counter = 0
        self.links = []
        self.mc = None
        self.entries = None
        self.core_index = []
        self.header_text = []
        self.internal_links = []
        self.external_links = []
        self.other_links = []

        # meta-data expected in library add process
        self.source = str(self.url_base)
        self.success_code = success_code

    def website_main_processor(self, img_start, output_index=True):

        """ Main processing of HTML scraped content and converting into blocks. """

        output = []
        counter = 0
        # by passing img_start explicitly- enables recursive calls to links/children sites
        img_counter = img_start

        long_running_string = ""

        # new all_text to remove duplications
        all_text = []

        internal_links = []
        external_links = []
        header_text = []
        unique_text_list = []
        unique_header_list = []

        last_text = ""
        last_header = ""

        text = ""

        for elements in self.html:

            content_found = 0
            img = ""
            img_success = 0
            img_url = ""
            img_name = ""

            link = ""
            link_type = ""

            # text = ""

            entry_type = "text"

            # if text only, then skip checks for images and links
            if not self.text_only:

                if "property" in elements.attrs:
                    if elements.attrs["property"] == "og:image":
                        if "content" in elements.attrs:

                            img_extension = elements["content"]
                            img_success, img, img_url, img_name = \
                                self.image_handler(img_extension, elements, img_counter)

                            if img_success == 1:
                                img_counter += 1
                                content_found += 1

                if "src" in elements.attrs:

                    img_extension = elements["src"]
                    img_success, img, img_url, img_name = self.image_handler(img_extension, elements, img_counter)

                    if img_success == 1:
                        img_counter += 1
                        content_found += 1

                if "href" in elements.attrs:

                    if elements.attrs["href"]:
                        link_success, link, link_type = self.link_handler(elements)
                        content_found += 1

                        if link_success == 0:
                            # skip .js files and other formatting in link crawling
                            # link_success == 0 if not .js // ==1 if .js file

                            if link_type == "internal":
                                if link != "/":
                                    if link not in internal_links:
                                        internal_links.append(link)

                            if link_type == "external":
                                external_links.append(link)

            # main check for text
            if elements.get_text():
                get_text = 1

                if elements.attrs == {}:
                    get_text = -1

                if "type" in elements.attrs:
                    # skip css and javascript
                    if elements.attrs["type"] == "text/css" or elements.attrs["type"] == "text/javascript":
                        get_text = -1

                if get_text == 1:

                    # text handler
                    s_out = ""

                    # alt for consideration to clean up string
                    # s_out += string.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ').replace('\t', ' ')

                    for string in elements.stripped_strings:
                        s_out += string + " "

                    # print("text: s_out - ", s_out, elements.attrs)

                    text += s_out

                    if text:
                        header_entry = []

                        if text not in unique_text_list:
                            unique_text_list.append(text)
                            content_found += 1
                            long_running_string += text + " "
                            last_text = text

                        if "h1" in elements.name:
                            header_entry = (counter, "h1", text)

                        if "h2" in elements.name:
                            header_entry = (counter, "h2", text)

                        if "h3" in elements.name:
                            header_entry = (counter, "h3", text)

                        if header_entry:
                            if text not in unique_header_list:
                                last_header = text
                                header_text.append(header_entry)
                                unique_header_list.append(text)

            # if looking for images and links, then prioritize in attribution
            if not self.text_only:
                if img and img_success == 1:
                    entry_type = "image"
                else:
                    if link:
                        entry_type = "link"
                    else:
                        if text:
                            entry_type = "text"
                        else:
                            content_found = 0
            else:
                entry_type = "text"

            if content_found > 0:
                master_index = (self.url_main, self.url_link, counter)
                if not text:
                    text = last_text

                entry = {"content_type": entry_type,
                         "text": text,
                         "image": {"image_name": img_name, "image_url": img_url},
                         "link": {"link_type": link_type, "link": link},
                         "master_index": master_index,
                         "last_header": last_header}

                # entry = (entry_type, text, (img_name, img_url), (link_type, link), master_index, last_header)

                counter += 1
                # save entry if image, or if (A) text > 50 and (B) not a dupe
                if entry_type == "image" or (len(text) > 50 and text not in all_text):
                    output.append(entry)
                    all_text.append(text)
                    text = ""

        self.image_counter = img_counter
        self.internal_links = internal_links
        self.external_links = external_links
        self.header_text = header_text

        if header_text:
            header_text_sorted = sorted(header_text, key=lambda x: x[1])
            self.header_text = header_text_sorted

        self.core_index = output
        self.entries = len(output)

        if not output_index:
            return len(output), img_counter

        return self.core_index

    def link_handler(self, elements):

        """ Handles processing of links found in main page content. """

        link_out = ""
        link_type = ""
        js_skip = 0

        if elements.attrs["href"].endswith(".js"):
            link_out = elements.attrs["href"]
            link_type = "js"
            js_skip = 1

        if elements.attrs["href"].endswith(".ico") or elements.attrs["href"].endswith(".ttf"):
            link_out = elements.attrs["href"]
            link_type = "other_formatting"
            js_skip = 1

        if elements.attrs["href"].endswith(".css"):
            link_out = elements.attrs["href"]
            link_type = "css"
            js_skip = 1

        if elements.attrs["href"].startswith(self.url_base):
            # save relative link only
            link_out = elements.attrs["href"][len(self.url_base):]
            link_type = "internal"

        if str(elements.attrs["href"])[0] == "/":
            # relative link
            if elements.attrs["href"]:
                if not elements.attrs["href"].startswith("//"):
                    link_out = elements.attrs["href"]
                    link_type = "internal"

        if elements.attrs["href"].startswith("https://") and \
                not elements.attrs["href"].startswith(self.url_base):
            # website but not the url_base - external link
            link_out = elements.attrs["href"]
            link_type = "external"

        return js_skip, link_out, link_type

    def image_handler(self, img_extension, elements, img_counter):

        """ Handles and processes images found in main content. """

        success = -1
        img_raw = []
        image_name = ""
        full_url = ""

        try:
            img_raw, response_code, full_url = self._request_image(img_extension, elements)

            if response_code == 200:

                if self.save_images:

                    # need to capture img type, e.g., .jpg
                    img_type = ""
                    if img_extension.endswith("png"): img_type = "png"
                    if img_extension.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                    if img_extension.endswith("tiff"): img_type = "tiff"
                    if img_extension.endswith("svg"): img_type = "svg"

                    # secondary check if not at end - break off at '?' query string
                    if img_type == "":
                        original_img_name = img_extension.split("/")[-1]
                        original_img_name = original_img_name.split("?")[0]
                        if original_img_name.endswith("png"): img_type = "png"
                        if original_img_name.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                        if original_img_name.endswith("tiff"): img_type = "tiff"
                        if original_img_name.endswith("svg"): img_type = "svg"

                    # only save image if valid img format found
                    if img_type in ("png", "jpg", "svg", "tiff"):
                        image_name = "image{}.{}".format(img_counter, img_type)
                        fp = self.local_dir + image_name
                        s = self._save_image(img_raw, fp)
                        success = 1

                    else:
                        logging.info("update:  WebSite -  found image OK but could not "
                                     "figure out img type: %s ", img_extension)

        except:
            logging.info("warning: WebSite - could not retrieve potential image: %s ", elements.attrs["src"])
            success = -1

        return success, img_raw, full_url, image_name

    def _save_image(self, img_raw, fp):

        """ Internal utility to save images found. """

        with open(fp, 'wb') as f:
            img_raw.decode_content = True
            shutil.copyfileobj(img_raw, f)

        return 0

    def _save_image_website(self, fp, img_num, doc_id, save_file_path):

        """ Internal utility for images. """

        # internal method to save image files and track counters

        img_type = img_num.split(".")[-1]
        img_core = img_num[len("image"):].split(".")[0]

        # image name of format:   image{{doc_ID}}_{{img_num}}.png
        new_img_name = "image" + str(doc_id) + "_" + str(img_core) + "." + img_type
        # new_img_name = "image" + str(library.image_ID) + "." + img_type
        created = 0

        img = open(os.path.join(fp, img_num), "rb").read()
        if img:
            f = open(os.path.join(save_file_path, new_img_name), "wb")
            f.write(img)
            f.close()
            created += 1

        return new_img_name, created

    # called by main handler
    def _request_image(self, img_extension, img):

        """ Retrieve images from links. """
        try:
            import requests
        except ImportError:
            raise LLMWareException(message="Exception: could not import `requests` library which is a required "
                                           "dependency for web parsing.")

        # relative link - refers back to main index page
        # check if url_main gives better performance than .url_base

        url_base = self.url_main
        # url_ext = img.attrs['src']
        url_ext = img_extension

        full_url = url_ext

        if url_ext:
            if url_ext.startswith("https:"):
                # this is an external link - just use the source
                full_url = url_ext

            if url_ext.startswith("/"):
                # relative ID - add url_base to get img

                full_url = url_base + url_ext

        r = requests.get(full_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})

        return r.raw, r.status_code, full_url

    # not called by the main handler - keep as direct callable method
    def get_all_links(self):

        """ Utility to retrieve all links. """

        internal_links = []
        external_links = []
        other_links = []
        js_links = []

        for content in self.html:

            found = 0
            js = 0

            if "href" in content.attrs:
                if content.attrs["href"]:

                    if content.attrs["href"].endswith(".js"):
                        js_links.append(content.attrs["href"])
                        js = 1

                    if content.attrs["href"].startswith(self.url_base):
                        # save relative link only
                        out = content.attrs["href"][len(self.url_base):]
                        internal_links.append(out)
                        found = 1

                    if str(content.attrs["href"])[0] == "/":
                        # relative link
                        out = content.attrs["href"]
                        if out:
                            # skip double //
                            if not out.startswith("//"):
                                internal_links.append(out)
                        found = 1

                    if content.attrs["href"].startswith("https://") and \
                            not content.attrs["href"].startswith(self.url_base):
                        # website but not the url_base - external link
                        out = content.attrs["href"]
                        external_links.append(out)
                        found = 1

                    if found == 0:
                        other_links.append(content.attrs["href"])

        self.internal_links = internal_links
        self.external_links = external_links
        self.other_links = other_links

        top_links = []

        for z in range(0, len(internal_links)):

            link_tokens = internal_links[z].split("/")
            for y in range(0, len(self.mc)):
                if self.mc[y][0].lower() in link_tokens:
                    if internal_links[z] not in top_links:
                        top_links.append(internal_links[z])
                    break

        link_results = {"internal_links": internal_links, "external_links": external_links,
                        "other_links": other_links, "top_links": top_links}

        return link_results

    # not called by main handler - keep as separate standalone method
    def get_all_img(self, save_dir):

        """ Utility to get all images from html pages. """

        counter = 0
        for content in self.html:
            counter += 1
            if "src" in content.attrs:
                if str(content).startswith("<img"):

                    if content.attrs["src"]:
                        try:
                            img_raw, response_code, full_url = self._request_image(content, self.url_base)

                            if response_code == 200:

                                # need to capture img type, e.g., .jpg
                                original_img_name = content.attrs["src"].split("/")[-1]
                                original_img_name = original_img_name.split("?")[0]
                                img_type = ""
                                if original_img_name.endswith(".png"):
                                    img_type = "png"
                                if original_img_name.endswith(".jpg"):
                                    img_type = "jpg"
                                if original_img_name.endswith(".svg"):
                                    img_type = "svg"
                                if img_type == "":
                                    img_type = original_img_name.split(".")[-1]

                                fp = save_dir + "img{}.{}".format(counter, img_type)
                                s = self._save_image(img_raw, fp)
                                counter += 1
                        except:
                            logging.error("error: failed to find image: %s ", content.attrs["src"])

        return 0

