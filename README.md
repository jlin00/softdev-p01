# Trivia Crack by Kirkland Meeseeks
  
## Team Roster
- Jackie Lin (project manager)  
- Junhee Lee (game developer)
- Michael Zhang (game developer)
- Amanda Zheng (user experience) 

## Abstract 
Our project utilizes RESTful APIs and a Bootstrap framework to create a login-based trivia game website. After registering for the site, users are able to play practice trivia questions on their own or play games with other users. There are two multiplayer modes: PVP and Team Relay. Users can choose to face off 1v1 in PVP to compete for money and points, or they can choose to play as a team in Team Relay. Leaderboards are created based on the score that users accumulate. The money obtained by users can be used to buy packs from the store, which contain collectible pictures that users can set as their profile picture.

## APIs Used
- [Open Trivia](https://docs.google.com/document/d/1yp2nicOExDYlrEfdvqspD17Kz5c-xMSWHudfmNjJgQ4/edit)
- [Wikipedia](https://docs.google.com/document/d/1KNf_h_Rysiftc88uZNZO4LMpAyQprUTSj-eg5CMz9a8/edit)
- [NASA](https://docs.google.com/document/d/1PWwglCaypRlHP-0URuF5s076vBoqEKQeNETeWADVaP4/edit)
- [Rick and Morty](https://docs.google.com/document/d/1oK0klhp__LHP9kxb3D70cbbI46i1mMnmDMI4y1XS3B4/edit)
- [Countries](https://docs.google.com/document/d/1C-umxnBAIUzQI9kLDaXG4-YbFsiOwwRTJ5c-DXAHTRM/edit?usp=drive_web&ouid=109502819417772013933)

## Launch Codes 
First, clone or download the project and navigate into the repository where it is stored. 
```
$ git clone git@github.com:jlin00/softdev-p01.git
$ cd softdev-p01/
```

Then, generate all the API keys necessary for this project. Navigate to the [NASA Open API](https://api.nasa.gov) page and generate a key. Inside the repository, run the following commands:
```
$ touch keys.txt
$ nano keys.txt
```
Copy and paste the API key you generated into the terminal. Then, hit [Ctrl+X], [Y], [Enter].  

Then, create a virtual environment like so:
```
$ python3 -m venv test
$ . ~/test/bin/activate
```

Install the required modules with the following command:
```
(test)$ pip install -r requirements.txt
```

Now, you can run the project!
```
(test)$ python3 app.py
```


