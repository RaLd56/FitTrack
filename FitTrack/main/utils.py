# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import time
import re


# class ProductSearchSession:
#     def __init__(self):
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  
#         self.driver = webdriver.Chrome(options=chrome_options)
#         self.url = 'https://health-diet.ru/calorie'
#         self.driver.get(self.url)
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Расширенная']")))
#         try:
#             fuller_search = self.driver.find_element(By.XPATH, "//*[text()='Расширенная']")
#             self.driver.execute_script("arguments[0].click();", fuller_search)
#         except Exception as e:
#             print(f"Error in page setup: {e}")
#             self.driver.quit()
    
#     def search_products(self, search_request):
#         try:
#             search_input = self.driver.find_element(By.ID, 't-search-food-top-menu')
#             search_input.clear()
#             search_input.send_keys(search_request)
#             search_input.send_keys(Keys.RETURN)
#             time.sleep(1.5)
#             WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.mzr-tree-node-sub-text')))
#             product_list = []
#             elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.mzr-tree-node')
#             for element in elements:
#                 product_list.append(element.text)
#             return product_list

#         except Exception as e:
#             return 404
    
#     def close(self):
#         self.driver.quit()


def send_verification_email(user, code):
    subject = 'Email Verification Code'
    html_message = render_to_string('main/verification_email.html', {'code': code})
    plain_message = strip_tags(html_message)
    from_email = 'fittrack_email@gmail.com'  
    to_email = user.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


def calculate_totals(meals):
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    
    calorie_pattern = re.compile(r'(\d+[.,]?\d*)\s*ккал', re.IGNORECASE)
    protein_pattern = re.compile(r'Б\s*(\d+\.?\d*)\s*г', re.IGNORECASE)
    fat_pattern = re.compile(r'Ж\s*(\d+\.?\d*)\s*г', re.IGNORECASE)
    carb_pattern = re.compile(r'У\s*(\d+\.?\d*)\s*г', re.IGNORECASE)

    for meal in meals:
        print(meal.meal_name)
        nutrition = meal.meal_nutrition
        quantity = meal.quantity

        
        calories = calorie_pattern.search(nutrition)
        print(calories)
        protein = protein_pattern.search(nutrition)
        print(protein)
        fat = fat_pattern.search(nutrition)
        print(fat)
        carbs = carb_pattern.search(nutrition)
        print(carbs)

        
        if calories:
            total_calories += float(calories.group(1).replace(',', '.')) * quantity / 100
        if protein:
            total_protein += float(protein.group(1)) * quantity / 100
        if fat:
            total_fat += float(fat.group(1)) * quantity / 100
        if carbs:
            total_carbs += float(carbs.group(1)) * quantity / 100

    return {
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
    }

