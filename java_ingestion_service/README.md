# Java Ingestion Service

This Spring Boot microservice watches a directory for new PDF or DOCX files and prints detected change entries. It mirrors the functionality of `release_analysis/ingestion.py`.

## Build

```bash
mvn package
```

## Run

```bash
java -jar target/java-ingestion-service-0.1.0.jar /path/to/watch
```

Each time a document is added to the folder, the service extracts text using PDFBox or Apache POI, naively segments by sentences, and prints the changes to the console.
