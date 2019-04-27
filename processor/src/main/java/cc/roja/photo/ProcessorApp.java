package cc.roja.photo;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Scanner;

import cc.roja.photo.model.ImageKey;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static java.lang.String.format;

public class ProcessorApp {
  private static final Logger LOG = LogManager.getLogger(ProcessorApp.class);

  public static void main(String[] args) throws IOException {
    String arg = args[0];
    if("-h".equals(arg)) {
      printUsage();
    } else if("-f".equals(arg)) {
      processSingleFile(args[1]);
    } else if("-F".equals(arg)) {
      processFilesFromInputFile(args[1]);
    } else {
      processFilesFromInput(System.in);
    }
  }

  private static void processSingleFile(String filename) throws IOException {
    Processor processor = new Processor();
    ImageKey imageKey = new ImageKey();
    imageKey.parse(filename);
    String imageId = processor.processPhoto(imageKey);
    printOutput(imageId);
  }

  private static void processFilesFromInputFile(String inputFile) throws IOException {
    InputStream inputStream = new FileInputStream(inputFile);
    processFilesFromInput(inputStream);
  }

  private static void processFilesFromInput(InputStream inputStream) throws IOException {
    Processor processor = new Processor();
    try (Scanner input = new Scanner(inputStream)) {
      int cnt = 0;
      while (input.hasNextLine()) {
        ImageKey imageKey = new ImageKey();
        imageKey.parse(input.nextLine());
        String imageId = processor.processPhoto(imageKey);
        cnt++;
        printOutput(imageId);
      }
      LOG.info(format("Processed %d files.", cnt));
    }
  }

  private static void printOutput(String imageId) {
    System.out.println("ImageId: "+imageId);
  }

  private static void printUsage() {
    System.err.println(
        "Usage: java cc.roja.photo.ProcessorApp [-h|-f (filename)|-F (filename)]\n" +
            "\t-h\tDisplay this help.\n" +
            "\t-f\tProcess named file.\n" +
            "\t-F\tProcess list of files from given file.\n" +
            "\tElse reads a list of filenames from stdin.\n" +
        "Environment Variables:\n" +
            "\tDB_JDBC_URL - URL of metadata database.\n" +
            "\tDB_USERNAME - Username for metadata database access.\n" +
            "\tDB_PASSWORD - Password for metadata database access.\n"
    );
  }
}
