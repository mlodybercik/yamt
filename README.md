# YAMT
Yamt stands for _Yet Another Media Transcoder_ and it's an very basic fronted for ffmpeg written in Flask. For now, it's made purely for *nix systems.

Frontend made in Bootstrap 4, backend consists of custom scheduler and settings management. 

It's very much in development, that's why I am using the built-in flask server and by default databases are stored in `/tmp/`.

## Requirements
Yamt uses `ffmpeg` and `ffprobe` so you need them in you PATH variable. You need `pipenv` for package management, it should download all necessary packages, and the very much needed `python3.8`.

## Usage
```
git clone https://github,com/krzesu0/yamt
cd yamt/
pipenv install
export FLASK_APP=yamt
export FLASK_ENV=development
pipenv shell
flask create_database
flask run --ip 0.0.0.0 --no-reload
```

## Development
I am working on a static website with yamt frontend for you to check it out before you download. Go ahead and make an pull request and I'll check your code out.