package com.example.ingestion; // root package for the service

import java.io.IOException; // basic I/O exceptions
import java.nio.file.*; // file watch utilities
import java.util.List; // collections
import java.util.stream.Stream; // simple stream processing

import org.apache.pdfbox.pdmodel.PDDocument; // PDF parsing
import org.apache.pdfbox.text.PDFTextStripper; // extract text from PDF
import org.apache.poi.xwpf.usermodel.XWPFDocument; // handle DOCX
import org.apache.poi.xwpf.usermodel.XWPFParagraph; // DOCX paragraphs
import org.springframework.boot.CommandLineRunner; // boot utility for CLI
import org.springframework.context.annotation.Bean; // define beans
import org.springframework.context.annotation.Configuration; // configuration class
import java.util.logging.Logger; // built-in logging

@Configuration // marks this as a configuration component
public class DocumentWatcher {

    private static final Logger LOG = Logger.getLogger(DocumentWatcher.class.getName()); // logger instance

    @Bean // run automatically when the application starts
    CommandLineRunner watchRunner() {
        return args -> { // lambda executed at startup with CLI args
            if (args.length == 0) {
                LOG.severe("Folder path required");
                return;
            }
            Path folder = Paths.get(args[0]); // path to watch
            if (!Files.isDirectory(folder)) {
                LOG.severe("Not a directory: " + folder);
                return;
            }
            WatchService watcher = FileSystems.getDefault().newWatchService(); // create watcher
            folder.register(watcher, StandardWatchEventKinds.ENTRY_CREATE); // listen for new files
            LOG.info("Watching folder: " + folder);
            while (true) { // main watch loop
                WatchKey key = watcher.take(); // block until event
                for (WatchEvent<?> event : key.pollEvents()) { // process events
                    WatchEvent.Kind<?> kind = event.kind();
                    if (kind == StandardWatchEventKinds.OVERFLOW) {
                        continue; // skip overflow events
                    }
                    Path filename = ((WatchEvent<Path>) event).context(); // file name
                    Path filePath = folder.resolve(filename); // absolute path
                    if (filename.toString().toLowerCase().endsWith(".pdf") ||
                        filename.toString().toLowerCase().endsWith(".docx")) {
                        LOG.info("Found document: " + filePath);
                        List<String> sentences = parseFile(filePath); // extract text
                        for (int i = 0; i < sentences.size(); i++) {
                            LOG.info(String.format("Change %d: %s", i + 1, sentences.get(i)));
                        }
                    }
                }
                boolean valid = key.reset(); // prepare for next iteration
                if (!valid) {
                    break; // exit if key is invalid
                }
            }
        };
    }

    private List<String> parseFile(Path path) throws IOException {
        String text; // hold extracted text
        if (path.toString().toLowerCase().endsWith(".pdf")) {
            // parse PDF files
            try (PDDocument doc = PDDocument.load(path.toFile())) {
                PDFTextStripper stripper = new PDFTextStripper();
                text = stripper.getText(doc);
            }
        } else {
            // parse DOCX files
            try (XWPFDocument doc = new XWPFDocument(Files.newInputStream(path))) {
                StringBuilder sb = new StringBuilder();
                for (XWPFParagraph p : doc.getParagraphs()) {
                    sb.append(p.getText()).append("\n"); // gather text
                }
                text = sb.toString();
            }
        }
        // naive segmentation by period
        try (Stream<String> stream = Stream.of(text.split("\\.\n?"))) {
            return stream.map(String::trim).filter(s -> !s.isEmpty()).toList();
        }
    }
}
