# Players for the Intro to AI module

## Description of the game

You can find the rules of the game in ./le-fantom-de-l-opera_rules_fr.pdf

## To launch a game

1) start the server

2) python3.6 inspector.py

3) python3.6 random.fantom.py

## To test a player's winrate

1) pip install requirements.txt

2) at the top of test_runner.py, specify the location of your server and player files you wish the script to test
```
server_file =  "./server.py"
inspector_file =  "./random_inspector.py"
fantom_file =  "./random_fantom.py"
```  

3) python3 test_runner.py

The results will be outputted in a 'test_results' directory.