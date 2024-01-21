# Marvel Champions image namer using OCR

Filtering app can be found in: [https://alaintxu.github.io/marvelcdb-filtering/](https://alaintxu.github.io/marvelcdb-filtering/)

This repo contains the app for identifying images and the images itself.

## Makin it work

* Copy any MC images (in spanish) to '/images/not_processed'.
* Copy the list of cards (in spanish) in json format to json folder.
* Update volume mount for json file in docker-compose.yml.

```yml
...
    volumes:
      - ./images:/app/images
      - ./jsons/cards_all_2023-11-28.json:/app/jsons/cards.json
...
```

* Execute docker-compose:

```bash
docker-compose up -d
```

* Enter [http://localhost:8001](http://localhost:8001)

## ToDo

* [ ] Search card manually.
* [x] Add code manually.
* [ ] Update cards.json with new cards.
* [ ] Could work for any language changing tesseract language.
* [x] Treat back images of cards. => done (not sure if working)
* [x] Rotate cards before moving => done
* [x] Transform cards to webp. => done
