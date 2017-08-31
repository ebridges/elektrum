package cc.roja.photo;

import static cc.roja.photo.util.DateUtil.parseDate;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
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
      String collectionId = getCollection(dao, keyInfo.get(0));
      AlbumInfo albumInfo = getAlbum(dao, collectionId, keyInfo.get(0) + keyInfo.get(1));

      ImageInfo imageInfo = new ImageInfo(albumInfo);
      metaDataExtractor.extract(imageFile, imageInfo);

      String artistName = imageInfo.getArtist();
      String artistId = getArtist(dao, artistName);

      return dao.getOrCreateImage(keyInfo.get(2), imageKey, imageInfo, albumInfo.getId(), artistId);
    }
  }

  private String getArtist(PhotoProcessorDAO dao, String artistName) {
    String artistId = null;
    if(artistName != null) {
      artistId = dao.getOrCreateArtist(artistName);
    }
    return artistId;
  }

  private AlbumInfo getAlbum(PhotoProcessorDAO dao, String collectionId, String path) {
    String regex = "(?<name>(?<date>[0-9]{4}[-]?[0-9]{2}[-]?[0-9]{0,2})(?<caption>[_A-Za-z0-9- ,']*))$";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(path);
    boolean success = matcher.find();
    if(!success) {
      throw new IllegalArgumentException("invalid album path: "+path);
    }

    String name = matcher.group("name");
    String date = matcher.group("date");
    String caption = matcher.group("caption");

    AlbumInfo albumInfo = albumInfo(name, path, date, caption, collectionId);

    String id = dao.getOrCreateAlbum(albumInfo);
    albumInfo.setId(id);

    return albumInfo;
  }

  private AlbumInfo albumInfo(String name, String path, String date, String caption, String collectionId) {
    LocalDate albumDate = parseDate(date);
    String albumCaption = null;
    if(caption != null && !caption.isEmpty()) {
      albumCaption = caption.replace("_", " ").trim();
    }

    return new AlbumInfo(
        name,
        path,
        albumCaption,
        null, // no source for this at this time.
        albumDate,
        collectionId
    );
  }


  private String getCollection(PhotoProcessorDAO dao, String path) {
    if(!path.matches("^/[0-9]{4}$")) {
      throw new IllegalArgumentException("invalid collection path: "+path);
    }

    String name = path.substring(1);
    return dao.getOrCreateCollection(name, path);
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
