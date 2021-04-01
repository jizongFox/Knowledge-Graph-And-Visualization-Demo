FROM neo4j:3.5.27
COPY Import2Neo4j /var/lib/neo4j/import
COPY . /app

EXPOSE 5000
EXPOSE 7474
EXPOSE 7687
ENV NEO4J_AUTH=neo4j/123456
#RUN apt update && apt install software-properties-common && apt install python3.8
#ENTRYPOINT cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///event.csv" AS line CREATE (event:EVENT{e_id:line.e_id, time:line.time, text:line.text});'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///location.csv" AS line CREATE (location:LOCATION{l_id:line.l_id, locationName:line.location});'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///patient.csv" AS line CREATE (patient:PATIENT{p_id:line.p_id, patientName:line.name, age:line.age,gender:line.gender});'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///topic.csv" AS line CREATE (topic:TOPIC{t_id:line.t_id, topicName:line.topic});'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///event-location.csv" AS line MATCH (FROM:EVENT{e_id:line.e_id}), (TO:LOCATION{l_id:line.l_id}) MERGE (FROM)-[EVENT_LOCATION: EVENT_LOCATION{type:"happenIn"}]->(TO);'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///event-topic.csv" AS line MATCH (FROM:EVENT{e_id:line.e_id}), (TO:TOPIC{t_id:line.t_id}) MERGE (FROM)-[EVENT_TOPIC: EVENT_TOPIC{type:"belong2"}]->(TO);'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///patient-event.csv" AS line MATCH (FROM:PATIENT{p_id:line.p_id}), (TO:EVENT{e_id:line.e_id}) MERGE (FROM)-[PATIENT_EVENT: PATIENT_EVENT{type:"hasEvent"}]->(TO);'
#CMD cypher-shell -u neo4j -p 123456 'LOAD CSV WITH HEADERS FROM "file:///patient-location.csv" AS line MATCH (FROM:PATIENT{p_id:line.p_id}), (TO:LOCATION{l_id:line.l_id}) MERGE (FROM)-[PATIENT_LOCATION: PATIENT_LOCATION{type:"diagnosedIn"}]->(TO);'


#CMD python KG-Search-Flask/app.py