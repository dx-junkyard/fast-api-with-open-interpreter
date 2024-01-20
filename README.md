# fast-api-with-open-interpreter

## export requirements

```bash
$ poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Docker

1. Build image

```bash
docker build -t fast-api-with-open-interpreter .
```

2. Run container

```bash
docker run -it --env-file=.env --rm -d --name mycontainer -p 80:80 fast-api-with-open-interpreter
```
3. Docker push

```bash
docker container commit <container-id> <hub-user>/<repo-name>[:<tag>]

docker tag <image-id> <repo-name>

docker push <hub-user>/<repo-name>[:<tag>]
```