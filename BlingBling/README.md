#Install neo4j enterprise
```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg
echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable 5' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j-enterprise=1:5.25.1
```
***Note:Java 17 or later***
#Restore backup file
```bash
sudo neo4j-admin database restore --from-path=neo4j-2024-10-27T12-05-17.backup
```
#Start neo4j server
```bash
sudo neo4j start
```
**Note:default username and password is neo4j**
