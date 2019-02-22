package cc.roja.photo;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.skife.jdbi.v2.DBI;

import org.apache.log4j.Logger;

@SuppressWarnings({"unused","WeakerAccess"})
public class Processor {
  private static final Logger LOG = Logger.getLogger(Processor.class);

  private DBI dbi;

  public Processor() {
    this.dbi = DatabaseManager.getDBI();
  }

  public String processPhoto(String imageKey) throws IOException {
    try (PhotoProcessorDAO dao = dbi.open(PhotoProcessorDAO.class)) {
      String id = dao.queryByPath(imageKey);
      if(id != null) {
        LOG.info(String.format("Skipping: [%s]", imageKey));
        return id;
      }
      LOG.info("Processing: " + imageKey);
      MetaDataExtractor metaDataExtractor = new MetaDataExtractor();

      File imageFile = ImageLoader.load(imageKey);

      List<String> keyInfo = parseKey(imageKey);

      ImageInfo imageInfo = new ImageInfo();
      metaDataExtractor.extract(imageFile, imageInfo);

      return dao.getOrCreateImage(keyInfo.get(2), imageKey, imageInfo);
    }
  }

  private List<String> parseKey(String imageKey) {
    // example key: "/2017/2017-08-22/20170822T113305_01.jpg"
    //              "/2003/20030522_Quebec_BikeTrip/dscn1650.jpg"
    // key structure: "/yyyy/yyyy-mm-dd/yyyymmddThhmm_##.jpg"

    String regex = "^(?<collection>[/][0-9]{4})(?<album>[/][0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2}[_A-Za-z0-9- ,']*)(?<image>[/a-zA-Z0-9._]+)";

    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(imageKey);
    boolean success = matcher.find();

    String collection = success ? matcher.group("collection") : null;
    String album = success ? matcher.group("album") : null;
    String image = success ? matcher.group("image") : null;

    LOG.debug("Collection: "+collection+", Album: "+album+", Image: "+image);

    return Arrays.asList( collection, album, image );
  }
}
