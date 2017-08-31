package cc.roja.photo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import org.apache.log4j.Logger;

public class ProcessorApp {
  private static final Logger LOG = Logger.getLogger(ProcessorApp.class);

  public static void main(String[] args) throws IOException {
    String arg = args[0];
    Processor processor = new Processor();
    if("-f".equals(arg)) {
      processFiles(processor, args[1]);
    } else {
      String imageId = processor.processPhoto(arg);
      LOG.info("imageId: " + imageId);
    }
  }

  private static void processFiles(Processor processor, String fileList) throws IOException {
    File fl = new File(fileList);
    FileReader frd = new FileReader(fl);
    try(BufferedReader brd = new BufferedReader(frd)) {
      String imageKey;
      while ((imageKey = brd.readLine()) != null) {
        String imageId = processor.processPhoto(imageKey);
        LOG.info("imageId: " + imageId);
      }
    }
  }
}
