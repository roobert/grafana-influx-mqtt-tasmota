rebuild:
  docker-compose build mqttbridge

create-network:
  docker create network network0

create-db:
  curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE plugs"

test-db:
  curl -G 'http://localhost:8086/query?pretty=true' --data-urlencode "db=plugs" --data-urlencode "q=\"SHOW MEASUREMENTS\""
