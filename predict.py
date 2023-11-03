import pickle
import numpy as np
# from extraction import single_info_dict


class Predict:
    """
    Contains methods to predict a lead
    """

    def encode_lead(self, data: dict) -> dict :
        """
        Takes a dictionary, integer encodes its categorical values, and returns it
        """
        # Encoding fields: category and country. 
        # hourly_ to and from and budget are in numeric form
        category_codes = {'Accounting': 0, 'Automation Testing': 1, 'Back-End Development': 2, 'Bookkeeping': 3, 'Business Analysis &amp; Strategy': 4, 'Business Applications Development': 5, 'CMS Development': 6, 'Coding Tutoring': 7, 'Community Management': 8, 'Data Engineering': 9, 'Data Entry': 10, 'Data Extraction': 11, 'Data Visualization': 12, 'Database Administration': 13, 'Database Development': 14, 'Desktop Software Development': 15, 'DevOps Engineering': 16, 'Development &amp; IT Project Management': 17, 'Digital Project Management': 18, 'Ecommerce Website Development': 19, 'Email, Phone &amp; Chat Support': 20, 'Executive Virtual Assistance': 21, 'Financial Analysis &amp; Modeling': 22, 'Financial Management/CFO': 23, 'Front-End Development': 24, 'Full Stack Development': 25, 'General Virtual Assistance': 26, 'Graphic Design': 27, 'HR Administration': 28, 'Instructional Design': 29, 'Logistics &amp; Supply Chain Management': 30, 'Manual Testing': 31, 'Mobile App Development': 32, 'Network Administration': 33, 'Other Digital Marketing': 34, 'Packaging Design': 35, 'Recruiting &amp; Talent Sourcing': 36, 'SEO': 37, 'Sales &amp; Business Development': 38, 'Scripting &amp; Automation': 39, 'Search Engine Marketing': 40, 'Solution Architecture': 41, 'Sourcing &amp; Procurement': 42, 'Systems Administration': 43, 'Systems Engineering': 44, 'Tech Support': 45, 'Training &amp; Development': 46, 'Web Design': 47}
        country_codes = {'Albania': 0, 'Algeria': 1, 'Andorra': 2, 'Australia': 3, 'Austria': 4, 'Bahrain': 5, 'Bangladesh': 6, 'Belgium': 7, 'Belize': 8, 'Bulgaria': 9, 'Burkina Faso': 10, 'Canada': 11, 'Chile': 12, 'China': 13, 'Colombia': 14, "Cote d'Ivoire": 15, 'Croatia': 16, 'Curacao': 17, 'Dominican Republic': 18, 'Egypt': 19, 'Estonia': 20, 'France': 21, 'French Polynesia': 22, 'Germany': 23, 'Ghana': 24, 'Guatemala': 25, 'Hong Kong': 26, 'India': 27, 'Indonesia': 28, 'Ireland': 29, 'Israel': 30, 'Italy': 31, 'Jordan': 32, 'Kenya': 33, 'Kuwait': 34, 'Latvia': 35, 'Lebanon': 36, 'Lithuania': 37, 'Luxembourg': 38, 'Madagascar': 39, 'Malaysia': 40, 'Malta': 41, 'Mauritius': 42, 'Mexico': 43, 'Morocco': 44, 'Myanmar': 45, 'Nepal': 46, 'Netherlands': 47, 'New Zealand': 48, 'Nigeria': 49, 'Norway': 50, 'Oman': 51, 'Pakistan': 52, 'Palestinian Territories': 53, 'Panama': 54, 'Peru': 55, 'Philippines': 56, 'Poland': 57, 'Portugal': 58, 'Puerto Rico': 59, 'Qatar': 60, 'Romania': 61, 'Rwanda': 62, 'Saudi Arabia': 63, 'Sierra Leone': 64, 'Singapore': 65, 'Somalia': 66, 'South Africa': 67, 'South Korea': 68, 'Spain': 69, 'Sri Lanka': 70, 'Suriname': 71, 'Sweden': 72, 'Switzerland': 73, 'Taiwan': 74, 'Tanzania': 75, 'Thailand': 76, 'Trinidad and Tobago': 77, 'Tunisia': 78, 'Turkey': 79, 'Uganda': 80, 'Ukraine': 81, 'United Arab Emirates': 82, 'United Kingdom': 83, 'United States': 84, 'United States Virgin Islands': 85, 'Vietnam': 86, 'Yemen': 87}

        # if empty fill with the most common one found in the data 
        # otherwise fill with encoding value
        category = data['category']
        country = data['country']
        budget = data['budget']
        hourly_from = data['hourly_from']
        hourly_to = data['hourly_to']

        if category == '':
            data['category'] = 25 # full stack development
        
        if country == '':
            data['country'] = 84 # united states
        
        if hourly_from == '':
            data['hourly_from'] = 0.0
        
        if hourly_to == '':
            data['hourly_to'] = 0.0
        
        if budget == '':
            data['budget'] = 0.0
        
        if category != '':
            code = category_codes[category]
            data['category'] = code
        
        if country != '':
            code = country_codes[country]
            data['country'] = code

        return data

    def vectorize_lead(self, data : dict) -> np.array:
        """
        Takes a dictionary object, vectorizes it, reshapes into 2D np array of shape: (1,5) and  returns it
        """
        # Vector item sequence [budget, hourly_from, hourly_to, encoded_country, encoded_category]
        vector = np.array([data['budget'], data['hourly_from'], data['hourly_to'], data['country'], data['category']])
        vector = vector.reshape(1, -1) # model requires the vector to be 2D in shape
        
        return vector
    
    def predict_lead(self, vector : np.array, ml_model : object) -> str:
        """
        Takes a vector of shape (1,5), 
        """
        lead_codes = {'Applied': 0, 'Rejected': 1}
        prediction = ml_model.predict(vector) # list is returned
        
        # inverting the prediction label to class name
        label = ""
        for key, val in lead_codes.items():
            if val == prediction[0]:
                label = key
        
        return label
