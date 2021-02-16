from routes import app, db

if __name__ == '__main__':
    db.create_all() #pragma no cover
    app.run(debug=True) #pragma no cover
