# The FineCast restAPI
The Finecast API is based on python 3 & Flask.


### Install
To install the server, please execute the following from your preferred cwd:

Clone repo
```
cd ~
git clone https://github.com/Cloudoki/finecast-api.git fapi
```

Move to `fapi` and install the dependencies
```
cd fapi
pip3 install -r requirements.txt
```

Create the .env file and populate
```
cp .env.example .env
nano .env
```

### Run
To run the server, please execute the following from the root env directory:

```
cd ../
python3 fapi
```

and open your browser:

[http://localhost:5000/v1](http://localhost:5000/v1)
