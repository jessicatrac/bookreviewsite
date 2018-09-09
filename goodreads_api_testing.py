# working with goodreads API to do the CS50W project 1... 
# Jessica Trac; August 2018
# 9781632168146

import requests

def main():

	isbns_user = input("What book?: ")
	book_res = requests.get("https://www.goodreads.com/book/review_counts.json", 
		params={"key": "0z74opx09u94JjbpeeUWg", "isbns": isbns_user})
	if book_res.status_code != 200:
		raise Exception("ERROR: API request unsuccessful.")
	book_data = book_res.json()
	book_rating = book_data["books"][0]["average_rating"]
	book_review = book_data["books"][0]["work_ratings_count"]
	print("There are %s reviews for this book" % book_review)
	print("The average rating is %s" % book_rating)
	#print(book_rating)

if __name__ == "__main__":
    main()