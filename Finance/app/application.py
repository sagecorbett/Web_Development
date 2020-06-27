import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, is_str_int

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash_query = db.execute("SELECT cash FROM users WHERE id = :id",
                            id=session["user_id"])[0]["cash"]

    portfolio_query = db.execute(
        "SELECT * FROM portfolio WHERE buyer_id = :id", id=session["user_id"])

    portfolio_data = []
    # get all data and put in dict and push to portfolio_data variable
    for share in portfolio_query:
        data = lookup(share['stock_name'])

        port_obj = {
            "symbol": share['stock_name'],
            "name": data['name'],
            "shares": share['shares'],
            "price": data['price'],
            "total": data['price'] * share['shares']
        }
        portfolio_data.append(port_obj)

    # loop through all stocks owned and add their current price to total
    total = 0
    for i in portfolio_data:
        total = total + i['total']

    # add the users total stock values and cash together
    total = total + cash_query

    print(portfolio_data)
    return render_template("index.html", data=portfolio_data, cash=cash_query, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # ensure user has enough money for this stock
        symbol = request.form.get("symbol")
        if not lookup(symbol):
            return apology("Sorry that symbol does not exist", 400)
        shares = request.form.get("shares")
        if not is_str_int(shares):
            return apology("Please enter a valid number.", 400)
        elif int(shares) < 1:
            return apology("Please enter a valid number.", 400)
        user_cash_lookup = db.execute("Select cash FROM users WHERE id = :id", id=session["user_id"])
        cash = user_cash_lookup[0]['cash']

        if lookup(symbol)['price'] * int(shares) > cash:
            return apology("Sorry you do not have enough money for this")
        else:
            # Check if the user currently has shares of this symbol
            current_shares = db.execute(
                "SELECT shares FROM portfolio WHERE buyer_id = :id AND stock_name = upper(:symbol)", id=session["user_id"], symbol=symbol)
            # If the user does not already have shares of this symbol we are going to inser it to the db
            if not current_shares:
                buy = db.execute("""
                INSERT INTO portfolio (
                    buyer_id,
                    shares,
                    price,
                    total,
                    stock_name
                    )
                VALUES (
                    :id,
                    :shares,
                    :price,
                    :total,
                    :stock
                    )
                    """,
                                 id=session["user_id"], shares=int(shares), price=lookup(symbol)['price'], total=lookup(symbol)['price'] * int(shares), stock=symbol.upper())
            # If the user has the shares of that symbol then we will update it accordingly
            else:
                update_shares = db.execute("""
                    UPDATE portfolio
                    SET shares = shares + :shares
                    WHERE stock_name = :stock
                    AND buyer_id = :id
                """, shares=shares, stock=symbol.upper(), id=session["user_id"])
            spent = lookup(symbol)['price'] * int(shares)
            spent_update = db.execute("UPDATE users SET cash = cash - :spent WHERE id = :id", spent=spent, id=session["user_id"])

            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    print(request.args.get("username"))
    result = db.execute("SELECT username FROM users WHERE username = :username", username=request.args.get("username"))
    if not result:
        print("it does not exists")
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session['user_id'])
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please make sure all forms are filled out", 400)

        symbol = lookup(symbol)
        if not symbol:
            return apology("Sorry that stock does not exist", 400)
        return render_template("stock.html", stock=symbol, price=format(symbol["price"], '.2f'))
    else:
        return render_template("quote.html")
    # return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        username_exist = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if not username or username_exist:
            return apology("Must have a username")

        if not password or not confirm:
            return apology("Make sure no fields are left blank")
        if not (password == confirm):
            return apology("Passwords do not match")

        hash = generate_password_hash(password)
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=username, hash=hash)

        if not result:
            return apology("That Username already exists")

        get_username_id = db.execute("SELECT id FROM users WHERE username = :username", username=username)
        if get_username_id:
            # session["user_id"] = get_username_id[0]["id"]
            return render_template("/login.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please select a symbol")
        shares = request.form.get("shares")
        # query the db for how many shares of the symbol this user has
        available_shares = db.execute(
            "SELECT shares FROM portfolio WHERE buyer_id = :id AND stock_name = :symbol", id=session["user_id"], symbol=symbol)
        # If the shares the user is trying to sell is bigger than available shares or shares is less than 1
        if int(shares) > int(available_shares[0]['shares']) or int(shares) < 1:
            return apology("You do not own enough shares")

        # get the current price of the stock
        current_price = lookup(symbol)

        # Update the users portfolio table
        update = db.execute("""
                    UPDATE portfolio
                    SET
                        price = price + :price,
                        shares = shares + :shares
                    WHERE buyer_id = :id
                    AND stock_name = :symbol""", price=-current_price["price"], shares=-int(shares), id=session["user_id"], symbol=symbol)

        # Take what the current price of the stock is and add it to the total cash of the user
        # current_cash = db.execute("""
        #                     SELECT cash
        #                     FROM users
        #                     WHERE id = :id
        # """, id=session["user_id"])

        set_cash = db.execute("""
                    UPDATE users
                    SET cash = cash + :cash
                    WHERE
                    id = :id
        """, id=session["user_id"], cash=current_price["price"] * int(shares))
        return redirect("/")
    else:
        symbol = db.execute("SELECT stock_name FROM portfolio WHERE buyer_id = :id", id=session["user_id"])
        return render_template("sell.html", data=symbol)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
