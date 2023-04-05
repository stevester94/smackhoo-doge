ssh dev.ssmackey.com 'docker kill doge-prod ; docker rm doge-prod; docker pull ssmackey/smackhoo-doge; docker run --name doge-prod -td --network=host --restart always ssmackey/smackhoo-doge ./server.py 5984'

