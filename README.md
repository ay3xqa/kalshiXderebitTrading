# Kalshi Tading
Tools for Algorithmic Trading


Setup
----
1. `cd server`: navigate to server directory
2. `venv python -m venv`: create a virtual environment in `server` directory
3. `venv/Scripts/activate`: activate the virtual environment (Windows)
4. `source ./venv/bin/activate`: activate the virtual environment (MacOS)
5. `pip install -r requirements.txt`: to install dependencies from `requirements.txt` in the `server` directory
6. `export KALSHI_ACCESS_KEY=<your_key>`: to set your kalshi access key as an envrionment variable
7. Name your .key file `kalshi-key.key` and place it in the `server` directory
8. Navigate to `client` directory
9. `npm install`: install npm packages

Note: use pip3 or python3 in place of pip and python if neccessary


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
