from yamt import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

# uwsgi --enable-threads --protocol=http --socket 0.0.0.0:5000 -w app:app