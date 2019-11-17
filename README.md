# Simple http server
With one available url for converting USD to RUB


## Getting Started

These instructions will get you a copy of the project up and running on your machine for development and testing purposes.

### Prerequisites

Install required system packages.

```
$ sudo apt-get update
$ sudo apt-get install git python3.7 python3.7-venv python3.7-dev build-essential python3-pip 
```

### Installing

Create base directory for project and venv and go to it
```
$ mkdir -p ~/.envs && cd $_
```

Create venv
```
$ python3.7 -m venv currency_conversion_env
```

Activate venv and clone repository
```
$ source currency_conversion_env/bin/activate
(currency_conversion_env) $ cd  && git clone https://github.com/etetin/currency_conversion.git
```

Move into project directory
```
(currency_conversion_env) $ cd currency_conversion
```

export env variable with value of app_id
```
(currency_conversion_env) $ export APP_ID=<your app id for openexchangerates.org>
```

Run server
```
(currency_conversion_env) $ python server.py
```

If you wanna specify your own host or port, you can pass this params in script:
```
(currency_conversion_env) $ python server.py --host 0.0.0.0 --port 5000
```


## TODO
console command for request
```
$ curl -d '{"amount": 3}' -X POST http://0.0.0.0:5000/convert 
```

about testing

if you wanna run server like background process, you can run it with using screen