# Web_Development
A Repo dedicated to some of my full-stack web development projects.



## Books CS50 Web Programming with Python
An app that allows users to create an account, search for a book via year, isbn, title, or author, leave a rating and review and see other users ratings. This app will also display ratings from goodreads API.

![Gif showing of product features](./Books/images/books.gif)

Built with: 
- Python
- Flask
- Flask_Session
- Postgres
- SQL ALCHEMY
- Jinja
- Sass / CSS
- GoodReads.com API

### API
Along with this website, the app has a built in restful API that allows you to make a GET request with a book ISBN to route `/api/<string: isbn>` and it will return information such as title, author, year, review count and average rating. 

![Picture of API response](./Books/images/api.png)



## Chat
A simple chat application made to teach students about the library socket.io

![Gif showing of product features](./Chat/assets/chat.gif)


Built with:
- socket.io
- Node JS
- Express JS
- JavaScript
- HTML
- CSS







## CS50 Finance

This app allows users to login/register and "pretend" buy/sell stocks, check real time stock prices powered by iexcloud.io API and keep track of their portfolio.
This project is part of problem set 8 for my Harvard cs50 class.

Built with:
 - Python
 - Flask
 - Jinja
 - SQLite
 

### Login page:
![login page](./Finance/images/login.png?raw=true "login page example")



### Home/Portfolio page
![home page](./Finance/images/portfolio.png?raw=true "Portfolio page example")



### Sell Stocks Page
![sell page](./Finance/images/sell.png?raw=true "Sell page example")