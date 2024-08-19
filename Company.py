import streamlit as st
import yaml
import pandas as pd
from itertools import combinations
from collections import defaultdict
from functools import reduce

st.set_page_config(
    page_title="Campaign Information",
    layout="wide"
)

# Define the values for dropdowns
occupations = [
    "Engineer", "Doctor", "Teacher", "Entrepreneur", "Banker",
    "Manager",  "Artist", "Chef", "Lawyer"
]
all_interests = [
    "Sports", "Music", "Travel", "Cooking", "Photography", "Reading",
    "Gardening", "Technology", "Fashion", "Art", "Fitness", "Movies",
    "Gaming", "Hiking", "Yoga", "Dancing", "Writing", "Cycling", "Electronics", "Painting"
]
categories = ["Beauty Products", "Books", "Watches", "Clothes", "Automobiles"]
cities = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai",
    "Kolkata", "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur",
    "Visakhapatnam", "Indore", "Thane", "Patna",
    "Vadodara", "Agra", "Varanasi", "Srinagar"
]

def load_customer_data():
    customers = pd.read_csv(r"Data_Set.csv")
    return customers

def save_filtered_customers_to_csv(filtered_customers, file_path=r"filtered_customer.csv"):
    filtered_customers.to_csv(file_path, index=False)

def create_co_occurrence_matrix(interests_list):
    co_occurrence = defaultdict(int)
    for interests in interests_list:
        interests = interests.lower().split(', ')
        for a, b in combinations(interests, 2):
            co_occurrence[(a, b)] += 1
            co_occurrence[(b, a)] += 1
    return co_occurrence

def find_related_interests(selected_interest, co_occurrence, top_n=3):
    related = {k: v for k, v in co_occurrence.items() if k[0] == selected_interest.lower()}
    sorted_related = sorted(related.items(), key=lambda item: item[1], reverse=True)
    return [interest for (interest, _), _ in sorted_related[:top_n]]

def filter_customers(customers, filters, co_occurrence):
    filter_conditions = []

    if 'age_range' in filters:
        filter_conditions.append((customers['Age'] >= filters['age_range'][0]) & (customers['Age'] <= filters['age_range'][1]))
    if 'gender' in filters:
        filter_conditions.append((customers['Gender'] == filters['gender']))
    if 'location' in filters:
        filter_conditions.append((customers['Location'] == filters['location']))
    if 'category' in filters:
        filter_conditions.append((customers['Category'] == filters['category']))
    if 'interest' in filters and 'Interest' in customers.columns:
        related_interests = find_related_interests(filters['interest'], co_occurrence)
        filter_conditions.append(customers['Interest'].str.contains(filters['interest'], case=False) |
                                 customers['Interest'].str.contains('|'.join(related_interests), case=False))

    if len(filter_conditions) > 3:
        return pd.DataFrame(), "Maximum 3 factors can be considered for filtering."

    if filter_conditions:
        filtered_customers = customers[
            reduce(lambda x, y: x & y, filter_conditions)
        ]
    else:
        filtered_customers = customers

    return filtered_customers, None

def company_profile_generator():
    with open(r'/home/arun-kumar-arali/Downloads/Epsilon-Project/tasks.yaml', 'r') as file:
        tasks = yaml.safe_load(file)

    st.title("Campaign Information")

    # Attributes
    company_name = st.text_input("Company Name", key="company_name")
    campaign_name = st.text_input("Campaign Name", key="campaign_name")
    product_name = st.text_input("Product Name", key="product_name")
    product_category = st.text_input("Product Category", key="product_category")
    product_highlight = st.text_input("Product Highlight", key="product_highlight")
    coupon_code = st.text_input("Coupon code", key="coupon_code")
    discount_applied = st.text_input("Discount offered!", key="discount_applied")
    support_email = st.text_input("Support Email", key="support_email")
    support_phone = st.text_input("Support Phone", key="support_phone")

    st.header("Target User Filters")
    filters = {}
    if st.checkbox("Filter by Age Range"):
        filters['age_range'] = st.slider("Select age range", min_value=0, max_value=100, value=(0, 100), step=1, key="filter_age_range")
    if st.checkbox("Filter by Gender"):
        filters['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"], key="filter_gender")
    if st.checkbox("Filter by Location"):
        filters['location'] = st.selectbox("Location", cities, key="filter_location")
    if st.checkbox("Filter by Category"):
        filters['category'] = st.selectbox("Product Category", categories, key="filter_category")
    if st.checkbox("Filter by Interest"):
        filters['interest'] = st.selectbox("User Interests", all_interests, key="filter_interest")

    if len(filters) > 3:
        st.error("Maximum 3 factors can be considered for filtering. Please uncheck one of the options.")
        return

    if st.button("👉 Generate Profile and Run 👈"):
        description_template = (
            'You are given detailed campaign information to generate a comprehensive report about the campaign, including a blend of user '
            'and company information. The attributes include company name, product name, product category, product highlight, target age of user, '
            'target country, user interests, and user income level. Use the information given about the campaign under the campaign_profile field '
            'to generate the report. '
            'Campaign profile: Company Name: {company_name}, Product Name: {product_name}, Product Category: {product_category}, Product highlights: {product_highlight},'
            'Coupon Code: {coupon_code}, Discount applied: {discount_applied}, Campaign Name: {campaign_name}, Target user age range: {min_age}-{max_age}, Target user Location: {target_location}, ' 
            'Target user interests: {user_interests}, Premium subscription customer: {premium_customer}, '
            'Target user occupation: {occupation}, User marital Status: {marital_status}, Target user income Level: {income_level}, '
            'Support Email: {support_email}, Support Phone: {support_phone}'
        )

        tasks['campaign_information_generation_task']['description'] = description_template.format(
            company_name=company_name,
            product_name=product_name,
            product_category=product_category,
            product_highlight=', '.join(product_highlight.split(',')),
            coupon_code=coupon_code,
            campaign_name=campaign_name,
            discount_applied=discount_applied,
            min_age=filters.get('age_range', (0, 100))[0],
            max_age=filters.get('age_range', (0, 100))[1],
            target_location=filters.get('location', 'Not specified'),
            user_interests=filters.get('interest', 'Not specified'),
            occupation="Not specified",
            marital_status="Not specified",
            income_level="Not specified",
            premium_customer="Not specified",
            support_email=support_email,
            support_phone=support_phone
        )
        with open(r'/home/arun-kumar-arali/Downloads/Epsilon-Project/tasks.yaml','w') as file:
            yaml.dump(tasks, file, default_flow_style=False, allow_unicode=True)
        st.success("✔️ User profile updated and task configuration saved!")

        customers = load_customer_data()

        # Create co-occurrence matrix based on the interests in the dataset
        interests_list = customers['Interest'].dropna().tolist()
        co_occurrence = create_co_occurrence_matrix(interests_list)

        filtered_customers, error_message = filter_customers(customers, filters, co_occurrence)
        if error_message:
            st.error(error_message)
        elif not filtered_customers.empty:
            save_filtered_customers_to_csv(filtered_customers, r"filtered_customer.csv")
            st.success("✔️ Filtered customers saved!")
        else:
            st.warning("No customers matched the filtering criteria.")

if __name__ == "__main__":
    company_profile_generator()
