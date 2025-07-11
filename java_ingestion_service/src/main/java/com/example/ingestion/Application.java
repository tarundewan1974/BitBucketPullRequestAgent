package com.example.ingestion; // root package

import org.springframework.boot.SpringApplication; // boot entry
import org.springframework.boot.autoconfigure.SpringBootApplication; // enable auto config

@SpringBootApplication // standard Spring Boot configuration
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args); // delegate to Spring
    }
}
