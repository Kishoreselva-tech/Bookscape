import pymysql
import pandas as pd
import streamlit as st
from pymysql.cursors import DictCursor

# Function to establish database connection
def connect_to_database():
    try:
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="lion",
            database="books",
            autocommit=True
        )
        mycursor = mydb.cursor(DictCursor)
        return mydb, mycursor
    except pymysql.MySQLError as err:
        st.error(f"Error connecting to the database: {err}")
        return None, None

def run_query(mycursor, query, params=None):
    try:
        mycursor.execute(query, params)
        results = mycursor.fetchall()
        if not results:
            st.warning("No results found for this query.")
            return None
        columns = [i[0] for i in mycursor.description]
        df = pd.DataFrame(results, columns=columns)
        return df
    except pymysql.MySQLError as err:
        st.error(f"Error executing query: {err}")
        return None

# Streamlit App
st.title("BookScape Explorer :book:")

# Sidebar Navigation
choice = st.sidebar.selectbox("Navigation", ["Home", "Explore Books", "Analytics"])

if choice == "Home":
    st.header("Welcome to BookScape Explorer! 🌟")
    st.markdown("""
    - 📚 Explore a vast collection of books.
    - 🔍 Search by title, author, or genre.
    - 🌟 Analyze books with advanced tools.
    """)

elif choice == "Explore Books":
    mydb, mycursor = connect_to_database()
    if mydb and mycursor:
        keyword = st.text_input("Search for books by keyword:")
        if keyword:
            query = "SELECT * FROM history_book WHERE book_title LIKE %s;"
            results_df = run_query(mycursor, query, ('%' + keyword + '%',))
            if results_df is not None:
                st.dataframe(results_df)
        mycursor.close()
        mydb.close()

