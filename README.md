# Finance Project BOT
## For set up API see [FinanceProjectApi](https://github.com/zhenerBY/FinanceProjectApi)

## Run this commands to start project
>
### create env
> python -m venv env
>
> source env/bin/activate
### install requirements
> pip install -r requirements.txt
### fill .env file based ion .env.template

### start bot (infinity pooling)

#### - preparation
- uncomment string in FinanceProjectBot.py with tag "# BOT infinity_polling"
- comment strings in FinanceProjectBot.py with tag "# BOT webhook"
#### - run
> python FinanceProjectBot.py
## Build project with Docker-Compose
- go to [FinanceProjectDocker](https://github.com/zhenerBY/FinanceProjectDocker)