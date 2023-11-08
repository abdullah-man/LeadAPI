# contains code to extract information from RSS Feed - One feed at a time
import numpy as np
from extraction_processing import StringProc
from app.database.db_operations import DbOperation


def extractor(feed : str) -> dict:
    """
    Extracts information from a lead's message content received as RSS feed.
    """
    # Instantiating StringProc for string processing operations
    processor = StringProc()
    # embedded info extraction
    single_info_dict= processor.extract_info(feed)

    if 'skills' in single_info_dict.keys():# if skills found in the data
        # cleaning: skills
        skills = single_info_dict['skills']
        skills = processor.remove_extra_whitespaces(skills)
        single_info_dict['skills'] = skills

    ## Job description extraction and cleaning
    message_content = processor.extract_message_txt(feed)
    # remove html
    message_content = processor.strip_html(message_content)
    # remove URLs
    message_content = processor.strip_urls(message_content)
    # remove &amp and &nbsp
    message_content = processor.replace_amp(message_content)
    message_content = processor.replace_nbsp(message_content)
    # remove all extra whitespaces along with newlines etc
    message_content = processor.remove_all_extra_symbols(message_content)

    # adding extracted message into extracted info dict 
    single_info_dict['message'] = message_content

    # Hourly Range and Budget processing
    if "hourly_range" in single_info_dict.keys():
        single_info_dict = processor.hourly_split_modify(data=single_info_dict)
    elif "budget" in single_info_dict.keys():
        single_info_dict = processor.budget_modify(data=single_info_dict)

    # removing hourly_range from the dictionary, not needed as converted into from and to informaiton
    if 'hourly_range' in single_info_dict.keys():
        del single_info_dict['hourly_range']

    ## amending single_info_dict to contain all db fields for query generation and label prediction
    db_fields = ['posted_on', 'category', 'skills', 'country', 'message', 'hourly_from', 'hourly_to', 'budget', 'label']
    for key in db_fields: # if single_info_dict does not have the database field then add it with empty 
        if key in single_info_dict.keys():
            continue
        else:
            single_info_dict[key] = ""


    return single_info_dict