elif choice == "Analytics":
    mydb, mycursor = connect_to_database()
    if mydb and mycursor:
        question = st.selectbox("Select an Analytics Query:", [
            "1. Check Availability of eBooks vs Physical Books",
            "2. Find the Publisher with the Most Books Published",
            "3. Identify the Publisher with the Highest Average Rating",
            "4. Get the Top 5 Most Expensive Books by Retail Price",
            "5. Find Books Published After 2010 with at Least 500 Pages",
            "6. List Books with Discounts Greater than 20%",
            "7. Find the Average Page Count for eBooks vs Physical Books",
            "8. Find the Top 3 Authors with the Most Books",
            "9. List Publishers with More than 10 Books",
            "10. Find the Average Page Count for Each Category",
            "11. Retrieve Books with More than 3 Authors",
            "12. Books with Ratings Count Greater Than the Average",
            "13. Books with the Same Author Published in the Same Year",
            "14. Books with a Specific Keyword in the Title",
            "15. Year with the Highest Average Book Price",
            "16. Count Authors Who Published 3 Consecutive Years",
            "17. Authors Who Have Published Books in the Same Year Under Different Publishers",
            "18. Average Retail Price of eBooks vs Physical Books",
            "19. Books with Ratings More than 2 Standard Deviations Away from Average Rating",
            "20. Publisher with Highest Average Rating (More Than 10 Books)"
        ])

        # Dictionary for queries
        queries = {
            "1. Check Availability of eBooks vs Physical Books": "SELECT isEbook, COUNT(*) AS book_count FROM history_book GROUP BY isEbook;",
            "2. Find the Publisher with the Most Books Published": "SELECT publisher, COUNT(*) AS book_count FROM history_book GROUP BY publisher ORDER BY book_count DESC LIMIT 1;",
            "3. Identify the Publisher with the Highest Average Rating": """
                SELECT publisher, AVG(averagerating) AS avg_rating 
                FROM history_book 
                GROUP BY publisher 
                ORDER BY avg_rating DESC 
                LIMIT 1;
            """,
            "4. Get the Top 5 Most Expensive Books by Retail Price": """
                SELECT book_title, amount_retailPrice 
                FROM history_book 
                ORDER BY amount_retailPrice DESC 
                LIMIT 5;
            """,
            "5. Find Books Published After 2010 with at Least 500 Pages": """
                SELECT book_title, year, pagecount 
                FROM history_book 
                WHERE year > 2010 AND pagecount >= 500;
            """,
            "6. List Books with Discounts Greater than 20%": """
                SELECT book_title, amount_listPrice, amount_retailPrice, 
                (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 AS discount_percentage 
                FROM history_book 
                WHERE amount_listPrice > 0 AND (amount_listPrice - amount_retailPrice) / amount_listPrice > 0.2;
            """,
            "7. Find the Average Page Count for eBooks vs Physical Books": """
                SELECT 
                CASE WHEN isebook = 1 THEN 'eBook' ELSE 'Physical Book' END AS book_type, 
                AVG(pagecount) AS avg_page_count 
                FROM history_book 
                GROUP BY isebook;
            """,
            "8. Find the Top 3 Authors with the Most Books": """
                SELECT book_authors, COUNT(*) AS book_count 
                FROM history_book 
                GROUP BY book_authors 
                ORDER BY book_count DESC 
                LIMIT 3;
            """,
            "9. List Publishers with More than 10 Books": """
                SELECT publisher, COUNT(*) AS book_count 
                FROM history_book 
                GROUP BY publisher 
                HAVING book_count > 10;
            """,
            "10. Find the Average Page Count for Each Category": """
                SELECT category, AVG(pagecount) AS avg_page_count 
                FROM history_book 
                GROUP BY category;
            """,
            "11. Retrieve Books with More than 3 Authors": """
                SELECT book_title, book_authors 
                FROM history_book 
                WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;
            """,
            "12. Books with Ratings Count Greater Than the Average": """
                SELECT book_title, ratings_count 
                FROM history_book 
                WHERE ratings_count > (SELECT AVG(ratings_count) FROM history_book);
            """,
            "13. Books with the Same Author Published in the Same Year": """
                SELECT book_title, book_authors, year 
                FROM history_book 
                WHERE book_authors IN (
                    SELECT book_authors 
                    FROM history_book 
                    GROUP BY book_authors, year 
                    HAVING COUNT(*) > 1
                );
            """,
            "14. Books with a Specific Keyword in the Title": "SELECT book_title FROM history_book WHERE book_title LIKE %s;",
            "15. Year with the Highest Average Book Price": """
                SELECT year, AVG(amount_retailPrice) AS avg_price 
                FROM history_book 
                GROUP BY year 
                ORDER BY avg_price DESC 
                LIMIT 1;
            """,
            "16. Count Authors Who Published 3 Consecutive Years": """
                SELECT book_authors, COUNT(DISTINCT year) AS year_count 
                FROM history_book 
                GROUP BY book_authors 
                HAVING year_count >= 3;
            """,
            "17. Authors Who Have Published Books in the Same Year Under Different Publishers": """
                SELECT book_authors, year, COUNT(DISTINCT publisher) AS publisher_count 
                FROM history_book 
                GROUP BY book_authors, year 
                HAVING publisher_count > 1;
            """,
            "18. Average Retail Price of eBooks vs Physical Books": """
                SELECT 
                CASE WHEN isebook = 1 THEN 'eBook' ELSE 'Physical Book' END AS book_type, 
                AVG(amount_retailPrice) AS avg_price 
                FROM history_book 
                GROUP BY isebook;
            """,
            "19. Books with Ratings More than 2 Standard Deviations Away from Average Rating": """
                SELECT book_title, averagerating 
                FROM history_book 
                WHERE ABS(averagerating - (SELECT AVG(averagerating) FROM history_book)) > 
                2 * (SELECT STD(averagerating) FROM history_book);
            """,
            "20. Publisher with Highest Average Rating (More Than 10 Books)": """
                SELECT publisher, AVG(averagerating) AS avg_rating 
                FROM history_book 
                GROUP BY publisher 
                HAVING COUNT(*) > 10 
                ORDER BY avg_rating DESC 
                LIMIT 1;
            """
        }

        query = queries.get(question)
        if query:
            if "%s" in query:  # For queries requiring input
                keyword = st.text_input("Enter Keyword:")
                if keyword:
                    results_df = run_query(mycursor, query, ('%' + keyword + '%',))
            else:
                results_df = run_query(mycursor, query)
            if results_df is not None:
                st.dataframe(results_df)
        mycursor.close()
        mydb.close()
