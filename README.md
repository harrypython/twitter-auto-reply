# twitter-auto-reply

Reply the first tweet result from a search using Firefox and Selenium.

## Clone the repo:
```bash 
git clone https://github.com/harrypython/twitter-auto-reply.git
cd twitter-auto-reply
```  
## Install the requirements: 
```bash 
pip install -r requirements.txt
```  

## Config file: config.json

```json
{
   "username":"your-twitter-username",
   "password":"your-twitter-password",
   "otp":"your-one-time-password-if-you-use",
   "search":"the message you are searching",
   "message":"the reply message, can be a link",
   "min_replies":0,
   "min_faves":0,
   "min_retweets":0,
   "headless":0,
   "exclude_word":"word-that-will-not-be-show-in-the-results"
} 
```

## Usage

```bash
python twitter-auto-reply.py --config my-config-file.json
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[ GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)

