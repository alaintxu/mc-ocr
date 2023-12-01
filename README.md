# Marvel Champions image namer using OCR

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

* Treat back images of cards. => done (not sure if working)
* Rotate cards before moving => done
* Transform cards to webp. => done
* Could work for any language changing tesseract language.
* Update cards.json with new cards.