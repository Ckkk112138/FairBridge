# FairBridge
FairBridge System. This system contains a frontend Vue app and a backend Flask app. It should be used with NaaVRE https://github.com/QCDIS/NaaVRE to convert workflow components to RO-Crate.

## Start Frontend
Make sure you have npm on your computer.

Go to the frontend folder and run:
```shell
npm run build
```
Run with serv:
```shell
serve -s dist
```

## Start Backend:

Install the dependencies:
```shell
pip install -r  requirements.txt
```
Run Flask application:
```shell
flask run --host=0.0.0.0
```
