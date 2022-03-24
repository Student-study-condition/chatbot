# Chat bot
This is a chat bot for the connected system, 
This chatbot has a register device in their ibm cloudant and recorded the following condition
- Temperature
- Humidity
- Light intensity
- Sound intensity

The bot can recommended user if the new study location is a good place to study by comparing the intended study location statistic with the new study location.

## Requirements for running bot locally
- python
- docker (optional)
### python dependency
- [telegram](https://github.com/python-telegram-bot/python-telegram-bot) for connect with telegram Api
- [pythondotenv](https://pypi.org/project/python-dotenv/) for using environment variable
- [pandas](https://pandas.pydata.org/) for modifying data from the db
- [numpy](https://numpy.org/doc/stable/index.html) for statistical analysis

### Environment variable
The environment variable example is on the github. Just change the .env.format file to .env. Then alter <your_...> to your credentail
- APP_TOKEN: token from telegram [bot-father](https://telegram.me/BotFather)
- CLOUDANT_URL
- CLOUDANT_APIKEY
- CLOUDANT_HOST
- CLOUDANT_SVC

### Running on the localhost
#### Activate virtual env
Linux / iOS
```
python3 -m venv venv
source venv/bin/activate
```
Windows
```
python -m venv venv
venv\Scripts\activate
```

#### run the bot on the localhost
```
python beta-bot.py
```

#### run the bot using docker container
```
Docker build -t docker name
```
- Then go to the docker desktop application and run the built docker image
- The bot should be ready to go