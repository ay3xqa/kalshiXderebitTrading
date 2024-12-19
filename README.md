# Kalshi Tading
Tools for Algorithmic Trading


Setup
----
1. `pip install -r requirements.txt`: to install dependencies from `requirements.txt` in the `server` directory
2. `export KALSHI_ACCESS_KEY=<your_key>`: to set your kalshi access key as an envrionment variable
3. Name your .key file `kalshi-key.key` and place it in the `server` directory


Running the Model and Dashboard locally
----
Open up two terminals - one for the server and one for the client
#### Client Terminal
`cd client`
<br>
`npm start`

#### Server Terminal
`cd server`
<br>
`venv/Scripts/activate`
<br>
`python app.py`
