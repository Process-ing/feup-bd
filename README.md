# FEUP-BD

Repository for the project of the [Databases](https://sigarra.up.pt/feup/en/UCURR_GERAL.FICHA_UC_VIEW?pv_ocorrencia_id=520317) course, at [FEUP](https://sigarra.up.pt/feup/en/web_page.Inicial).

## Objectives of the Project

The goal of this project was to design, create and populate a database, from an adequate theme. This means creating the conceptual model (first delivery), converting it to a relational model and an SQL schema and populating the database with adequate data.

The theme that we chose was a database for a live video streaming service (inspired and heavily based on [Twitch](https://twitch.tv/)).

## Instructions to Run the Parser

1. Clone the repository
2. Follow [Twitch's API tutorial](https://dev.twitch.tv/docs/authentication/) to get a client ID and an app access token
3. Open `final-delivery/parser`
4. Place your client ID and your token where marked in `request.py`
5. Run the first script:
    ```
    python request.py ALL
    ```
6. (Optional) Fill a file `population_files/json/chat_messages.json` with possible chat messages (it should be a standard JavaScript object, whose keys are the streamer's names and the values are the lists with the respective chat messages)
7. Run the second script:
    ```
    python parse.py
    ```

## Tips and Tricks (for anyone doing a similar project)

 - When choosing a theme, if you want to fill the database with real information, find an API that works with the theme (if you don't find later, you're kind of screwed)
 - Using an API to populate the database is kind of easy. You just need the `request` module of Python to handle the requests for you
 - If you don't care about veracity, we strongly advise using the [Faker](https://faker.readthedocs.io/en/master/) module of Python, which generates random data, like names, emails and dates (the documentation is a little obscure, but, for most things, it works really well)

 ## Contributors

  - [Bruno Oliveira](https://github.com/Process-ing)
  - [João Mendes](https://github.com/The-Memechanic)
  - [Rodrigo Ribeiro](https://github.com/Rodrigo-up09)

## Results

  - First delivery (40%): 19.3/20
  - Final delivery (60%): 19.4/20

Grade: 19.4/20


