import re
import pandas as pd
from datetime import datetime

class StringProc:
    """
    This class contains methods for information extraction from passed string 
    and performing cleaning operations 
    """
    
    def extract_info(self, txt: str) -> dict:
        """
        Extracts information of Hourly Rate, Budget, Category, Skills, Country
        from the passed string and returns a dictionary with keys named after the
        aforementioned keywords and their respective values
        """
        raw_extract = re.findall(r"<b>(.*?)<br>|<b>(.*?)\n", txt)
        if len(raw_extract)==0: # if job does not have embedded information
            date_time_now = datetime.now()
            date_time_now = date_time_now.strftime("%d/%m/%Y %H:%M")
            return {'Posted On': date_time_now, 'Budget':'', 'Category':'', 'Country':'', 'Skills':''}

        raw_ext = [] # raw_extract has tuples that have null strings along with info - extracting relevant info into this list
        for tupl in raw_extract:
            for entry in tupl:
                if entry != '':
                    raw_ext.append(entry)

        extracted_dict = dict()
        for item in raw_ext:        
                if 'Budget</b>' in item:
                    value = item.split(":")[1] # split item on : select the info at index pos 1
                    value = value.strip()
                    extracted_dict['budget'] = value
                elif 'Hourly Range</b>' in item:
                    value = item.split(":")[1]
                    value = value.strip()
                    extracted_dict['hourly_range'] = value
                elif 'Skills</b>' in item:
                    value = item.split(":")[1]
                    value = value.strip()
                    extracted_dict['skills'] = value
                elif 'Category</b>' in item:
                    value = item.split(":")[1] 
                    value = value.strip()
                    extracted_dict['category'] = value
                elif 'Country</b>' in item:
                    value = item.split(":")[1] 
                    value = value.strip()
                    extracted_dict['country'] = value
                elif 'Posted On</b>' in item:
                    # finds first occurrence of : and slice to extract time. 
                    # As time also has : in it, so slicing on first occurrence of : instead
                    # of splitting on : 
                    value = item[item.find(":")+1 : ]
                    value = value.strip()
                    extracted_dict['posted_on'] = value
                    # print(value)
    
        return extracted_dict

    def strip_html(self, txt: str) -> str:
        """
        Removes html tags from the text - potentially removes any other text between <> symbols as well
        """
        return re.sub(r'<.*?>', "", txt)

    def strip_urls(self, txt: str) -> str:
        """
        Strips away the urls in the pased string
        """
        return re.sub(r'https?://\S+', "", txt)

    def extract_message_txt(self, txt: str) -> str:
        """
        Returns string from start to the first occurrence of bold tag <b>
        """
        return txt[:txt.find("<b>")]

    def remove_extra_whitespaces(self, text):
        """
        Only removes more than one space. Does not remove newline tab etc characters. 
        """
        return re.sub(r' +', ' ', text)

    def remove_all_extra_symbols(self, text):
        """
        Removes all extra whitespaces and some symbols along with newlines tabs etc
        """
        text = re.sub( '\+', ' ', text) # forgot exact meaning - related to multiple space removal
        return re.sub( '\s+', ' ', text).strip()

    def replace_amp(self, text):
        """
        Replaces &amp; with a space : " "
        """
        text = text.replace('&amp;', ' ')
        return text

    def replace_nbsp(self, text):
        """
        Replaces &amp; with a space : " "
        """
        text = text.replace('&nbsp;', ' ')
        return text
    
    def punctuation_remove(self, text):
        """
        Removes punctuation and special characters from the contents of passed column of dataframe
        """
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub( '\s+', ' ', text).strip()
        return text

    def price_modify(self, txt: str) -> float:
        """
        Strips away the dollar $ sign and , from the pased string which is representing
        price e.g $500 or $2,000 and returns a float value after type casting 
        """
        txt = re.sub(r'\$', "", txt)
        txt = re.sub(r',', "", txt)
        return txt
    
    def hourly_split_modify(self, data: dict)->dict:
        """Extracts Hourly from and Hourly to info from Hourly Range from the 
        passed dictionary object, modifies them by removing $ sign and , and
        add this info into dict object and returns it
        """
        try:
            price_range = data['hourly_range']
            price_range = price_range.split("-")
            for i, price in enumerate(price_range):
                price_range[i] = self.price_modify(price)
            data['hourly_from'] = float(price_range[0])
            data['hourly_to'] = float(price_range[1])
        except Exception as e: # exception occurs when split does not find - to split over i.e. empty Hourly Range
            data['hourly_from']  = ''
            data['hourly_to'] = ''
        
        return data


    def budget_modify(self, data: dict)->dict:
        """Reads Budget info from the passed dictionary object, modifies it by
        removing $ sign and ,
        """
        try:
            price_value = data['budget']
            if not(isinstance(price_value, float)): # if budget is not a float value, then modify it
                price_value = self.price_modify(price_value)
                price_value = float(price_value)
                data['budget'] = price_value
        except Exception as e: # exception occurs on float type casting of an empty string i.e. empty Budget price
            data['budget'] = '' 
        
        return data
    
    def emoji_remove(self, text : str) -> str:
        """
        Removes Emojis from passed string
        """
        emoj = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
                          "]+", re.UNICODE)
        return re.sub(emoj, '', text)



def populate_new_fields(dataframe: pd.DataFrame, mesg: list, embedded_info: list, ) -> pd.DataFrame:
        """
        Populates an empty passed pandas dataframe with values passed through mesg and embedded_info parameters
        and returns the altered dataframe object
        """
        # adding the message text into the dict
        for indx, dic_ in enumerate(embedded_info):
            dic_['message'] = mesg[indx]
            dataframe.loc[len(dataframe)] = dic_
        return dataframe

